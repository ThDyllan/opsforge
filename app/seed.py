from __future__ import annotations

import json
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import add_audit_log
from .models import Alert, Incident, Runbook, Service, utc_now
from .runbooks import RUNBOOK_DEFINITIONS


def seed_database(db: Session) -> None:
    services = _ensure_demo_services(db)
    _ensure_demo_signals(db, services)
    _ensure_runbooks(db)
    db.commit()


def _ensure_demo_services(db: Session) -> dict[str, Service]:
    definitions = [
        {
            "name": "API Gateway",
            "slug": "api-gateway",
            "description": "Point d'entrée public des API de démonstration.",
            "environment": "production",
            "status": "healthy",
            "owner": "Plateforme",
        },
        {
            "name": "Payment Service",
            "slug": "payment-service",
            "description": "Autorisation et capture des paiements de démonstration.",
            "environment": "production",
            "status": "degraded",
            "owner": "Dyllan",
        },
        {
            "name": "Inventory Service",
            "slug": "inventory-service",
            "description": "Disponibilité et réservation du stock de démonstration.",
            "environment": "production",
            "status": "healthy",
            "owner": "Supply",
        },
        {
            "name": "Notification Service",
            "slug": "notification-service",
            "description": "Envoi des notifications de démonstration.",
            "environment": "staging",
            "status": "unknown",
            "owner": "Plateforme",
        },
        {
            "name": "Backup Service",
            "slug": "backup-service",
            "description": "Représente le contrôle de sauvegarde PostgreSQL de démonstration.",
            "environment": "production",
            "status": "degraded",
            "owner": "Dyllan",
        },
    ]

    services: dict[str, Service] = {}
    for definition in definitions:
        service = db.scalar(select(Service).where(Service.slug == definition["slug"]))
        if service is None:
            service = Service(**definition)
            db.add(service)
            db.flush()
        services[definition["slug"]] = service
    return services


def _ensure_demo_signals(db: Session, services: dict[str, Service]) -> None:
    now = utc_now()
    primary_alert = db.scalar(
        select(Alert).where(
            Alert.source == "opsforge-demo",
            Alert.title == "Échec de la sauvegarde quotidienne",
        )
    )
    if primary_alert is None:
        primary_alert = Alert(
            service_id=services["backup-service"].id,
            source="opsforge-demo",
            title="Échec de la sauvegarde quotidienne",
            message=(
                "La sauvegarde planifiée n'a pas produit d'archive valide. "
                "Une investigation opérateur est requise."
            ),
            severity="critical",
            status="acknowledged",
            received_at=now - timedelta(minutes=42),
        )
        db.add(primary_alert)
        db.flush()

    primary_incident = db.scalar(
        select(Incident).where(
            Incident.source_alert_id == primary_alert.id,
            Incident.title == "Sauvegarde de production en échec",
        )
    )
    if primary_incident is None:
        primary_incident = Incident(
            service_id=services["backup-service"].id,
            source_alert_id=primary_alert.id,
            title="Sauvegarde de production en échec",
            description=(
                "La sauvegarde quotidienne de démonstration doit être diagnostiquée "
                "avant confirmation du retour à la normale."
            ),
            severity="critical",
            status="investigating",
            owner="Dyllan",
            created_at=now - timedelta(minutes=35),
            updated_at=now - timedelta(minutes=30),
        )
        db.add(primary_incident)
        db.flush()
        add_audit_log(
            db,
            action="incident.declared",
            entity_type="Incident",
            entity_id=primary_incident.id,
            actor="Dyllan",
            details={
                "service_id": primary_incident.service_id,
                "source_alert_id": primary_incident.source_alert_id,
                "severity": primary_incident.severity,
                "seeded_demo": True,
            },
        )
        add_audit_log(
            db,
            action="incident.status_changed",
            entity_type="Incident",
            entity_id=primary_incident.id,
            actor="Dyllan",
            details={"from": "open", "to": "investigating", "seeded_demo": True},
        )

    secondary_alert = db.scalar(
        select(Alert).where(
            Alert.source == "opsforge-demo",
            Alert.title == "Latence élevée sur le paiement",
        )
    )
    if secondary_alert is None:
        db.add(
            Alert(
                service_id=services["payment-service"].id,
                source="opsforge-demo",
                title="Latence élevée sur le paiement",
                message="Le temps de réponse dépasse le seuil de démonstration depuis 10 minutes.",
                severity="warning",
                status="new",
                received_at=now - timedelta(minutes=18),
            )
        )

    info_alert = db.scalar(
        select(Alert).where(
            Alert.source == "opsforge-demo",
            Alert.title == "Déploiement de l'API terminé",
        )
    )
    if info_alert is None:
        db.add(
            Alert(
                service_id=services["api-gateway"].id,
                source="opsforge-demo",
                title="Déploiement de l'API terminé",
                message="Le déploiement de démonstration est terminé et le service répond.",
                severity="info",
                status="resolved",
                received_at=now - timedelta(hours=3),
                resolved_at=now - timedelta(hours=2, minutes=55),
            )
        )

    resolved_incident = db.scalar(
        select(Incident).where(
            Incident.title == "Latence API résolue après vérification",
            Incident.source_alert_id.is_(None),
        )
    )
    if resolved_incident is None:
        resolved_at = now - timedelta(days=1, hours=2)
        db.add(
            Incident(
                service_id=services["api-gateway"].id,
                title="Latence API résolue après vérification",
                description=(
                    "Incident historique de démonstration conservé pour montrer "
                    "la différence entre une file active et les incidents résolus."
                ),
                severity="medium",
                status="resolved",
                owner="Dyllan",
                created_at=resolved_at - timedelta(minutes=25),
                updated_at=resolved_at,
                resolved_at=resolved_at,
            )
        )


def _ensure_runbooks(db: Session) -> None:
    for definition in RUNBOOK_DEFINITIONS:
        runbook = db.scalar(select(Runbook).where(Runbook.key == definition["key"]))
        if runbook is None:
            runbook = Runbook(key=definition["key"])
            db.add(runbook)

        runbook.name = definition["name"]
        runbook.description = definition["description"]
        runbook.mode = definition["mode"]
        runbook.instructions = definition["instructions"]
        runbook.steps_json = json.dumps(definition["steps"], ensure_ascii=False)
        runbook.required_context = definition["required_context"]
        runbook.risk_level = definition["risk_level"]
        runbook.automation_key = definition["automation_key"]
        runbook.enabled = True
