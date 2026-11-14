
import os
import requests

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse
from opentelemetry.trace import Status, StatusCode


from catalog_service.telemetry import trace_span
from catalog_service.telemetry import trace_function


EXCLUDED_PATHS = {
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware.

    - Extracts Bearer token from Authorization header.
    - Falls back to token query parameter.
    - Verifies token using the auth service.
    - Attaches user information to request.state.
    - Creates OpenTelemetry spans for authentication operations.3wr35ra3eft6
    """
    @trace_function("auth dispatch")
    async def dispatch(self, request: Request, call_next):

        # Skip authentication for excluded paths
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        auth_service_url = os.getenv(
            "AUTH_SERVICE_URL",
            "http://auth-service:8081"
        ).rstrip("/")

        verify_url = f"{auth_service_url}/verify"

        # --------------------------------------------------
        # 1. Extract authentication token
        # --------------------------------------------------

        with trace_span(
            "auth.token.extraction",
            {
                "auth.operation": "extract_token",
                "http.request.method": request.method,
            }
        ) as span:

            auth_header = request.headers.get("authorization")
            token = None

            if auth_header:
                scheme, separator, credentials = auth_header.partition(" ")

                if separator and scheme.lower() == "bearer":
                    token = credentials.strip()
                elif not separator:
                    token = auth_header.strip()

            # Fallback to query parameter
            if not token:
                token = request.query_params.get("token")

            span.set_attribute(
                "auth.token.present",
                bool(token)
            )

        if not token:
            span.set_status(Status(StatusCode.ERROR))
            return JSONResponse(
                {"detail": "Authorization token missing"},
                status_code=401
            )

        # --------------------------------------------------
        # 2. Verify token with auth service
        # --------------------------------------------------

        try:
            with trace_span(
                "auth.verify",
                {
                    "auth.operation": "token_verification",
                    "auth.service.url": verify_url,
                }
            ) as span:

                # requests.post is synchronous, so execute in threadpool
                resp = await run_in_threadpool(
                    requests.post,
                    verify_url,
                    params={"token": token},
                    timeout=5,
                )
                span.set_attribute(
                    "http.response.status_code",
                    resp.status_code
                )

                span.set_attribute(
                    "auth.success",
                    resp.status_code == 200
                )

                if resp.status_code != 200:
                    span.set_attribute(
                        "auth.failure_reason",
                        "invalid_token"
                    )

        except requests.RequestException as exc:

            with trace_span(
                "auth.verification.error",
                {
                    "auth.operation": "token_verification",
                    "error.type": type(exc).__name__,
                }
            ) as span:
                span.set_status(
                    __import__(
                        "opentelemetry.trace",
                        fromlist=["Status", "StatusCode"]
                    ).Status(
                        __import__(
                            "opentelemetry.trace",
                            fromlist=["StatusCode"]
                        ).StatusCode.ERROR
                    )
                )

            return JSONResponse(
                {"detail": "Auth service unreachable"},
                status_code=503
            )

        # --------------------------------------------------
        # 3. Handle unauthorized response
        # --------------------------------------------------

        if resp.status_code != 200:

            try:
                payload = resp.json()
                print(payload)

                detail = (
                    payload.get("detail")
                    or payload.get("message")
                    or "Unauthorized"
                ) if isinstance(payload, dict) else "Unauthorized"

            except ValueError:
                detail = "Unauthorized"

            return JSONResponse(
                {"detail": detail},
                status_code=401
            )

        # --------------------------------------------------
        # 4. Attach authenticated user information
        # --------------------------------------------------

        with trace_span(
            "auth.attach_user",
            {
                "auth.operation": "attach_user"
            }
        ):

            try:
                payload = resp.json()

                user_info = (
                    payload.get("user")
                    if isinstance(payload, dict)
                    else None
                )

                if user_info:
                    request.state.user = user_info
                else:
                    request.state.token = token

            except ValueError:
                request.state.token = token

        # --------------------------------------------------
        # 5. Continue request processing
        # --------------------------------------------------

        with trace_span(
            "auth.request.continue",
            {
                "auth.operation": "continue_request"
            }
        ):
            response = await call_next(request)

        return response
