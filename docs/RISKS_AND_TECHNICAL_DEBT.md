# Risks and Technical Debt

## Purpose

This file tracks known limitations, technical debts, and future decisions so they are not forgotten or hidden.

These items are documented tradeoffs in the current project scope. They should be reviewed when the relevant phase begins, but they do not automatically require immediate implementation.

## Current Known Technical Debts

### Tests Use SQLite While Runtime Uses PostgreSQL

The current pytest suite uses an in-memory SQLite database, while the application runtime uses PostgreSQL.

This was acceptable for MVP1 because it kept tests fast, independent from Docker services, and easy to run and explain.

The limitation is that SQLite tests do not fully reproduce PostgreSQL-specific behavior, including differences in SQL syntax, data types, constraints, transactions, and connection behavior.

A possible future improvement is to add PostgreSQL integration tests using Docker Compose or a PostgreSQL service in CI. This is not required unless explicitly selected for a later task.

### metadata.create_all() Is Used Instead of Migrations

MVP1 creates database tables with SQLAlchemy `metadata.create_all()` during application startup.

Alembic and migration history were intentionally out of scope for MVP1 to keep the application simple and exam-friendly.

The limitation is that schema changes do not have a versioned migration path. Migration tooling should be considered only if later project changes make it necessary.

### No Authentication

Authentication is intentionally out of scope for the current educational MVP.

OpsForge is currently treated as a local, single-user exam project rather than a public or multi-user production service.

This is a documented scope decision, not an overlooked production requirement.

### Trivy Is Non-Blocking in Phase 2

The Phase 2 Trivy image scan reports `HIGH` and `CRITICAL` findings, but it does not block the GitHub Actions workflow.

This was intentional so security findings are visible before the project defines a vulnerability acceptance policy.

A stricter blocking policy is deferred to Phase 3.

## Phase 3 Guardrails

Phase 3 should implement backup/restore and security documentation.

Backup and restore scripts, if created, must remain simple, readable, and explainable in approximately 30 seconds during the oral exam.

Avoid over-engineering. Phase 3 should not introduce:

- Vault
- Cloud backup storage
- Automated secret rotation
- A cron scheduler
- Encryption infrastructure
- Enterprise security tooling

These capabilities remain out of scope unless the user explicitly decides otherwise in a later task.

## Upcoming Decisions to Remember

### Phase 3

- Choose between documented backup/restore commands only or simple scripts plus documentation.
- Define the backup file location and naming convention.
- Define the vulnerability blocking policy after reviewing Trivy findings.

### Phase 4

- Choose between local k3s image import and registry publishing.
- Choose between NodePort and Ingress.
- Define the PostgreSQL storage approach in Kubernetes.

### Phase 5

- Define the exact application metrics to expose.

## Oral Exam Note

These items are not hidden failures.

They are known scope decisions, technical tradeoffs, and deferred improvements. During the oral exam, they should be explained honestly by stating:

- why the current choice was appropriate for the project phase;
- what limitation the choice creates;
- what future improvement is possible;
- why that improvement was not added prematurely.
