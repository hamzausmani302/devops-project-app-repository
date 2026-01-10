# Inference Service

Microservice that demonstrates inference-related logic and messaging integration for the sample project.

## Overview

- Implements inference-related workflows and integrates with the project's messaging layer (RabbitMQ) for async communication.
- Includes a lightweight HTTP surface and message adapters to publish/consume inference requests and results.

## Files

- `main.py` — service entrypoint and HTTP endpoints
- `messaging_service.py` — high-level messaging helper
- `rabbitmq_message_adapter.py` — RabbitMQ adapter used by the service
- `config.py` — configuration values for connections and ports
- `requirements.txt` — Python dependencies

## Run (local)

1. Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Ensure a message broker is available (RabbitMQ) if you use the messaging features.

3. Start the service:

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## Messaging

- The service includes an adapter for RabbitMQ. Check `rabbitmq_message_adapter.py` and `messaging_service.py` for publish/consume examples.
- Use local RabbitMQ (Docker image `rabbitmq:3-management`) for development.

