# OpsForge — Automated infrastructure deployment (Ansible)

This directory automates the deployment of the whole OpsForge infrastructure on a
local Kubernetes (k3d) cluster with **Ansible**, using the `kubernetes.core`
collection. It orchestrates the manifests in [`../k8s/`](../k8s/) — it does not
redefine OpsForge.

**Flow:** prerequisites → k3d cluster → build & import the API image → apply the
Kubernetes resources (PostgreSQL, API, monitoring) waiting for each tier to be
**ready** → verify `/health` and `/ready`.

## Layout

```
ansible/
  deploy.yml                 # main playbook (runs the roles below in order)
  teardown.yml               # delete the k3d cluster
  inventory.ini              # control node (localhost)
  group_vars/all.yml         # all variables (cluster name, ports, image, DB, timeouts)
  roles/
    prerequisites/           # check docker / k3d / kubectl / python k8s client
    cluster/                 # create the k3d cluster (idempotent) + kubeconfig
    image/                   # docker build + k3d image import
    kubernetes_resources/    # apply k8s manifests in order, wait until ready
    verify/                  # pods running + /health and /ready return 200
  Dockerfile                 # containerised control node (Ansible + k3d/kubectl/docker CLI)
  run.sh                     # convenience wrapper around the control node
  requirements.yml           # kubernetes.core collection
```

## Run it

Requires Docker. The control node is packaged as a container so it works on any
machine (it drives the host Docker daemon through the mounted socket).

```bash
# Deploy (default cluster name "opsforge", API on http://localhost:8080)
./run.sh

# Tear it down
./run.sh teardown.yml

# Deploy into an isolated cluster (used for testing; never touches an existing one)
./run.sh deploy.yml -e cluster_name=opsforge-test -e api_host_port=8090 -e kubeapi_host_port=6446
```

On a Linux or WSL host that already has `ansible`, `k3d`, `kubectl` and the
`kubernetes` Python client, you can skip the container and run the playbook
directly:

```bash
ansible-galaxy collection install -r requirements.yml
ansible-playbook -i inventory.ini deploy.yml
```

## Notes

- **No separate credential manifest is committed.** The PostgreSQL `Secret` is
  generated at deploy time from the variables in `group_vars/all.yml`. Those hold
  a **non-sensitive local demo default** (the same throwaway credential as
  `docker-compose.yml`), not a real secret — override them (`-e db_password=...`)
  or use `ansible-vault` for anything real.
- **Idempotent.** Re-running `deploy.yml` converges without recreating the cluster
  or the resources.
- The competency mapping (RNCP CP N°2) and the design rationale are documented in
  [`../docs/ANSIBLE.md`](../docs/ANSIBLE.md).
