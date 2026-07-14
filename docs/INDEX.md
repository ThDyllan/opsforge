# OpsForge Documentation Index

## Purpose

This file is the documentation entry point for OpsForge.

It provides the recommended path for understanding the project, its current state, its planned phases, its architecture decisions, and the validation evidence for completed phases.

## Recommended Reading Order

1. [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) - Project overview, current state, roles, and strict contribution rules.
2. [`ROADMAP.md`](ROADMAP.md) - Phase plan, scope, and Definition of Done for each phase.
3. [`PHASE_SYNC_PROTOCOL.md`](PHASE_SYNC_PROTOCOL.md) - Required synchronization process before, during, and after each project phase.
4. [`ENGINEERING_CHARTER.md`](ENGINEERING_CHARTER.md) - Independent engineering-partner role, approval boundaries, and learning contract.
5. [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) - Git and GitHub checks required before, during, and after project phases.
6. [`MVP1_VERIFICATION.md`](MVP1_VERIFICATION.md) - Phase 1 validation evidence for the local MVP1 application.
7. [`CI_CD.md`](CI_CD.md) - Phase 2 CI/CD design, workflow behavior, and GitHub Actions result.
8. [`PHASE2_VERIFICATION.md`](PHASE2_VERIFICATION.md) - Phase 2 validation evidence.
9. [`BACKUP_RESTORE.md`](BACKUP_RESTORE.md) - Phase 3 local PostgreSQL backup, archive validation, and restore procedure.
10. [`SECURITY.md`](SECURITY.md) - Phase 3 security scope, secrets strategy, Trivy policy, and known limitations.
11. [`PHASE3_VERIFICATION.md`](PHASE3_VERIFICATION.md) - Phase 3 implementation and validation evidence.
12. [`KUBERNETES.md`](KUBERNETES.md) - Phase 4 k3d deployment procedure, PostgreSQL resources, and persistence limits.
13. [`PHASE4_VERIFICATION.md`](PHASE4_VERIFICATION.md) - Phase 4 implementation and validation evidence.
14. [`MONITORING.md`](MONITORING.md) - Phase 5 monitoring strategy and application metrics scope.
15. [`PHASE5_VERIFICATION.md`](PHASE5_VERIFICATION.md) - Phase 5 implementation and validation evidence.
16. [`ARCHITECTURE.md`](ARCHITECTURE.md) - Implemented application, delivery, Kubernetes, and monitoring architecture.
17. [`ORAL_PREPARATION.md`](ORAL_PREPARATION.md) - Suggested RNCP demonstration path, jury questions, and evidence to collect.
18. [`PHASE6_VERIFICATION.md`](PHASE6_VERIFICATION.md) - Current Phase 6 implementation evidence and remaining validation.
19. [`RISKS_AND_TECHNICAL_DEBT.md`](RISKS_AND_TECHNICAL_DEBT.md) - Known limitations, deferred improvements, guardrails, and upcoming decisions.
20. [`DECISIONS.md`](DECISIONS.md) - Architecture and technical decisions recorded for the project.

## Oral Preparation Path

For oral preparation, read these documents first:

1. [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)
2. [`ROADMAP.md`](ROADMAP.md)
3. [`PHASE_SYNC_PROTOCOL.md`](PHASE_SYNC_PROTOCOL.md)
4. [`ENGINEERING_CHARTER.md`](ENGINEERING_CHARTER.md)
5. [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md)
6. [`DECISIONS.md`](DECISIONS.md)
7. [`RISKS_AND_TECHNICAL_DEBT.md`](RISKS_AND_TECHNICAL_DEBT.md)
8. The verification file for each completed phase

The current phase verification files are:

- [`MVP1_VERIFICATION.md`](MVP1_VERIFICATION.md) for Phase 1.
- [`PHASE2_VERIFICATION.md`](PHASE2_VERIFICATION.md) for Phase 2.
- [`PHASE3_VERIFICATION.md`](PHASE3_VERIFICATION.md) for Phase 3 validation evidence.
- [`PHASE4_VERIFICATION.md`](PHASE4_VERIFICATION.md) for Phase 4 validation evidence.
- [`PHASE5_VERIFICATION.md`](PHASE5_VERIFICATION.md) for validated Phase 5 monitoring evidence.
- [`PHASE6_VERIFICATION.md`](PHASE6_VERIFICATION.md) for current Phase 6 evidence.

[`ORAL_PREPARATION.md`](ORAL_PREPARATION.md) provides the current oral demonstration path and should be refined with final screenshots before the exam.

## Current Validated Phases

- Phase 1 - MVP1 Local App: validated.
- Phase 2 - CI/CD: validated.
- Phase 3 - Backup and Security: validated.
- Phase 4 - k3s/Kubernetes Deployment: validated.
- Phase 5 - Monitoring: validated.
- Phase 6 - Operational Product and Exam Evidence: in progress.

## Maintenance Rule

After each phase, update this index if a new major documentation file is created or if a phase status changes.
