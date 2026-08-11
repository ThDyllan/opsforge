#!/usr/bin/env bash
# Run an OpsForge Ansible playbook from the containerised control node.
#
#   ./run.sh                       # deploy (deploy.yml)
#   ./run.sh teardown.yml          # tear the cluster down
#   ./run.sh deploy.yml -e cluster_name=opsforge-test -e api_host_port=8090 -e kubeapi_host_port=6446
#
# On a Linux/WSL host with ansible + k3d + kubectl installed you can instead run
# `ansible-playbook -i inventory.ini deploy.yml` directly, without this wrapper.
set -euo pipefail

# Git Bash on Windows rewrites Unix-style paths passed to native binaries; disable
# that so the container-side paths (docker socket, /work) reach Docker unchanged.
# Harmless (ignored) on Linux/WSL.
export MSYS_NO_PATHCONV=1

here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/.." && pwd)"
playbook="${1:-deploy.yml}"
[ "$#" -gt 0 ] && shift || true

# Build the control node image (context = the ansible/ directory).
( cd "$here" && docker build -t opsforge-ansible-control . )

# The image sets ANSIBLE_CONFIG=/work/ansible/ansible.cfg; we still pass the
# inventory explicitly so it is parsed regardless of how the config is picked up.
docker run --rm \
  --add-host=host.docker.internal:host-gateway \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$repo":/work \
  opsforge-ansible-control \
  ansible-playbook -i inventory.ini "$playbook" "$@"
