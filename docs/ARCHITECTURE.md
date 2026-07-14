# OpsForge Architecture

## Purpose

This document describes the implemented OpsForge architecture and the boundaries that make it suitable for an RNCP demonstration. It is a local educational platform, not a production deployment design.

## System View

```mermaid
flowchart LR
    User[Operator] --> Dashboard[Jinja2 dashboard]
    Dashboard --> API[FastAPI application]
    API --> Database[(PostgreSQL)]
    API --> Metrics[/metrics]
    Metrics --> Prometheus[Prometheus in k3d]
    Prometheus --> Grafana[Grafana dashboard]
    Prometheus --> AlertRule[OpsForgeApiDown]

    GitHub[GitHub push or pull request] --> CI[GitHub Actions]
    CI --> Unit[SQLite unit tests]
    CI --> Integration[PostgreSQL integration test]
    CI --> Build[Docker image build]
    CI --> Trivy[Trivy image scan]

    Build --> LocalImage[k3d local image import]
    LocalImage --> K8sAPI[OpsForge API Deployment]
    K8sAPI --> K8sDatabase[PostgreSQL StatefulSet and PVC]
```

## Operational Flow

The application models a supervised-service workflow:

```text
Service -> Alert -> Incident -> RunbookExecution -> AuditLog
```

- A service represents an application under supervision.
- An alert may be attached to one service.
- An incident may inherit the service of its source alert.
- The API rejects an incident that supplies a service different from the source alert service.
- The dashboard can set an incident to `investigating` or `resolved` and execute a predefined runbook with the incident context.
- A runbook request with unrelated service and incident records is persisted as a failed, audited execution without storing the unrelated service link.
- Every runbook execution creates an `AuditLog` record.

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

## Deliberate Limits

- The tests use both fast SQLite unit tests and one PostgreSQL integration test, but they are not exhaustive database compatibility testing.
- Images are built in CI but not pushed to a registry. k3d image import is local and manual.
- Prometheus and Grafana are local, use ephemeral storage, and are accessed through port-forwarding.
- Alert detection has no Alertmanager or notification channel.
- `metadata.create_all()` is used instead of migrations.
- There is no authentication because OpsForge remains a local, single-user educational application.
