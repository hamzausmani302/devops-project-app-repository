# Auth Service

![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)

Stateless authentication microservice for the GenStore platform. Handles user login, session token issuance, and token verification. All other backend services call this service to validate requests.

---

## Overview

```
  Client ──POST /login──► Auth Service ──► token issued
                                   │
  Catalog Service ──GET /verify──► Auth Service ──► valid | unauthorized
```

- Issues opaque session tokens on successful login
- Verifies tokens on demand (called by Catalog Service per-request)
- Backed by a static JSON user database (demo-only; see roadmap for production path)
- Stateless HTTP server — no persistent storage required in current form

---

## API Endpoints

| Method | Path | Auth Required | Description |
|--------|------|--------------|-------------|
| `GET` | `/health` | No | Liveness probe — returns `200 OK` |
| `POST` | `/login` | No | Authenticate and receive a session token |
| `POST` | `/logout` | No | Invalidate session (token-based) |
| `GET` | `/verify` | No | Validate a token (`?token=<token>`) |
| `GET` | `/users/{user_id}` | No | Retrieve user metadata by ID |

### POST /login

```bash
curl -X POST http://localhost:8081/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "password123"}'
```

**Response `200 OK`:**
```json
{
  "token": "user_001.john@example.com.2024-01-15T10:30:00.abc123def456",
  "user": {
    "id": "user_001",
    "email": "john@example.com",
    "name": "John Doe",
    "role": "user"
  },
  "expiresIn": 3600
}
```

**Response `401 Unauthorized`:**
```json
{ "detail": "Invalid credentials" }
```

### GET /verify

```bash
curl "http://localhost:8081/verify?token=user_001.john%40example.com.2024-01-15T10:30:00.abc123"
```

**Response `200 OK`:** Returns the user object associated with the token.
**Response `401 Unauthorized`:** Token is invalid or expired.

---

## Test Users

Seeded in `users_db.json`:

| Email | Password | Role |
|-------|----------|------|
| `john@example.com` | `password123` | user |
| `jane@example.com` | `password456` | admin |
| `admin@example.com` | `admin123` | admin |

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8081` | HTTP server port |

Copy `.env.example` to `.env` and adjust as needed.

---

## Local Development

### Run with Python

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Start (development mode with reload)
uvicorn main:app --host 0.0.0.0 --port 8081 --reload

# Or use the entrypoint directly
python main.py
```

Service available at: http://localhost:8081
Interactive API docs: http://localhost:8081/docs

### Run with Docker

```bash
docker build -t hamzausmani021/auth-service:dev .
docker run -p 8081:8081 hamzausmani021/auth-service:dev
```

---

## Project Structure

```
auth-service/
├── main.py            # FastAPI application and all endpoint definitions
├── config.py          # Pydantic settings — reads from env / .env file
├── users_db.json      # Static user database (demo)
├── requirements.txt   # Python dependencies
├── Dockerfile         # Multi-stage build (python:3.9-slim base)
├── .env.example       # Environment variable template
├── .ver               # Service version — drives the Docker image tag in CI
└── tests/             # pytest test suite
```

---

## Testing

```bash
pip install pytest
pytest tests/ -v
```

---

## Kubernetes Deployment

In production, this service is deployed via the `auth-service` Helm chart in [charts-repository](../../charts-repository/auth-service/). Key runtime characteristics:

- **Service names:** `auth-service-stable` (active) and `auth-service-preview` (preview)
- **Rollout strategy:** Blue-Green (default) — configurable to Canary
- **Traffic routing:** `trafficMode: virtualservice` in production (Istio VirtualService)
- **Inter-service communication:** Catalog Service calls `http://auth-service-stable:8081` in production

---

## Roadmap

- [ ] JWT token generation and verification (RS256)
- [ ] Password hashing with bcrypt / argon2
- [ ] Refresh token support with sliding expiration
- [ ] User registration endpoint
- [ ] Role-Based Access Control (RBAC) middleware
- [ ] PostgreSQL backend (replace JSON file)
- [ ] Email verification flow
- [ ] Rate limiting on `/login`
