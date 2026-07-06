# OpsForge Roadmap

## Phase 1 - MVP1 Local App

### Scope

- FastAPI
- PostgreSQL
- Docker Compose
- Dashboard
- Services, alerts, incidents, runbooks, audit logs
- Tests
- README

### Definition of Done

- `docker compose up --build` starts the app successfully.
- `/health` returns status ok.
- `/dashboard` renders successfully.
- Services, alerts, incidents, runbooks, and audit logs are accessible through the API.
- The flow `Service -> Alert -> Incident -> Runbook -> AuditLog` is demonstrable.
- Tests pass.
- README explains how to run and test the project.
- The user explicitly validates Phase 1 as complete.

## Phase 2 - CI/CD

Status: completed and explicitly validated by the user on 2026-06-18.

### Scope

- GitHub Actions
- pytest
- Docker image build
- Trivy scan

### Definition of Done

- GitHub Actions runs on push or pull request.
- Tests run in CI.
- Docker image builds in CI.
- Trivy scan runs in CI.
- CI result is documented.
- The user explicitly validates Phase 2 as complete.

## Phase 3 - Backup and Security

Status: completed and explicitly validated by the user on 2026-07-06.

### Scope

- `pg_dump` backup script or documented command
- Restore procedure
- Security documentation
- Environment variables and secrets strategy

### Definition of Done

- Backup command or script works.
- Restore procedure is documented and tested.
- Security choices are documented.
- Secrets/configuration strategy is explained.
- The user explicitly validates Phase 3 as complete.

## Phase 4 - k3s/Kubernetes Deployment

### Scope

- Deployment
- Service
- ConfigMap
- Secret
- PersistentVolume
- NodePort or Ingress depending on feasibility

### Definition of Done

- Application runs in k3s/Kubernetes.
- Pods are healthy.
- Application is reachable through NodePort or Ingress.
- Configuration is handled through ConfigMap.
- Sensitive values are handled through Secret.
- PostgreSQL uses persistent storage.
- Deployment procedure is documented.
- The user explicitly validates Phase 4 as complete.

## Phase 5 - Monitoring

### Scope

- `/metrics` endpoint
- Prometheus
- Grafana dashboard

### Definition of Done

- The application exposes metrics.
- Prometheus scrapes the application.
- Grafana displays a dashboard.
- Dashboard includes at least basic request/application indicators.
- Monitoring setup is documented.
- The user explicitly validates Phase 5 as complete.

## Phase 6 - Exam Documentation

### Scope

- Architecture diagram
- Deployment procedure
- Backup/restore procedure
- Rollback procedure
- Screenshots
- Dossier projet notes
- Soutenance preparation

### Definition of Done

- Documentation explains the project clearly.
- Architecture is documented.
- Deployment is documented.
- Backup/restore is documented.
- Security choices are documented.
- Screenshots are collected.
- The oral demonstration path is prepared.
- The user explicitly validates Phase 6 as complete.
