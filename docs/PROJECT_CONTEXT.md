# OpsForge Project Context

## Project Overview

OpsForge is a personal RNCP DevOps school project.

It is a DevOps incident and service supervision platform. The project incrementally builds toward production-representative deployment patterns, phase by phase.

OpsForge is not a full enterprise production platform. It must remain simple, explainable, and defendable for an exam.

## Current MVP1

The current MVP1 is a FastAPI + PostgreSQL + Docker Compose application.

Current MVP1 stack:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Jinja2
- pytest
- Docker Compose

Core business flow:

```text
Service -> Alert -> Incident -> Runbook -> AuditLog
```

Runbooks are safe predefined actions only. Arbitrary shell command execution is forbidden.

## Current State

- MVP1 has been generated.
- Docker Compose starts correctly.
- PostgreSQL starts correctly.
- FastAPI starts correctly.
- `/health` works.
- `/dashboard` works after fixing the TemplateResponse issue.
- Tests currently pass.
- Phase 1 / MVP1 has been explicitly validated by the user.
- Phase 2 / CI/CD has been explicitly validated by the user after a successful GitHub Actions run covering tests, Docker image build, and Trivy scanning.
- Phase 3 / Backup and Security was locally verified and explicitly validated by the user on 2026-07-06.
- Phase 4 / k3d-Kubernetes Deployment has been explicitly validated by the user on 2026-07-09 after final checks passed. Phase 4A added the k3d/PostgreSQL foundation, and Phase 4B added the locally imported API image, Deployment, NodePort Service, and successful `/health` access.
- Phase 5 / Monitoring has been explicitly validated by the user on 2026-07-14 at commit `23194f0`. Phase 5A added a minimal Prometheus-compatible `/metrics` endpoint for the FastAPI application. Phase 5B deployed Prometheus inside k3d and verified scraping of the Kubernetes-deployed API. Phase 5C deployed Grafana and verified the `OpsForge Monitoring` dashboard. Phase 5D added the `OpsForgeApiDown` Prometheus alert rule and verified outage detection by scaling the API Deployment to zero, then restoring it.
- Known limitations, technical debts, and upcoming decisions are tracked in `docs/RISKS_AND_TECHNICAL_DEBT.md`.
- Phase transitions must follow `docs/PHASE_SYNC_PROTOCOL.md`.

## Role Distribution

- User: project owner, project manager, and final decision-maker.
- ChatGPT: architecture guidance, scope control, explanation, RNCP alignment, and prompt preparation.
- Codex: implementation only, following explicit tasks.
- Claude: occasional reviewer and scope challenger.

## Conflict Rule

If ChatGPT and Claude disagree, the user has the final decision.

No implementation should be done until the user validates the direction.

## Strict Contribution Rules

- Always read `PROJECT_CONTEXT.md` before implementing a task.
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
