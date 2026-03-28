# Frontend Service

![Nginx](https://img.shields.io/badge/Nginx-stable--alpine-009639?logo=nginx)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)

Static Single-Page Application (SPA) for the GenStore platform, served by Nginx. Provides the user-facing web interface for authentication, product browsing, and order placement. Backend service URLs are injected at runtime via a ConfigMap-mounted `env.js` file, making the frontend environment-agnostic.

---

## Overview

```
  Browser ──HTTP──► Nginx (port 80)
                        │
                        ├── / index.html      (product catalog)
                        ├── /login.html       (authentication)
                        └── /product.html     (product detail)
                                │
                         env.js defines:
                         AUTH_SERVICE_URL
                         CATALOG_SERVICE_URL
```

The frontend is intentionally thin — all business logic lives in the backend services. The SPA communicates directly with Auth Service and Catalog Service via their exposed URLs.

---

## Pages

| Page | File | Description |
|------|------|-------------|
| Catalog | `index.html` + `js/index.js` | Lists available products, requires login |
| Login | `login.html` + `js/login.js` | Authenticates via Auth Service, stores token |
| Product Detail | `product.html` + `js/product.js` | Product info and order placement |

---

## Runtime Configuration

Backend endpoints are configured in `env.js`:

```javascript
// env.js — edited for local development, injected via ConfigMap in Kubernetes
const AUTH_SERVICE_URL    = "http://localhost:8081";
const CATALOG_SERVICE_URL = "http://localhost:8000";
```

In Kubernetes, `env.js` is replaced by a ConfigMap at deploy time (see the `frontend-service` Helm chart). The Nginx server serves the ConfigMap-mounted file in place of the one baked into the image, allowing a single image to run in any environment.

---

## Local Development

### Option 1 — Full Stack (recommended)

Run all services together with Docker Compose:

```bash
cd ../../infra-repository/docker
docker compose up -d
```

Frontend available at: http://localhost:8080

### Option 2 — Static File Server (frontend only)

```bash
# Requires Python — no Nginx required
cd frontend-service/
python -m http.server 8080
```

Open: http://localhost:8080

> Note: CORS and API calls require the backend services to be running. Update `env.js` to point to running instances.

### Option 3 — Docker

```bash
docker build -t hamzausmani021/frontend-service:dev .
docker run -p 8080:80 hamzausmani021/frontend-service:dev
```

---

## Nginx Configuration

`nginx.conf` configures the server to:
- Serve static files from `/var/www/devops-project`
- Return `index.html` for unknown paths (SPA fallback)
- Set appropriate cache headers for static assets

---

## Project Structure

```
frontend-service/
├── index.html             # Catalog page
├── login.html             # Login page
├── product.html           # Product detail page
├── env.js                 # Runtime environment config (overridden by ConfigMap in K8s)
├── js/
│   ├── index.js           # Catalog page logic — calls GET /products
│   ├── login.js           # Login form — calls POST /login, stores token
│   └── product.js         # Product detail — calls GET /products/{id}, POST /orders
├── nginx.conf             # Nginx server configuration
├── Dockerfile             # nginx:stable-alpine3.23 base
├── .dockerignore          # Excludes node_modules, .git etc from build context
└── .ver                   # Version file — drives Docker image tag in CI
```

---

## Kubernetes Deployment

Deployed via the `frontend-service` Helm chart in [charts-repository](../../charts-repository/frontend-service/). Key runtime characteristics:

- **ConfigMap:** `env.js` is rendered as a Kubernetes ConfigMap from Helm values (`authServiceUrl`, `catalogServiceUrl`) and mounted over the baked-in file
- **Replicas:** 5 in production (scaled for traffic)
- **Rollout strategy:** Canary in production — gradual traffic shift with manual promotion gate
- **Traffic routing:** `trafficMode: virtualservice` (Istio) in production

---

## Roadmap

- [ ] Build toolchain (Vite or webpack) for asset bundling and hashing
- [ ] Proper framework (React or Vue) for maintainability
- [ ] Content Security Policy headers in Nginx config
- [ ] Asset compression (gzip/brotli) enabled in Nginx
- [ ] HTTPS-only enforcement (redirect HTTP → HTTPS)
