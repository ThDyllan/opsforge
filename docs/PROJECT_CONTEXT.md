# OpsForge Project Context

## Project Overview

OpsForge is a personal RNCP DevOps school project.

It is a local, single-operator incident console. An operator can qualify service signals, declare and investigate incidents, follow controlled runbooks, and retrieve audit evidence. The project also demonstrates the DevOps lifecycle around that product, phase by phase.

OpsForge is not a full enterprise production platform. It must remain simple, explainable, and defendable for an exam.

## Technical Foundation

OpsForge began as a FastAPI + PostgreSQL + Docker Compose MVP and now includes validated CI, backup/restore, local k3d deployment, and monitoring.

Core stack:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Jinja2
- pytest
- Docker Compose

Core business flow:

```text
Service -> Alert -> Incident -> RunbookExecution -> AuditLog
```

Runbooks can be manual checklists or approved automated Python behaviors. Arbitrary shell commands, scripts, and code execution are forbidden.

## Current State

- MVP1 has been generated.
- Docker Compose starts correctly.
- PostgreSQL starts correctly.
- FastAPI starts correctly.
- `/health` works.
- `/dashboard` remains a compatibility redirect to the multipage operator console at `/overview`.
- The operator console provides Overview, Alerts, Incidents, Services, Runbooks, Activity, Monitoring, and Help views without requiring Swagger for the main workflow.
- Tests currently pass through a fast SQLite suite and an isolated PostgreSQL core-flow integration test.
- Phase 1 / MVP1 has been explicitly validated by the user.
- Phase 2 / CI/CD has been explicitly validated by the user after a successful GitHub Actions run covering tests, Docker image build, and Trivy scanning.
- Phase 3 / Backup and Security was locally verified and explicitly validated by the user on 2026-07-06.
- Phase 4 / k3d-Kubernetes Deployment has been explicitly validated by the user on 2026-07-09 after final checks passed. Phase 4A added the k3d/PostgreSQL foundation, and Phase 4B added the locally imported API image, Deployment, NodePort Service, and successful `/health` access.
- Phase 5 / Monitoring has been explicitly validated by the user on 2026-07-14 at commit `23194f0`. Phase 5A added a minimal Prometheus-compatible `/metrics` endpoint for the FastAPI application. Phase 5B deployed Prometheus inside k3d and verified scraping of the Kubernetes-deployed API. Phase 5C deployed Grafana and verified the `OpsForge Monitoring` dashboard. Phase 5D added the `OpsForgeApiDown` Prometheus alert rule and verified outage detection by scaling the API Deployment to zero, then restoring it.
- Phase 6 / Operational Product and Exam Evidence is in progress on `phase6-operator-ux`. The current review candidate adds forward-only domain transitions, one active incident per source alert, complete mutation auditing, managed manual/approved runbooks, isolated PostgreSQL test data, clean generic demonstration data, and a multipage Jinja operator console. Automated backend and structural page checks pass, but final visual/responsive review, current GitHub Actions evidence, screenshots, and explicit user validation are still required.
- The product behavior and manual validation path are documented in `docs/PRODUCT_GUIDE.md` and `docs/PHASE6_MANUAL_TEST.md`.
- Known limitations, technical debts, and upcoming decisions are tracked in `docs/RISKS_AND_TECHNICAL_DEBT.md`.
- Phase transitions must follow `docs/PHASE_SYNC_PROTOCOL.md`.
- Engineering collaboration follows `docs/ENGINEERING_CHARTER.md`.

## Role Distribution

- User: project owner, project manager, and final decision-maker.
- ChatGPT: architecture guidance, scope control, explanation, RNCP alignment, and prompt preparation.
- Codex: primary technical engineering partner. It inspects, challenges, recommends, implements approved work, and explains technical tradeoffs.
- Claude: occasional reviewer and scope challenger.

## Conflict Rule

If ChatGPT and Claude disagree, the user has the final decision.

No broad change, commit, or push should be made until the user validates the direction. Codex may perform discovery and present an engineering brief before that decision.

## Strict Contribution Rules

- Always read `PROJECT_CONTEXT.md` before implementing a task.
- Keep changes coherent, evidence-based, and within the approved phase scope.
- Treat ideas outside the approved scope as future work unless the user explicitly approves them.
- Challenge outdated, contradictory, or weak instructions openly rather than silently ignoring them.
- Do not add new technologies unless explicitly requested.
- If completing the task requires a decision not covered by the task description, stop and ask instead of assuming.
- Prefer small, verifiable changes.
- After every change, explain what changed and how to test it.
- Existing tests must pass.
- If a change affects the README or docs, update them.
- Do not move to the next phase unless the current phase Definition of Done is validated by the user.
