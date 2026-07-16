from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import get_db
from .domain import (
    ALERT_TRANSITIONS,
    INCIDENT_TRANSITIONS,
    add_audit_log,
    operator_from_request,
    transition_allowed,
)
from .models import Alert, AuditLog, Incident, Runbook, RunbookExecution, Service, utc_now
from .runbooks import approved_automation_keys, execute_runbook
from .schemas import (
    AlertCreate,
    AlertRead,
    AuditLogRead,
    IncidentCreate,
    IncidentRead,
    IncidentStatusUpdate,
    IncidentUpdate,
    RunbookCreate,
    RunbookExecutionRead,
    RunbookExecutionRequest,
    RunbookRead,
    RunbookUpdate,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)


router = APIRouter(prefix="/api")


def _commit_unique(db: Session, detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=detail) from exc


def _flush_unique(db: Session, detail: str) -> None:
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=detail) from exc


@router.get("/services", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)):
    return db.scalars(select(Service).order_by(Service.name)).all()


@router.post("/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    service = Service(**payload.model_dump())
    db.add(service)
    _flush_unique(db, "Ce slug de service existe déjà.")
    add_audit_log(
        db,
        action="service.created",
        entity_type="Service",
        entity_id=service.id,
        actor=operator_from_request(request),
        details={"slug": service.slug, "status": service.status},
    )
    _commit_unique(db, "Ce slug de service existe déjà.")
    db.refresh(service)
    return service


@router.get("/services/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service introuvable.")
    return service


@router.patch("/services/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service introuvable.")

    changes: dict[str, dict[str, object | None]] = {}
    for field, value in payload.model_dump(exclude_unset=True).items():
        previous = getattr(service, field)
        if previous != value:
            changes[field] = {"from": previous, "to": value}
            setattr(service, field, value)
    if changes:
        add_audit_log(
            db,
            action="service.updated",
            entity_type="Service",
            entity_id=service.id,
            actor=operator_from_request(request),
            details={"changes": changes},
        )
    _commit_unique(db, "Ce slug de service existe déjà.")
    db.refresh(service)
    return service


@router.get("/alerts", response_model=list[AlertRead])
def list_alerts(db: Session = Depends(get_db)):
    return db.scalars(select(Alert).order_by(Alert.received_at.desc())).all()


@router.post("/alerts", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: AlertCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    if data["status"] != "new":
        raise HTTPException(status_code=422, detail="Une nouvelle alerte doit commencer à l'état new.")
    if data["service_id"] is not None and db.get(Service, data["service_id"]) is None:
        raise HTTPException(status_code=404, detail="Service introuvable.")

    alert = Alert(**data)
    if alert.status == "resolved":
        alert.resolved_at = utc_now()
    db.add(alert)
    db.flush()
    add_audit_log(
        db,
        action="alert.created",
        entity_type="Alert",
        entity_id=alert.id,
        actor=operator_from_request(request),
        details={
            "service_id": alert.service_id,
            "severity": alert.severity,
            "status": alert.status,
            "source": alert.source,
        },
    )
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/alerts/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerte introuvable.")
    return alert


@router.get("/alerts/{alert_id}/active-incident", response_model=IncidentRead | None)
def get_alert_active_incident(alert_id: int, db: Session = Depends(get_db)):
    if db.get(Alert, alert_id) is None:
        raise HTTPException(status_code=404, detail="Alerte introuvable.")
    return db.scalar(
        select(Incident)
        .where(Incident.source_alert_id == alert_id, Incident.status != "resolved")
        .order_by(Incident.created_at.desc())
    )


def _transition_alert(
    alert_id: int,
    target: str,
    request: Request,
    db: Session,
) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerte introuvable.")
    if not transition_allowed(ALERT_TRANSITIONS, alert.status, target):
        raise HTTPException(
            status_code=409,
            detail=f"Transition d'alerte impossible : {alert.status} vers {target}.",
        )
    if alert.status == target:
        return alert

    previous = alert.status
    alert.status = target
    alert.resolved_at = utc_now() if target == "resolved" else None
    add_audit_log(
        db,
        action=f"alert.{target}",
        entity_type="Alert",
        entity_id=alert.id,
        actor=operator_from_request(request),
        details={"from": previous, "to": target, "service_id": alert.service_id},
    )
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertRead)
def acknowledge_alert(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    return _transition_alert(alert_id, "acknowledged", request, db)


@router.patch("/alerts/{alert_id}/resolve", response_model=AlertRead)
def resolve_alert(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    return _transition_alert(alert_id, "resolved", request, db)


@router.get("/incidents", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    return db.scalars(select(Incident).order_by(Incident.created_at.desc())).all()


@router.post("/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    source_alert = None

    if data["status"] != "open":
        raise HTTPException(status_code=422, detail="Un incident déclaré doit commencer à l'état open.")

    if data["source_alert_id"] is None:
        if data["service_id"] is None or not (data["description"] or "").strip():
            raise HTTPException(
                status_code=422,
                detail="Un incident manuel nécessite un service et une description.",
            )
    if data["service_id"] is not None and db.get(Service, data["service_id"]) is None:
        raise HTTPException(status_code=404, detail="Service introuvable.")

    if data["source_alert_id"] is not None:
        source_alert = db.get(Alert, data["source_alert_id"])
        if source_alert is None:
            raise HTTPException(status_code=404, detail="Alerte source introuvable.")
        active_incident = db.scalar(
            select(Incident)
            .where(
                Incident.source_alert_id == source_alert.id,
                Incident.status != "resolved",
            )
            .order_by(Incident.created_at.desc())
        )
        if active_incident is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cette alerte possède déjà l'incident actif #{active_incident.id}."
                ),
            )
        if (
            data["service_id"] is not None
            and source_alert.service_id is not None
            and data["service_id"] != source_alert.service_id
        ):
            raise HTTPException(
                status_code=409,
                detail="Le service de l'incident doit correspondre à celui de l'alerte.",
            )
        if data["service_id"] is None:
            data["service_id"] = source_alert.service_id
        if data["service_id"] is None:
            raise HTTPException(
                status_code=422,
                detail="L'alerte source doit être associée à un service.",
            )

    incident = Incident(**data)
    if incident.status == "resolved":
        incident.resolved_at = utc_now()
    db.add(incident)
    db.flush()
    add_audit_log(
        db,
        action="incident.declared",
        entity_type="Incident",
        entity_id=incident.id,
        actor=operator_from_request(request),
        details={
            "service_id": incident.service_id,
            "source_alert_id": incident.source_alert_id,
            "severity": incident.severity,
            "status": incident.status,
            "owner": incident.owner,
        },
    )
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/incidents/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable.")
    return incident


@router.patch("/incidents/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable.")
    if incident.status == "resolved":
        raise HTTPException(status_code=409, detail="Un incident résolu est en lecture seule.")

    changes: dict[str, dict[str, object | None]] = {}
    for field, value in payload.model_dump(exclude_unset=True).items():
        previous = getattr(incident, field)
        if previous != value:
            changes[field] = {"from": previous, "to": value}
            setattr(incident, field, value)
    if changes:
        incident.updated_at = utc_now()
        action = "incident.owner_changed" if set(changes) == {"owner"} else "incident.updated"
        add_audit_log(
            db,
            action=action,
            entity_type="Incident",
            entity_id=incident.id,
            actor=operator_from_request(request),
            details={"changes": changes},
        )
        db.commit()
        db.refresh(incident)
    return incident


@router.patch("/incidents/{incident_id}/status", response_model=IncidentRead)
def update_incident_status(
    incident_id: int,
    payload: IncidentStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable.")
    if not transition_allowed(INCIDENT_TRANSITIONS, incident.status, payload.status):
        raise HTTPException(
            status_code=409,
            detail=f"Transition d'incident impossible : {incident.status} vers {payload.status}.",
        )
    if incident.status == payload.status:
        return incident

    previous = incident.status
    incident.status = payload.status
    incident.updated_at = utc_now()
    incident.resolved_at = utc_now() if payload.status == "resolved" else None
    add_audit_log(
        db,
        action="incident.status_changed",
        entity_type="Incident",
        entity_id=incident.id,
        actor=operator_from_request(request),
        details={"from": previous, "to": payload.status},
    )
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/runbooks", response_model=list[RunbookRead])
def list_runbooks(db: Session = Depends(get_db)):
    return db.scalars(select(Runbook).order_by(Runbook.name)).all()


@router.post("/runbooks", response_model=RunbookRead, status_code=status.HTTP_201_CREATED)
def create_runbook(
    payload: RunbookCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude={"steps"})
    if payload.automation_key and payload.automation_key not in approved_automation_keys():
        raise HTTPException(
            status_code=422,
            detail="Cette automatisation n'est pas dans la liste approuvée.",
        )
    runbook = Runbook(**data)
    runbook.steps = payload.steps
    db.add(runbook)
    _flush_unique(db, "Cette clé de runbook existe déjà.")
    add_audit_log(
        db,
        action="runbook.created",
        entity_type="Runbook",
        entity_id=runbook.id,
        actor=operator_from_request(request),
        details={
            "key": runbook.key,
            "mode": runbook.mode,
            "required_context": runbook.required_context,
        },
    )
    _commit_unique(db, "Cette clé de runbook existe déjà.")
    db.refresh(runbook)
    return runbook


@router.get("/runbooks/{runbook_id:int}", response_model=RunbookRead)
def get_runbook(runbook_id: int, db: Session = Depends(get_db)):
    runbook = db.get(Runbook, runbook_id)
    if runbook is None:
        raise HTTPException(status_code=404, detail="Runbook introuvable.")
    return runbook


@router.patch("/runbooks/{runbook_id:int}", response_model=RunbookRead)
def update_runbook(
    runbook_id: int,
    payload: RunbookUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    runbook = db.get(Runbook, runbook_id)
    if runbook is None:
        raise HTTPException(status_code=404, detail="Runbook introuvable.")

    changes: dict[str, object] = {}
    data = payload.model_dump(exclude_unset=True)
    steps = data.pop("steps", None)
    for field, value in data.items():
        if getattr(runbook, field) != value:
            changes[field] = {"from": getattr(runbook, field), "to": value}
            setattr(runbook, field, value)
    if steps is not None and runbook.steps != [step.strip() for step in steps if step.strip()]:
        changes["steps"] = {"from": runbook.steps, "to": steps}
        runbook.steps = steps
    if changes:
        add_audit_log(
            db,
            action="runbook.updated",
            entity_type="Runbook",
            entity_id=runbook.id,
            actor=operator_from_request(request),
            details={"changes": changes},
        )
        db.commit()
        db.refresh(runbook)
    return runbook


@router.post("/runbooks/{runbook_key}/execute", response_model=RunbookExecutionRead)
def execute_runbook_route(
    runbook_key: str,
    payload: RunbookExecutionRequest | None = None,
    db: Session = Depends(get_db),
):
    runbook = db.scalar(select(Runbook).where(Runbook.key == runbook_key))
    if runbook is None:
        raise HTTPException(status_code=404, detail="Runbook introuvable.")
    if not runbook.enabled:
        raise HTTPException(status_code=409, detail="Ce runbook est désactivé.")
    return execute_runbook(db, runbook, payload or RunbookExecutionRequest())


@router.get("/runbook-executions", response_model=list[RunbookExecutionRead])
def list_runbook_executions(db: Session = Depends(get_db)):
    return db.scalars(
        select(RunbookExecution).order_by(RunbookExecution.finished_at.desc()).limit(100)
    ).all()


@router.get("/audit-logs", response_model=list[AuditLogRead])
def list_audit_logs(db: Session = Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()
