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

## Implemented Phase 5 Architecture

Phase 5 uses Prometheus and Grafana inside the local k3d cluster so the monitoring stack supervises the Kubernetes-deployed OpsForge service.

The implemented approach is:

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

## Phase 5D Prometheus Alert Rule

Phase 5D uses Prometheus alert rules only. Alertmanager is intentionally not deployed in this phase.

Alertmanager would add notification routing, receivers, silences, and delivery configuration. For the current RNCP local demonstration, the required proof is that Prometheus detects an anomaly on the deployed service.

The alert rule is:

| Field | Value |
| --- | --- |
| Alert name | `OpsForgeApiDown` |
| Expression | `up{job="opsforge-api"} == 0` |
| Duration | `30s` |
| Label | `severity: critical` |
| Label | `service: opsforge-api` |
| Summary | `OpsForge API is down` |
| Description | `Prometheus cannot scrape the OpsForge API metrics endpoint.` |

The duration is `30s` because the local Prometheus scrape and evaluation intervals are both `15s`. This is long enough to avoid a one-scrape blip, while still keeping the oral exam demonstration short and understandable.

## Alert Verification

Check that Prometheus knows the rule:

```text
http://localhost:9090/api/v1/rules
```

Check active alerts:

```text
http://localhost:9090/api/v1/alerts
```

Useful PromQL query:

```promql
up{job="opsforge-api"}
```

Expected healthy result:

```text
1
```

## Outage Simulation

Simulate an API outage by scaling only the API Deployment to zero:

```powershell
kubectl -n opsforge scale deployment/opsforge-api --replicas=0
```

After the alert duration plus scrape/evaluation time, Prometheus should show:

- `up{job="opsforge-api"}` returning `0`;
- `OpsForgeApiDown` in `pending` or `firing` state;
- `/api/v1/alerts` showing the alert when firing.

## Restore the API

Restore the API immediately after the alert is observed:

```powershell
kubectl -n opsforge scale deployment/opsforge-api --replicas=1
kubectl -n opsforge rollout status deployment/opsforge-api
```

Then verify:

```powershell
curl.exe -fsS http://localhost:8080/health
curl.exe -fsS http://localhost:8080/metrics
```

Expected recovery:

- API Pod returns to `1/1 Running`;
- `/health` returns `{"status":"ok","service":"opsforge"}`;
- `/metrics` returns OpsForge metrics;
- `up{job="opsforge-api"}` returns `1`;
- `OpsForgeApiDown` returns to inactive or disappears from active alerts.

## Operational Interpretation

`OpsForgeApiDown` means Prometheus cannot scrape the OpsForge API metrics endpoint.

For this project, the operator should:

1. check the API Pod status;
2. check the API Deployment rollout;
3. verify `/health`;
4. restore the API replica if it was intentionally scaled down;
5. investigate Pod logs or deployment events if it was not intentional.

## Out of Scope for Phase 5A, 5B, 5C, and 5D

Phase 5A, 5B, 5C, and 5D do not deploy:

- Alertmanager;
- Grafana alerting;
- notification routing.

Business/database metrics such as incident or alert counts are also deferred. They should be added only if they remain simple and do not require application refactoring.

Further alert routing remains a possible future improvement only if explicitly selected.
