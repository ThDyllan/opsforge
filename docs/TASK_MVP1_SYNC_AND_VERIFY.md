# TASK — MVP1 synchronization, documentation, and verification

Read this carefully before doing anything.

You are working on OpsForge, a personal RNCP DevOps school project.

Your role in this task:
- Create project context documentation.
- Verify that the existing MVP1 matches the intended project scope.
- Test the current API endpoints.
- Produce a clear verification report.
- Do not implement new features.
- Do not refactor the application.
- Do not fix bugs unless explicitly asked later.

Very important:
Everything is forbidden by default unless explicitly requested in this task.
If completing the task requires a decision not covered by this task description, stop and ask instead of assuming.

Creating temporary test data through the existing API during verification is allowed.
Do not create new scripts, fixtures, seed files, or helper tools to do this.
Use existing endpoints or existing seed data only.

Current project path:
C:\Users\Dyllan\Desktop\Work\opsforge

Current known state:
- MVP1 exists.
- Stack: FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Jinja2, pytest, Docker Compose.
- Docker Compose starts.
- PostgreSQL starts.
- FastAPI starts.
- /health works.
- /dashboard works after fixing a TemplateResponse issue.
- Tests currently pass: 7 passed.

Core project flow:
Service → Alert → Incident → Runbook → AuditLog

## PART 1 — Confirm understanding

Before creating or modifying files, write a short summary explaining:
- what OpsForge is;
- what MVP1 currently is;
- what the core flow is;
- what you are allowed to do in this task;
- what you are not allowed to do in this task.

## PART 2 — Create documentation files

Create the folder:

docs/

Create these files:

docs/PROJECT_CONTEXT.md
docs/ROADMAP.md
docs/DECISIONS.md
docs/MVP1_VERIFICATION.md

### 1. docs/PROJECT_CONTEXT.md

Explain clearly:
- OpsForge is a personal RNCP DevOps school project.
- It is a DevOps incident and service supervision platform.
- The project incrementally builds toward production-representative deployment patterns, phase by phase.
- It is not a full enterprise production platform.
- The current MVP1 is a FastAPI + PostgreSQL + Docker Compose application.
- The core business flow is:
  Service → Alert → Incident → Runbook → AuditLog
- Runbooks are safe predefined actions only.
- Arbitrary shell command execution is forbidden.
- The project must remain simple, explainable, and defendable for an exam.

Add the current state:
- MVP1 has been generated.
- Docker Compose starts correctly.
- PostgreSQL starts correctly.
- FastAPI starts correctly.
- /health works.
- /dashboard works after fixing the TemplateResponse issue.
- Tests currently pass.

Add the role distribution:
- User: project owner, project manager, and final decision-maker.
- ChatGPT: architecture guidance, scope control, explanation, RNCP alignment, and prompt preparation.
- Codex: implementation only, following explicit tasks.
- Claude: occasional reviewer and scope challenger.

Add conflict rule:
- If ChatGPT and Claude disagree, the user has the final decision.
- No implementation should be done until the user validates the direction.

Add strict contribution rules:
- Always read PROJECT_CONTEXT.md before implementing a task.
- Do only the requested task.
- Everything not explicitly requested is out of scope by default.
- Do not expand scope.
- Do not add new technologies unless explicitly requested.
- If completing the task requires a decision not covered by the task description, stop and ask instead of assuming.
- Prefer small, verifiable changes.
- After every change, explain what changed and how to test it.
- Existing tests must pass.
- If a change affects the README or docs, update them.
- Do not move to the next phase unless the current phase Definition of Done is validated by the user.

### 2. docs/ROADMAP.md

Document the project phases and include a Definition of Done for each phase.

#### Phase 1 — MVP1 local app

Scope:
- FastAPI
- PostgreSQL
- Docker Compose
- dashboard
- services, alerts, incidents, runbooks, audit logs
- tests
- README

Definition of Done:
- `docker compose up --build` starts the app successfully.
- `/health` returns status ok.
- `/dashboard` renders successfully.
- Services, alerts, incidents, runbooks, and audit logs are accessible through the API.
- The flow Service → Alert → Incident → Runbook → AuditLog is demonstrable.
- Tests pass.
- README explains how to run and test the project.
- The user explicitly validates Phase 1 as complete.

#### Phase 2 — CI/CD

Scope:
- GitHub Actions
- pytest
- Docker image build
- Trivy scan

Definition of Done:
- GitHub Actions runs on push or pull request.
- Tests run in CI.
- Docker image builds in CI.
- Trivy scan runs in CI.
- CI result is documented.
- The user explicitly validates Phase 2 as complete.

#### Phase 3 — Backup and security

Scope:
- pg_dump backup script or documented command
- restore procedure
- security documentation
- environment variables and secrets strategy

Definition of Done:
- Backup command or script works.
- Restore procedure is documented and tested.
- Security choices are documented.
- Secrets/configuration strategy is explained.
- The user explicitly validates Phase 3 as complete.

#### Phase 4 — k3s/Kubernetes deployment

Scope:
- Deployment
- Service
- ConfigMap
- Secret
- PersistentVolume
- NodePort or Ingress depending on feasibility

Definition of Done:
- Application runs in k3s/Kubernetes.
- Pods are healthy.
- Application is reachable through NodePort or Ingress.
- Configuration is handled through ConfigMap.
- Sensitive values are handled through Secret.
- PostgreSQL uses persistent storage.
- Deployment procedure is documented.
- The user explicitly validates Phase 4 as complete.

#### Phase 5 — Monitoring

Scope:
- /metrics endpoint
- Prometheus
- Grafana dashboard

Definition of Done:
- The application exposes metrics.
- Prometheus scrapes the application.
- Grafana displays a dashboard.
- Dashboard includes at least basic request/application indicators.
- Monitoring setup is documented.
- The user explicitly validates Phase 5 as complete.

#### Phase 6 — Exam documentation

Scope:
- architecture diagram
- deployment procedure
- backup/restore procedure
- rollback procedure
- screenshots
- dossier projet notes
- soutenance preparation

Definition of Done:
- Documentation explains the project clearly.
- Architecture is documented.
- Deployment is documented.
- Backup/restore is documented.
- Security choices are documented.
- Screenshots are collected.
- The oral demonstration path is prepared.
- The user explicitly validates Phase 6 as complete.

### 3. docs/DECISIONS.md

Create an Architecture Decision Record style file with initial decisions:

Decision 001 — Use FastAPI for backend
Decision 002 — Use PostgreSQL as relational database
Decision 003 — Use Docker Compose for MVP1 local environment
Decision 004 — Use Jinja2 instead of React for MVP1 dashboard
Decision 005 — Forbid arbitrary shell command execution in runbooks
Decision 006 — Use metadata.create_all() for MVP1 instead of Alembic
Decision 007 — Keep Kubernetes, CI/CD, and monitoring for later phases
Decision 008 — No authentication in MVP1

For each decision, include:
- Context
- Decision
- Reason
- Consequences

For Decision 008, explain:
- MVP1 is a local, single-user exam project.
- Authentication is intentionally deferred to avoid over-scoping.
- This is a documented scope decision, not an oversight.
- Security is still addressed through safe runbooks, no arbitrary command execution, audit logs, and later secret management.

## PART 3 — Inspect code and verify MVP1

Inspect the existing code without refactoring it.

Check:
- existing models;
- existing routes;
- existing runbooks;
- existing tests;
- docker-compose.yml;
- README.md.

Verify whether the existing code supports the intended core flow:

Service → Alert → Incident → Runbook → AuditLog

Security check:
Confirm that app/runbooks.py contains only predefined safe actions.
Confirm that there is no arbitrary shell command execution.
Specifically check that there is no unsafe use of subprocess, os.system, shell=True, eval, exec, or arbitrary user-provided command execution.

Run the test suite.

Prefer testing inside Docker if the app is running there:

```bash
docker compose exec api pytest
```

If that is not possible, use the local pytest command and report what you used.

Test the main endpoints manually if possible:

- GET /health
- GET /dashboard
- GET /api/services
- GET /api/alerts
- GET /api/incidents
- GET /api/runbooks
- GET /api/audit-logs

Also test the core flow if the current API supports it:

1. Create or identify a service.
2. Create an alert linked to that service.
3. Create an incident linked to that alert through source_alert_id if supported.
4. Execute a safe predefined runbook.
5. Verify that a RunbookExecution is created if accessible.
6. Verify that an AuditLog entry is created.

Do not add missing endpoints.
Do not fix missing logic.
Only report findings.

## PART 4 — Write docs/MVP1_VERIFICATION.md

In docs/MVP1_VERIFICATION.md, write a clear verification report with:

- Date of verification.
- Commands executed.
- Test results.
- Endpoint verification table.
- Runbook security check result.
- Whether the core flow is fully demonstrable or only partially demonstrable.
- Any missing or weak points found.
- Whether Phase 1 Definition of Done is fully met or not yet.
- Recommended next small task, without implementing it.

Important:
If Phase 1 is not fully complete, say so honestly.
Do not mark Phase 1 complete unless all Definition of Done items are actually verified.

## Final response

After completing the task, summarize:
- files created;
- commands run;
- test result;
- endpoint result;
- runbook security check result;
- whether you think MVP1 is complete or still needs fixes;
- any question or decision needed from the user.

Again:
Do not modify application logic.
Do not refactor.
Do not add features.
Documentation and verification only.
