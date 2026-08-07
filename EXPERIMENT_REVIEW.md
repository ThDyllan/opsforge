# OpsForge — Independent Review (branch `claude/experimentation-review`)

External engineering review and experimentation branch. `main` is untouched.
Every change is a separate, cherry-pickable commit. Baseline before changes:
**29 unit + 1 Postgres integration test passing**. After changes:
**33 unit + 1 Postgres integration passing**, `ruff check .` clean, all 10
operator pages returning HTTP 200, full incident workflow exercised on the live
Postgres app.

## Diagnostic summary

OpsForge is a genuinely strong RNCP DevOps project: coherent domain, audited
state machines, allowlisted runbooks (no arbitrary shell), a hardened Dockerfile,
a real CI pipeline, k8s + Prometheus/Grafana, and unusually honest documentation.
The review found **one real data-loss bug**, a handful of accuracy/UX gaps, and
several infrastructure hardening opportunities — no critical security holes.
Notably, no XSS was found (autoescape on, no `|safe`, `urlencode` on URL params)
and the HTTP-verb discipline in the web layer is correct.

## Confirmed bug

- **Managed runbooks silently lost operator edits.** The six code-defined
  runbooks are re-synchronised on every startup by `seed._ensure_runbooks`, so
  any edit to one was reverted on the next restart — while the UI still offered
  an "Edit" button on them. Proven with a probe (edit → reseed → value reverted).
  Fixed in commit 1 by making managed runbooks read-only (API + UI) with a
  "Managé" badge.

## What changed (per commit)

1. **Protect managed runbooks from silent overwrite** — API rejects edits to
   managed runbooks (409), edit page redirects, "Managé" badge shown, operator
   runbooks stay editable. +3 tests.
2. **Seed a realistic demo runbook execution** — `seed_database` never created a
   `RunbookExecution`, so first-boot runbook history / incident timeline /
   activity feed were empty despite the README advertising seeded "execution"
   data. Now seeds one execution of `generate_incident_report` against the
   primary incident through the real `execute_runbook` path (audit trail
   included), idempotently. +1 test.
3. **Polish operator console UX** — enforce the "locked" service select on the
   incident form (was a dead attribute; server now derives the service from the
   source alert and it cannot drift); derive avatar initials from `operator_name`
   instead of a hardcoded mismatched "DT"; add empty-states to the overview
   alerts table, overview activity feed, and monitoring services table.
4. **Add Ruff lint gate + clean up CI** — new advisory-lint stage (`ruff check`),
   dev tooling split into `requirements-dev.txt` (runtime image stays lean),
   fixed the misleading Trivy step (it set `exit-code: 1` while
   `continue-on-error` swallowed it — looked blocking, never was; now honestly
   advisory), scoped `push` to main + added a `concurrency` group. Ruff also
   surfaced a dead `select` import and three over-long lines, now fixed.
5. **Harden Kubernetes workloads** — resources requests/limits everywhere,
   API container `securityContext` (runAsNonRoot 10001, drop ALL caps, no
   privilege escalation, RuntimeDefault seccomp, read-only root FS + `/tmp`
   emptyDir), and a Postgres `livenessProbe`. YAML/shape validated; **not**
   re-applied to a live k3d cluster on this branch.
6. **Sync docs with actual behaviour** — historical note on MVP1_VERIFICATION
   (runbook-executions endpoint now exists; six runbooks not five); clarified the
   alert lifecycle (a new alert may be resolved without acknowledgement);
   corrected "manual incidents require severity" (it defaults to medium).

## Recommended to take into `main`

- **Commit 1 (managed runbooks)** — fixes a real data-loss trap. *Confirm you
  accept the "managed = read-only" product decision first.*
- **Commit 2 (seed execution)** — low risk, makes the demo and the README honest.
- **Commit 3 (UX polish)** — low risk, visible quality.
- **Commit 4 (Ruff + CI)** — high value for a DevOps jury; the Trivy fix removes
  a genuinely misleading configuration.

## Take with a decision from you

- **Commit 5 (k8s hardening)** — correct and high-value, but **validate on your
  k3d cluster** before merging (re-apply the manifests, confirm the API pod comes
  up healthy with the read-only root FS, and that Postgres stays Ready). If the
  read-only FS causes any issue, drop just that one line.
- **Trivy policy (in commit 4)** — kept non-blocking as your docs decided. A
  stronger option is a *fixable-only* blocking gate (`ignore-unfixed: true`,
  remove `continue-on-error`) so CI fails only on actionable CVEs. This is a
  policy choice — left to you.

## Not done / left as follow-ups (need your input or cluster access)

- Postgres `runAsNonRoot` and a Grafana admin password via Secret (both need
  cluster testing; the official images need care around privilege drop).
- Template de-duplication into macros (execution row, search field, owner chip,
  enabled badge) — safe refactor, but no visual regression harness on this branch.
- Application-level single-active-incident rule is not backed by a DB constraint
  (already documented in RISKS_AND_TECHNICAL_DEBT.md).
- The `X-OpsForge-Actor` audit actor is client-supplied (spoofable) — acceptable
  for the mono-operator scope, already documented.

## Verdict

Exam-ready. The foundation is solid and now carries fewer rough edges: no known
data-loss bug, an honest CI security gate, a lint stage, hardened k8s manifests,
and docs that match the code. The remaining items are documented scope choices,
not defects — which is exactly the posture a jury rewards.
