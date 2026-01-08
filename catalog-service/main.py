from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from catalog_service.api.api_router_definition import router
from catalog_service.core.middlewares.auth_middleware import AuthMiddleware
from config import settings
app = FastAPI()
origins = [
    "*",
]
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True, # Allow cookies, authorization headers, etc.
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers in cross-origin requests
)

app.include_router(router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
