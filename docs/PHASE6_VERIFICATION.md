# Phase 6 Verification

## Status

Phase 6 is in progress. The first operational-product and evidence slice was locally verified on 2026-07-15 and passed GitHub Actions for commit `83469cb Implement Phase 6 balanced review candidate`, but Phase 6 is not user-validated yet.

## Implemented In This Slice

- Incident creation rejects a service that conflicts with its source alert.
- Runbook execution records an unrelated service and incident request as a failed, audited execution without persisting the unrelated service link.
- The Jinja dashboard exposes an incident workspace with incident status actions, predefined runbook execution, and recent runbook activity.
- `/health` remains a process liveness endpoint and `/ready` verifies PostgreSQL connectivity.
- The API image runs as a non-root user and has a Docker healthcheck.
- Docker Compose binds PostgreSQL to `127.0.0.1` by default.
- The Docker build context excludes repository metadata, tests, documentation, backups, local configuration, and Kubernetes material.
- GitHub Actions now separates SQLite unit tests from a PostgreSQL integration test.
- The Python base image and resolved dependencies are pinned to the locally tested Phase 6 build.

## Local Evidence

- SQLite unit tests: `13 passed, 1 warning` with `docker compose exec api pytest`.
- PostgreSQL integration test: `1 passed, 1 warning` with `docker compose exec api pytest tests/postgres_integration.py`.
- The shared warning is the tracked `StarletteDeprecationWarning` from the current `fastapi.testclient` path; it does not mask a failed test.
- Docker image build succeeded with the non-root `opsforge` user and configured healthcheck.
- Compose `/health` returned `200` during a controlled PostgreSQL outage while `/ready` returned `503`, then returned to ready after PostgreSQL restarted.
- The k3d API Deployment using `opsforge-api:phase6` rolled out `1/1` and returned successful `/health` and `/ready` responses.
- Prometheus returned `up{job="opsforge-api"} = 1`; `OpsForgeApiDown` was inactive; Grafana health was `ok` after the Phase 6 API rollout.
- The refreshed pinned image passed the SQLite and PostgreSQL integration tests. Its Trivy scan reported `19 HIGH` and `3 CRITICAL` Debian findings with no known fixes; the CI policy remains non-blocking and this limitation is documented.

## GitHub Actions Evidence

- The `CI` workflow completed successfully on the `phase6-balanced-review` branch for commit `83469cb`.
- The workflow passed `13` SQLite unit tests and `1` PostgreSQL integration test.
- The Docker image build succeeded.
- Trivy ran successfully as a non-blocking scan and reported `19 HIGH` and `3 CRITICAL` findings. These findings remain documented security debt; a green workflow is not a claim that the image is vulnerability-free.

## Manual Dashboard Smoke Test

The user completed the dashboard smoke test on 2026-07-15:

- the incident status changed to `investigating` through the dashboard;
- `generate_incident_report` completed with a visible `success` result;
- the execution appeared in `Recent runbook activity` after refresh;
- the `Resolve` action was confirmed to work and remove an incident from the open workspace.

The test also confirmed a usability limitation: creating alerts and incidents still requires FastAPI `/docs` and manual identifier selection. A separate operator-centered UX lot will address this after the current review candidate is merged.

## Remaining Validation

- Capture final dashboard, Kubernetes, Prometheus, and Grafana screenshots.
- Review the complete Phase 6 scope with the user and obtain explicit Phase 6 validation.
