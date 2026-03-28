# GenStore — Cloud-Native Microservices Platform

![CI](https://github.com/hamzausmani302/devops-project-app-repository/actions/workflows/ci.yml/badge.svg)
![Docker Hub](https://img.shields.io/badge/Docker%20Hub-hamzausmani021-blue?logo=docker)
![Platform](https://img.shields.io/badge/platform-Kubernetes-326CE5?logo=kubernetes)
![Service Mesh](https://img.shields.io/badge/mesh-Istio-466BB0?logo=istio)
![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo)
![Progressive Delivery](https://img.shields.io/badge/delivery-Argo%20Rollouts-orange)

GenStore is a production-grade, cloud-native e-commerce demonstration platform built to showcase real-world DevOps engineering practices. It features a microservices architecture with GitOps-driven deployments, progressive delivery strategies (Blue-Green and Canary), and a full service mesh via Istio.

> **Purpose:** This project mirrors the operational complexity of large-scale production systems — not the application business logic itself, but the infrastructure, deployment pipelines, traffic management, and operational patterns that surround it. It covers the same toolchain used by senior DevOps and SRE teams at scale.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Technology Stack](#technology-stack)
- [CI/CD Pipeline](#cicd-pipeline)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Versioning Convention](#versioning-convention)
- [Related Repositories](#related-repositories)
- [Roadmap](#roadmap)

---

## Architecture Overview

### System Diagram

```
                        ┌──────────────────────────────────────────────┐
                        │          Istio Gateway / Nginx Ingress        │
                        │      (trafficMode: virtualservice / ingress)  │
                        └──────────────────┬───────────────────────────┘
                                           │
                        ┌──────────────────▼───────────────────────────┐
                        │              Frontend Service                 │
                        │        Nginx · Static HTML/JS SPA            │
                        │                Port 80                        │
                        └───────┬──────────────────────┬───────────────┘
                                │                      │
              ┌─────────────────▼──┐           ┌───────▼──────────────┐
              │    Auth Service    │           │   Catalog Service     │
              │  FastAPI · :8081   │◄──────────│  FastAPI · :8000      │
              │  Token issuance &  │  /verify  │  Products & Orders    │
              │  verification      │           │  (auth-guarded)       │
              └────────────────────┘           └──────────┬────────────┘
                                                          │  AMQP publish
                                              ┌───────────▼────────────┐
                                              │       RabbitMQ          │
                                              │   AMQP   · Port 5672   │
                                              │   Mgmt UI· Port 15672  │
                                              └───────────┬────────────┘
                                                          │  AMQP consume
                                              ┌───────────▼────────────┐
                                              │   Inference Service     │
                                              │   Python · Async       │
                                              │   Order processing &   │
                                              │   product generation   │
                                              └────────────────────────┘
```

### Kubernetes Deployment Layer

```
  ┌───────────────────────────────────────────────────────────────────────┐
  │                         Kubernetes Cluster                             │
  │                                                                        │
  │   ┌─────────────────────────────────────────────────────────────┐     │
  │   │                    Argo Rollouts                             │     │
  │   │   Blue-Green ── instant switchover (default)                │     │
  │   │   Canary     ── 20% → 50% → 100% with manual gates          │     │
  │   └─────────────────────────────────────────────────────────────┘     │
  │                                                                        │
  │   ┌────────────────────────┐   ┌──────────────────────────────┐       │
  │   │      Istio Service     │   │        ArgoCD GitOps          │       │
  │   │      Mesh (optional)   │   │   Auto-sync from infra repo   │       │
  │   │   mTLS · Telemetry     │   │   Prune · SelfHeal            │       │
  │   └────────────────────────┘   └──────────────────────────────┘       │
  │                                                                        │
  │   ┌────────────────────────────────────────────────────────────┐      │
  │   │              Helm Umbrella Chart (app-umbrella)             │      │
  │   │   auth · catalog · frontend · inference · rabbitmq · misc  │      │
  │   └────────────────────────────────────────────────────────────┘      │
  └───────────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. External traffic hits the **Istio Gateway** (production) or **Nginx Ingress** (configurable via `trafficMode`)
2. The **Frontend** SPA makes API calls routed through the gateway to backend services
3. **Catalog Service** calls **Auth Service** on every protected request to validate the session token
4. On order placement, **Catalog Service** publishes an event to **RabbitMQ** (`orders` queue)
5. **Inference Service** consumes the event asynchronously and executes the processing workflow

---

## Services

| Service | Language / Runtime | Port | Docker Image | Description |
|---------|--------------------|------|-------------|-------------|
| [frontend-service](./frontend-service/) | HTML5 · JS · Nginx | 80 | `hamzausmani021/frontend-service` | Static SPA — login, catalog, and product pages |
| [auth-service](./auth-service/) | Python 3.9 · FastAPI | 8081 | `hamzausmani021/auth-service` | Token issuance and session verification |
| [catalog-service](./catalog-service/) | Python 3.9 · FastAPI | 8000 | `hamzausmani021/catalog-service` | Product listing and order placement |
| [inference-service](./inference-service/) | Python 3.9 · FastAPI | 8000 | `hamzausmani021/inference-service` | Async order processing via RabbitMQ |
| rabbitmq | — | 5672 / 15672 | `rabbitmq:management-alpine` | AMQP message broker |

Each service has its own `Dockerfile`, `.ver` version file, and independent release lifecycle.

---

## Technology Stack

### Application Layer

| Concern | Technology |
|---------|-----------|
| Frontend | HTML5, Vanilla JS, Nginx `stable-alpine` |
| API Framework | Python 3.9, FastAPI, Uvicorn |
| Messaging | RabbitMQ — pika (AMQP 0-9-1 client) |
| Config Management | pydantic-settings, python-dotenv |

### Infrastructure & Platform

| Concern | Technology |
|---------|-----------|
| Containerization | Docker |
| Orchestration | Kubernetes |
| Service Mesh | Istio 1.24.x |
| GitOps Controller | ArgoCD |
| Progressive Delivery | Argo Rollouts (Blue-Green · Canary) |
| Package Management | Helm 3 (Umbrella pattern) |
| Artifact Registries | Docker Hub · AWS ECR (OCI) |
| CI/CD | GitHub Actions |
| Traffic Routing | Istio VirtualService · Kubernetes Gateway API · Nginx Ingress |
| Local Development | Docker Compose |

---

## CI/CD Pipeline

The entire release cycle is version-file driven. No manual steps are needed after the initial version bump.

### Release Workflow

**Step 1 — Bump the service version:**
```bash
echo "1.2.3" > auth-service/.ver
git add auth-service/.ver
git commit -m "release: auth-service 1.2.3"
git push
```

**Step 2 — GitHub Actions (`ci.yml`) automatically:**
- Detects the changed `.ver` file via diff
- Builds the Docker image: `hamzausmani021/{service}:{version}`
- Pushes to Docker Hub
- Creates and pushes a git tag: `{service}/{version}`

**Step 3 — In `charts-repository`, bump the chart version:**
```yaml
# charts-repository/auth-service/Chart.yaml
version: 1.1.9   # was 1.1.8
```

**Step 4 — Charts CI automatically:**
- Detects the `Chart.yaml` version bump
- Runs `helm lint`
- Packages the chart
- Pushes to AWS ECR OCI registry: `oci://168836624397.dkr.ecr.us-east-1.amazonaws.com/helm`
- Tags the release: `auth-service/1.1.9`

**Step 5 — In `infra-repository`, open a PR to update `helm/prod/values.yaml`:**
```yaml
auth-service:
  image:
    tag: "1.2.3"
```

**Step 6 — After PR merge, ArgoCD detects the change and triggers an Argo Rollout.**

### Pipeline Flow Diagram

```
  [app-repository]
  .ver bump ──► CI detects change
               ├── docker build & push ──► Docker Hub
               └── git tag: service/version

  [charts-repository]
  Chart.yaml version bump ──► Charts CI
                              ├── helm lint
                              ├── helm package
                              ├── push OCI ──► AWS ECR
                              └── git tag: chart/version

  [infra-repository]
  values.yaml PR ──► merge ──► ArgoCD auto-sync ──► Argo Rollout
```

### Deployment Strategies

| Strategy | Configuration | Behavior |
|----------|--------------|----------|
| **Blue-Green** | `rollout.strategy: blueGreen` | Full preview environment spun up; traffic switches instantly on promotion. `autoPromotionEnabled: false` requires manual approval. |
| **Canary** | `rollout.strategy: canary` | Gradual traffic shift: 20% → pause 30s → 50% → manual gate → 100%. Istio VirtualService or Gateway API handle weighted routing. |

Traffic routing mode is controlled per-service via `trafficMode`:

| `trafficMode` | Mechanism |
|--------------|-----------|
| `ingress` | Nginx Ingress (default, simple) |
| `gatewayapi` | Kubernetes Gateway API + HTTPRoute |
| `virtualservice` | Istio VirtualService (production) |

---

## Local Development

### Prerequisites

- Docker Desktop ≥ 24.x
- Docker Compose v2 (`docker compose` not `docker-compose`)

### Start the Full Stack

```bash
cd infra-repository/docker
docker compose up -d
```

### Service Endpoints (Local)

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8080 |
| Auth Service | http://localhost:8081 |
| Catalog Service | http://localhost:8000 |
| RabbitMQ Management UI | http://localhost:15672 |

### Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| RabbitMQ Management UI | `guest` | `guest` |

Test user accounts are seeded in [auth-service/users_db.json](./auth-service/users_db.json) (see [Auth Service README](./auth-service/README.md)).

### Build Individual Images

```bash
# Build a single service
docker build -t hamzausmani021/auth-service:dev ./auth-service
docker build -t hamzausmani021/catalog-service:dev ./catalog-service
docker build -t hamzausmani021/frontend-service:dev ./frontend-service
docker build -t hamzausmani021/inference-service:dev ./inference-service
```

### Run a Service Standalone (without Compose)

```bash
# Auth Service
cd auth-service
pip install -r requirements.txt
python main.py

# Catalog Service (requires RabbitMQ + Auth Service)
cd catalog-service
pip install -r requirements.txt
python main.py
```

---

## Environment Variables

### Auth Service

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8081` | HTTP server port |

### Catalog Service

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | HTTP server port |
| `RABBITMQ_HOST` | `localhost` | RabbitMQ hostname |
| `RABBITMQ_PORT` | `5672` | RabbitMQ AMQP port |
| `RABBITMQ_TOPIC` | `orders` | Queue name for order events |
| `AUTH_SERVICE_URL` | `http://auth-service:8081` | Auth service base URL |

### Inference Service

| Variable | Default | Description |
|----------|---------|-------------|
| `RABBITMQ_HOST` | `localhost` | RabbitMQ hostname |
| `RABBITMQ_PORT` | `5672` | RabbitMQ AMQP port |
| `RABBITMQ_TOPIC` | `orders` | Queue name to consume |

---

## API Reference

Full interactive docs are served by FastAPI at `/docs` on each service when running locally.

### Auth Service (`/auth-service/*` via gateway in prod)

| Method | Path | Auth Required | Description |
|--------|------|--------------|-------------|
| `GET` | `/health` | No | Liveness probe |
| `POST` | `/login` | No | Authenticate and receive a session token |
| `POST` | `/logout` | Yes | Invalidate the current session |
| `GET` | `/verify` | No | Validate a token (`?token=<token>`) |
| `GET` | `/users/{user_id}` | Yes | Retrieve user details |

**Example — Login:**
```bash
curl -X POST http://localhost:8081/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "password123"}'
```
```json
{
  "token": "user_001.john@example.com.2024-01-15T10:30:00.abc123def456",
  "user": { "id": "user_001", "email": "john@example.com", "name": "John Doe", "role": "user" },
  "expiresIn": 3600
}
```

### Catalog Service (`/catalog-service/*` via gateway in prod)

| Method | Path | Auth Required | Description |
|--------|------|--------------|-------------|
| `GET` | `/health` | No | Liveness probe |
| `GET` | `/products` | Yes | List all products |
| `GET` | `/products/{id}` | Yes | Get a single product |
| `POST` | `/orders` | Yes | Place an order (publishes to RabbitMQ) |

---

## Versioning Convention

Each service maintains an independent version via a `.ver` file:

```
auth-service/.ver         →  controls Docker image tag
catalog-service/.ver      →  controls Docker image tag
frontend-service/.ver     →  controls Docker image tag
inference-service/.ver    →  controls Docker image tag
```

Git tags follow `{service}/{semver}` (e.g., `auth-service/1.1.3`). Chart versions in `charts-repository` are separately versioned and follow the same tag convention (`auth-service/1.1.9`).

---

## Related Repositories

| Repository | Purpose |
|-----------|---------|
| [charts-repository](../charts-repository/) | Helm charts for all services — linted, packaged, and pushed to AWS ECR |
| [infra-repository](../infra-repository/) | ArgoCD configuration, GitOps app definitions, production Helm values, Kubernetes manifests |

---

## Roadmap

See [infra-repository/TODO.md](../infra-repository/TODO.md) for the full prioritized backlog. Key planned items:

- [ ] TLS termination and Istio mTLS (PeerAuthentication + DestinationRule)
- [ ] Prometheus metrics instrumentation and Grafana dashboards
- [ ] Kiali for real-time service topology visualization
- [ ] Horizontal Pod Autoscaling driven by load test baselines
- [ ] Production EKS cluster deployment
- [ ] Separate per-service repositories with isolated pipelines

---

## Security

Credentials must never be committed to version control. All secrets are to be created out-of-band and referenced by Kubernetes Secret name. See [infra-repository](../infra-repository/) for the secret configuration pattern used in this project.
