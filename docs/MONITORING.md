# Monitoring

## Purpose

Phase 5 adds observability to OpsForge so the deployed service can be supervised with Prometheus and Grafana.

The monitoring scope must remain simple, local, and explainable for the RNCP exam. It must monitor the actual OpsForge service instead of only installing tools.

## Phase 5A Scope

Phase 5A prepares the application for Prometheus scraping by exposing a Prometheus-compatible `/metrics` endpoint.

The endpoint currently exposes:

- HTTP request count;
- HTTP request latency histogram;
- labels for HTTP method, route template, and status code.

The `/metrics` endpoint itself is excluded from the custom request metrics to keep the output cleaner.

## Metrics Endpoint

The API exposes metrics at:

```text
/metrics
```

The response uses the Prometheus text exposition format and the Prometheus content type.

Current custom metric names:

- `opsforge_http_requests_total`
- `opsforge_http_request_duration_seconds`

Route labels use FastAPI route templates when available, such as `/api/services/{service_id}`, instead of raw dynamic URLs. This avoids high-cardinality labels.

## Planned Phase 5 Architecture

Phase 5 uses Prometheus and Grafana inside the local k3d cluster so the monitoring stack supervises the Kubernetes-deployed OpsForge service.

The intended approach is:

- keep the OpsForge application in the `opsforge` namespace;
- deploy Prometheus and Grafana in a dedicated `monitoring` namespace;
- configure Prometheus to scrape the OpsForge API through its internal Kubernetes Service;
- expose Grafana locally only for demonstration;
- add a simple alert rule that can detect an API unavailability anomaly.

## Phase 5B Prometheus Deployment

Phase 5B deploys Prometheus inside k3d in the `monitoring` namespace.

Prometheus uses a static scrape configuration for the OpsForge API:

```yaml
job_name: opsforge-api
metrics_path: /metrics
targets:
  - opsforge-api.opsforge.svc.cluster.local:8000
```

Static configuration is used for this phase because it is simple, readable, and enough to prove that Prometheus can scrape the deployed API. Kubernetes service discovery and RBAC are deferred.

The Prometheus Service is `ClusterIP`. It is not exposed with NodePort, and the k3d cluster does not need to be recreated.

## Access Prometheus Locally

Use port-forwarding when the Prometheus UI or API must be accessed from Windows:

```powershell
kubectl -n monitoring port-forward svc/prometheus 9090:9090
```

Then open:

```text
http://localhost:9090
```

## Check Prometheus Targets

With port-forwarding active, check targets through:

```text
http://localhost:9090/api/v1/targets
```

The expected target is:

```text
opsforge-api
```

The expected scrape URL is:

```text
http://opsforge-api.opsforge.svc.cluster.local:8000/metrics
```

The target must report `UP`.

## Basic PromQL Queries

Useful Phase 5B checks:

```promql
up{job="opsforge-api"}
opsforge_http_requests_total
opsforge_http_request_duration_seconds_count
```

Expected result:

- `up{job="opsforge-api"}` returns `1`;
- OpsForge HTTP metrics return at least one time series after requests have reached the API.

## Out of Scope for Phase 5A and 5B

Phase 5A and 5B do not deploy:

- Grafana;
- Alertmanager;
- dashboards;
- alert rules.

Business/database metrics such as incident or alert counts are also deferred. They should be added only if they remain simple and do not require application refactoring.

Grafana dashboards and alert/anomaly demonstration remain for later Phase 5 slices.
