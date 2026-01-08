from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import run_in_threadpool
from fastapi import Request
from fastapi.responses import JSONResponse
import requests
import os

EXCLUDED_PATHS = ["/docs", "/openapi.json"]

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that verifies incoming requests using the auth service.

    - Extracts token from Authorization header (Bearer ...) or from `token` query param
    - Calls the auth service `/verify?token=...` endpoint (configurable via AUTH_SERVICE_URL)
    - On success: attaches `user` info (if returned) to `request.state.user` and continues
    - On failure: returns a JSONResponse with 401 or 503
    """
    async def dispatch(self, request: Request, call_next):
        # Auth service base URL (env var or default)
        auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8081")
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        # 1) Extract token from Authorization header (Bearer <token>)
        token = None
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth_header:
                # If header provided without 'Bearer', take whole value
                token = auth_header.strip()

        # 2) Fallback: check query param ?token=...
        if not token:
            token = request.query_params.get("token")

        if not token:
            return JSONResponse({"detail": "Authorization token missing"}, status_code=401)

        # 3) Call auth service verify endpoint in threadpool to avoid blocking
        verify_url = f"{auth_service_url.rstrip('/')}/verify"
        try:
            # run_in_threadpool expects a callable; use a lambda to pass kwargs
            resp = requests.post(verify_url, params={"token": token})
        except Exception as exc:
            return JSONResponse({"detail": f"Auth service unreachable: {str(exc)}"}, status_code=503)
        # If auth service returns non-200, reject the request
        if resp.status_code != 200:
            # Try to forward the error detail if available
            try:
                payload = resp.json()
                detail = payload.get("detail") or payload.get("message") or "Unauthorized"
            except Exception:
                detail = "Unauthorized"
            return JSONResponse({"detail": detail}, status_code=401)

        # Attach user info to request.state if returned by verify endpoint
        try:
            payload = resp.json()
            # If the verify endpoint returns user info under 'user', attach it
            user_info = payload.get("user") if isinstance(payload, dict) else None
            if user_info:
                request.state.user = user_info
            else:
                # Store token at least
                request.state.token = token
        except Exception:
            # Non-json or missing body; still proceed
            request.state.token = token

        # Proceed to the next handler
        response = await call_next(request)
        return response