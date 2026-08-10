# Automating the infrastructure deployment with Ansible

## Purpose

OpsForge's Kubernetes architecture (k3d cluster, PostgreSQL, API, Prometheus,
Grafana) was originally deployed with a documented sequence of `k3d` and
`kubectl` commands. This directory replaces that manual sequence with an
**Ansible** automation that provisions and deploys the whole infrastructure in
one command, waits for each tier to become ready, and verifies the result.

It directly covers the RNCP TP-01414 competency **CP N°2 « Automatiser le
déploiement d'une infrastructure »**, whose reference context expects
*« une plateforme de type Ansible ou Terraform »*.

Everything lives in [`../ansible/`](../ansible/). The playbook **orchestrates the
existing manifests in [`../k8s/`](../k8s/)** — it does not redefine OpsForge.

## What the automation does

`ansible/deploy.yml` runs five roles in dependency order:

| Role | Responsibility | How |
| --- | --- | --- |
| `prerequisites` | Fail fast if the control node lacks a tool | `docker`, `k3d`, `kubectl`, python `kubernetes` |
| `cluster` | Create the k3d cluster **if absent**, produce a kubeconfig | `k3d` CLI (idempotent) |
| `image` | Build the API image and load it into the cluster | `docker build` + `k3d image import` |
| `kubernetes_resources` | Apply the manifests **in order**, waiting for each tier | `kubernetes.core.k8s` with `wait: true` |
| `verify` | Prove it works | pods `Running` + `/health` and `/ready` return `200` |

## Why this is real orchestration, not a `kubectl apply` wrapper

This was a deliberate design goal. The automation adds what a blind
`kubectl apply -f k8s/` cannot:

- **Ordering with readiness gating** — PostgreSQL is applied and the playbook
  *waits until it is ready* before deploying the API, which itself is waited on
  before the monitoring stack. `kubernetes.core.k8s` with `wait: true` blocks on
  the actual rollout status.
- **Idempotent convergence** — re-running the playbook does not recreate the
  cluster or the resources; a second run reports almost everything as `ok`
  (unchanged).
- **Secret injection without a committed credential** — the PostgreSQL `Secret`
  is built at deploy time from variables, so no credential file is in Git.
- **End-to-end verification** — the run only succeeds if the API answers `200` on
  `/health` and `/ready` (the latter proving PostgreSQL connectivity via
  `SELECT 1`).
- **Explicit prerequisites and a reproducible control node** — the control node
  itself is defined as code (`ansible/Dockerfile`).

`k3d` and `docker` are driven through their CLIs (natural for those tools), while
the Kubernetes API work goes through the `kubernetes.core` collection.

## Why Ansible rather than Terraform

Both are named by the reference. OpsForge's scope is **local, without a cloud
provider**. Ansible fits that scope naturally: it *orchestrates* the sequence
"prepare → create cluster → build/import → apply → wait → verify" on the local
Docker/k3d environment. Terraform shines when it **provisions cloud resources**
(VPC, VMs, a managed Kubernetes) — exactly the cloud layer OpsForge deliberately
keeps out of scope. Using Terraform only to drive a local k3d cluster would be
heavier and less honest to explain. Deploying to a cloud provider with Terraform
is the documented next step (see CP N°4, questioned at the oral, not required in
the project).

## Mapping to CP N°2 criteria

| Critère de performance (REAC) | Evidence in this project |
| --- | --- |
| **Les serveurs déployés sont fonctionnels** | The run gates on PostgreSQL and the API becoming ready, then verifies `/health = 200` and `/ready = 200` (DB reachable). |
| **L'architecture est conforme au cahier des charges** | The playbook deploys the documented architecture (namespaces, PostgreSQL StatefulSet + PVC + Service, API Deployment + NodePort, Prometheus + Grafana) from the versioned `k8s/` manifests; see [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`KUBERNETES.md`](KUBERNETES.md). |
| **Les scripts sont documentés** | Roles are small and commented; usage in [`../ansible/README.md`](../ansible/README.md); rationale and mapping in this file. |
| *Savoir: « outil d'automatisation de type Ansible ou Terraform »* | Ansible + the `kubernetes.core` collection. |

## Validation performed

Tested on a real k3d cluster, in an **isolated** cluster (`opsforge-ansible-test`,
API on port 8090) so an existing cluster was never touched:

- **Fresh deploy** — cluster created, image built and imported, all resources
  applied and ready, `/health = 200`, `/ready = 200`.
- **Idempotence** — a second run recreated nothing (`ok=21, changed=2`).
- **Teardown / recreate** — cluster deleted, then rebuilt from scratch and
  verified again; a pre-existing `opsforge` cluster remained intact throughout.

## Limits (honest scope)

- Deploys to **local k3d**, not a cloud provider (documented scope; the same
  automation pattern would target a cloud Kubernetes for CP N°4).
- The control node is containerised because this workstation has no full WSL Linux
  distribution; on Linux/WSL the playbook runs directly.
- TLS verification is skipped **only** for the local control connection to the
  ephemeral cluster (reached through `host.docker.internal`).
