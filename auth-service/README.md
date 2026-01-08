# Auth Service

A simple FastAPI authentication service with dummy database support.

## Features

- ✅ User login with email and password
- ✅ Token generation
- ✅ Token verification
- ✅ User retrieval
- ✅ Dummy JSON database
- ✅ Error handling

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Service

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The service will be available at `http://localhost:8001`

## API Endpoints

### Health Check

```
GET /health
```

### Login

```
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**

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

### Logout

```
POST /logout
```

### Verify Token

```
GET /verify?token=<token>
```

### Get User

```
GET /users/{user_id}
```

## Test Users

The service comes with dummy users in `users_db.json`:

| Email             | Password    | Role  |
| ----------------- | ----------- | ----- |
| john@example.com  | password123 | user  |
| jane@example.com  | password456 | admin |
| admin@example.com | admin123    | admin |

## Architecture

- **main.py** - Main FastAPI application with all endpoints
- **users_db.json** - Dummy user database
- **requirements.txt** - Python dependencies
- **.env.example** - Environment configuration template

## Future Enhancements

- [ ] Implement proper JWT token generation and verification
- [ ] Add password hashing (bcrypt)
- [ ] Implement refresh tokens
- [ ] Add user registration endpoint
- [ ] Add role-based access control (RBAC)
- [ ] Connect to real database (PostgreSQL, MongoDB)
- [ ] Add email verification
- [ ] Add password reset functionality
