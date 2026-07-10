# Risks and Technical Debt

## Purpose

This file tracks known limitations, technical debts, and future decisions so they are not forgotten or hidden.

These items are documented tradeoffs in the current project scope. They should be reviewed when the relevant phase begins, but they do not automatically require immediate implementation.

## Current Known Technical Debts

### Tests Use SQLite While Runtime Uses PostgreSQL

The current pytest suite uses an in-memory SQLite database, while the application runtime uses PostgreSQL.

This was acceptable for MVP1 because it kept tests fast, independent from Docker services, and easy to run and explain.

The limitation is that SQLite tests do not fully reproduce PostgreSQL-specific behavior, including differences in SQL syntax, data types, constraints, transactions, and connection behavior.

A possible future improvement is to add PostgreSQL integration tests using Docker Compose or a PostgreSQL service in CI. This is not required unless explicitly selected for a later task.

### metadata.create_all() Is Used Instead of Migrations

MVP1 creates database tables with SQLAlchemy `metadata.create_all()` during application startup.

Alembic and migration history were intentionally out of scope for MVP1 to keep the application simple and exam-friendly.

The limitation is that schema changes do not have a versioned migration path. Migration tooling should be considered only if later project changes make it necessary.

### No Authentication

Authentication is intentionally out of scope for the current educational MVP.

OpsForge is currently treated as a local, single-user exam project rather than a public or multi-user production service.

This is a documented scope decision, not an overlooked production requirement.

### Trivy Remains Non-Blocking in Phase 3

The Trivy image scan reports `HIGH` and `CRITICAL` findings, but it does not block the GitHub Actions workflow.

Phase 3 reviewed this policy and intentionally keeps it non-blocking for the current local educational scope. Findings remain visible and must be understood and documented.

A stricter blocking policy can be considered later if the deployment scope or risk tolerance changes.

### Local Backups Are Not a Production Backup Strategy

Phase 3 stores database backups only in the local `backups/` directory. Generated files are ignored by Git but are not encrypted, copied offsite, scheduled, or automatically rotated.

This is sufficient to demonstrate backup and restore mechanics for the current RNCP phase. It does not protect against workstation loss or provide production disaster recovery.

### Phase 4 local-path Storage Is Node-Local

The Phase 4 PostgreSQL PVC uses the k3s `local-path` StorageClass. Data persists when the PostgreSQL Pod is recreated on the existing k3d node, but the storage is not distributed and is not guaranteed to survive cluster deletion or node loss.

This is a deliberate local learning choice. Phase 3 backups remain necessary and local-path storage must not be described as production disaster recovery.

### Phase 4 Local Secrets Must Remain Untracked

The tracked `k8s/secret.example.yaml` contains placeholders only. Real local Kubernetes credentials are stored in the ignored `k8s/secret.local.yaml` file.

Accidentally staging or sharing the local Secret file would expose the demonstration credentials. Git ignore status must be checked before future Phase 4 commits.

### k3d Image Import Is Local and Manual

Phase 4 imports the API image directly into k3d without a registry. Each rebuilt image must be imported again before Kubernetes can use it.

This avoids registry scope in Phase 4 but is not an automated image delivery pipeline.

### The API Health Endpoint Is Not Database-Aware

The Kubernetes API probes use the existing `/health` endpoint. It confirms that the FastAPI process responds, but it does not continuously verify PostgreSQL connectivity.

An init container waits for PostgreSQL before API startup, and the application connects to PostgreSQL during its startup lifecycle. A dedicated database-aware readiness endpoint remains a possible later improvement and is not added during Phase 4 because it would change application logic.

### Phase 5A Metrics Are Not Full Monitoring Yet

Phase 5A exposes Prometheus-compatible application metrics at `/metrics`, but Prometheus and Grafana are not deployed yet.

This means Phase 5A prepares the API for scraping but does not by itself satisfy the full monitoring Definition of Done. Later Phase 5 work must still prove scraping, dashboarding, alerting, and anomaly detection against the deployed service.

### Phase 5A Does Not Include Business Metrics

The first metrics slice tracks HTTP request count and latency only.

Incident and alert count metrics are deferred because they would require database queries or additional application behavior. They can be considered later if they remain simple and do not require refactoring.

### Phase 5B Prometheus Is Minimal and Local

Phase 5B deploys Prometheus inside k3d with a static scrape configuration and a `ClusterIP` Service.

Prometheus data uses ephemeral Pod storage. This is enough to demonstrate scraping and PromQL during the RNCP phase, but it is not a durable monitoring data store.

Prometheus is accessed from Windows with `kubectl port-forward` instead of NodePort or Ingress. This avoids cluster recreation and extra exposure, but it is a local demonstration pattern rather than production access.

Kubernetes service discovery, RBAC-based target discovery, Alertmanager, Grafana dashboards, and alert/anomaly demonstration remain deferred to later Phase 5 slices.

## Phase 3 Guardrails

Phase 3 should implement backup/restore and security documentation.

Backup and restore scripts, if created, must remain simple, readable, and explainable in approximately 30 seconds during the oral exam.

Avoid over-engineering. Phase 3 should not introduce:

- Vault
- Cloud backup storage
- Automated secret rotation
- A cron scheduler
- Encryption infrastructure
- Enterprise security tooling

These capabilities remain out of scope unless the user explicitly decides otherwise in a later task.

## Upcoming Decisions to Remember

### Phase 5

- Deploy Grafana inside k3d.
- Decide the safest local Grafana access method.
- Add a simple alert rule and anomaly demonstration.

## Oral Exam Note

These items are not hidden failures.

They are known scope decisions, technical tradeoffs, and deferred improvements. During the oral exam, they should be explained honestly by stating:

- why the current choice was appropriate for the project phase;
- what limitation the choice creates;
- what future improvement is possible;
- why that improvement was not added prematurely.
