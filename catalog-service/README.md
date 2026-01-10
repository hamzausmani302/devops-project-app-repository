# Catalog Service

A lightweight FastAPI-based microservice that serves product catalog data for the sample application.

## Overview

- Reads product data from `data.json` and exposes simple read-only APIs for consumers.
- Intended for demo and local development use inside the full-devops-project.

## Features

- List products
- Get product details by ID
- Basic health check endpoint

## Files

- `main.py` — FastAPI application entrypoint
- `config.py` — runtime configuration
- `data.json` — product data used by the service
- `requirements.txt` — Python dependencies

## Run (local)

1. Create a virtual environment and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Run the service:

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

The service will be available at `http://localhost:8002` (default port used in this project may vary).

## API (examples)

- `GET /health` — health check
- `GET /products` — list all products
- `GET /products/{product_id}` — get product details

Refer to `main.py` for exact route definitions and parameter names.

## Notes

- This is a demo service built for local testing. For production use, replace the JSON file with a proper database and add pagination, caching, and authentication as needed.
