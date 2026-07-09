# Phase 4 Verification

## Status

Phase 4 is completed and explicitly validated by the user on 2026-07-09 after final checks passed.

Phase 4A was locally verified on 2026-07-07. Phase 4B was locally verified on 2026-07-08. Final validation checks were rerun on 2026-07-09 before marking the phase complete.

## Phase 4A Scope

Phase 4A covered the k3d cluster foundation and PostgreSQL only.

Phase 4B then added the OpsForge API workload, NodePort Service, and Windows access through `http://localhost:8080`.

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
- [x] The local `opsforge-api:phase4` image was built successfully.
- [x] The image was imported into the `opsforge` k3d cluster.
- [x] The API Deployment uses one replica and `imagePullPolicy: Never`.
- [x] The API init container waits for PostgreSQL with `pg_isready`.
- [x] API readiness and liveness probes use `/health`.
- [x] Deployment `opsforge-api` reports `1/1` available.
- [x] The API Pod reports `Running` and `1/1` ready.
- [x] The API NodePort Service exposes `8000:30080/TCP`.
- [x] PostgreSQL remains internal through its ClusterIP Service.
- [x] `http://localhost:8080/health` returns the expected healthy response.
- [x] `http://localhost:8080/dashboard` returns HTTP 200.
- [x] Final repository and Secret safety checks passed on 2026-07-09.
- [x] Final Kubernetes resource checks passed on 2026-07-09.
- [x] Final application access checks passed on 2026-07-09.
- [x] `git diff --check` passed on 2026-07-09.
- [x] The user explicitly validates Phase 4 as complete.

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

## Phase 4B Evidence

- Docker image: `opsforge-api:phase4`, build successful.
- k3d import: one image imported successfully into cluster `opsforge`.
- Deployment: `opsforge-api`, ready `1/1`, available `1`.
- API Pod image: `opsforge-api:phase4`, ready `true`, zero restarts during verification.
- API Service: `NodePort`, `8000:30080/TCP`.
- Windows mapping: `127.0.0.1:8080` to NodePort 30080.
- `/health`: `{"status":"ok","service":"opsforge"}`.
- `/dashboard`: HTTP 200.
- PostgreSQL Service remained `ClusterIP` on port 5432.

## Final Validation Evidence

Final checks rerun on 2026-07-09 confirmed:

- `k8s/secret.local.yaml` is ignored by Git and is not tracked.
- k3d cluster `opsforge` reports one ready server.
- Kubernetes node `k3d-opsforge-server-0` reports `Ready`.
- PostgreSQL Pod `postgres-0` reports `Running` and `1/1` ready.
- API Pod `opsforge-api` reports `Running` and `1/1` ready.
- PVC `postgres-data` reports `Bound`.
- Service `opsforge-api` exposes `8000:30080/TCP`.
- Service `postgres` remains internal through `ClusterIP` on port 5432.
- `http://localhost:8080/health` returns `{"status":"ok","service":"opsforge"}`.
- `http://localhost:8080/dashboard` returns HTTP 200.
- `git diff --check` passed; only line-ending warnings were reported by Git.

## Validation Result

The technical Phase 4 scope is implemented, locally verified, and explicitly validated by the user.

This document records the validated Phase 4 state. After pushing the validation commit, GitHub Actions must be checked according to `docs/GIT_WORKFLOW.md`.
