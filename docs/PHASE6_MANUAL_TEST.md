# Phase 6 Manual Operator Test

## Purpose

This procedure validates the visible operator experience that HTTP and unit tests cannot fully prove. It must be run by the user before Phase 6 is explicitly validated.

Use generic demonstration data only. Do not enter client, employer, credential, or production-system information.

## Prerequisites

1. Start the local stack:

   ```powershell
   docker compose up --build -d
   ```

2. Confirm:

   ```powershell
   curl.exe http://localhost:8000/health
   curl.exe http://localhost:8000/ready
   ```

3. Open `http://localhost:8000/overview` in a desktop browser.

The test deliberately creates demonstration records. OpsForge has no delete workflow in this version, so use a recognizable title such as `Validation Phase 6 - YYYYMMDD`.

## A. Navigation And Orientation

- Confirm the sidebar contains Vue d'ensemble, Alertes, Incidents, Services, Runbooks, Activite, Monitoring and Aide.
- Confirm the global `Declarer un incident` action remains visible.
- Open every section and confirm the active navigation item is clear.
- Confirm no text, button, badge or table overlaps at the normal desktop size.
- Confirm Lucide icons render instead of empty squares or raw icon names.

Expected result: a new operator can identify the urgent queues, reference data, evidence and help areas without using `/docs`.

## B. Create And Qualify An Alert

1. Open Alertes, then `Creer une alerte`.
2. Select `Backup Service`.
3. Use:

   ```text
   Source: manual-phase6
   Title: Validation Phase 6 - YYYYMMDD
   Message: Echec de sauvegarde simule pour le test operateur.
   Severity: critical
   ```

4. Submit the form.
5. Search for the title in the alert queue.
6. Expand the row and confirm the complete message is readable.
7. Click `Acquitter`.

Expected result: the alert appears as critical, attached to Backup Service, and moves from `Nouvelle` to `Acquittee`.

## C. Open One Incident From The Alert

1. Click `Ouvrir un incident` on the alert.
2. Confirm the service and alert context are prefilled.
3. Use a clear incident description and keep severity `critical`.
4. Create the incident.
5. Return to the alert queue.

Expected result: the action now opens the existing incident. Creating a second active incident for the same alert is not offered and the API rejects a duplicate attempt with HTTP `409`.

## D. Use The Incident Command Center

1. Confirm the page shows the incident ID, title, description, service, source alert, severity, status and owner.
2. Clear the owner and submit; confirm it becomes `Non assigne`.
3. Set the owner back to `Dyllan`.
4. Move the incident from `Ouvert` to `En investigation`.
5. Confirm direct or backward transitions are not offered.

Expected result: each owner or status change appears in the incident timeline and in Activite.

## E. Execute Runbooks

### Manual Runbook

1. Open `Diagnostiquer un echec de sauvegarde` in the incident page.
2. Read the instructions and checklist.
3. Confirm every step.
4. Select `Succes` and enter a generic conclusion.
5. Confirm the execution.

Expected result: a successful execution and its conclusion appear in execution history and the incident timeline.

### Approved Automation

1. Execute `Generer le rapport d'incident`.
2. Read the generated output.

Expected result: the report summarizes the current incident and creates both a `RunbookExecution` and audit evidence. No shell command is requested or executed.

## F. Resolve The Two Lifecycles

1. Resolve the incident from the Command Center.
2. Confirm its actions become read-only and the resolution appears in the timeline.
3. Return to the source alert.
4. Confirm the alert is still acknowledged.
5. Resolve the alert separately.

Expected result: incident and alert lifecycles remain independent, and both final actions are audited.

## G. Reference And Evidence Pages

- Open Backup Service and confirm related alerts/incidents are visible.
- Open Runbooks and inspect mode, context, risk and execution history.
- Open Activite and find the actions performed during this test.
- Open Monitoring and confirm real platform checks are clearly separated from simulated service states.
- Open Aide and confirm the product flow, scenario, glossary and limitations are understandable.

## H. Responsive Check

Use browser responsive mode at approximately `390 x 844` and verify:

- the sidebar opens and closes from the menu button;
- the global incident action remains reachable;
- forms use one readable column;
- command-center panels stack vertically;
- tables scroll horizontally inside their own area;
- no text or action overlaps another element;
- no control causes the page width to overflow unexpectedly.

Repeat a quick check at approximately `768 x 1024` and `1440 x 900`.

## I. Screenshot List

Collect current screenshots only after the final candidate is rebuilt:

1. Overview with active operational data.
2. Alert queue with filters and an expanded alert.
3. Incident Command Center before resolution.
4. Manual runbook checklist and successful result.
5. Incident timeline containing owner, status and runbook events.
6. Global Activity journal.
7. Monitoring page explaining real versus simulated data.
8. Help scenario or glossary.
9. GitHub Actions run with both test steps, Docker build and Trivy.
10. Kubernetes workloads and healthy probes.
11. Prometheus target and `OpsForgeApiDown` rule.
12. Grafana `OpsForge Monitoring` dashboard.

Do not capture private Atera references, employer information, local secrets or real credentials.

## Validation Record

Record after the test:

- browser and viewport used;
- test date;
- result of sections A through H;
- screenshot locations;
- defects found;
- user validation decision.

Phase 6 remains in progress until this manual experience is reviewed, current CI is green, required evidence is collected, and the user explicitly validates it.
