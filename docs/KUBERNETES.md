# Kubernetes Deployment

## Phase 4 Scope

Phase 4A establishes the local k3s/Kubernetes foundation with k3d and deploys PostgreSQL only.

Phase 4B builds and imports the local OpsForge API image, deploys the API, exposes it through NodePort, and verifies `/health` from Windows.

## Why k3d Is Used

k3d runs k3s nodes inside Docker containers. It fits the existing Windows and Docker Desktop environment while keeping the cluster lightweight, reproducible, and easy to explain for the RNCP project.

The Phase 4 cluster contains one k3s server node and no agent nodes. The Kubernetes API is exposed on `127.0.0.1:6445` so `kubectl` can reach it reliably from Windows.

## Prerequisites

- Docker Desktop is running with Linux containers.
- `k3d` is installed and available.
- `kubectl` is installed and available.
- Commands are run from the repository root.

Verify the tools:

```powershell
k3d version
kubectl version --client
docker version
```

## Create the Cluster

Create the cluster from the tracked configuration:

```powershell
k3d cluster create --config k8s/k3d-cluster.yaml
kubectl get nodes
```

The cluster is named `opsforge`. Its configuration maps Windows `127.0.0.1:8080` to NodePort `30080` for the Phase 4B API Service.

## Namespace

All OpsForge Kubernetes resources use the `opsforge` namespace:

```powershell
kubectl apply -f k8s/namespace.yaml
```

## Secret and ConfigMap Strategy

`k8s/configmap.yaml` stores the non-sensitive database name, host, and port.

`k8s/secret.example.yaml` is tracked and contains placeholders only. Create the local Secret manifest before applying PostgreSQL:

```powershell
Copy-Item k8s/secret.example.yaml k8s/secret.local.yaml
```

Replace the placeholders in `k8s/secret.local.yaml` with local values. This file is ignored by Git and must never be committed.

Apply both resources:

```powershell
kubectl apply -f k8s/secret.local.yaml
kubectl apply -f k8s/configmap.yaml
```

Kubernetes Secrets keep credentials and the API `DATABASE_URL` separate from the workload manifest. They do not replace a production secret manager and are not claimed to provide encrypted secret management in this local phase.

## PostgreSQL Resources

Apply the resources in order:

```powershell
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl -n opsforge rollout status statefulset/postgres --timeout=180s
```

Phase 4A uses:

- one PostgreSQL `StatefulSet` replica;
- an internal `ClusterIP` Service on port 5432;
- a `pg_isready` readiness probe;
- a 1 Gi `ReadWriteOnce` PVC;
- the k3s `local-path` StorageClass.

The Local Path Provisioner dynamically creates the PersistentVolume requested by the PVC.

## Verify PostgreSQL

```powershell
kubectl get nodes
kubectl get ns
kubectl -n opsforge get pods,svc,pvc
kubectl get pv
kubectl -n opsforge exec postgres-0 -- sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Expected results:

- the k3s node is `Ready`;
- namespace `opsforge` is `Active`;
- Pod `postgres-0` is `Running` and `1/1` ready;
- PVC `postgres-data` and its PV are `Bound`;
- `pg_isready` reports that PostgreSQL accepts connections.

## Verify Persistence Across Pod Recreation

Create a temporary marker:

```powershell
kubectl -n opsforge exec postgres-0 -- psql -U opsforge -d opsforge -c "CREATE TABLE phase4a_persistence_check (id integer PRIMARY KEY, marker text NOT NULL); INSERT INTO phase4a_persistence_check VALUES (1, 'phase4a-persisted');"
```

Delete only the Pod and wait for the StatefulSet to recreate it:

```powershell
kubectl -n opsforge delete pod postgres-0
kubectl -n opsforge rollout status statefulset/postgres --timeout=180s
```

Verify and remove the marker:

```powershell
kubectl -n opsforge exec postgres-0 -- psql -U opsforge -d opsforge -tAc "SELECT marker FROM phase4a_persistence_check WHERE id = 1;"
kubectl -n opsforge exec postgres-0 -- psql -U opsforge -d opsforge -c "DROP TABLE phase4a_persistence_check;"
```

The marker proves that PostgreSQL data survives Pod deletion and recreation.

## Persistence Limitation

The `local-path` volume is local to the k3d node. Phase 4A proves persistence across PostgreSQL Pod recreation only.

It does not claim that data survives `k3d cluster delete opsforge`, node loss, workstation loss, or a production disaster. Phase 3 backups remain a separate concern.

## Build and Import the API Image

Build the application image locally:

```powershell
docker build -t opsforge-api:phase6 .
```

Import it directly into the k3d cluster:

```powershell
k3d image import opsforge-api:phase6 --cluster opsforge
```

The current API Deployment uses `opsforge-api:phase6` with `imagePullPolicy: Never`. Direct import keeps the local Kubernetes workflow simple and avoids adding registry publishing, credentials, or registry infrastructure.

The image must be rebuilt and re-imported after application changes.

## Deploy the API

Apply the updated local configuration and the API resources:

```powershell
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.local.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl -n opsforge rollout status deployment/opsforge-api --timeout=180s
```

The API Deployment uses one replica and listens on container port 8000.

Before FastAPI starts, a small init container based on `postgres:16-alpine` waits for the internal PostgreSQL Service with `pg_isready`. This replaces Docker Compose `depends_on` without modifying application logic.

The API container uses two probes:

- liveness uses `/health` to confirm the FastAPI process responds;
- readiness uses `/ready` to confirm that the application can query PostgreSQL.

This keeps a live process from receiving Kubernetes traffic when its required database is unavailable.

## API NodePort

The `opsforge-api` Service exposes container port 8000 through NodePort 30080. The k3d cluster maps that port to Windows `127.0.0.1:8080`.

NodePort is used because it is the smallest local mechanism that satisfies external access. Ingress, TLS, and an Ingress controller configuration remain out of scope.

PostgreSQL remains available only through its internal ClusterIP Service and is not exposed to Windows.

## Verify the API

```powershell
kubectl -n opsforge get deployments,pods,svc,pvc
curl.exe -fsS http://localhost:8080/health
curl.exe -fsS http://localhost:8080/ready
curl.exe -sS -o NUL -w "%{http_code}" http://localhost:8080/dashboard
```

Expected results:

- Deployment `opsforge-api` reports `1/1` available;
- the API Pod reports `Running` and `1/1` ready;
- Service `opsforge-api` reports `8000:30080/TCP`;
- `/health` returns `{"status":"ok","service":"opsforge"}`;
- `/ready` returns `{"status":"ready","service":"opsforge"}`;
- `/dashboard` returns HTTP 200.

## Phase 4 Validation Status

Phase 4A and Phase 4B are implemented, locally verified, and explicitly validated by the user on 2026-07-09.

The validated local Kubernetes scope is intentionally limited to k3d, PostgreSQL with local-path PVC storage, a locally imported API image, and NodePort access from Windows.
