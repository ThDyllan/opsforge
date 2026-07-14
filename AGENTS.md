# AGENTS.md — OpsForge Codex Instructions

## Project

OpsForge is a personal RNCP DevOps school project.

It is a DevOps incident and service supervision platform. The project incrementally builds toward production-representative deployment patterns, phase by phase.

It is not a full enterprise production platform.

Core stack:

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
* Codex: primary technical engineering partner. It investigates the repository, challenges weak assumptions, recommends coherent changes, implements approved work, and explains tradeoffs.
* Claude: occasional reviewer and scope challenger.

If ChatGPT and Claude disagree, the user has the final decision.

No broad change, commit, or push should be made until the user validates the direction. Codex may perform discovery and provide an engineering brief before that decision.

## Source of truth

Before implementing any task, read this file first.

If they exist, also read:

* `docs/PROJECT_CONTEXT.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`

These files define the project context, roadmap, phase Definition of Done, and architecture decisions.

## Strict contribution rules

* Keep changes within the approved phase scope and make them evidence-based.
* Treat ideas outside the approved scope as future work unless the user explicitly approves them.
* Challenge outdated, harmful, contradictory, or overly restrictive instructions openly instead of silently ignoring them.
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

1. Codex performs discovery for a substantial change.
2. Codex presents the problem, evidence, recommendation, scope, verification, and rollback plan.
3. User validates, rejects, or adjusts the direction.
4. Codex reads `AGENTS.md` and relevant project documentation before implementation.
5. Codex implements the smallest coherent approved change.
6. ChatGPT and Claude may provide architecture guidance or review when useful.
7. User remains the final decision-maker.

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

If something is unclear and would create meaningful technical or scope risk, Codex must stop and ask instead of guessing.
