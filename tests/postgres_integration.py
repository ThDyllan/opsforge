from __future__ import annotations

import os
from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.seed import seed_database


def _prepare_database() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


def test_postgresql_core_flow() -> None:
    database_url = os.environ.get("DATABASE_URL", "")
    assert database_url.startswith("postgresql+psycopg://")

    _prepare_database()
    slug = f"postgresql-integration-{uuid4().hex[:12]}"
    with TestClient(app) as client:
        service_response = client.post(
            "/api/services",
            json={
                "name": "PostgreSQL Integration Service",
                "slug": slug,
                "environment": "test",
                "status": "healthy",
            },
        )
        service = service_response.json()
        alert_response = client.post(
            "/api/alerts",
            json={
                "service_id": service["id"],
                "source": "postgresql-integration",
                "title": "PostgreSQL integration alert",
                "message": "Verifies the core flow against PostgreSQL.",
                "severity": "critical",
            },
        )
        alert = alert_response.json()
        incident_response = client.post(
            "/api/incidents",
            json={
                "source_alert_id": alert["id"],
                "title": "PostgreSQL integration incident",
                "severity": "high",
            },
        )
        incident = incident_response.json()
        execution_response = client.post(
            "/api/runbooks/generate_incident_report/execute",
            json={
                "service_id": service["id"],
                "incident_id": incident["id"],
                "requested_by": "postgresql-integration",
            },
        )
        execution = execution_response.json()
        logs_response = client.get("/api/audit-logs")

    assert service_response.status_code == 201
    assert alert_response.status_code == 201
    assert incident_response.status_code == 201
    assert incident["service_id"] == service["id"]
    assert execution_response.status_code == 200
    assert execution["status"] == "success"
    assert execution["service_id"] == service["id"]
    assert execution["incident_id"] == incident["id"]
    assert any(
        log["action"] == "runbook.executed"
        and log["entity_type"] == "RunbookExecution"
        and log["entity_id"] == execution["id"]
        for log in logs_response.json()
    )
