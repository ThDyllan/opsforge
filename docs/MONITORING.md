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

## Phase 5C Grafana Dashboard

Phase 5C deploys Grafana inside k3d in the `monitoring` namespace.

Grafana uses the internal Prometheus Service as its datasource:

```text
http://prometheus.monitoring.svc.cluster.local:9090
```

The datasource and dashboard are provisioned with Kubernetes ConfigMaps so the setup is reproducible from manifests.

Grafana is exposed with a `ClusterIP` Service. It is accessed from Windows with port-forwarding:

```powershell
kubectl -n monitoring port-forward svc/grafana 3000:3000
```

Then open:

```text
http://localhost:3000
```

For this local demonstration, Grafana uses the default local credentials:

```text
admin / admin
```

This is acceptable only for the local RNCP demo environment. It is not production-safe and must not be presented as a real security strategy.

## OpsForge Monitoring Dashboard

The provisioned dashboard is named:

```text
OpsForge Monitoring
```

It contains these panels:

| Panel | PromQL query |
| --- | --- |
| API availability | `up{job="opsforge-api"}` |
| HTTP request volume | `sum(rate(opsforge_http_requests_total[1m]))` |
| HTTP request count by status | `sum by (status_code) (opsforge_http_requests_total)` |
| HTTP latency p95 | `histogram_quantile(0.95, sum(rate(opsforge_http_request_duration_seconds_bucket[5m])) by (le))` |
| HTTP request count by route | `sum by (route) (opsforge_http_requests_total)` |

The route panel is safe because OpsForge uses route-template labels such as `/health` and `/api/services/{service_id}`, not raw dynamic URLs.

## Why ClusterIP and Port-Forward Are Used

Prometheus and Grafana remain internal Kubernetes services. Local access uses `kubectl port-forward`.

This avoids:

- changing the k3d cluster port mappings;
- recreating the cluster;
- adding Ingress or TLS before they are needed;
- exposing monitoring tools more widely than required for the local demo.

## Remaining Phase 5 Work

Phase 5D still needs to add a simple alert rule and anomaly demonstration.

Alertmanager, Grafana alerting, and notification routing remain out of scope unless explicitly selected later.

## Out of Scope for Phase 5A, 5B, and 5C

Phase 5A, 5B, and 5C do not deploy:

- Alertmanager;
- alert rules.

Business/database metrics such as incident or alert counts are also deferred. They should be added only if they remain simple and do not require application refactoring.

Alert/anomaly demonstration remains for a later Phase 5 slice.
