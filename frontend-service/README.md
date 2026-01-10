# Frontend Service

A small static frontend for the sample application, served with Nginx in the project's Docker setup.

## Overview

- Static HTML/JS app that consumes the backend microservices (auth, catalog, inference).
- Includes `index.html`, `login.html`, `product.html`, client-side JS in `js/`, and an Nginx `Dockerfile` and configuration.

## Files

- `index.html`, `login.html`, `product.html` — main UI pages
- `js/` — frontend JavaScript (index.js, login.js, product.js)
- `env.js` — environment config used by the frontend
- `nginx.conf`, `Dockerfile` — containerization for static hosting

## Run (local)

Simple static server (quick local test):

```bash
# from frontend-service directory
python -m http.server 8080
# then open http://localhost:8080 in a browser
```

Run in Docker (builds an image that serves the site with Nginx):

```bash
# from frontend-service directory
docker build -t full-devops-frontend .
docker run -p 8080:80 full-devops-frontend
```

## Configuration

- Edit `env.js` to point to local backend endpoints during development.

## Notes

- This frontend is purposely minimal for demonstration. For production, add a build step (webpack, Vite), asset hashing, and secure configuration for backend endpoints.