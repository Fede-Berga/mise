## kind Deployment on Rocky Linux

This guide explains how to run Mise on a **single Rocky Linux machine** using:

- `kind` (Kubernetes in Docker) for the cluster
- The `infra/kind/cluster-rocky.yaml` config tuned for systemd cgroups

This is ideal for:

- A **single-restaurant** on-prem box
- A **development/staging** environment mimicking production Helm/Kubernetes

---

### 1. Prerequisites (Rocky Linux)

- Rocky Linux 9.x
- User with `sudo` privileges
- Installed:
  - Docker or containerd (Docker recommended for kind)
  - `kubectl`
  - `kind`

#### 1.1 Install Docker

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
newgrp docker
```

#### 1.2 Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

#### 1.3 Install kind

```bash
GO111MODULE=on go install sigs.k8s.io/kind@v0.24.0
echo 'export PATH="$PATH:$HOME/go/bin"' >> ~/.bashrc
source ~/.bashrc
```

---

### 2. Create the Cluster

Config file: `infra/kind/cluster-rocky.yaml`

```bash
cd /home/fbergamini/Projects/personal/mise
kind create cluster --config infra/kind/cluster-rocky.yaml

kubectl cluster-info
kubectl get nodes
```

The config:

- Uses Kubernetes v1.30 images
- Maps host ports **80/443** into the control plane (for Traefik ingress)
- Enables systemd cgroups (required on Rocky)

---

### 3. Install Base Dependencies

You can either:

- Use **Helm umbrella charts** (`infra/helm/mise-platform`) once wired, or
- Apply manifests directly (for an initial POC)

Typical namespaces:

- `mise-system` — ingress, cert-manager, Keycloak, MinIO
- `mise-data` — PostgreSQL, Dragonfly, NATS, ClickHouse, Meilisearch
- `mise-core` — Mise microservices

Example (simplified) using Helm once charts exist:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update

helm install mise-deps ./infra/helm/mise-deps -n mise-system --create-namespace
helm install mise ./infra/helm/mise-platform -n mise-core --create-namespace
```

Until the Helm charts are implemented, this file primarily documents:

- Cluster creation for Rocky
- Port mappings
- Namespaces and expectations for operators

---

### 4. Single vs Multi-Restaurant on kind

On a single Rocky box:

- **Single restaurant**:
  - Create **one Keycloak realm** (e.g. `restaurant-main`)
  - Keep DB size and ClickHouse retention modest
- **Many restaurants**:
  - Use:
    - Per-restaurant realms, or
    - One shared realm with `tenant_id` and groups
  - Enable PostgreSQL RLS everywhere
  - Increase storage for PostgreSQL, ClickHouse, MinIO

The same cluster and manifests support both; the difference is **how you configure Keycloak and the DB**.

---

### 5. Teardown

To destroy the cluster completely:

```bash
kind delete cluster --name mise
```

This removes all Kubernetes resources but leaves Docker images and volumes intact.

---

### 6. Path to Production

Once you outgrow a single Rocky node:

- Move from `kind` to:
  - Upstream Kubernetes, or
  - A managed K8s (EKS, GKE, AKS), or
  - A bare-metal cluster (k3s, kubeadm)
- Reuse the **same Helm charts** you validated on `kind`
- Adjust:
  - Storage classes
  - Domain names (ingress)
  - Resource requests/limits

The goal is: **what works on `kind` on Rocky should work unchanged on a multi-node cluster**, aside from scaling and infra-specific details.
