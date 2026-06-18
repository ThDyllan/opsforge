# OpsForge

OpsForge is an RNCP DevOps school project. MVP1 is a small FastAPI, PostgreSQL, and Docker Compose application for incident and service supervision.

Documentation entry point: [`docs/INDEX.md`](docs/INDEX.md)

This first version intentionally stays simple:

- FastAPI API with SQLAlchemy 2.x models
- PostgreSQL in Docker Compose
- SQLAlchemy `metadata.create_all()` on startup
- Jinja2 dashboard
- Safe predefined demo runbooks only
- pytest coverage for core API behavior

MVP1 does not include React, Kubernetes, Prometheus, Grafana, Terraform, Ansible, Redis, Celery, Keycloak, auth, or Alembic.

## Run With Docker

```bash
docker compose up --build
```

Dashboard:

```text
http://localhost:8000/dashboard
```

Health:

```text
http://localhost:8000/health
```

The database is seeded automatically on first startup with demo services, alerts, incidents, and runbooks.

## Run Tests

Start the Docker Compose environment, then run tests inside the API container:

```bash
docker compose exec api pytest
```

Tests use an in-memory SQLite database. In the local Docker Compose workflow, the `tests/` directory is mounted into the API container for test discovery.

## CI/CD

Phase 2 uses GitHub Actions for the first CI/CD workflow.

On push and pull request, CI installs Python dependencies, runs `pytest`, builds the Docker image, and runs a non-blocking Trivy image scan.

See `docs/CI_CD.md` for details.

## API Routes

General:

- `GET /health`
- `GET /`
- `GET /dashboard`

Services:

- `GET /api/services`
- `POST /api/services`
- `GET /api/services/{service_id}`

Alerts:

- `GET /api/alerts`
- `POST /api/alerts`
- `GET /api/alerts/{alert_id}`
- `PATCH /api/alerts/{alert_id}/acknowledge`
- `PATCH /api/alerts/{alert_id}/resolve`

Incidents:

- `GET /api/incidents`
- `POST /api/incidents`
- `GET /api/incidents/{incident_id}`
- `PATCH /api/incidents/{incident_id}/status`

Runbooks:

- `GET /api/runbooks`
- `POST /api/runbooks/{runbook_key}/execute`

Audit logs:

- `GET /api/audit-logs`

## Demo Runbooks

Only safe predefined runbooks are implemented:

- `health_check_service`
- `generate_incident_report`
- `mark_incident_resolved`
- `simulate_backup_check`
- `restart_demo_service`

Runbooks do not execute arbitrary shell commands. Every runbook execution creates a `RunbookExecution` record and an `AuditLog` record.
