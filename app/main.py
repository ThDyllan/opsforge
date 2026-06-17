from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, time, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import Alert, AuditLog, Incident, Runbook, Service, utc_now
from .runbooks import execute_predefined_runbook
from .schemas import (
    AlertCreate,
    AlertRead,
    AuditLogRead,
    IncidentCreate,
    IncidentRead,
    IncidentStatusUpdate,
    RunbookExecutionRead,
    RunbookExecutionRequest,
    RunbookRead,
    ServiceCreate,
    ServiceRead,
)
from .seed import seed_database


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="OpsForge", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "opsforge"}


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/dashboard", include_in_schema=False)
def dashboard(request: Request, db: Session = Depends(get_db)):
    today_start = datetime.combine(date.today(), time.min, tzinfo=timezone.utc)
    total_services = db.scalar(select(func.count(Service.id))) or 0
    open_incidents = (
        db.scalar(select(func.count(Incident.id)).where(Incident.status != "resolved")) or 0
    )
    alerts_today = (
        db.scalar(select(func.count(Alert.id)).where(Alert.received_at >= today_start)) or 0
    )
    services = db.scalars(select(Service).order_by(Service.name)).all()
    recent_alerts = db.scalars(
        select(Alert).order_by(Alert.received_at.desc()).limit(5)
    ).all()
    incidents = db.scalars(
        select(Incident).where(Incident.status != "resolved").order_by(Incident.created_at.desc())
    ).all()
    runbooks = db.scalars(
        select(Runbook).where(Runbook.enabled.is_(True)).order_by(Runbook.name)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "total_services": total_services,
            "open_incidents": open_incidents,
            "alerts_today": alerts_today,
            "services": services,
            "recent_alerts": recent_alerts,
            "incidents": incidents,
            "runbooks": runbooks,
        },
    )


@app.get("/api/services", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)):
    return db.scalars(select(Service).order_by(Service.name)).all()


@app.post("/api/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(**payload.model_dump())
    db.add(service)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service slug already exists.") from exc
    db.refresh(service)
    return service


@app.get("/api/services/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found.")
    return service


@app.get("/api/alerts", response_model=list[AlertRead])
def list_alerts(db: Session = Depends(get_db)):
    return db.scalars(select(Alert).order_by(Alert.received_at.desc())).all()


@app.post("/api/alerts", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if data["service_id"] is not None and db.get(Service, data["service_id"]) is None:
        raise HTTPException(status_code=404, detail="Service not found.")

    alert = Alert(**data)
    if alert.status == "resolved":
        alert.resolved_at = utc_now()
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@app.get("/api/alerts/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return alert


@app.patch("/api/alerts/{alert_id}/acknowledge", response_model=AlertRead)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.status = "acknowledged"
    alert.resolved_at = None
    db.commit()
    db.refresh(alert)
    return alert


@app.patch("/api/alerts/{alert_id}/resolve", response_model=AlertRead)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.status = "resolved"
    alert.resolved_at = utc_now()
    db.commit()
    db.refresh(alert)
    return alert


@app.get("/api/incidents", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    return db.scalars(select(Incident).order_by(Incident.created_at.desc())).all()


@app.post("/api/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()

    if data["service_id"] is not None and db.get(Service, data["service_id"]) is None:
        raise HTTPException(status_code=404, detail="Service not found.")

    source_alert = None
    if data["source_alert_id"] is not None:
        source_alert = db.get(Alert, data["source_alert_id"])
        if source_alert is None:
            raise HTTPException(status_code=404, detail="Source alert not found.")
        if data["service_id"] is None and source_alert.service_id is not None:
            data["service_id"] = source_alert.service_id

    incident = Incident(**data)
    if incident.status == "resolved":
        incident.resolved_at = utc_now()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@app.get("/api/incidents/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return incident


@app.patch("/api/incidents/{incident_id}/status", response_model=IncidentRead)
def update_incident_status(
    incident_id: int,
    payload: IncidentStatusUpdate,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    incident.status = payload.status
    incident.resolved_at = utc_now() if payload.status == "resolved" else None
    db.commit()
    db.refresh(incident)
    return incident


@app.get("/api/runbooks", response_model=list[RunbookRead])
def list_runbooks(db: Session = Depends(get_db)):
    return db.scalars(select(Runbook).order_by(Runbook.name)).all()


@app.post("/api/runbooks/{runbook_key}/execute", response_model=RunbookExecutionRead)
def execute_runbook(
    runbook_key: str,
    payload: RunbookExecutionRequest | None = None,
    db: Session = Depends(get_db),
):
    runbook = db.scalar(select(Runbook).where(Runbook.key == runbook_key))
    if runbook is None:
        raise HTTPException(status_code=404, detail="Runbook not found.")
    if not runbook.enabled:
        raise HTTPException(status_code=409, detail="Runbook is disabled.")
    request = payload or RunbookExecutionRequest()
    return execute_predefined_runbook(db, runbook, request)


@app.get("/api/audit-logs", response_model=list[AuditLogRead])
def list_audit_logs(db: Session = Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(50)).all()
