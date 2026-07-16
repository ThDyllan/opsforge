from __future__ import annotations

import os
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient
from psycopg import sql
from sqlalchemy.engine import make_url


def _admin_connection(database_url: str):
    url = make_url(database_url)
    return psycopg.connect(
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname="postgres",
        autocommit=True,
    )


def test_postgresql_core_flow_uses_ephemeral_database() -> None:
    runtime_url = os.environ.get("DATABASE_URL", "")
    assert runtime_url.startswith("postgresql+psycopg://")

    database_name = f"opsforge_test_{uuid4().hex[:12]}"
    with _admin_connection(runtime_url) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))

    previous_url = runtime_url
    test_url = make_url(runtime_url).set(database=database_name)
    os.environ["DATABASE_URL"] = test_url.render_as_string(hide_password=False)

    try:
        from app.database import engine
        from app.main import app

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
                headers={"X-OpsForge-Actor": "postgresql-integration"},
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
                    "description": "Verifies incident persistence in PostgreSQL.",
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
    finally:
        if "engine" in locals():
            engine.dispose()
        os.environ["DATABASE_URL"] = previous_url
        with _admin_connection(runtime_url) as admin:
            admin.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (database_name,),
            )
            admin.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))

    with _admin_connection(runtime_url) as admin:
        remaining = admin.execute(
            "SELECT count(*) FROM pg_database WHERE datname = %s", (database_name,)
        ).fetchone()
    assert remaining == (0,)
