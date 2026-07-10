# Phase 5 Verification

## Status

Phase 5B is implemented and locally verified. Phase 5 is not complete and is not user-validated.

Phase 5A adds a minimal Prometheus-compatible `/metrics` endpoint to the FastAPI application so Prometheus can scrape OpsForge in a later phase slice.

Phase 5B deploys Prometheus inside k3d and verifies that it scrapes the Kubernetes-deployed OpsForge API through the internal Service.

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
- [ ] The user reviews Phase 5A and Phase 5B.

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

## Remaining Phase 5 Work

Later Phase 5 slices must still:

1. deploy Grafana;
2. configure a Prometheus datasource;
3. create a small dashboard;
4. add a simple alert rule and anomaly demonstration;
5. document final evidence;
6. receive explicit user validation.

## Validation Result

Phase 5A and Phase 5B are locally verified. Phase 5 must not be marked complete until Grafana dashboarding, alert/anomaly evidence, documentation, and explicit user validation are complete.
