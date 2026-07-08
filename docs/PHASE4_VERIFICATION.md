# Phase 4 Verification

## Status

Phase 4 is in progress. Phase 4A was implemented and locally verified on 2026-07-07, but Phase 4 is not user-validated or complete.

## Phase 4A Scope

Phase 4A covers the k3d cluster foundation and PostgreSQL only. No OpsForge API workload or Service has been created.

## Tooling

- k3d: `v5.9.0`
- bundled k3s: `v1.35.5-k3s1`
- kubectl client: `v1.34.1`
- Docker Engine: `29.5.3`

## Verification Checklist

- [x] The single-node `opsforge` k3d cluster was created from `k8s/k3d-cluster.yaml`.
- [x] The k3s node reports `Ready`.
- [x] Namespace `opsforge` reports `Active`.
- [x] The local Secret was applied from an ignored file.
- [x] The non-sensitive PostgreSQL ConfigMap was applied.
- [x] The PostgreSQL ClusterIP Service was created.
- [x] StatefulSet `postgres` has one ready replica.
- [x] Pod `postgres-0` reports `Running` and `1/1` ready.
- [x] `pg_isready` reports that PostgreSQL accepts connections.
- [x] PVC `postgres-data` is `Bound` to a dynamically provisioned 1 Gi local-path PV.
- [x] PostgreSQL data survived Pod deletion and recreation.
- [x] The temporary persistence marker was removed after verification.
- [x] `k8s/secret.local.yaml` is ignored by Git.
- [ ] Phase 4B API deployment and external access are implemented.
- [ ] The user explicitly validates Phase 4 as complete.

## Cluster and PostgreSQL Evidence

- Cluster: `opsforge`
- Node: `k3d-opsforge-server-0`, status `Ready`
- Namespace: `opsforge`, status `Active`
- PostgreSQL Pod: `postgres-0`, status `Running`, ready `1/1`
- PostgreSQL Service: `ClusterIP`, port 5432
- PVC: `postgres-data`, status `Bound`, capacity 1 Gi, access mode `ReadWriteOnce`, StorageClass `local-path`
- Readiness result: `/var/run/postgresql:5432 - accepting connections`

The first cluster creation exposed an unreachable `host.docker.internal` kubeconfig endpoint from Windows. The tracked cluster configuration now explicitly exposes the Kubernetes API through `127.0.0.1:6445`; the recreated cluster is reachable with `kubectl`.

## Persistence Evidence

1. The marker `phase4a-persisted` was inserted into a temporary table.
2. Original Pod UID: `25238083-2155-499f-991a-92f7a2b0a266`.
3. Pod `postgres-0` was deleted.
4. The StatefulSet recreated it with UID `685aa503-d926-4456-9770-3aea63c77b7c`.
5. The marker remained available after recreation.
6. PostgreSQL returned to the ready state.
7. The temporary test table was removed.

This proves persistence across Pod recreation only, not across complete k3d cluster deletion.

## Phase 4B Remaining Work

- Build and import the local `opsforge-api` image.
- Create API configuration and Secret consumption.
- Create the API Deployment.
- Handle PostgreSQL startup dependency safely.
- Add API readiness/liveness probes.
- Create the API NodePort Service on 30080.
- Verify `/health` from Windows through `http://localhost:8080`.
- Complete Phase 4 documentation and request explicit user validation.
