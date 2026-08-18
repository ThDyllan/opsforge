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

Status: completed and explicitly validated by the user on 2026-07-09. Phase 4A was locally verified on 2026-07-07, Phase 4B API deployment was locally verified on 2026-07-08, and final validation checks passed on 2026-07-09.

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

Status: completed and explicitly validated by the user on 2026-07-14. Phase 5A adds a minimal Prometheus-compatible `/metrics` endpoint to the API. Phase 5B deploys Prometheus inside k3d and verifies that it scrapes the Kubernetes-deployed API. Phase 5C deploys Grafana and verifies the `OpsForge Monitoring` dashboard. Phase 5D adds the `OpsForgeApiDown` Prometheus alert rule and verifies outage detection by scaling the API Deployment to zero, then restoring it.

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

## Phase 6 - Operational Product and Exam Evidence

Status: completed and explicitly validated by the user on 2026-08-19. The manual desktop/workflow/responsive review was performed by the user; it surfaced two real defects (a 422 on the list filter forms when no service was selected, and an unreadable compressed incidents table on mobile) which were fixed, regression-tested (test suite 35 -> 38) and re-validated on the merged candidate (PRs #4 and #5, final candidate `f6e4a79`), together with a small UX polish pass (filters applied on select change, brand favicon). Screenshots and CI evidence for the final candidate were collected during the review sessions.

### Scope

- Domain integrity safeguards, forward-only transitions, and negative tests.
- A multipage Jinja operator console with operational queues and an Incident Command Center.
- Managed manual runbooks and allowlisted automated runbooks.
- Mutation auditing and incident timelines.
- Generic demonstration scenarios and isolated PostgreSQL test data.
- PostgreSQL-aware readiness and non-root container execution.
- SQLite unit tests plus PostgreSQL integration coverage in CI.
- Architecture diagram
- Deployment procedure
- Backup/restore procedure
- Rollback procedure
- Screenshots
- Dossier projet notes
- Soutenance preparation

### Definition of Done

- Documentation explains the project clearly.
- Invalid service, alert, incident, and runbook relationships are rejected or safely audited.
- The console demonstrates the `Service -> Alert -> Incident -> RunbookExecution -> AuditLog` flow without requiring Swagger.
- Alert and incident lifecycles are forward-only, and one source alert cannot create two active incidents.
- Manual and automated runbooks are usable only with compatible context and never execute arbitrary commands.
- Meaningful operator mutations and runbook results are auditable.
- PostgreSQL integration tests do not pollute the demonstration database.
- `/health` and `/ready` have separate, documented liveness and readiness roles.
- SQLite unit tests and the PostgreSQL integration test pass locally and in GitHub Actions.
- Architecture is documented.
- Deployment is documented.
- Backup/restore is documented.
- Security choices are documented.
- Screenshots are collected.
- The product guide, manual operator test, and oral demonstration path are prepared.
- Desktop and responsive operator workflows are manually reviewed.
- The current Phase 6 candidate passes GitHub Actions.
- The user explicitly validates Phase 6 as complete.

### Phase 6 Final Sub-step - Infrastructure Deployment Automation (CP N°2)

Status: implemented, validated on a local k3d cluster. Added late in Phase 6, after the operator-product candidate, to close the RNCP CP N°2 competency ("Automatiser le deploiement d'une infrastructure"), which the earlier phases covered only through a manual `k3d`/`kubectl` sequence.

Scope:

- An Ansible playbook (`ansible/deploy.yml`, `kubernetes.core` collection) that orchestrates the existing `k8s/` manifests: create the k3d cluster (idempotent), build and import the API image, apply PostgreSQL, API, and monitoring waiting for each tier to be ready, then verify `/health` and `/ready`.
- A containerised control node (`ansible/run.sh`) as the supported, validated way to run it.
- Documentation and CP N°2 mapping in [`ANSIBLE.md`](ANSIBLE.md).

Definition of Done:

- One command deploys the whole local infrastructure and verifies it.
- Re-running the playbook is idempotent.
- Scope stays local k3d: no container registry, no cloud provisioning, no remote/complete CD.
- The deployment automation is documented and mapped to CP N°2.

This does not close the outstanding Phase 6 verification items above (final screenshots, current-branch CI evidence, and the manual visual/responsive review remain to be produced).
