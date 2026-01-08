"""
FastAPI Authentication Service
Simple auth service with dummy database for login functionality
"""

from fastapi import FastAPI, HTTPException, status,  Header, Response

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Annotated
from config import settings

app = FastAPI(title=settings.app_name, version=settings.version)
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True, # Allow cookies, authorization headers, etc.
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers in cross-origin requests
)
# ============================================================================
# Models
# ============================================================================

class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: str
    role: str


class LoginResponse(BaseModel):
    """Login response model"""
    token: str
    user: UserResponse
    expiresIn: int = 3600  # Token expires in 1 hour


# ============================================================================
# Database Operations
# ============================================================================

def load_users_db() -> list:
    """Load users from JSON file"""
    db_path = os.path.join(os.path.dirname(__file__), "users_db.json")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {db_path} not found")
        return []


def find_user_by_email(email: str) -> Optional[dict]:
    """Find user by email in database"""
    users = load_users_db()
    for user in users:
        if user["email"] == email:
            return user
    return None


def generate_token(user_id: str, email: str) -> str:
    """Generate a dummy JWT-like token"""
    # In production, use proper JWT library
    timestamp = datetime.utcnow().isoformat()
    random_string = secrets.token_hex(16)
    token = f"{user_id}|.|{email}|.|{timestamp}|.|{random_string}"
    return token


# ============================================================================
# Routes
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}

@app.get("/authorize")
async def authorize(
    cookie: Annotated[Optional[str], Header(alias="Authorization")],
    request_uri: Annotated[str, Header()],
    request_method: Annotated[str, Header()],
):
    print(request_uri, request_method, cookie)
    parts = cookie.split("|.|")
    if parts[1] == "john@example.com":
        # set headers
        users = load_users_db()
        for user in users:
            if user["id"] == parts[0]:
                user = user
                headers = {
                    "x-user-id": user["id"],
                    "x-username": user["email"],
                    "x-user-role": user["role"],
                    "authorization": cookie
                }
                return Response(
                    content="OK",
                    headers=headers,
                    status_code=200
                )
    return Response(
        status_code=401,
        content="Unathorized"
    )


@app.post("/authorize")
async def authorize(
    cookie: Annotated[Optional[str], Header(alias="Authorization")],
    request_uri: Annotated[str, Header()],
    request_method: Annotated[str, Header()],
):
    print(request_uri, request_method, cookie)
    parts = cookie.split("|.|")
    print(parts)
    if parts[1] == "john@example.com":
        # set headers
        users = load_users_db()
        for user in users:
            if user["id"] == parts[0]:
                user = user
                headers = {
                    "x-user-id": user["id"],
                    "x-username": user["email"],
                    "x-user-role": user["role"],
                    "authorization": cookie
                }
                return Response(
                    content="OK",
                    headers=headers,
                    status_code=200
                )
    return Response(
        status_code=401,
        content="Unathorized"
    )



@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint
    
    Accepts email and password, validates against dummy database,
    and returns token and user information.
    
    Args:
        request: LoginRequest with email and password
        
    Returns:
        LoginResponse with token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    
    # Validate input
    email = request.email.strip().lower()
    password = request.password
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Find user in database
    user = find_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    token = generate_token(user["id"], user["email"])
    
    # Build response
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"]
    )
    
    response = LoginResponse(
        token=token,
        user=user_response,
        expiresIn=3600
    )
    
    return response


@app.post("/logout")
async def logout():
    """
    Logout endpoint
    
    In production, this would invalidate the token.
    For now, it's just a placeholder.
    """
    return {"message": "Logged out successfully"}


@app.post("/verify")
async def verify_token(token: Optional[str] = None):
    """
    Verify token endpoint
    
    Args:
        token: Authorization token to verify
        
    Returns:
        User info if token is valid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required"
        )
    
    # In production, verify the JWT token properly
    # For now, just return a success response
    return {"message": "Token is valid", "token": token}


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """
    Get user by ID
    
    Args:
        user_id: User ID to fetch
        
    Returns:
        User information
    """
    users = load_users_db()
    
    for user in users:
        if user["id"] == user_id:
            return UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                role=user["role"]
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
