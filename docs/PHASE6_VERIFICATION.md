# Phase 6 Verification

## Status

Phase 6 is in progress and is not user-validated yet.

The balanced technical slice was previously verified in GitHub Actions at commit `83469cb`. The larger operator-product candidate is being prepared on branch `phase6-operator-ux`; its current implementation checkpoints are:

- `c2693e3 Checkpoint operator UX spike`
- `99ee624 Build audited incident domain and managed runbooks`
- `a562985 Build multipage operator console`

Final validation still requires current-branch CI evidence, a user-led visual/responsive workflow review, final screenshots, and explicit user approval.

## Candidate Scope

### Domain Integrity

- Alerts move forward through `new -> acknowledged -> resolved`.
- Incidents move forward through `open -> investigating -> resolved`.
- Resolved objects are not reopened in this version.
- An incident linked to an alert must use the same service.
- One source alert can have only one active incident.
- Resolving an incident does not resolve the source alert automatically.
- Manual incidents require a service, title, description, and severity.
- Meaningful service, alert, incident, runbook, and execution mutations are audited.

### Runbooks

- Runbooks are maintained through API and Jinja forms.
- Manual runbooks contain instructions, ordered steps, a checklist, notes, and an operator-confirmed outcome.
- Automated runbooks select only an approved Python behavior through `automation_key`.
- Context requirements (`none`, `service`, or `incident`), enabled state, and risk level are visible.
- Incompatible or failed attempts still create a `RunbookExecution` and audit evidence.
- No arbitrary command, script, `eval`, or shell execution is accepted.

### Operator Console

- `/overview` provides operational orientation rather than every product action.
- `/alerts` provides search, filters, message expansion, status actions, and incident context.
- `/incidents` provides a compact queue and dedicated Incident Command Center.
- `/services` separates catalog maintenance from urgent work.
- `/runbooks` provides catalog, creation, editing, context, and history.
- `/activity` exposes the global audit journal.
- `/monitoring` distinguishes real platform telemetry from simulated business data.
- `/help` provides first steps, a guided scenario, glossary, architecture, and honest limits.
- `/dashboard` remains a compatibility redirect to `/overview`.

### Data And Test Isolation

- Seed data is idempotent, generic, and centered on a Backup Service demonstration scenario.
- No private Atera or employer data is present in the repository.
- The PostgreSQL integration test creates and drops a unique temporary database.
- PostgreSQL tests no longer add records to the demonstration database.
- Existing databases receive only a small additive startup compatibility bridge; no local volume is destroyed.

## Local Automated Evidence - 2026-07-17

| Check | Result |
| --- | --- |
| SQLite suite | `29 passed, 1 warning` |
| Isolated PostgreSQL integration | `1 passed, 1 warning` |
| Python compilation | Passed with `python -m compileall -q app` |
| JavaScript syntax | Passed with Node `v24.18.0` and `node --check app/static/app.js` |
| Docker image build | Passed for isolated Compose and tag `opsforge-api:phase6-operator-ux` |
| Local Trivy image scan | Completed: `19 HIGH`, `3 CRITICAL`, `0` findings with a known fixed version |
| Isolated `/health` | HTTP `200` |
| Compose service health | API and PostgreSQL healthy |
| HTML routes | 17 representative pages returned HTTP `200` |
| Internal links | 53 generated local links returned successfully |
| Static assets | CSS, application JavaScript, and Lucide asset returned successfully |
| HTML structure | One `main` and one `h1` per page; no duplicate IDs or unresolved Jinja markers found |
| Private-reference scan | No private client, employer, ticket, or reference-report data found; Atera is named only to identify the excluded private UX reference |
| Arbitrary execution scan | No `subprocess`, `os.system`, `Popen`, shell execution, `eval`, or `exec` pattern found in `app/` |
| Local Kubernetes secret | `k8s/secret.local.yaml` remains ignored and untracked |

The shared warning is the tracked `StarletteDeprecationWarning` from the current FastAPI test-client dependency path. It does not hide a failed test.

## Isolated PostgreSQL Workflow Evidence

A fresh Docker Compose project on port `8010` was used so the normal local database was not modified.

The seeded Backup Service scenario verified:

- manual diagnostic runbook returned HTTP `200` and `success`;
- the incident moved from investigation to resolved;
- the source alert remained independently `acknowledged`;
- the incident timeline contained runbook and resolution events.

A second temporary operator flow verified:

- alert creation returned `201`;
- acknowledgement returned `200`;
- incident creation returned `201`;
- a duplicate active incident returned `409`;
- investigation returned `200`;
- report runbook execution returned `200` and `success`;
- incident resolution returned `200`;
- separate alert resolution returned `200`.

## Previous Platform Evidence

The earlier balanced Phase 6 slice already proved:

- separate `/health` liveness and PostgreSQL-aware `/ready` behavior;
- non-root API image execution and Docker healthcheck;
- PostgreSQL bound to `127.0.0.1` in Docker Compose;
- k3d rollout with successful liveness/readiness;
- Prometheus target up, inactive `OpsForgeApiDown`, and healthy Grafana after restore;
- GitHub Actions success for commit `83469cb` with SQLite, PostgreSQL, Docker build, and non-blocking Trivy.

That evidence remains valid for the underlying platform, but the current operator-product branch must receive its own CI result before merge review.

## Browser Validation Limitation

The in-app browser automation connection was attempted on 2026-07-17. The connector rejected the session because its required sandbox-policy metadata was unavailable. No alternate automation workaround was used.

Therefore, automated checks do not claim visual layout, responsive behavior, or click interaction validation. The required manual procedure is documented in [`PHASE6_MANUAL_TEST.md`](PHASE6_MANUAL_TEST.md).

## Security Evidence And Limits

- Runbook automation is allowlisted and cannot execute operator-supplied code.
- Private UX references and the reference PDF were never copied into the repository.
- Real platform monitoring and simulated business status are labeled separately.
- Authentication remains intentionally absent for the local mono-operator scope.
- Trivy remains non-blocking. The local candidate scan reports `19 HIGH` and `3 CRITICAL` Debian findings with no known fixed version; the current CI log must show and retain this evidence.

## Remaining Validation

- Complete the manual desktop/tablet/mobile operator workflow.
- Capture the product, CI, Kubernetes, Prometheus, Grafana, backup/restore, and security evidence listed in `PHASE6_MANUAL_TEST.md`.
- Confirm the final branch passes GitHub Actions.
- Review the final diff against `main`.
- Obtain explicit Phase 6 user validation.

## Current Conclusion

The Phase 6 candidate is technically coherent and passes its automated local checks. It is ready for human UX review, not yet ready to be described as Phase 6 complete.
