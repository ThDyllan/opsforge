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

Later Phase 5 slices should deploy Prometheus and Grafana inside the local k3d cluster.

The intended approach is:

- keep the OpsForge application in the `opsforge` namespace;
- deploy Prometheus and Grafana in a dedicated `monitoring` namespace;
- configure Prometheus to scrape the OpsForge API through its internal Kubernetes Service;
- expose Grafana locally only for demonstration;
- add a simple alert rule that can detect an API unavailability anomaly.

## Out of Scope for Phase 5A

Phase 5A does not deploy:

- Prometheus;
- Grafana;
- Alertmanager;
- Kubernetes monitoring manifests;
- dashboards;
- alert rules.

Business/database metrics such as incident or alert counts are also deferred. They should be added only if they remain simple and do not require application refactoring.
