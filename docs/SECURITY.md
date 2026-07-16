# Security

## Current Scope

OpsForge is a local, single-user RNCP educational project. Phase 3 documents practical security choices without presenting the application as production-hardened.

Current controls include:

- manual runbooks and allowlisted automated behaviors with no arbitrary command execution;
- audit logs for meaningful business mutations and every runbook attempt;
- environment-based database configuration;
- ignored local secrets and backup artifacts;
- non-root API container execution;
- local Compose PostgreSQL bound to `127.0.0.1` by default;
- automated Trivy visibility in GitHub Actions.

## Environment Variables and Secrets

`docker-compose.yml` reads PostgreSQL and application configuration from environment variables. The tracked `.env.example` shows the expected variable names and local demonstration values.

For local configuration:

1. copy `.env.example` to `.env`;
2. replace demonstration values with local values;
3. keep `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `DATABASE_URL` consistent;
4. never commit `.env`.

The existing Compose fallback values and `.env.example` values are for local demonstration only. They are not suitable production credentials.

The Compose PostgreSQL port is available locally as `127.0.0.1:5432` by default. This prevents accidental exposure on every host network interface, but it does not make the demonstration credentials production-safe.

Secrets must not be written into scripts, source code, documentation examples, commits, or generated logs.

## Backup Data

Database backups can contain application data and must not be committed. Generated files under `backups/` are ignored by Git. Phase 3 stores backups only on the local workstation and does not add encryption or offsite storage.

## Trivy Policy

Trivy remains non-blocking in Phase 3. The scan still runs in GitHub Actions and exposes `HIGH` and `CRITICAL` findings, but findings do not fail the workflow.

This is a deliberate educational-scope decision: findings remain visible and must be understood and documented, while a blocking acceptance policy is deferred until the project has a justified enforcement threshold. Phase 3 does not change GitHub Actions behavior.

## Known Limitations

- No authentication or authorization.
- No encrypted backups.
- No enterprise secret manager such as Vault.
- No automated secret rotation.
- No production hardening or public deployment claim.
- No defined vulnerability blocking threshold.
- No automatic backup schedule, rotation, or offsite copy.
- Trivy findings are visible but non-blocking.
- Runbook output can prove only the approved handler or operator confirmation recorded by OpsForge; simulated actions are labeled as simulations.

These choices keep the project small, explainable, and aligned with its current RNCP phase. They must be presented as known limitations, not production security guarantees.
