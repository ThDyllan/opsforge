# OpsForge Documentation Index

## Purpose

This file is the documentation entry point for OpsForge.

It provides the recommended path for understanding the project, its current state, its planned phases, its architecture decisions, and the validation evidence for completed phases.

## Recommended Reading Order

1. [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) - Project overview, current state, roles, and strict contribution rules.
2. [`ROADMAP.md`](ROADMAP.md) - Phase plan, scope, and Definition of Done for each phase.
3. [`PHASE_SYNC_PROTOCOL.md`](PHASE_SYNC_PROTOCOL.md) - Required synchronization process before, during, and after each project phase.
4. [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) - Git and GitHub checks required before, during, and after project phases.
5. [`MVP1_VERIFICATION.md`](MVP1_VERIFICATION.md) - Phase 1 validation evidence for the local MVP1 application.
6. [`CI_CD.md`](CI_CD.md) - Phase 2 CI/CD design, workflow behavior, and GitHub Actions result.
7. [`PHASE2_VERIFICATION.md`](PHASE2_VERIFICATION.md) - Phase 2 validation evidence.
8. [`BACKUP_RESTORE.md`](BACKUP_RESTORE.md) - Phase 3 local PostgreSQL backup, archive validation, and restore procedure.
9. [`SECURITY.md`](SECURITY.md) - Phase 3 security scope, secrets strategy, Trivy policy, and known limitations.
10. [`PHASE3_VERIFICATION.md`](PHASE3_VERIFICATION.md) - Phase 3 implementation and validation evidence.
11. [`KUBERNETES.md`](KUBERNETES.md) - Phase 4 k3d deployment procedure, PostgreSQL resources, and persistence limits.
12. [`PHASE4_VERIFICATION.md`](PHASE4_VERIFICATION.md) - Phase 4 implementation and validation evidence.
13. [`MONITORING.md`](MONITORING.md) - Phase 5 monitoring strategy and application metrics scope.
14. [`PHASE5_VERIFICATION.md`](PHASE5_VERIFICATION.md) - Phase 5 implementation and validation evidence.
15. [`RISKS_AND_TECHNICAL_DEBT.md`](RISKS_AND_TECHNICAL_DEBT.md) - Known limitations, deferred improvements, guardrails, and upcoming decisions.
16. [`DECISIONS.md`](DECISIONS.md) - Architecture and technical decisions recorded for the project.

## Oral Preparation Path

For oral preparation, read these documents first:

1. [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)
2. [`ROADMAP.md`](ROADMAP.md)
3. [`PHASE_SYNC_PROTOCOL.md`](PHASE_SYNC_PROTOCOL.md)
4. [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md)
5. [`DECISIONS.md`](DECISIONS.md)
6. [`RISKS_AND_TECHNICAL_DEBT.md`](RISKS_AND_TECHNICAL_DEBT.md)
7. The verification file for each completed phase

The current phase verification files are:

- [`MVP1_VERIFICATION.md`](MVP1_VERIFICATION.md) for Phase 1.
- [`PHASE2_VERIFICATION.md`](PHASE2_VERIFICATION.md) for Phase 2.
- [`PHASE3_VERIFICATION.md`](PHASE3_VERIFICATION.md) for Phase 3 validation evidence.
- [`PHASE4_VERIFICATION.md`](PHASE4_VERIFICATION.md) for Phase 4 validation evidence.
- [`PHASE5_VERIFICATION.md`](PHASE5_VERIFICATION.md) for Phase 5 work in progress.

A dedicated `ORAL_PREPARATION.md` file will be created later during the exam documentation phase, once the technical scope is closer to final.

## Current Validated Phases

- Phase 1 - MVP1 Local App: validated.
- Phase 2 - CI/CD: validated.
- Phase 3 - Backup and Security: validated.
- Phase 4 - k3s/Kubernetes Deployment: validated.
- Phase 5 - Monitoring: in progress; Phase 5A application metrics started.

## Maintenance Rule

After each phase, update this index if a new major documentation file is created or if a phase status changes.
