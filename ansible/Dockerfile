# Ansible control node: bundles Ansible + kubernetes.core and the k3d/kubectl/docker
# CLIs. The automation is run from this container via ansible/run.sh, which drives
# the host Docker daemon through the mounted socket. This containerised control node
# is the supported, validated way to run it.
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    ANSIBLE_COLLECTIONS_PATH=/root/.ansible/collections \
    # Point Ansible at our config explicitly. The repo is bind-mounted from a
    # world-writable location, so Ansible would otherwise ignore ansible.cfg
    # (and thus its inventory) for safety. An explicit ANSIBLE_CONFIG is honoured.
    ANSIBLE_CONFIG=/work/ansible/ansible.cfg

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates tar \
 && rm -rf /var/lib/apt/lists/*

# Ansible + the Python Kubernetes client used by kubernetes.core.
# Pinned to the versions actually validated for this project.
RUN pip install "ansible-core==2.17.14" "kubernetes==36.0.3"

# kubectl
RUN curl -fsSL -o /usr/local/bin/kubectl \
      "https://dl.k8s.io/release/v1.31.5/bin/linux/amd64/kubectl" \
 && chmod +x /usr/local/bin/kubectl

# k3d CLI (drives the host Docker daemon via the mounted socket)
RUN curl -fsSL -o /usr/local/bin/k3d \
      "https://github.com/k3d-io/k3d/releases/download/v5.9.0/k3d-linux-amd64" \
 && chmod +x /usr/local/bin/k3d

# Docker CLI only (static binary), used for `docker build`
RUN curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-27.5.1.tgz" \
      | tar -xz -C /usr/local/bin --strip-components=1 docker/docker

# Ansible collection for Kubernetes (pinned to the validated version)
RUN ansible-galaxy collection install kubernetes.core:6.5.0

WORKDIR /work/ansible
