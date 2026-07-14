# OpsForge Oral Preparation

## Purpose

This guide is the practical demonstration path for the RNCP oral exam. It is based on implemented behavior and should be rehearsed after the final environment is prepared.

## Suggested Demonstration Path

1. Start with the product: open `/dashboard` and show services, alerts, open incidents, available runbooks, and recent runbook activity.
2. Explain the business chain: an alert belongs to a service, an incident inherits that service, and a safe predefined runbook produces an audited execution.
3. Use an incident workspace card: set an incident to `investigating`, run `Generate incident report`, show the result in recent activity, then resolve the incident.
4. Run `docker compose exec api pytest` and explain that fast unit tests use SQLite.
5. Run `docker compose exec api pytest tests/postgres_integration.py` and explain that this proves the core flow against PostgreSQL without making the fast suite slow.
6. Show the GitHub Actions workflow: SQLite tests, PostgreSQL integration test, Docker build, and non-blocking Trivy scan.
7. Show `scripts/backup.ps1` and `scripts/restore.ps1`, then explain that the default restore verifies a temporary database instead of replacing the main database.
8. Show k3d resources with `kubectl -n opsforge get pods,svc,pvc` and open `http://localhost:8080/health` and `http://localhost:8080/ready`.
9. Show Prometheus and Grafana with port-forwarding. Demonstrate `OpsForgeApiDown` by scaling the API to zero only when the restore command is ready.

## Questions To Be Ready For

| Question | Honest answer |
| --- | --- |
| Why Jinja2 rather than React? | The project needs an operational interface, not frontend framework complexity. Jinja2 makes the workflow visible while keeping the stack small and explainable. |
| Why both SQLite and PostgreSQL tests? | SQLite gives fast isolated feedback. A separate PostgreSQL integration test protects the core flow from database-specific differences. |
| Why separate `/health` and `/ready`? | A running web process is not useful if PostgreSQL is unavailable. Liveness detects a dead process; readiness prevents traffic from reaching an API that cannot use its dependency. |
| Why are runbooks safe? | They are fixed Python behaviors. The API never accepts or executes arbitrary shell commands. |
| Why is Trivy non-blocking? | Findings are visible and documented, but this local educational project has not defined a justified vulnerability acceptance threshold. A green CI result does not mean no vulnerabilities exist. |
| Why k3d image import and NodePort? | They are the smallest local mechanisms to demonstrate Kubernetes deployment without registry, Ingress, or cloud infrastructure scope. |
| What would change in production? | Migrations, authentication, registry delivery, managed secrets, durable/offsite backups, persistent monitoring, alert routing, and a defined vulnerability policy would be considered deliberately. |

## Evidence To Collect Before The Exam

- A current dashboard screenshot showing the incident workspace and runbook activity.
- GitHub Actions run showing both test steps, Docker build, and Trivy scan.
- k3d workload status, `/health`, and `/ready` evidence.
- Prometheus target/rule evidence and Grafana dashboard screenshot.
- Backup creation and temporary restore verification output.
- A short note of current known limitations from `RISKS_AND_TECHNICAL_DEBT.md`.
