from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, time, timezone
from pathlib import Path
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from .api import router as api_router
from .database import Base, SessionLocal, engine, get_db
from .migrations import ensure_schema_compatibility
from .models import Alert, Incident, Runbook, RunbookExecution, Service
from .seed import seed_database


BASE_DIR = Path(__file__).resolve().parent

HTTP_REQUESTS_TOTAL = Counter(
    "opsforge_http_requests_total",
    "Total HTTP requests handled by OpsForge.",
    ["method", "route", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "opsforge_http_request_duration_seconds",
    "HTTP request latency in seconds for OpsForge.",
    ["method", "route", "status_code"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility(engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="OpsForge", version="0.2.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(api_router)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _route_label(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path or "unmatched"


@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - start_time
    labels = {
        "method": request.method,
        "route": _route_label(request),
        "status_code": str(response.status_code),
    }
    HTTP_REQUESTS_TOTAL.labels(**labels).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(**labels).observe(elapsed)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "opsforge"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is not ready.") from exc
    return {"status": "ready", "service": "opsforge"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
        select(Alert)
        .options(selectinload(Alert.service))
        .order_by(Alert.received_at.desc())
        .limit(5)
    ).all()
    actionable_alerts = db.scalars(
        select(Alert)
        .options(selectinload(Alert.service))
        .where(Alert.status != "resolved")
        .order_by(Alert.received_at.desc())
    ).all()
    incidents = db.scalars(
        select(Incident)
        .options(selectinload(Incident.service), selectinload(Incident.source_alert))
        .where(Incident.status != "resolved")
        .order_by(Incident.created_at.desc())
    ).all()
    runbooks = db.scalars(
        select(Runbook).where(Runbook.enabled.is_(True)).order_by(Runbook.name)
    ).all()
    recent_executions = db.scalars(
        select(RunbookExecution)
        .options(
            selectinload(RunbookExecution.runbook),
            selectinload(RunbookExecution.service),
            selectinload(RunbookExecution.incident),
        )
        .order_by(RunbookExecution.finished_at.desc())
        .limit(6)
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
            "actionable_alerts": actionable_alerts,
            "incidents": incidents,
            "runbooks": runbooks,
            "recent_executions": recent_executions,
        },
    )
