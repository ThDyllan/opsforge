#!/usr/bin/env bash
# Run an OpsForge Ansible playbook from the containerised control node.
#
#   ./run.sh                       # deploy (deploy.yml)
#   ./run.sh teardown.yml          # tear the cluster down
#   ./run.sh deploy.yml -e cluster_name=opsforge-test -e api_host_port=8090
#
# On a Linux/WSL host with ansible + k3d + kubectl installed you can instead run
# `ansible-playbook deploy.yml` directly, without this wrapper.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/.." && pwd)"
playbook="${1:-deploy.yml}"
[ "$#" -gt 0 ] && shift || true

docker build -t opsforge-ansible-control "$here"
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$repo":/work \
  opsforge-ansible-control \
  ansible-playbook "$playbook" "$@"
