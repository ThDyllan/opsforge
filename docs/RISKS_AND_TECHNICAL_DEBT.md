# Risks and Technical Debt

## Purpose

This file tracks known limitations, technical debts, and future decisions so they are not forgotten or hidden.

These items are documented tradeoffs in the current project scope. They should be reviewed when the relevant phase begins, but they do not automatically require immediate implementation.

## Current Known Technical Debts

### Test Coverage Uses SQLite Fast Feedback and Focused PostgreSQL Integration

The fast unit suite uses an in-memory SQLite database, while the application runtime uses PostgreSQL. A separate PostgreSQL integration test now verifies the core flow in Docker Compose and GitHub Actions.

This keeps most feedback fast, isolated, and easy to run while adding an explicit runtime-database check.

The remaining limitation is that one core-flow test does not fully reproduce every PostgreSQL-specific behavior, such as advanced transactions, concurrent connections, or every future query shape.

A future improvement would be targeted PostgreSQL coverage whenever a later feature introduces database-specific behavior. Broad duplication of every SQLite test is not necessary now.

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

The local Phase 6 scan of the pinned image reported `19 HIGH` and `3 CRITICAL` Debian findings. Trivy reported no known fix for those findings in the refreshed base image. This is visible security debt, not a green-security claim.

### Pinned Dependencies Require Deliberate Maintenance

The Docker base digest and Python dependency set are pinned so local and CI builds are reproducible.

This prevents unreviewed version drift, but it also means updates must be made intentionally. A dependency or base-image refresh should include Docker build, SQLite tests, PostgreSQL integration testing, and a new Trivy scan before it is accepted.

### TestClient Deprecation Warning

The current test suite passes with one `StarletteDeprecationWarning` from `fastapi.testclient`. The warning comes from the current FastAPI/Starlette test-client path, not from a failed assertion.

Replacing the test harness with an async HTTP client would add complexity without improving the current domain evidence. The warning is tracked and should be revisited when the framework provides a stable replacement path or when the test architecture otherwise needs to change.

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

### Readiness Checks Only Basic Database Connectivity

`/health` intentionally checks only process liveness. `/ready` now runs `SELECT 1` against PostgreSQL and Kubernetes uses it as the readiness probe.

This proves basic database reachability but does not check every business dependency or query. That deeper dependency model remains out of scope.

### Metrics Are Technical Rather Than Business-Level

Prometheus and Grafana are deployed and Phase 5 is validated. The current custom metrics remain HTTP request count and latency only.

Incident and alert count metrics are not collected because they would require additional database queries or application behavior.

### Phase 5A Does Not Include Business Metrics

The first metrics slice tracks HTTP request count and latency only.

Incident and alert count metrics are deferred because they would require database queries or additional application behavior. They can be considered later if they remain simple and do not require refactoring.

### Phase 5B Prometheus Is Minimal and Local

Phase 5B deploys Prometheus inside k3d with a static scrape configuration and a `ClusterIP` Service.

Prometheus data uses ephemeral Pod storage. This is enough to demonstrate scraping and PromQL during the RNCP phase, but it is not a durable monitoring data store.

Prometheus is accessed from Windows with `kubectl port-forward` instead of NodePort or Ingress. This avoids cluster recreation and extra exposure, but it is a local demonstration pattern rather than production access.

Kubernetes service discovery, RBAC-based target discovery, Alertmanager, and persistent Prometheus storage remain out of scope.

### Phase 5C Grafana Is Minimal and Local

Phase 5C deploys Grafana inside k3d with a provisioned Prometheus datasource and a provisioned `OpsForge Monitoring` dashboard.

Grafana is exposed only through a `ClusterIP` Service and local `kubectl port-forward`. This is appropriate for the local RNCP demo, but it is not a production access model.

The local demo uses Grafana's default `admin/admin` credentials. This must be explained as local-only and not production-safe.

Grafana does not use persistent storage in this phase. The dashboard and datasource are reproducible from ConfigMaps, but any manual UI changes inside Grafana would not be treated as durable project state.

Grafana alerting, Alertmanager, notification routing, TLS, Ingress, authentication hardening, and production dashboard governance remain out of scope. Prometheus alert-rule detection is implemented separately through `OpsForgeApiDown`.

### Phase 5D Alerting Has No Notification Routing

Phase 5D adds a Prometheus alert rule named `OpsForgeApiDown` and proves that it fires when the API Deployment is scaled to zero.

This demonstrates local anomaly detection, but it does not send notifications because Alertmanager is intentionally out of scope.

The outage simulation is safe only if the API is restored immediately after the alert is observed:

```powershell
kubectl -n opsforge scale deployment/opsforge-api --replicas=1
```

The alert should be explained as a supervision demonstration, not as a complete production incident response system.

## Current Guardrails

Backup/restore and security documentation are complete. Future changes must preserve their simple, explainable local scope unless the user explicitly expands it.

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

- Decide whether the final dossier needs recreated screenshots from the current home-PC environment.
- Define a Trivy blocking threshold only when a specific risk policy is justified.
- Decide whether a registry-based deployment path is worth adding after the exam scope is frozen.
- Consider business metrics only if they can remain simple and demonstrably useful.

## Oral Exam Note

These items are not hidden failures.

They are known scope decisions, technical tradeoffs, and deferred improvements. During the oral exam, they should be explained honestly by stating:

- why the current choice was appropriate for the project phase;
- what limitation the choice creates;
- what future improvement is possible;
- why that improvement was not added prematurely.
