# Kubernetes Deployment

## Phase 4A Scope

Phase 4A establishes the local k3s/Kubernetes foundation with k3d and deploys PostgreSQL only.

The OpsForge API is not deployed in Phase 4A. Its image build/import, Deployment, NodePort Service, and `/health` verification remain Phase 4B work.

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

The cluster is named `opsforge`. Its configuration also reserves the future Phase 4B mapping from Windows `127.0.0.1:8080` to NodePort `30080`. Phase 4A does not create an API Service on that port.

## Namespace

All OpsForge Kubernetes resources use the `opsforge` namespace:

```powershell
kubectl apply -f k8s/namespace.yaml
```

## Secret and ConfigMap Strategy

`k8s/configmap.yaml` stores the non-sensitive database name.

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

Kubernetes Secrets keep credentials separate from the workload manifest. They do not replace a production secret manager and are not claimed to provide encrypted secret management in this local phase.

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

## Phase 4B Remaining Work

- Build the local OpsForge API image.
- Import it with `k3d image import`.
- Create the API Deployment.
- Add safe PostgreSQL startup handling and API health probes.
- Create the API NodePort Service on 30080.
- Verify `/health` through `http://localhost:8080`.
