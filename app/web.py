from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, selectinload

from .database import get_db
from .models import Alert, AuditLog, Incident, Runbook, RunbookExecution, Service
from .runbooks import RUNBOOK_DEFINITIONS


BASE_DIR = Path(__file__).resolve().parent
router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


LABELS = {
    "healthy": "Opérationnel",
    "degraded": "Dégradé",
    "down": "Indisponible",
    "unknown": "Inconnu",
    "new": "Nouvelle",
    "acknowledged": "Acquittée",
    "resolved": "Résolu",
    "open": "Ouvert",
    "investigating": "En investigation",
    "info": "Information",
    "warning": "Avertissement",
    "critical": "Critique",
    "low": "Faible",
    "medium": "Moyen",
    "high": "Élevé",
    "manual": "Manuel",
    "automated": "Automatisé",
    "none": "Aucun contexte",
    "service": "Service requis",
    "incident": "Incident requis",
    "success": "Succès",
    "failed": "Échec",
}

ACTION_LABELS = {
    "service.created": "Service créé",
    "service.updated": "Service modifié",
    "alert.created": "Alerte créée",
    "alert.acknowledged": "Alerte acquittée",
    "alert.resolved": "Alerte résolue",
    "incident.declared": "Incident déclaré",
    "incident.updated": "Incident modifié",
    "incident.owner_changed": "Responsable modifié",
    "incident.status_changed": "Statut de l'incident modifié",
    "incident.runbook_executed": "Runbook exécuté sur l'incident",
    "runbook.created": "Runbook créé",
    "runbook.updated": "Runbook modifié",
    "runbook.executed": "Runbook exécuté",
}

ENTITY_LABELS = {
    "Service": "Service",
    "Alert": "Alerte",
    "Incident": "Incident",
    "Runbook": "Runbook",
    "RunbookExecution": "Exécution",
}


def _datetime_fr(value: datetime | None) -> str:
    if value is None:
        return "-"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


def _details_dict(value: str | None) -> dict[str, object]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {"detail": value}
    return parsed if isinstance(parsed, dict) else {"detail": parsed}


templates.env.filters["datetime_fr"] = _datetime_fr
templates.env.filters["label"] = lambda value: LABELS.get(value, value)
templates.env.filters["action_label"] = lambda value: ACTION_LABELS.get(value, value)
templates.env.filters["entity_label"] = lambda value: ENTITY_LABELS.get(value, value)
templates.env.filters["details_dict"] = _details_dict


def _base_context(
    request: Request,
    db: Session,
    *,
    page_title: str,
    active_nav: str,
) -> dict[str, object]:
    active_incident_count = db.scalar(
        select(func.count(Incident.id)).where(Incident.status != "resolved")
    ) or 0
    new_alert_count = db.scalar(
        select(func.count(Alert.id)).where(Alert.status == "new")
    ) or 0
    return {
        "request": request,
        "page_title": page_title,
        "active_nav": active_nav,
        "active_incident_count": active_incident_count,
        "new_alert_count": new_alert_count,
        "operator_name": "Dyllan",
    }


def _render(
    request: Request,
    db: Session,
    template_name: str,
    *,
    page_title: str,
    active_nav: str,
    **context: object,
):
    full_context = _base_context(
        request,
        db,
        page_title=page_title,
        active_nav=active_nav,
    )
    full_context.update(context)
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=full_context,
    )


def _active_incident_map(alerts: list[Alert]) -> dict[int, Incident]:
    active: dict[int, Incident] = {}
    for alert in alerts:
        candidates = [item for item in alert.source_incidents if item.status != "resolved"]
        if candidates:
            active[alert.id] = max(candidates, key=lambda item: item.created_at)
    return active


def _last_activity_map(db: Session, incident_ids: list[int]) -> dict[int, datetime]:
    if not incident_ids:
        return {}
    rows = db.execute(
        select(AuditLog.entity_id, func.max(AuditLog.created_at))
        .where(
            AuditLog.entity_type == "Incident",
            AuditLog.entity_id.in_(incident_ids),
        )
        .group_by(AuditLog.entity_id)
    ).all()
    return {entity_id: created_at for entity_id, created_at in rows if entity_id is not None}


@router.get("/dashboard")
def legacy_dashboard() -> RedirectResponse:
    return RedirectResponse(url="/overview", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/overview")
def overview(request: Request, db: Session = Depends(get_db)):
    incident_severity_order = case(
        (Incident.severity == "critical", 4),
        (Incident.severity == "high", 3),
        (Incident.severity == "medium", 2),
        (Incident.severity == "low", 1),
        else_=0,
    )
    active_incidents = db.scalars(
        select(Incident)
        .options(selectinload(Incident.service))
        .where(Incident.status != "resolved")
        .order_by(incident_severity_order.desc(), Incident.updated_at.desc())
    ).all()
    recent_alerts = db.scalars(
        select(Alert)
        .options(selectinload(Alert.service), selectinload(Alert.source_incidents))
        .order_by(Alert.received_at.desc())
        .limit(7)
    ).all()
    active_by_alert = _active_incident_map(recent_alerts)
    active_alert_ids = set(
        db.scalars(
            select(Incident.source_alert_id).where(
                Incident.source_alert_id.is_not(None), Incident.status != "resolved"
            )
        ).all()
    )
    alerts_without_incident = db.scalar(
        select(func.count(Alert.id)).where(
            Alert.status != "resolved",
            Alert.id.not_in(active_alert_ids) if active_alert_ids else True,
        )
    ) or 0
    impaired_services = db.scalars(
        select(Service)
        .where(Service.status.in_(["degraded", "down"]))
        .order_by(Service.status, Service.name)
    ).all()
    activity = db.scalars(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(7)
    ).all()
    stats = {
        "active_incidents": len(active_incidents),
        "critical_incidents": sum(item.severity == "critical" for item in active_incidents),
        "new_alerts": db.scalar(select(func.count(Alert.id)).where(Alert.status == "new")) or 0,
        "critical_alerts": db.scalar(
            select(func.count(Alert.id)).where(
                Alert.severity == "critical", Alert.status != "resolved"
            )
        )
        or 0,
        "alerts_without_incident": alerts_without_incident,
        "impaired_services": len(impaired_services),
    }
    return _render(
        request,
        db,
        "overview.html",
        page_title="Vue d'ensemble",
        active_nav="overview",
        stats=stats,
        incidents=active_incidents[:6],
        recent_alerts=recent_alerts,
        active_incident_by_alert=active_by_alert,
        impaired_services=impaired_services,
        activity=activity,
    )


@router.get("/alerts")
def alerts_list(
    request: Request,
    q: str = "",
    alert_status: str = Query(default="", alias="status"),
    severity: str = "",
    service_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Alert).options(
        selectinload(Alert.service), selectinload(Alert.source_incidents)
    )
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Alert.title.ilike(pattern),
                Alert.message.ilike(pattern),
                Alert.source.ilike(pattern),
            )
        )
    if alert_status:
        statement = statement.where(Alert.status == alert_status)
    if severity:
        statement = statement.where(Alert.severity == severity)
    if service_id is not None:
        statement = statement.where(Alert.service_id == service_id)
    alerts = db.scalars(statement.order_by(Alert.received_at.desc())).all()
    services = db.scalars(select(Service).order_by(Service.name)).all()
    return _render(
        request,
        db,
        "alerts/list.html",
        page_title="Alertes",
        active_nav="alerts",
        alerts=alerts,
        services=services,
        active_incident_by_alert=_active_incident_map(alerts),
        filters={
            "q": q,
            "status": alert_status,
            "severity": severity,
            "service_id": service_id,
        },
    )


@router.get("/alerts/new")
def alert_new(
    request: Request,
    service_id: int | None = None,
    db: Session = Depends(get_db),
):
    services = db.scalars(select(Service).order_by(Service.name)).all()
    return _render(
        request,
        db,
        "alerts/form.html",
        page_title="Créer une alerte",
        active_nav="alerts",
        services=services,
        selected_service_id=service_id,
    )


@router.get("/incidents")
def incidents_list(
    request: Request,
    q: str = "",
    incident_status: str = Query(default="active", alias="status"),
    severity: str = "",
    service_id: int | None = None,
    owner: str = "",
    db: Session = Depends(get_db),
):
    statement = select(Incident).options(
        selectinload(Incident.service), selectinload(Incident.source_alert)
    )
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(Incident.title.ilike(pattern), Incident.description.ilike(pattern))
        )
    if incident_status == "active":
        statement = statement.where(Incident.status != "resolved")
    elif incident_status:
        statement = statement.where(Incident.status == incident_status)
    if severity:
        statement = statement.where(Incident.severity == severity)
    if service_id is not None:
        statement = statement.where(Incident.service_id == service_id)
    if owner == "unassigned":
        statement = statement.where(or_(Incident.owner.is_(None), Incident.owner == ""))
    elif owner:
        statement = statement.where(Incident.owner == owner)

    incidents = db.scalars(statement.order_by(Incident.updated_at.desc())).all()
    services = db.scalars(select(Service).order_by(Service.name)).all()
    owners = db.scalars(
        select(Incident.owner)
        .where(Incident.owner.is_not(None), Incident.owner != "")
        .distinct()
        .order_by(Incident.owner)
    ).all()
    return _render(
        request,
        db,
        "incidents/list.html",
        page_title="Incidents",
        active_nav="incidents",
        incidents=incidents,
        services=services,
        owners=owners,
        last_activity=_last_activity_map(db, [item.id for item in incidents]),
        filters={
            "q": q,
            "status": incident_status,
            "severity": severity,
            "service_id": service_id,
            "owner": owner,
        },
    )


@router.get("/incidents/new")
def incident_new(
    request: Request,
    alert_id: int | None = None,
    service_id: int | None = None,
    db: Session = Depends(get_db),
):
    source_alert = None
    if alert_id is not None:
        source_alert = db.scalar(
            select(Alert)
            .options(selectinload(Alert.service), selectinload(Alert.source_incidents))
            .where(Alert.id == alert_id)
        )
        if source_alert is None:
            raise HTTPException(status_code=404, detail="Alerte introuvable.")
        active = _active_incident_map([source_alert]).get(source_alert.id)
        if active is not None:
            return RedirectResponse(
                url=f"/incidents/{active.id}", status_code=status.HTTP_303_SEE_OTHER
            )
        service_id = source_alert.service_id
    services = db.scalars(select(Service).order_by(Service.name)).all()
    return _render(
        request,
        db,
        "incidents/form.html",
        page_title="Déclarer un incident",
        active_nav="incidents",
        services=services,
        source_alert=source_alert,
        selected_service_id=service_id,
    )


@router.get("/incidents/{incident_id}")
def incident_detail(
    incident_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    incident = db.scalar(
        select(Incident)
        .options(selectinload(Incident.service), selectinload(Incident.source_alert))
        .where(Incident.id == incident_id)
    )
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable.")

    runbooks = db.scalars(
        select(Runbook).where(Runbook.enabled.is_(True)).order_by(Runbook.name)
    ).all()
    compatible_runbooks = [
        runbook
        for runbook in runbooks
        if runbook.required_context in {"none", "incident"}
        or (runbook.required_context == "service" and incident.service_id is not None)
    ]
    executions = db.scalars(
        select(RunbookExecution)
        .options(selectinload(RunbookExecution.runbook))
        .where(RunbookExecution.incident_id == incident.id)
        .order_by(RunbookExecution.finished_at.desc())
    ).all()
    logs = db.scalars(
        select(AuditLog)
        .where(AuditLog.entity_type == "Incident", AuditLog.entity_id == incident.id)
        .order_by(AuditLog.created_at.desc())
    ).all()
    if not any(log.action == "incident.declared" for log in logs):
        timeline: list[dict[str, object]] = [
            {
                "action": "incident.declared",
                "actor": incident.owner or "Système historique",
                "created_at": incident.created_at,
                "details": {"legacy_fallback": True},
            }
        ]
    else:
        timeline = []
    timeline.extend(
        {
            "action": log.action,
            "actor": log.actor,
            "created_at": log.created_at,
            "details": _details_dict(log.details),
        }
        for log in logs
    )
    timeline.sort(key=lambda item: item["created_at"], reverse=True)
    return _render(
        request,
        db,
        "incidents/detail.html",
        page_title=f"Incident #{incident.id}",
        active_nav="incidents",
        incident=incident,
        runbooks=compatible_runbooks,
        executions=executions,
        latest_execution=executions[0] if executions else None,
        timeline=timeline,
    )


@router.get("/services")
def services_list(
    request: Request,
    q: str = "",
    service_status: str = Query(default="", alias="status"),
    environment: str = "",
    db: Session = Depends(get_db),
):
    statement = select(Service)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Service.name.ilike(pattern),
                Service.slug.ilike(pattern),
                Service.description.ilike(pattern),
            )
        )
    if service_status:
        statement = statement.where(Service.status == service_status)
    if environment:
        statement = statement.where(Service.environment == environment)
    services = db.scalars(statement.order_by(Service.name)).all()
    environments = db.scalars(
        select(Service.environment).distinct().order_by(Service.environment)
    ).all()
    service_ids = [item.id for item in services]
    alert_counts = dict(
        db.execute(
            select(Alert.service_id, func.count(Alert.id))
            .where(Alert.service_id.in_(service_ids), Alert.status != "resolved")
            .group_by(Alert.service_id)
        ).all()
    ) if service_ids else {}
    incident_counts = dict(
        db.execute(
            select(Incident.service_id, func.count(Incident.id))
            .where(Incident.service_id.in_(service_ids), Incident.status != "resolved")
            .group_by(Incident.service_id)
        ).all()
    ) if service_ids else {}
    return _render(
        request,
        db,
        "services/list.html",
        page_title="Services",
        active_nav="services",
        services=services,
        environments=environments,
        alert_counts=alert_counts,
        incident_counts=incident_counts,
        filters={"q": q, "status": service_status, "environment": environment},
    )


@router.get("/services/new")
def service_new(request: Request, db: Session = Depends(get_db)):
    return _render(
        request,
        db,
        "services/form.html",
        page_title="Créer un service",
        active_nav="services",
        service=None,
    )


@router.get("/services/{service_id}/edit")
def service_edit(service_id: int, request: Request, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service introuvable.")
    return _render(
        request,
        db,
        "services/form.html",
        page_title=f"Modifier {service.name}",
        active_nav="services",
        service=service,
    )


@router.get("/services/{service_id}")
def service_detail(service_id: int, request: Request, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service introuvable.")
    alerts = db.scalars(
        select(Alert).where(Alert.service_id == service.id).order_by(Alert.received_at.desc())
    ).all()
    incidents = db.scalars(
        select(Incident)
        .where(Incident.service_id == service.id)
        .order_by(Incident.updated_at.desc())
    ).all()
    return _render(
        request,
        db,
        "services/detail.html",
        page_title=service.name,
        active_nav="services",
        service=service,
        alerts=alerts,
        incidents=incidents,
    )


@router.get("/runbooks")
def runbooks_list(
    request: Request,
    q: str = "",
    mode: str = "",
    enabled: str = "",
    db: Session = Depends(get_db),
):
    statement = select(Runbook)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(Runbook.name.ilike(pattern), Runbook.description.ilike(pattern))
        )
    if mode:
        statement = statement.where(Runbook.mode == mode)
    if enabled in {"true", "false"}:
        statement = statement.where(Runbook.enabled.is_(enabled == "true"))
    runbooks = db.scalars(statement.order_by(Runbook.name)).all()
    runbook_ids = [item.id for item in runbooks]
    execution_counts = dict(
        db.execute(
            select(RunbookExecution.runbook_id, func.count(RunbookExecution.id))
            .where(RunbookExecution.runbook_id.in_(runbook_ids))
            .group_by(RunbookExecution.runbook_id)
        ).all()
    ) if runbook_ids else {}
    return _render(
        request,
        db,
        "runbooks/list.html",
        page_title="Runbooks",
        active_nav="runbooks",
        runbooks=runbooks,
        execution_counts=execution_counts,
        filters={"q": q, "mode": mode, "enabled": enabled},
    )


@router.get("/runbooks/new")
def runbook_new(request: Request, db: Session = Depends(get_db)):
    automation_options = [item for item in RUNBOOK_DEFINITIONS if item["automation_key"]]
    return _render(
        request,
        db,
        "runbooks/form.html",
        page_title="Créer un runbook",
        active_nav="runbooks",
        runbook=None,
        automation_options=automation_options,
    )


@router.get("/runbooks/{runbook_id}/edit")
def runbook_edit(runbook_id: int, request: Request, db: Session = Depends(get_db)):
    runbook = db.get(Runbook, runbook_id)
    if runbook is None:
        raise HTTPException(status_code=404, detail="Runbook introuvable.")
    return _render(
        request,
        db,
        "runbooks/form.html",
        page_title=f"Modifier {runbook.name}",
        active_nav="runbooks",
        runbook=runbook,
        automation_options=[],
    )


@router.get("/runbooks/{runbook_id}")
def runbook_detail(runbook_id: int, request: Request, db: Session = Depends(get_db)):
    runbook = db.get(Runbook, runbook_id)
    if runbook is None:
        raise HTTPException(status_code=404, detail="Runbook introuvable.")
    executions = db.scalars(
        select(RunbookExecution)
        .options(
            selectinload(RunbookExecution.service),
            selectinload(RunbookExecution.incident),
        )
        .where(RunbookExecution.runbook_id == runbook.id)
        .order_by(RunbookExecution.finished_at.desc())
        .limit(30)
    ).all()
    services = db.scalars(select(Service).order_by(Service.name)).all()
    incidents = db.scalars(
        select(Incident)
        .where(Incident.status != "resolved")
        .order_by(Incident.updated_at.desc())
    ).all()
    return _render(
        request,
        db,
        "runbooks/detail.html",
        page_title=runbook.name,
        active_nav="runbooks",
        runbook=runbook,
        executions=executions,
        services=services,
        incidents=incidents,
    )


@router.get("/activity")
def activity_list(
    request: Request,
    q: str = "",
    entity_type: str = "",
    action: str = "",
    db: Session = Depends(get_db),
):
    statement = select(AuditLog)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                AuditLog.actor.ilike(pattern),
                AuditLog.action.ilike(pattern),
                AuditLog.details.ilike(pattern),
            )
        )
    if entity_type:
        statement = statement.where(AuditLog.entity_type == entity_type)
    if action:
        statement = statement.where(AuditLog.action == action)
    logs = db.scalars(statement.order_by(AuditLog.created_at.desc()).limit(200)).all()
    actions = db.scalars(select(AuditLog.action).distinct().order_by(AuditLog.action)).all()
    return _render(
        request,
        db,
        "activity.html",
        page_title="Activité",
        active_nav="activity",
        logs=logs,
        actions=actions,
        filters={"q": q, "entity_type": entity_type, "action": action},
    )


@router.get("/monitoring")
def monitoring(request: Request, db: Session = Depends(get_db)):
    services = db.scalars(select(Service).order_by(Service.name)).all()
    return _render(
        request,
        db,
        "monitoring.html",
        page_title="Monitoring",
        active_nav="monitoring",
        services=services,
    )


@router.get("/help")
def help_page(request: Request, db: Session = Depends(get_db)):
    return _render(
        request,
        db,
        "help.html",
        page_title="Aide",
        active_nav="help",
    )
