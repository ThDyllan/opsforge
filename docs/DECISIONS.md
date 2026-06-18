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
