# Phase 5 Verification

## Status

Phase 5C is implemented and locally verified. Phase 5 is not complete and is not user-validated.

Phase 5A adds a minimal Prometheus-compatible `/metrics` endpoint to the FastAPI application so Prometheus can scrape OpsForge in a later phase slice.

Phase 5B deploys Prometheus inside k3d and verifies that it scrapes the Kubernetes-deployed OpsForge API through the internal Service.

Phase 5C deploys Grafana inside k3d and verifies that the `OpsForge Monitoring` dashboard displays data from the existing Prometheus datasource.

## Phase 5A Scope

Phase 5A covers application metrics only:

- add the `prometheus-client` dependency;
- expose `/metrics` in Prometheus text format;
- collect HTTP request count;
- collect HTTP request latency;
- use low-cardinality labels: method, route template, and status code;
- keep `/metrics` itself out of the custom request metrics;
- add tests for the metrics endpoint.

## Phase 5B Scope

Phase 5B covers Prometheus scraping only:

- build the API image as `opsforge-api:phase5`;
- import the image into the `opsforge` k3d cluster;
- update the API Deployment to use `opsforge-api:phase5`;
- deploy Prometheus in the `monitoring` namespace;
- configure Prometheus with a static scrape target:
  `opsforge-api.opsforge.svc.cluster.local:8000`;
- expose Prometheus only through a `ClusterIP` Service;
- verify Prometheus through local `kubectl port-forward`;
- confirm the `opsforge-api` target is `UP`;
- confirm OpsForge metrics are queryable with PromQL.

## Phase 5C Scope

Phase 5C covers Grafana dashboarding only:

- deploy Grafana in the `monitoring` namespace;
- configure the Prometheus datasource through Grafana provisioning;
- use the internal Prometheus URL:
  `http://prometheus.monitoring.svc.cluster.local:9090`;
- provision the `OpsForge Monitoring` dashboard;
- expose Grafana only through a `ClusterIP` Service;
- access Grafana from Windows with local `kubectl port-forward`;
- verify that the dashboard and panel queries return OpsForge metrics.

## Out of Scope

Phase 5A does not include:

- Prometheus deployment;
- Grafana deployment;
- Alertmanager;
- Kubernetes monitoring manifests;
- dashboard provisioning;
- alert rules;
- anomaly simulation;
- UI redesign;
- authentication;
- Helm, Loki, ELK, Terraform, or Ansible.

Phase 5B still does not include Grafana, Alertmanager, dashboard provisioning, alert rules, anomaly simulation, Ingress, TLS, or PostgreSQL exposure.

Phase 5C still does not include Alertmanager, Grafana alerting, alert rules, anomaly simulation, Ingress, TLS, or PostgreSQL exposure.

## Verification Checklist

- [x] `/metrics` endpoint was added.
- [x] `/metrics` returns Prometheus-compatible text output.
- [x] HTTP request count metric was added.
- [x] HTTP request latency histogram was added.
- [x] Metrics use method, route template, and status code labels.
- [x] `/metrics` is excluded from custom request metrics.
- [x] Tests were added for `/metrics`.
- [x] Existing tests pass after the change.
- [x] Docker image `opsforge-api:phase5a` builds successfully.
- [x] `git diff --check` passes.
- [x] API image `opsforge-api:phase5` builds successfully.
- [x] API image `opsforge-api:phase5` is imported into k3d.
- [x] API Deployment uses `opsforge-api:phase5`.
- [x] API Deployment rollout succeeds.
- [x] `/metrics` is available from the Kubernetes-deployed API.
- [x] Monitoring namespace is created.
- [x] Prometheus ConfigMap, Deployment, and Service are created.
- [x] Prometheus Pod reports `Running` and `1/1` ready.
- [x] Prometheus Service is `ClusterIP`.
- [x] Prometheus target `opsforge-api` reports `UP`.
- [x] PromQL query `up{job="opsforge-api"}` returns `1`.
- [x] PromQL query `opsforge_http_requests_total` returns OpsForge HTTP metrics.
- [x] PromQL query `opsforge_http_request_duration_seconds_count` returns OpsForge HTTP metrics.
- [x] PostgreSQL remains internal through a `ClusterIP` Service.
- [x] Grafana datasource ConfigMap is created.
- [x] Grafana dashboard provider ConfigMap is created.
- [x] Grafana dashboard ConfigMap is created.
- [x] Grafana Deployment is created.
- [x] Grafana Service is `ClusterIP`.
- [x] Grafana Pod reports `Running` and `1/1` ready.
- [x] Grafana datasource points to internal Prometheus.
- [x] Dashboard `OpsForge Monitoring` is provisioned and visible.
- [x] API availability panel query returns data.
- [x] HTTP request volume panel query returns data.
- [x] HTTP request count by status panel query returns data.
- [x] HTTP latency p95 panel query returns data.
- [x] HTTP request count by route panel query returns data.
- [x] No PostgreSQL exposure was added.
- [x] No Alertmanager or alerting resources were added.
- [ ] The user reviews Phase 5A, Phase 5B, and Phase 5C.

## Phase 5A Evidence

- Baseline local test command: `python -m pytest -q` could not run because the host Python environment does not have `pytest` installed.
- Docker build: `docker build -t opsforge-api:phase5a .` passed.
- Tests in the Phase 5A image: `8 passed`.
- Quality check: `git diff --check` passed; only line-ending warnings were reported by Git.

## Phase 5B Evidence

- API image build: `docker build -t opsforge-api:phase5 .` passed.
- k3d image import: `k3d image import opsforge-api:phase5 --cluster opsforge` passed.
- API Deployment image: `opsforge-api:phase5`.
- API rollout: `deployment "opsforge-api" successfully rolled out`.
- API Pod: `opsforge-api-9b9b474b5-pfkkk`, ready `1/1`, status `Running`.
- PostgreSQL Pod: `postgres-0`, ready `1/1`, status `Running`.
- PostgreSQL Service: `ClusterIP`, port `5432/TCP`.
- API Service: `NodePort`, `8000:30080/TCP`.
- `/metrics` from Windows through the existing API NodePort returned OpsForge metrics, including:
  - `opsforge_http_requests_total`;
  - `opsforge_http_request_duration_seconds_count`.
- Monitoring namespace: `monitoring`.
- Prometheus Pod: `prometheus-5b5d5d45c9-mp7dg`, ready `1/1`, status `Running`.
- Prometheus Service: `ClusterIP`, port `9090/TCP`.
- Prometheus scrape URL:
  `http://opsforge-api.opsforge.svc.cluster.local:8000/metrics`.
- Prometheus target status: `opsforge-api` is `UP`.
- PromQL `up{job="opsforge-api"}` returned value `1`.
- PromQL `opsforge_http_requests_total` returned an OpsForge `/health` series.
- PromQL `opsforge_http_request_duration_seconds_count` returned an OpsForge `/health` series.

## Phase 5C Evidence

- Grafana namespace: `monitoring`.
- Grafana Pod: `grafana-9769c6bfd-jwn5q`, ready `1/1`, status `Running`.
- Grafana Service: `ClusterIP`, port `3000/TCP`.
- Access method: `kubectl -n monitoring port-forward svc/grafana 3000:3000`.
- Grafana health API: database status `ok`.
- Datasource name: `Prometheus`.
- Datasource type: `prometheus`.
- Datasource URL:
  `http://prometheus.monitoring.svc.cluster.local:9090`.
- Dashboard title: `OpsForge Monitoring`.
- Dashboard UID: `opsforge-monitoring`.
- Dashboard search result count: `1`.
- Panel query `up{job="opsforge-api"}` returned value `1`.
- Panel query `sum(rate(opsforge_http_requests_total[1m]))` returned data.
- Panel query `sum by (status_code) (opsforge_http_requests_total)` returned status code `200` data.
- Panel query `histogram_quantile(0.95, sum(rate(opsforge_http_request_duration_seconds_bucket[5m])) by (le))` returned data.
- Panel query `sum by (route) (opsforge_http_requests_total)` returned route data for `/health` and `/dashboard`.
- Grafana alert rules API returned `0` rules.
- PostgreSQL Service remained `ClusterIP` on port `5432/TCP`.
- Screenshot evidence can be added later during Phase 6 exam documentation if needed.

## Remaining Phase 5 Work

Later Phase 5 slices must still:

1. add a simple alert rule and anomaly demonstration;
2. document final evidence;
3. receive explicit user validation.

## Validation Result

Phase 5A, Phase 5B, and Phase 5C are locally verified. Phase 5 must not be marked complete until alert/anomaly evidence, final documentation, and explicit user validation are complete.
