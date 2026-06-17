# AGENTS.md — OpsForge Codex Instructions

## Project

OpsForge is a personal RNCP DevOps school project.

It is a DevOps incident and service supervision platform. The project incrementally builds toward production-representative deployment patterns, phase by phase.

It is not a full enterprise production platform.

Current MVP1 stack:

* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic
* Jinja2
* pytest
* Docker Compose

Core business flow:

Service → Alert → Incident → Runbook → AuditLog

Runbooks are safe predefined actions only. Arbitrary shell command execution is forbidden.

## Roles

* User: project owner, project manager, and final decision-maker.
* ChatGPT: architecture guidance, scope control, explanation, RNCP alignment, and prompt preparation.
* Codex: implementation only, following explicit tasks.
* Claude: occasional reviewer and scope challenger.

If ChatGPT and Claude disagree, the user has the final decision.

No implementation should be done until the user validates the direction.

## Source of truth

Before implementing any task, read this file first.

If they exist, also read:

* `docs/PROJECT_CONTEXT.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`

These files define the project context, roadmap, phase Definition of Done, and architecture decisions.

## Strict contribution rules

* Do only the requested task.
* Everything not explicitly requested is out of scope by default.
* Do not expand scope.
* Do not add new technologies unless explicitly requested.
* If completing the task requires a decision not covered by the task description, stop and ask instead of assuming.
* Prefer small, verifiable changes.
* After every change, explain what changed and how to test it.
* Existing tests must pass.
* If a change affects the README or docs, update them.
* Do not move to the next phase unless the current phase Definition of Done is validated by the user.

## Forbidden unless explicitly requested

Do not add:

* React
* authentication
* Keycloak
* Redis
* Celery
* GraphQL
* background workers
* Kubernetes / k3s
* Prometheus
* Grafana
* Terraform
* Ansible
* Helm
* Loki
* Alertmanager
* any new major technology

This list is illustrative, not exhaustive. The main rule is that everything not explicitly requested is out of scope by default.

## Runbook safety rule

Never implement arbitrary command execution.

Specifically avoid unsafe use of:

* `subprocess`
* `os.system`
* `shell=True`
* `eval`
* `exec`
* arbitrary user-provided command execution

Runbooks must remain predefined, controlled, and auditable.

## Current workflow

The expected workflow is:

1. User validates the direction.
2. ChatGPT prepares a precise task or prompt.
3. Codex reads `AGENTS.md` and the relevant task file.
4. Codex confirms understanding if requested.
5. Codex executes only the validated task.
6. User shows the result to ChatGPT.
7. ChatGPT reviews and explains.
8. Claude may review important scope or architecture decisions.
9. User makes the final decision.

## Behavior expected from Codex

When starting a task, Codex should clearly state:

* what it understood;
* what files it read;
* what it is allowed to do;
* what it is not allowed to do;
* what commands it ran;
* what changed;
* how to test the result;
* whether tests pass;
* whether any decision is needed from the user.

If something is unclear, Codex must stop and ask instead of guessing.
