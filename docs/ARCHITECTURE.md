# OpsForge Architecture

## Purpose

This document describes the implemented OpsForge architecture and the boundaries that make it suitable for an RNCP demonstration. It is a local educational platform, not a production deployment design.

## System View

```mermaid
flowchart LR
    User[Single operator] --> Web[Jinja2 operator console]
    Web --> API[FastAPI API routes]
    API --> Domain[Domain transitions and runbooks]
    Domain --> Database[(PostgreSQL)]
    API --> Audit[AuditLog and incident timeline]
    API --> Metrics[/metrics]
    Metrics --> Prometheus[Prometheus in k3d]
    Prometheus --> Grafana[Grafana dashboard]
    Prometheus --> AlertRule[OpsForgeApiDown]

    GitHub[GitHub push or pull request] --> CI[GitHub Actions]
    CI --> Unit[SQLite unit tests]
    CI --> Integration[Isolated PostgreSQL integration test]
    CI --> Build[Docker image build]
    CI --> Trivy[Trivy image scan]

    Build --> LocalImage[k3d local image import]
    LocalImage --> K8sAPI[OpsForge API Deployment]
    K8sAPI --> K8sDatabase[PostgreSQL StatefulSet and PVC]
```

## Application Structure

- `app/main.py` owns startup, liveness, readiness, metrics, static files, and router registration.
- `app/web.py` owns read-only HTML page composition and Jinja filters.
- `app/api.py` exposes service, alert, incident, runbook, execution, and audit APIs.
- `app/domain.py` centralizes transition rules, audit helpers, and relationship validation.
- `app/runbooks.py` implements manual completion and the allowlist of approved automated behaviors.
- `app/models.py` and `app/schemas.py` define persistence and request/response contracts.
- `app/seed.py` creates idempotent, generic demonstration data.
- `app/migrations.py` contains a small additive startup compatibility bridge for the Phase 6 schema evolution.
- `app/templates/` and `app/static/` provide the multipage server-rendered operator console.

The HTML console calls the same JSON API used by tests. Jinja renders queues and context; a small framework-free JavaScript file submits forms and contextual actions.

## Operational Flow

The application models a supervised-service workflow:

```text
Service -> Alert -> Incident -> Runbook -> RunbookExecution -> AuditLog
```

- A service represents an application under supervision.
- An alert may be attached to one service.
- An incident may inherit the service of its source alert.
- The API rejects an incident that supplies a service different from the source alert service.
- Alert transitions are `new -> acknowledged -> resolved`; incident transitions are `open -> investigating -> resolved`.
- One source alert can have only one active incident. A recurring problem creates a new incident only after the previous one is resolved.
- Resolving an incident does not automatically resolve its source alert.
- Manual runbooks use checklists and an operator-confirmed outcome.
- Automated runbooks can use only an approved `automation_key`; there is no arbitrary shell or script execution.
- A runbook request with incompatible context is persisted as a failed, audited execution without retaining an invalid relationship.
- Meaningful service, alert, incident, runbook, and execution mutations create audit evidence. Incident-specific logs form the Command Center timeline.

## Operator Console

The interface is split by operational responsibility:

- Overview summarizes urgent work and the real platform state.
- Alerts is the signal queue.
- Incidents is the ownership queue; each incident has a dedicated Command Center.
- Services and Runbooks are maintained reference catalogs.
- Activity is the global audit journal.
- Monitoring distinguishes real platform telemetry from simulated business-service state.
- Help explains the workflow, terms, demonstration scenario, and limits.

`/dashboard` is retained only as a compatibility redirect to `/overview`.

## Runtime Layers

### Docker Compose

Docker Compose is the local development and backup environment. The API and PostgreSQL run as separate containers. PostgreSQL is bound to `127.0.0.1` by default, so it remains available to local tooling without being exposed on every network interface.

The API image runs as the non-root `opsforge` user. Its Docker healthcheck calls `/health`, which checks that the FastAPI process responds.

### Kubernetes

The local k3d cluster runs one API Deployment and one PostgreSQL StatefulSet with local-path persistent storage. The API is exposed locally through NodePort on `http://localhost:8080`.

The probes have separate responsibilities:

- `/health` is the liveness signal: the FastAPI process is responding.
- `/ready` is the readiness signal: the application can execute `SELECT 1` against PostgreSQL.

This prevents Kubernetes from routing traffic to an API process that is alive but cannot use its required database.

### Monitoring

Prometheus scrapes the API through the internal Kubernetes service. Grafana uses Prometheus as a provisioned datasource and displays the tracked dashboard. `OpsForgeApiDown` becomes firing when Prometheus cannot scrape the API for 30 seconds.

Prometheus does not currently create business alerts inside OpsForge. Service statuses and business alerts shown in the operator console are demonstration data and are labeled as such.

## Test Isolation

`tests/test_app.py` recreates an in-memory SQLite schema for fast isolated feedback. `tests/postgres_integration.py` connects to the configured PostgreSQL server, creates a uniquely named temporary database, verifies the core flow, disposes its connections, and drops the temporary database.

This prevents PostgreSQL CI or local integration tests from adding records to the operator demonstration database.

## Deliberate Limits

- The tests use both fast SQLite unit tests and one PostgreSQL integration test, but they are not exhaustive database compatibility testing.
- Images are built in CI but not pushed to a registry. k3d image import is local and manual.
- Prometheus and Grafana are local, use ephemeral storage, and are accessed through port-forwarding.
- Alert detection has no Alertmanager or notification channel.
- `metadata.create_all()` is used instead of migrations.
- The Phase 6 additive compatibility bridge is not a replacement for versioned Alembic migrations.
- There is no authentication because OpsForge remains a local, single-user educational application.
- Service health values and business alerts are simulated; only the platform health, metrics, Kubernetes, Prometheus, Grafana, and alert rule are real technical signals.
- The one-active-incident rule is enforced by application logic, not a database partial unique constraint.
