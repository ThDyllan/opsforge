from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Alert, Incident, Runbook, Service, utc_now
from .runbooks import RUNBOOK_DEFINITIONS


def seed_database(db: Session) -> None:
    has_services = db.scalar(select(Service.id).limit(1))
    if has_services:
        return

    services = {
        "api-gateway": Service(
            name="API Gateway",
            slug="api-gateway",
            description="Public entry point for the platform APIs.",
            environment="production",
            status="healthy",
            owner="platform-team",
        ),
        "payment-service": Service(
            name="Payment Service",
            slug="payment-service",
            description="Handles payment authorization and capture flows.",
            environment="production",
            status="degraded",
            owner="payments-team",
        ),
        "inventory-service": Service(
            name="Inventory Service",
            slug="inventory-service",
            description="Tracks stock availability and reservation events.",
            environment="production",
            status="down",
            owner="supply-team",
        ),
        "notification-service": Service(
            name="Notification Service",
            slug="notification-service",
            description="Sends email and SMS notifications.",
            environment="staging",
            status="unknown",
            owner="platform-team",
        ),
    }
    db.add_all(services.values())
    db.flush()

    now = utc_now()
    alerts = [
        Alert(
            service_id=services["api-gateway"].id,
            source="synthetic-monitor",
            title="API latency above baseline",
            message="P95 latency is above the warning threshold.",
            severity="warning",
            status="new",
            received_at=now - timedelta(minutes=35),
        ),
        Alert(
            service_id=services["payment-service"].id,
            source="payment-monitor",
            title="Payment authorization failures",
            message="Authorization failures are above the critical threshold.",
            severity="critical",
            status="acknowledged",
            received_at=now - timedelta(hours=1),
        ),
        Alert(
            service_id=services["inventory-service"].id,
            source="database-check",
            title="Inventory database unavailable",
            message="The inventory database did not respond to the latest health probe.",
            severity="critical",
            status="new",
            received_at=now - timedelta(hours=2),
        ),
        Alert(
            service_id=services["notification-service"].id,
            source="deploy-pipeline",
            title="Notification worker deployed",
            message="Staging worker deployment completed successfully.",
            severity="info",
            status="resolved",
            received_at=now - timedelta(hours=4),
            resolved_at=now - timedelta(hours=3, minutes=50),
        ),
    ]
    db.add_all(alerts)
    db.flush()

    incidents = [
        Incident(
            service_id=services["payment-service"].id,
            source_alert_id=alerts[1].id,
            title="Payment failures impacting checkout",
            description="Checkout is intermittently failing during card authorization.",
            severity="high",
            status="investigating",
            owner="payments-team",
            created_at=now - timedelta(minutes=55),
        ),
        Incident(
            service_id=services["inventory-service"].id,
            source_alert_id=alerts[2].id,
            title="Inventory service unavailable",
            description="Inventory reads are failing because the database is unavailable.",
            severity="critical",
            status="open",
            owner="supply-team",
            created_at=now - timedelta(hours=1, minutes=45),
        ),
    ]
    db.add_all(incidents)

    runbooks = [
        Runbook(
            key=item["key"],
            name=item["name"],
            description=item["description"],
            enabled=True,
        )
        for item in RUNBOOK_DEFINITIONS
    ]
    db.add_all(runbooks)
    db.commit()
