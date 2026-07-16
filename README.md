# OpsForge

OpsForge is a local, single-operator incident console built for an RNCP DevOps project. It lets an operator qualify signals, take ownership of incidents, follow controlled runbooks, and retain an audit trail. The application is supported by CI, backup/restore, local Kubernetes, and monitoring evidence.

Documentation entry point: [`docs/INDEX.md`](docs/INDEX.md)

The implemented foundation stays intentionally explainable:

- FastAPI API with SQLAlchemy 2.x models
- PostgreSQL in Docker Compose
- SQLAlchemy `metadata.create_all()` on startup
- Multipage Jinja2 operator console
- Managed manual runbooks and allowlisted automated runbooks
- SQLite unit tests plus a PostgreSQL integration test
- Docker Compose, local k3d deployment, Prometheus, and Grafana

OpsForge does not include React, authentication, Redis, Celery, Terraform, Ansible, Helm, Alertmanager, or Alembic.

## Run With Docker

```bash
docker compose up --build
```

Operator console:

```text
http://localhost:8000/overview
```

`/dashboard` remains as a compatibility redirect to `/overview`.

Health:

```text
http://localhost:8000/health
```

Readiness:

```text
http://localhost:8000/ready
```

The database is seeded automatically with an idempotent generic scenario centered on Backup Service, plus supporting service, alert, incident, runbook, execution, and audit data.

PostgreSQL is bound to `127.0.0.1` by default, so it is available to local tools but not exposed on every network interface.

## Run Tests

Start the Docker Compose environment, then run tests inside the API container:

```bash
docker compose exec api pytest
```

The fast suite uses an in-memory SQLite database. In the local Docker Compose workflow, the `tests/` directory is mounted read-only into the API container for test discovery.

Run the separate PostgreSQL core-flow integration test with:

```bash
docker compose exec api pytest tests/postgres_integration.py
```

The PostgreSQL test creates an isolated temporary database, verifies the core flow, then drops that database. It does not add test records to the demonstration database.

## Operator Experience

The console is organized around the real workflow:

- `/overview` - operational orientation and platform state
- `/alerts` - searchable signal queue and contextual actions
- `/incidents` - incident queue and dedicated Command Center
- `/services` - service catalog and related operational data
- `/runbooks` - manual and approved automated procedures
- `/activity` - global audit journal
- `/monitoring` - real platform monitoring versus simulated business state
- `/help` - first steps, guided scenario, glossary, architecture, and limits

See [`docs/PRODUCT_GUIDE.md`](docs/PRODUCT_GUIDE.md) for the product model and [`docs/PHASE6_MANUAL_TEST.md`](docs/PHASE6_MANUAL_TEST.md) for the final operator test.

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
- `PATCH /api/services/{service_id}`

Alerts:

- `GET /api/alerts`
- `POST /api/alerts`
- `GET /api/alerts/{alert_id}`
- `GET /api/alerts/{alert_id}/active-incident`
- `PATCH /api/alerts/{alert_id}/acknowledge`
- `PATCH /api/alerts/{alert_id}/resolve`

Incidents:

- `GET /api/incidents`
- `POST /api/incidents`
- `GET /api/incidents/{incident_id}`
- `PATCH /api/incidents/{incident_id}`
- `PATCH /api/incidents/{incident_id}/status`

Runbooks:

- `GET /api/runbooks`
- `POST /api/runbooks`
- `GET /api/runbooks/{runbook_id}`
- `PATCH /api/runbooks/{runbook_id}`
- `POST /api/runbooks/{runbook_key}/execute`
- `GET /api/runbook-executions`

Audit logs:

- `GET /api/audit-logs`

## Demo Runbooks

Automated runbooks can invoke only these approved behaviors:

- `health_check_service`
- `generate_incident_report`
- `mark_incident_resolved`
- `simulate_backup_check`
- `restart_demo_service`

The seed also includes the manual checklist `diagnostic_echec_sauvegarde`. Operators can maintain manual runbooks, or select one of the approved automation keys for an automated runbook.

Runbooks never accept arbitrary shell commands or executable scripts. Every attempted runbook execution creates a `RunbookExecution` record and audit evidence, including controlled failures.
