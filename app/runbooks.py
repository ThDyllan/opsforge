from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import INCIDENT_TRANSITIONS, add_audit_log, json_text, transition_allowed
from .models import Incident, Runbook, RunbookExecution, Service, utc_now
from .schemas import RunbookExecutionRequest


RUNBOOK_DEFINITIONS = [
    {
        "key": "health_check_service",
        "name": "Vérifier l'état d'un service",
        "description": "Lit l'état de démonstration actuellement enregistré pour un service.",
        "mode": "automated",
        "instructions": "Utiliser cette action pour confirmer le contexte avant une investigation.",
        "steps": ["Identifier le service", "Lire son état et son environnement"],
        "required_context": "service",
        "risk_level": "low",
        "automation_key": "health_check_service",
    },
    {
        "key": "generate_incident_report",
        "name": "Générer le rapport d'incident",
        "description": "Produit un résumé textuel contrôlé de l'incident courant.",
        "mode": "automated",
        "instructions": "Exécuter après qualification pour conserver un résumé dans l'historique.",
        "steps": ["Lire l'incident", "Produire le résumé"],
        "required_context": "incident",
        "risk_level": "low",
        "automation_key": "generate_incident_report",
    },
    {
        "key": "mark_incident_resolved",
        "name": "Clôturer l'incident",
        "description": "Passe un incident en investigation à l'état résolu.",
        "mode": "automated",
        "instructions": "À utiliser uniquement après validation du retour à la normale.",
        "steps": ["Vérifier le diagnostic", "Confirmer le retour à la normale"],
        "required_context": "incident",
        "risk_level": "medium",
        "automation_key": "mark_incident_resolved",
    },
    {
        "key": "simulate_backup_check",
        "name": "Contrôler la sauvegarde de démonstration",
        "description": "Simule un contrôle d'archive sans lancer de commande système.",
        "mode": "automated",
        "instructions": "Cette automatisation est une simulation explicitement identifiée.",
        "steps": ["Lire l'état simulé", "Enregistrer le résultat"],
        "required_context": "service",
        "risk_level": "low",
        "automation_key": "simulate_backup_check",
    },
    {
        "key": "restart_demo_service",
        "name": "Simuler le redémarrage d'un service",
        "description": "Enregistre une simulation de redémarrage, sans action sur l'hôte.",
        "mode": "automated",
        "instructions": "Aucune commande système n'est exécutée par cette action.",
        "steps": ["Confirmer le service", "Enregistrer la simulation"],
        "required_context": "service",
        "risk_level": "medium",
        "automation_key": "restart_demo_service",
    },
    {
        "key": "diagnostic_echec_sauvegarde",
        "name": "Diagnostiquer un échec de sauvegarde",
        "description": "Checklist manuelle pour qualifier l'incident de sauvegarde de démonstration.",
        "mode": "manual",
        "instructions": "Suivre les étapes puis confirmer le résultat observé dans OpsForge.",
        "steps": [
            "Confirmer le service et l'alerte à l'origine de l'incident.",
            "Vérifier l'horodatage de la dernière sauvegarde de démonstration.",
            "Contrôler le résultat simulé de l'archive.",
            "Documenter la conclusion avant de clôturer l'incident.",
        ],
        "required_context": "incident",
        "risk_level": "low",
        "automation_key": None,
    },
]


def approved_automation_keys() -> set[str]:
    return set(AUTOMATION_HANDLERS)


def execute_runbook(
    db: Session,
    runbook: Runbook,
    request: RunbookExecutionRequest,
) -> RunbookExecution:
    started_at = utc_now()
    status = "success"
    output = ""
    details: dict[str, object] = {
        "runbook_key": runbook.key,
        "mode": runbook.mode,
        "required_context": runbook.required_context,
    }

    service = db.get(Service, request.service_id) if request.service_id is not None else None
    incident = db.get(Incident, request.incident_id) if request.incident_id is not None else None

    if incident is not None and service is None and incident.service_id is not None:
        service = db.get(Service, incident.service_id)

    if request.service_id is not None and service is None:
        status, output = "failed", f"Service {request.service_id} introuvable."
        details["requested_service_id"] = request.service_id
    elif request.incident_id is not None and incident is None:
        status, output = "failed", f"Incident {request.incident_id} introuvable."
        details["requested_incident_id"] = request.incident_id
    elif (
        service is not None
        and incident is not None
        and incident.service_id is not None
        and service.id != incident.service_id
    ):
        status, output = (
            "failed",
            f"Le service {service.id} ne correspond pas à l'incident {incident.id}.",
        )
        details["requested_service_id"] = service.id
        details["incident_service_id"] = incident.service_id
        service = None
    elif runbook.required_context == "service" and service is None:
        status, output = "failed", "Ce runbook nécessite un service."
    elif runbook.required_context == "incident" and incident is None:
        status, output = "failed", "Ce runbook nécessite un incident."
    elif runbook.mode == "manual":
        status, output, details = _complete_manual_runbook(runbook, request, details)
    else:
        handler = AUTOMATION_HANDLERS.get(runbook.automation_key or "")
        if handler is None:
            status, output = "failed", "Cette automatisation n'est pas approuvée."
        else:
            status, output, details = handler(db, service, incident, details)

    execution = RunbookExecution(
        runbook_id=runbook.id,
        service_id=service.id if service else None,
        incident_id=incident.id if incident else None,
        status=status,
        requested_by=request.requested_by,
        output=output,
        details=json_text(details),
        started_at=started_at,
        finished_at=utc_now(),
    )
    db.add(execution)
    db.flush()

    add_audit_log(
        db,
        action="runbook.executed",
        entity_type="RunbookExecution",
        entity_id=execution.id,
        actor=request.requested_by,
        details={
            "runbook_id": runbook.id,
            "runbook_key": runbook.key,
            "incident_id": incident.id if incident else None,
            "service_id": service.id if service else None,
            "status": status,
            "output": output,
        },
    )
    if incident is not None:
        if (
            runbook.automation_key == "mark_incident_resolved"
            and status == "success"
        ):
            add_audit_log(
                db,
                action="incident.status_changed",
                entity_type="Incident",
                entity_id=incident.id,
                actor=request.requested_by,
                details={"from": details.get("previous_status"), "to": "resolved"},
            )
        add_audit_log(
            db,
            action="incident.runbook_executed",
            entity_type="Incident",
            entity_id=incident.id,
            actor=request.requested_by,
            details={
                "execution_id": execution.id,
                "runbook_id": runbook.id,
                "runbook_name": runbook.name,
                "status": status,
                "output": output,
            },
        )

    db.commit()
    db.refresh(execution)
    return execution


def _complete_manual_runbook(
    runbook: Runbook,
    request: RunbookExecutionRequest,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    expected = set(range(len(runbook.steps)))
    completed = set(request.completed_steps)
    details["completed_steps"] = sorted(completed)
    details["step_count"] = len(expected)
    details["notes"] = request.notes

    if request.outcome is None:
        return "failed", "Le résultat de la procédure manuelle doit être confirmé.", details
    if request.outcome == "success" and expected and completed != expected:
        return "failed", "Toutes les étapes doivent être confirmées avant un succès.", details

    output = request.notes or "Procédure manuelle confirmée par l'opérateur."
    return request.outcome, output, details


def _health_check_service(
    db: Session,
    service: Service | None,
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    assert service is not None
    details["service"] = {
        "slug": service.slug,
        "status": service.status,
        "environment": service.environment,
        "status_source": "demo",
    }
    return (
        "success",
        f"Le service {service.name} est déclaré {service.status} dans {service.environment}.",
        details,
    )


def _generate_incident_report(
    db: Session,
    service: Service | None,
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    assert incident is not None
    details["incident"] = {
        "id": incident.id,
        "title": incident.title,
        "severity": incident.severity,
        "status": incident.status,
        "owner": incident.owner,
    }
    output = (
        f"Incident #{incident.id} - {incident.title}. "
        f"Sévérité={incident.severity}, statut={incident.status}, "
        f"responsable={incident.owner or 'non assigné'}."
    )
    return "success", output, details


def _mark_incident_resolved(
    db: Session,
    service: Service | None,
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    assert incident is not None
    if not transition_allowed(INCIDENT_TRANSITIONS, incident.status, "resolved"):
        details["current_status"] = incident.status
        return (
            "failed",
            "L'incident doit être en investigation avant sa résolution.",
            details,
        )

    previous_status = incident.status
    incident.status = "resolved"
    incident.resolved_at = utc_now()
    incident.updated_at = utc_now()
    details["incident_id"] = incident.id
    details["previous_status"] = previous_status
    return "success", f"L'incident #{incident.id} a été résolu.", details


def _simulate_backup_check(
    db: Session,
    service: Service | None,
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    details["backup_status"] = "valid_demo_archive"
    details["simulation"] = True
    return (
        "success",
        "Contrôle simulé terminé : l'archive de démonstration est lisible.",
        details,
    )


def _restart_demo_service(
    db: Session,
    service: Service | None,
    incident: Incident | None,
    details: dict[str, object],
) -> tuple[str, str, dict[str, object]]:
    assert service is not None
    details["service"] = {"id": service.id, "slug": service.slug}
    details["simulation"] = True
    return (
        "success",
        f"Redémarrage simulé pour {service.name}; aucune commande système exécutée.",
        details,
    )


AutomationHandler = Callable[
    [Session, Service | None, Incident | None, dict[str, object]],
    tuple[str, str, dict[str, object]],
]

AUTOMATION_HANDLERS: dict[str, AutomationHandler] = {
    "health_check_service": _health_check_service,
    "generate_incident_report": _generate_incident_report,
    "mark_incident_resolved": _mark_incident_resolved,
    "simulate_backup_check": _simulate_backup_check,
    "restart_demo_service": _restart_demo_service,
}


# Compatibility for imports used by the validated MVP tests and earlier documentation.
execute_predefined_runbook = execute_runbook
