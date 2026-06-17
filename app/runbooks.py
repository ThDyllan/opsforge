from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuditLog, Incident, Runbook, RunbookExecution, Service, utc_now
from .schemas import RunbookExecutionRequest


RUNBOOK_DEFINITIONS = [
    {
        "key": "health_check_service",
        "name": "Health check service",
        "description": "Reports the current OpsForge status for one service or all services.",
    },
    {
        "key": "generate_incident_report",
        "name": "Generate incident report",
        "description": "Creates a short text report for an incident or open incidents.",
    },
    {
        "key": "mark_incident_resolved",
        "name": "Mark incident resolved",
        "description": "Marks a selected incident as resolved inside OpsForge.",
    },
    {
        "key": "simulate_backup_check",
        "name": "Simulate backup check",
        "description": "Runs a safe demo backup status check without shell commands.",
    },
    {
        "key": "restart_demo_service",
        "name": "Restart demo service",
        "description": "Simulates a restart action for documentation and demo purposes.",
    },
]


def _json_text(value: dict[str, object]) -> str:
    return json.dumps(value, sort_keys=True)


def execute_predefined_runbook(
    db: Session,
    runbook: Runbook,
    request: RunbookExecutionRequest,
) -> RunbookExecution:
    started_at = utc_now()
    status = "success"
    output = ""
    details: dict[str, object] = {"runbook_key": runbook.key}

    service = db.get(Service, request.service_id) if request.service_id is not None else None
    incident = db.get(Incident, request.incident_id) if request.incident_id is not None else None

    if request.service_id is not None and service is None:
        status = "failed"
        output = f"Service {request.service_id} was not found."
        details["requested_service_id"] = request.service_id
    elif request.incident_id is not None and incident is None:
        status = "failed"
        output = f"Incident {request.incident_id} was not found."
        details["requested_incident_id"] = request.incident_id
    elif runbook.key == "health_check_service":
        status, output, details = _health_check_service(db, service, details)
    elif runbook.key == "generate_incident_report":
        status, output, details = _generate_incident_report(db, incident, details)
    elif runbook.key == "mark_incident_resolved":
        status, output, details = _mark_incident_resolved(incident, details)
    elif runbook.key == "simulate_backup_check":
        output = "Backup check simulation completed successfully. Latest demo backup is valid."
        details["backup_status"] = "valid"
    elif runbook.key == "restart_demo_service":
        status, output, details = _restart_demo_service(service, details)
    else:
        status = "failed"
        output = f"Runbook '{runbook.key}' is not implemented in MVP1."

    finished_at = utc_now()
    execution = RunbookExecution(
        runbook_id=runbook.id,
        service_id=service.id if service else None,
        incident_id=incident.id if incident else None,
        status=status,
        requested_by=request.requested_by,
        output=output,
        details=_json_text(details),
        started_at=started_at,
        finished_at=finished_at,
    )
    db.add(execution)
    db.flush()

    audit_log = AuditLog(
        action="runbook.executed",
        entity_type="RunbookExecution",
        entity_id=execution.id,
        actor=request.requested_by,
        details=_json_text(
            {
                "runbook_key": runbook.key,
                "status": status,
                "output": output,
            }
        ),
    )
    db.add(audit_log)
    db.commit()
    db.refresh(execution)
    return execution


def _health_check_service(
    db: Session,
    service: Service | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    if service:
        output = f"Service {service.slug} is currently {service.status} in {service.environment}."
        details["service"] = {
            "slug": service.slug,
            "status": service.status,
            "environment": service.environment,
        }
        return "success", output, details

    services = db.scalars(select(Service).order_by(Service.slug)).all()
    status_counts: dict[str, int] = {}
    for item in services:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1

    details["service_count"] = len(services)
    details["status_counts"] = status_counts
    return "success", f"Checked {len(services)} services. Status summary: {status_counts}.", details


def _generate_incident_report(
    db: Session,
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    if incident:
        details["incident"] = {
            "id": incident.id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
        }
        output = (
            f"Incident #{incident.id}: {incident.title}. "
            f"Severity={incident.severity}, status={incident.status}."
        )
        return "success", output, details

    open_incidents = db.scalars(
        select(Incident).where(Incident.status != "resolved").order_by(Incident.created_at.desc())
    ).all()
    details["open_incident_count"] = len(open_incidents)
    details["open_incident_ids"] = [item.id for item in open_incidents]
    return "success", f"Generated summary for {len(open_incidents)} open incidents.", details


def _mark_incident_resolved(
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    if incident is None:
        details["reason"] = "incident_id is required"
        return "failed", "mark_incident_resolved requires an incident_id.", details

    incident.status = "resolved"
    incident.resolved_at = utc_now()
    details["incident_id"] = incident.id
    return "success", f"Incident #{incident.id} was marked resolved.", details


def _restart_demo_service(
    service: Service | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    if service:
        details["service"] = {"id": service.id, "slug": service.slug}
        return "success", f"Simulated restart for service {service.slug}.", details

    details["scope"] = "demo"
    return "success", "Simulated restart completed for demo service group.", details
