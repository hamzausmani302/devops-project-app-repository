# Inference Service

![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-AMQP-FF6600?logo=rabbitmq)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![Async](https://img.shields.io/badge/pattern-Event%20Driven-blueviolet)

Event-driven microservice that processes order events published by the Catalog Service. Consumes messages from RabbitMQ asynchronously and runs the product inference/generation workflow. This service has no synchronous HTTP interface exposed to end-users — it operates entirely through the message queue.

---

## Overview

```
  Catalog Service
       │
       │  AMQP publish → orders queue
       ▼
  RabbitMQ
       │
       │  AMQP consume
       ▼
  Inference Service
       │
       └── process order → simulate generation workflow
```

- Consumes messages from the `orders` RabbitMQ queue
- Processes each order through the inference workflow
- Designed as a background worker — decoupled from the request path
- Demonstrates async, event-driven integration patterns in a microservices architecture

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RABBITMQ_HOST` | `localhost` | RabbitMQ hostname or Kubernetes service name |
| `RABBITMQ_PORT` | `5672` | RabbitMQ AMQP port |
| `RABBITMQ_TOPIC` | `orders` | Queue name to consume from |

---

## Local Development

### Prerequisites

- Python 3.9+
- RabbitMQ instance (local or Docker)

### Run with Python

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
python main.py
```

The service will connect to RabbitMQ and begin listening on the configured queue.

### Run with Docker Compose (recommended)

Run alongside all other services:

```bash
cd ../../infra-repository/docker
docker compose up -d
```

### Run with Docker (standalone)

```bash
docker build -t hamzausmani021/inference-service:dev .

docker run \
  -e RABBITMQ_HOST=host.docker.internal \
  -e RABBITMQ_PORT=5672 \
  -e RABBITMQ_TOPIC=orders \
  hamzausmani021/inference-service:dev
```

---

## Project Structure

```
inference-service/
├── main.py                          # Service entrypoint — starts the consumer loop
├── messaging_service.py             # High-level messaging abstraction
├── rabbitmq_message_adapter.py      # pika-based RabbitMQ consumer/publisher adapter
├── config.py                        # Pydantic settings — reads from env
├── requirements.txt                 # Python dependencies (pika, pydantic-settings)
├── Dockerfile                       # python:3.9-slim base
├── .dockerignore                    # Build context exclusions
└── .ver                             # Version file — drives Docker image tag in CI
```

### Key Components

**`rabbitmq_message_adapter.py`** — Low-level adapter wrapping the pika library:
- Establishes and maintains the AMQP connection
- Declares the queue (idempotent)
- Handles acknowledgement (ack/nack) after processing
- Reconnect logic on connection loss

**`messaging_service.py`** — Higher-level orchestration:
- Wires the adapter to the processing callback
- Provides a clean interface for `main.py`

**`main.py`** — Entry point:
- Initializes configuration
- Starts the blocking consumer loop

---

## Kubernetes Deployment

Deployed via the `inference-service` Helm chart in [charts-repository](../../charts-repository/inference-service/). Key runtime characteristics:

- **No Ingress / HTTPRoute:** This service has no external HTTP surface — excluded from gateway routing
- **Internal only:** Communicates exclusively via RabbitMQ
- **Rollout strategy:** Blue-Green (default) — configurable to Canary
- **Traffic routing:** `trafficMode: virtualservice` in production
- **RabbitMQ connection:** Uses `RABBITMQ_HOST=rabbitmq` (Kubernetes service name)

---

## Roadmap

- [ ] Dead-letter queue (DLQ) for failed message processing
- [ ] Message retry with exponential backoff
- [ ] Prometheus metrics (messages consumed, processing latency, error rate)
- [ ] Integration with a real inference model (e.g., via an ML API)
- [ ] Output publishing — write results back to a results queue or database
- [ ] Horizontal scaling — multiple consumer replicas with competing consumer pattern
