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

## What Ansible adds here

Ansible orchestrates the **complete, multi-tool workflow** as a single
reproducible, idempotent run, while `kubernetes.core` manages the Kubernetes
resources declaratively:

- **One workflow across several tools** — Docker (build), k3d (cluster + image
  import), the Kubernetes API (apply), and an HTTP check are sequenced in one
  playbook, with dependency ordering (PostgreSQL ready → API ready → monitoring).
- **Declarative Kubernetes management** — `kubernetes.core.k8s` applies each
  manifest and, with `wait: true`, blocks until the resource reports ready.
- **Idempotent convergence** — re-running does not recreate the cluster or the
  resources; a second run reports almost everything as `ok` (unchanged).
- **End-to-end verification** — the run only succeeds if the API answers `200` on
  `/health` and `/ready` (the latter proving PostgreSQL connectivity via
  `SELECT 1`).
- **Deploy-time Secret** — the PostgreSQL `Secret` is generated from variables at
  deploy time, so no separate credential manifest is committed (see *Credentials*
  below).
- **Reproducible control node** — defined as code in `ansible/Dockerfile`.

`k3d` and `docker` are driven through their CLIs (natural for those tools); the
Kubernetes work goes through the `kubernetes.core` collection.

## Why Ansible rather than Terraform

Both are accepted by the reference and both are legitimate infrastructure-as-code
tools; they simply have different strengths. Terraform is **declarative and
state-based** — you describe a desired end state and it reconciles the real world
to it. Ansible is **procedural orchestration** — you describe an ordered sequence
of steps, potentially across several tools. Our task here is exactly that kind of
sequence (prepare the control node → create the k3d cluster → build and import the
image → apply the Kubernetes resources in order → wait → verify), so Ansible maps
to it naturally. Provisioning cloud infrastructure (a VPC, a managed Kubernetes,
…) would be a natural fit for Terraform, and is the direction of CP N°4
(questioned at the oral, not required in this project).

## Mapping to CP N°2 criteria

| Critère de performance (REAC) | Evidence in this project |
| --- | --- |
| **Les serveurs déployés sont fonctionnels** | The run gates on PostgreSQL and the API becoming ready, then verifies `/health = 200` and `/ready = 200` (DB reachable). |
| **L'architecture est conforme au cahier des charges** | The playbook deploys the documented architecture (namespaces, PostgreSQL StatefulSet + PVC + Service, API Deployment + NodePort, Prometheus + Grafana) from the versioned `k8s/` manifests; see [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`KUBERNETES.md`](KUBERNETES.md). |
| **Les scripts sont documentés** | Roles are small and commented; usage in [`../ansible/README.md`](../ansible/README.md); rationale and mapping in this file. |
| *Savoir: « outil d'automatisation de type Ansible ou Terraform »* | Ansible + the `kubernetes.core` collection. |

## Credentials

There is **no separate credential manifest** in Git: the PostgreSQL `Secret` is
generated at deploy time from the variables in `ansible/group_vars/all.yml`.
Those variables hold a **non-sensitive local demonstration default** — the same
kind of throwaway credential used by `docker-compose.yml` for local runs (the
actual values are not identical), not a real secret. Override them on the command
line (`-e db_password=...`) or move them to `ansible-vault` for anything beyond
local demonstration.

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
- The **containerised control node (`ansible/run.sh`) is the supported, validated
  way** to run this automation. The playbook assumes that context — in particular
  it reaches the cluster through `host.docker.internal`, which `run.sh` wires up —
  so running `ansible-playbook` directly on a host is not supported as-is.
- TLS verification is skipped **only** for the local control connection to the
  ephemeral cluster (reached through `host.docker.internal`).
