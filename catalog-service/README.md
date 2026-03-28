# Catalog Service

![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-AMQP-FF6600?logo=rabbitmq)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)

Core backend microservice for the GenStore platform. Serves the product catalog and handles order placement. Every authenticated request is verified against the Auth Service, and orders are published asynchronously to RabbitMQ for downstream processing.

---

## Overview

```
  Client ──GET /products──► Catalog Service ──GET /verify──► Auth Service
                                   │
                         POST /orders
                                   │
                                   └──► RabbitMQ (orders queue)
                                                  │
                                         Inference Service consumes
```

- Reads product data from `data.json` (demo-only; see roadmap for DB path)
- Validates request tokens by calling Auth Service before serving protected routes
- Publishes order events to RabbitMQ using the pika AMQP client
- Structured as a proper Python package (`catalog_service/`) with layered architecture

---

## API Endpoints

| Method | Path | Auth Required | Description |
|--------|------|--------------|-------------|
| `GET` | `/health` | No | Liveness probe — returns `200 OK` |
| `GET` | `/products` | Yes | List all available products |
| `GET` | `/products/{product_id}` | Yes | Get product details by ID |
| `POST` | `/orders` | Yes | Place an order (publishes to RabbitMQ) |

### GET /products

```bash
curl http://localhost:8000/products \
  -H "Authorization: Bearer <token>"
```

**Response `200 OK`:**
```json
[
  { "id": "prod_001", "name": "Product A", "price": 29.99, "category": "art" },
  { "id": "prod_002", "name": "Product B", "price": 49.99, "category": "photo" }
]
```

### POST /orders

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"product_id": "prod_001", "quantity": 1}'
```

**Response `202 Accepted`:** Order accepted and queued.
**Response `401 Unauthorized`:** Token missing or invalid.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | HTTP server port |
| `RABBITMQ_HOST` | `localhost` | RabbitMQ hostname or Kubernetes service name |
| `RABBITMQ_PORT` | `5672` | RabbitMQ AMQP port |
| `RABBITMQ_TOPIC` | `orders` | Queue name for order events |
| `AUTH_SERVICE_URL` | `http://auth-service:8081` | Auth Service base URL for token verification |

> In production Kubernetes, `AUTH_SERVICE_URL` is set to `http://auth-service-stable:8081` to route to the active (stable) deployment, not the preview.

---

## Local Development

### Prerequisites

- Python 3.9+
- RabbitMQ running locally (or via Docker Compose)
- Auth Service running (for authenticated endpoints)

### Quick Start (with Docker Compose)

The easiest way to run the full stack:
```bash
cd ../../infra-repository/docker
docker compose up -d
```

### Run Standalone

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Start RabbitMQ (if not already running)
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:management-alpine

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Service available at: http://localhost:8000
Interactive API docs: http://localhost:8000/docs

### Run with Docker

```bash
docker build -t hamzausmani021/catalog-service:dev .

docker run -p 8000:8000 \
  -e RABBITMQ_HOST=host.docker.internal \
  -e AUTH_SERVICE_URL=http://host.docker.internal:8081 \
  hamzausmani021/catalog-service:dev
```

---

## Project Structure

```
catalog-service/
├── main.py                          # FastAPI application entrypoint
├── config.py                        # Pydantic settings
├── data.json                        # Product catalog data (demo)
├── orders.json / order.json         # Order data (demo)
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container build (python:3.9-slim)
├── .ver                             # Version file — drives Docker image tag in CI
│
└── catalog_service/                 # Main application package
    ├── api/
    │   ├── api_router_definition.py # Central router registration
    │   ├── deps.py                  # FastAPI dependency injection (auth guard)
    │   └── routers/
    │       ├── home/                # Root / health routes
    │       ├── orders/              # Order placement routes
    │       └── product/             # Product listing routes
    ├── core/
    │   ├── middlewares/             # Request middleware (logging, auth)
    │   ├── model/
    │   │   └── orders/              # Order data models (Pydantic)
    │   └── services/                # Business logic layer
    ├── infra/
    │   └── services/
    │       └── messaging/           # RabbitMQ publisher (pika)
    └── util/                        # Shared utilities
```

---

## Testing

```bash
pip install pytest
pytest tests/ -v
```

---

## Kubernetes Deployment

Deployed via the `catalog-service` Helm chart in [charts-repository](../../charts-repository/catalog-service/). Key runtime characteristics:

- **Service names:** `catalog-service-stable` and `catalog-service-preview`
- **Rollout strategy:** Blue-Green (default) — configurable to Canary
- **Traffic routing:** `trafficMode: virtualservice` in production (Istio VirtualService)
- **RabbitMQ connection:** Uses `RABBITMQ_HOST=rabbitmq` (Kubernetes service name)

---

## Roadmap

- [ ] PostgreSQL backend (replace `data.json`)
- [ ] Pagination and filtering on `/products`
- [ ] Response caching (Redis)
- [ ] Idempotent order submission (deduplication key)
- [ ] Order status tracking endpoint
- [ ] Dead-letter queue handling for failed publishes
