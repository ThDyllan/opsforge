# OpsForge Architecture Decisions

## Decision 001 - Use FastAPI for Backend

### Context

OpsForge MVP1 needs a small backend API that is easy to understand, test, and explain during an exam.

### Decision

Use FastAPI for the backend application.

### Reason

FastAPI provides clear route definitions, automatic API documentation, Pydantic integration, and a simple developer experience.

### Consequences

The application can expose API endpoints quickly while staying readable. Future backend changes should stay consistent with FastAPI patterns.

## Decision 002 - Use PostgreSQL as Relational Database

### Context

OpsForge manages related data: services, alerts, incidents, runbooks, runbook executions, and audit logs.

### Decision

Use PostgreSQL as the relational database.

### Reason

PostgreSQL is a common production database and fits the relational shape of the project.

### Consequences

The project demonstrates a realistic database choice for DevOps deployment and backup phases. Local development requires a PostgreSQL service through Docker Compose.

## Decision 003 - Use Docker Compose for MVP1 Local Environment

### Context

MVP1 must run locally with the API and database together.

### Decision

Use Docker Compose for the MVP1 local environment.

### Reason

Docker Compose keeps the local setup simple and makes the API/database relationship explicit.

### Consequences

The application can be started with one command. Kubernetes and more advanced deployment concerns stay deferred to later phases.

## Decision 004 - Use Jinja2 Instead of React for MVP1 Dashboard

### Context

MVP1 needs a basic dashboard, but frontend complexity is not part of the first phase.

### Decision

Use Jinja2 templates for the MVP1 dashboard instead of React.

### Reason

Jinja2 keeps the dashboard simple, server-rendered, and easy to explain.

### Consequences

The project avoids unnecessary frontend tooling in MVP1. Any richer frontend can be considered only if explicitly requested in a later validated phase.

## Decision 005 - Forbid Arbitrary Shell Command Execution in Runbooks

### Context

OpsForge includes demo runbooks, but unsafe command execution would create unnecessary security risk and exam complexity.

### Decision

Runbooks must be predefined, controlled actions only. Arbitrary shell command execution is forbidden.

### Reason

Safe runbooks keep the project auditable and prevent user-provided command execution from reaching the host or container shell.

### Consequences

Runbook features must remain limited to explicitly implemented safe actions. The code must avoid `subprocess`, `os.system`, `shell=True`, `eval`, `exec`, and arbitrary user-provided command execution.

## Decision 006 - Use metadata.create_all() for MVP1 Instead of Alembic

### Context

MVP1 needs database tables, but formal migration management is not required yet.

### Decision

Use SQLAlchemy `metadata.create_all()` on startup for MVP1.

### Reason

This keeps the first phase simple and focused on demonstrating the application flow.

### Consequences

Schema migration history is not available in MVP1. Alembic can be introduced later only if explicitly requested and justified by a future phase.

## Decision 007 - Keep Kubernetes, CI/CD, and Monitoring for Later Phases

### Context

OpsForge is planned as a phased DevOps project, but MVP1 must stay small and locally demonstrable.

### Decision

Keep Kubernetes, CI/CD, and monitoring out of MVP1 and reserve them for later roadmap phases.

### Reason

Deferring these topics prevents over-scoping and makes each phase easier to explain and validate.

### Consequences

MVP1 remains a Docker Compose application. Kubernetes, CI/CD, and monitoring work should not be added until their phases are explicitly validated.

## Decision 008 - No Authentication in MVP1

### Context

MVP1 is a local, single-user exam project.

### Decision

Do not add authentication in MVP1.

### Reason

Authentication is intentionally deferred to avoid over-scoping. This is a documented scope decision, not an oversight.

Security is still addressed through safe runbooks, no arbitrary command execution, audit logs, and later secret management.

### Consequences

MVP1 should not be exposed as a real multi-user production service. Authentication can be considered in a later validated phase if the user explicitly requests it.

## Decision 009 - Mount Tests Into the API Container for Local Docker Testing

### Context

The command `docker compose exec api pytest` initially collected 0 tests because the running API container did not have access to the `tests/` directory.

MVP1 needs a simple Docker-based local testing workflow that is easy to explain and verify.

### Decision

Mount the local tests directory into the API container in `docker-compose.yml`:

```yaml
./tests:/app/tests:ro
```

### Reason

This makes tests available for local and development testing with `docker compose exec api pytest` without baking tests into the application image.

The application image remains focused on running the API, while Docker Compose provides the local test environment.

### Consequences

`docker compose exec api pytest` can discover and run the MVP1 test suite.

This is a local MVP1 testing decision, not a production deployment pattern.

Future production-oriented container images should not assume that test files are mounted or present at runtime unless a later phase explicitly decides otherwise.

## Decision 010 - Use GitHub Actions for Phase 2 CI/CD

### Context

Phase 2 requires a CI/CD pipeline that runs on push or pull request, executes tests, builds the Docker image, and runs a Trivy scan.

OpsForge is an RNCP DevOps school project, so the CI/CD implementation must remain simple, visible, and easy to explain.

### Decision

Use GitHub Actions for the initial Phase 2 CI/CD workflow.

The workflow checks out the repository, sets up Python 3.12, installs dependencies from `requirements.txt`, runs `pytest`, builds the Docker image, and runs a Trivy image scan.

### Reason

GitHub Actions integrates directly with GitHub repositories and provides a clear way to demonstrate automated tests, image build validation, and security scanning.

This satisfies the Phase 2 scope without introducing deployment, registry publishing, Kubernetes, monitoring, or additional infrastructure.

### Consequences

The CI/CD result will be visible in GitHub Actions after the workflow is pushed to GitHub.

The Docker image is built for validation but not pushed to a registry in Phase 2.

The first Trivy scan is non-blocking so findings are visible without enforcing a security policy before Phase 3 defines stricter security expectations.

## Decision 011 - Use SQLite for Fast MVP Tests While PostgreSQL Remains the Runtime Database

### Context

OpsForge runs with PostgreSQL, but the current pytest suite uses an in-memory SQLite database.

MVP1 needed tests that were fast, isolated, and easy to run locally and in CI without requiring a PostgreSQL service.

### Decision

Use in-memory SQLite for the current MVP test suite while keeping PostgreSQL as the application runtime database.

Treat this as a temporary testing strategy rather than proof of complete PostgreSQL compatibility.

### Reason

SQLite keeps the MVP tests simple and provides quick feedback for core API behavior.

This was appropriate for Phase 1 and Phase 2, where application simplicity and CI verification were more important than database-specific integration coverage.

### Consequences

The tests do not fully reproduce PostgreSQL-specific behavior, including possible differences in data types, constraints, SQL behavior, transactions, and connections.

A future phase may add PostgreSQL integration tests through Docker Compose or CI if the user explicitly decides that the additional fidelity is required.

## Decision 012 - Use Local Custom-Format PostgreSQL Backups for Phase 3

### Context

Phase 3 requires a backup command or script, a tested restore procedure, and an approach that remains simple enough to explain during the RNCP oral exam.

### Decision

Use PowerShell scripts that run PostgreSQL tools through the existing Docker Compose `db` service.

Create custom-format `.dump` archives inside the database container with `pg_dump`, copy them to the local `backups/` directory with `docker compose cp`, and restore them with `pg_restore`.

Restore verification uses a temporary database by default. Restoring into the main database requires an explicit option and confirmation.

### Reason

The PostgreSQL tools already exist in the database image and match the server version. Custom format supports archive inspection and controlled restore, while `docker compose cp` avoids redirecting binary output through PowerShell.

### Consequences

No PostgreSQL client installation is required on the host. Generated backups stay local and are ignored by Git.

This approach does not provide encryption, offsite storage, scheduling, or automatic rotation. Those capabilities remain outside Phase 3.

## Decision 013 - Keep Trivy Non-Blocking in Phase 3

### Context

Phase 2 introduced a non-blocking Trivy image scan so vulnerability findings were visible before a formal enforcement policy existed.

### Decision

Keep the Trivy scan non-blocking during Phase 3 and document the choice as a known security limitation.

### Reason

OpsForge remains a local RNCP educational project. Visibility and understanding of findings are required, but a blocking threshold is not yet justified by the current scope.

### Consequences

GitHub Actions continues to report findings without failing solely because of Trivy results. Findings must be reviewed and documented, and a stricter policy can be considered later if the deployment scope changes.

## Decision 014 - Use k3d for the Local Phase 4 Cluster

### Context

Phase 4 needs a local k3s/Kubernetes environment on Windows, where OpsForge already uses Docker Desktop.

### Decision

Use a single-node k3d cluster named `opsforge`. Expose the Kubernetes API on `127.0.0.1:6445` and map Windows port 8080 to API NodePort 30080.

### Reason

k3d runs k3s inside Docker and reuses the existing Docker Desktop environment. This avoids the additional VM, WSL service, networking, and kubeconfig work of a separate native k3s host.

### Consequences

The environment is appropriate for local learning and demonstration, but it is not a multi-node or production Kubernetes platform.

## Decision 015 - Use Local k3d Image Import and NodePort for the API

### Context

The Phase 4B API image must be available to k3s without introducing external registry publishing, and the application must be reachable from Windows.

### Decision

Build the API image locally and import it with `k3d image import`. Do not add a registry.

Expose the future API through NodePort 30080, mapped by k3d to `127.0.0.1:8080`. Do not add Ingress in Phase 4.

### Reason

Direct image import and NodePort are the smallest mechanisms that satisfy the local Phase 4 requirements.

### Consequences

The image must be rebuilt and re-imported after application changes. Kubernetes cannot pull this local image from an external source because `imagePullPolicy` is `Never`.

## Decision 016 - Use local-path Storage for PostgreSQL

### Context

Phase 4 requires PostgreSQL persistent storage while remaining simple and local.

### Decision

Run one PostgreSQL StatefulSet replica with a 1 Gi `ReadWriteOnce` PVC using the k3s `local-path` StorageClass.

### Reason

k3s provides dynamic local-path provisioning by default, so the project can demonstrate PV/PVC binding and data persistence without adding a storage platform.

### Consequences

PostgreSQL data persists across Pod recreation on the existing node. It is not guaranteed to survive complete cluster deletion, node loss, or workstation loss.

## Decision 017 - Expose Prometheus-Compatible Application Metrics

### Context

Phase 5 requires OpsForge to be supervised with Prometheus and Grafana. Before deploying monitoring tools, the application needs a scrapeable metrics endpoint.

The first monitoring slice must stay small and avoid database queries, UI redesign, and application refactoring.

### Decision

Expose a `/metrics` endpoint from FastAPI using `prometheus-client`.

Collect minimal HTTP metrics:

- request count;
- request latency histogram;
- labels for HTTP method, route template, and status code.

Exclude `/metrics` itself from the custom request metrics.

### Reason

This provides Prometheus-compatible application metrics while keeping the implementation easy to explain.

Using route templates instead of raw URLs avoids high-cardinality labels for dynamic API paths.

### Consequences

Prometheus can scrape the API in a later Phase 5 slice.

Phase 5A does not deploy Prometheus, Grafana, dashboards, alert rules, or Alertmanager. It only prepares the application for monitoring.

## Decision 018 - Deploy Prometheus Inside k3d With Static Scrape Configuration

### Context

Phase 5 must supervise the OpsForge service deployed in Kubernetes. The monitoring stack should prove that the Kubernetes-deployed API is observable, while remaining small enough to explain during the RNCP oral exam.

### Decision

Deploy Prometheus as a Kubernetes `Deployment` in a dedicated `monitoring` namespace.

Expose Prometheus with a `ClusterIP` Service and access it locally with `kubectl port-forward` when needed.

Configure Prometheus with a static scrape target:

```text
opsforge-api.opsforge.svc.cluster.local:8000
```

Use `/metrics` as the metrics path.

### Reason

Running Prometheus inside k3d demonstrates supervision of a Kubernetes-deployed service without introducing external monitoring infrastructure.

Static scrape configuration avoids RBAC and Kubernetes service discovery complexity during this phase.

Using `ClusterIP` plus port-forwarding avoids recreating the k3d cluster or adding a NodePort only for Prometheus.

### Consequences

Prometheus can scrape the OpsForge API through Kubernetes internal DNS.

The Prometheus setup is local and intentionally minimal. It does not include Grafana, Alertmanager, persistent Prometheus storage, Kubernetes service discovery, Ingress, TLS, or production-grade monitoring operations.

## Decision 019 - Deploy Grafana Inside k3d With Provisioned Dashboard

### Context

Phase 5 must make OpsForge supervision visible and demonstrable for the RNCP jury. Prometheus scraping already proves metrics collection, but Grafana is needed to show a readable monitoring dashboard.

### Decision

Deploy Grafana as a Kubernetes `Deployment` in the existing `monitoring` namespace.

Provision:

- the Prometheus datasource with a ConfigMap;
- a dashboard provider with a ConfigMap;
- the `OpsForge Monitoring` dashboard with a ConfigMap.

Expose Grafana with a `ClusterIP` Service and access it locally with:

```powershell
kubectl -n monitoring port-forward svc/grafana 3000:3000
```

Use the internal Prometheus datasource URL:

```text
http://prometheus.monitoring.svc.cluster.local:9090
```

### Reason

This keeps the monitoring stack inside Kubernetes and shows that the Kubernetes-deployed OpsForge API is supervised through Prometheus and Grafana.

ConfigMap provisioning keeps the dashboard reproducible without Helm or manual UI-only setup.

ClusterIP plus port-forwarding avoids changing k3d port mappings, adding Ingress, or recreating the cluster.

### Consequences

Grafana is available for local demonstration and displays OpsForge API availability, request volume, request status, latency, and route-level request counts.

The setup intentionally does not add Grafana alerting, Alertmanager, Loki, Ingress, TLS, persistent Grafana storage, authentication hardening, or production monitoring operations.

## Decision 020 - Use a Prometheus Rule for the Phase 5 Alert Demonstration

### Context

Phase 5 must demonstrate that OpsForge supervision detects an anomaly on the deployed service.

Prometheus and Grafana are already deployed inside k3d. The project needs the smallest defensible alerting mechanism without adding a notification stack.

### Decision

Add a Prometheus alert rule named `OpsForgeApiDown`.

The rule is:

```promql
up{job="opsforge-api"} == 0
```

The alert uses a `30s` duration, labels `severity: critical` and `service: opsforge-api`, and annotations explaining that Prometheus cannot scrape the OpsForge API metrics endpoint.

Do not deploy Alertmanager in Phase 5D. Do not add Grafana alerting.

### Reason

Prometheus alert rules directly prove that the monitoring system detects the API outage.

A `30s` duration is appropriate for the local demo because Prometheus scrapes and evaluates every `15s`. It avoids reacting to a single transient scrape while keeping the demonstration short.

Alertmanager would add notification routing and receivers, which are not required to prove anomaly detection for this local RNCP phase.

### Consequences

OpsForge can demonstrate an outage scenario by scaling the API Deployment to zero and observing the `OpsForgeApiDown` alert firing.

The alert has no external notification channel. Operators must check Prometheus during the local demonstration.

Future work may add Alertmanager or notification routing only if explicitly selected.

## Decision 021 - Keep Fast SQLite Tests and Add a PostgreSQL Integration Test

### Context

The original pytest suite used only in-memory SQLite, while OpsForge runs on PostgreSQL. SQLite remains useful for fast isolated feedback, but it cannot prove all PostgreSQL behavior.

### Decision

Keep `tests/test_app.py` as the fast SQLite unit suite. Add `tests/postgres_integration.py` as a separately invoked core-flow test against PostgreSQL.

GitHub Actions starts a PostgreSQL service container and runs this integration test in a separate pytest process after the SQLite suite.

### Reason

Separate processes prevent the SQLite test environment from overriding the PostgreSQL database configuration. The approach improves confidence in the main business flow without making every unit test dependent on a database service.

### Consequences

CI takes slightly longer and contains two explicit test steps. The local PostgreSQL integration test is non-destructive: it prepares tables if needed and creates unique data without dropping existing tables.

This is focused integration coverage, not a claim of exhaustive PostgreSQL compatibility testing.

## Decision 022 - Separate Process Liveness From PostgreSQL Readiness

### Context

The original Kubernetes liveness and readiness probes both used `/health`, which only confirmed that the FastAPI process responded. An API process with no database connectivity could therefore remain ready to receive traffic.

### Decision

Keep `/health` as the process liveness endpoint. Add `/ready`, which executes `SELECT 1` through SQLAlchemy and returns `503` when PostgreSQL is unavailable.

Kubernetes uses `/ready` for readiness and continues to use `/health` for liveness.

### Reason

The two checks answer different operational questions. Restarting a live process does not fix every database outage, while removing an unready API from traffic is appropriate.

### Consequences

The project can demonstrate a controlled PostgreSQL outage where `/health` remains `200` and `/ready` becomes `503`. The checks remain intentionally simple and do not introduce a broader dependency health framework.

## Decision 023 - Harden Local API Runtime Defaults

### Context

The API image ran as root, Docker builds sent unnecessary repository material as context, and Docker Compose published PostgreSQL on every host interface by default.

### Decision

Run the API image as a dedicated non-root `opsforge` user, add a Docker healthcheck for `/health`, add a `.dockerignore`, and bind the Docker Compose PostgreSQL port to `127.0.0.1` by default.

### Reason

These changes reduce unnecessary privileges, avoid including local artifacts and documentation in the image build context, and prevent accidental LAN exposure of the local demonstration database.

### Consequences

The official Compose test command continues to work under the non-root user. Local tools can still reach PostgreSQL through `127.0.0.1:5432`, while remote devices cannot use the default binding.

This is practical local hardening, not a claim of production container security or complete network isolation.

## Decision 024 - Pin the Tested Application Dependencies and Base Image

### Context

Version ranges in `requirements.txt` and the mutable `python:3.12-slim` tag allowed local and CI builds to resolve different package and operating-system versions over time.

### Decision

Pin the full Python dependency set resolved by the tested Phase 6 image. Pin the Python slim base image to the tested digest:

```text
python:3.12-slim@sha256:c3d81d25b3154142b0b42eb1e61300024426268edeb5b5a26dd7ddf64d9daf28
```

### Reason

The same Dockerfile and requirements file should produce the same dependency set during local builds and CI. This makes test, Trivy, and exam evidence reproducible instead of date-dependent.

### Consequences

Dependency and base-image updates now require a deliberate review, rebuild, test run, and vulnerability scan.

Pinning stabilizes the tested image; it does not automatically remove vulnerabilities. The current refreshed image scan still reports `19 HIGH` and `3 CRITICAL` Debian findings without known fixes.
