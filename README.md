# OpsForge

OpsForge is an RNCP DevOps school project for incident and service supervision. It starts as a FastAPI, PostgreSQL, and Docker Compose application, then demonstrates CI, backup/restore, local Kubernetes, and monitoring in deliberate phases.

Documentation entry point: [`docs/INDEX.md`](docs/INDEX.md)

The implemented foundation stays intentionally small:

- FastAPI API with SQLAlchemy 2.x models
- PostgreSQL in Docker Compose
- SQLAlchemy `metadata.create_all()` on startup
- Jinja2 dashboard
- Safe predefined demo runbooks only
- SQLite unit tests plus a PostgreSQL integration test
- Docker Compose, local k3d deployment, Prometheus, and Grafana

OpsForge does not include React, authentication, Redis, Celery, Terraform, Ansible, Helm, Alertmanager, or Alembic.

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

Readiness:

```text
http://localhost:8000/ready
```

The database is seeded automatically on first startup with demo services, alerts, incidents, and runbooks.

PostgreSQL is bound to `127.0.0.1` by default, so it is available to local tools but not exposed on every network interface.

## Run Tests

Start the Docker Compose environment, then run tests inside the API container:

```bash
docker compose exec api pytest
```

Tests use an in-memory SQLite database. In the local Docker Compose workflow, the `tests/` directory is mounted into the API container for test discovery.

Run the separate PostgreSQL core-flow integration test with:

```bash
docker compose exec api pytest tests/postgres_integration.py
```

## CI/CD

Phase 2 uses GitHub Actions for the first CI/CD workflow.

On push and pull request, CI runs SQLite unit tests, a PostgreSQL integration test, a Docker image build, and a non-blocking Trivy image scan.

See `docs/CI_CD.md` for details.

## Backup and Security

Phase 3 adds local PostgreSQL backup and restore scripts plus documented security choices. Backups use PostgreSQL custom `.dump` format and are stored under the Git-ignored `backups/` directory.

```powershell
.\scripts\backup.ps1
.\scripts\restore.ps1 -BackupFile .\backups\opsforge_backup_YYYYMMDD_HHMMSS.dump
```

The default restore command verifies the archive in a temporary database and does not replace the main database. See `docs/BACKUP_RESTORE.md` and `docs/SECURITY.md` for details.

## Kubernetes

Phase 4 has been validated. Phase 4A provides the local k3d/PostgreSQL foundation, and Phase 4B deploys the locally imported API image through NodePort at `http://localhost:8080`.

See `docs/KUBERNETES.md` and `docs/PHASE4_VERIFICATION.md` for the deployment procedure and validation evidence.

## Monitoring

Phase 5 is validated. Prometheus scrapes the Kubernetes-deployed API, Grafana provides the `OpsForge Monitoring` dashboard, and `OpsForgeApiDown` detects a controlled API outage.

See `docs/MONITORING.md` and `docs/PHASE5_VERIFICATION.md` for the monitoring strategy and current verification status.

## API Routes

General:

- `GET /health`
- `GET /ready`
- `GET /metrics`
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
