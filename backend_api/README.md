# Jira Dashboard Backend API

A secure FastAPI backend service for the Jira Dashboard web application. This service handles user authentication with Jira credentials, manages secure sessions, and provides REST API endpoints for retrieving Jira project data.

## Features

- **Secure Authentication**: JWT-based authentication with Jira credentials (email, domain, API token)
- **Session Management**: Secure session handling with encrypted API token storage
- **Jira Integration**: Direct integration with Jira REST API for project data retrieval
- **Input Validation**: Comprehensive input validation and sanitization using Pydantic
- **Error Handling**: Robust error handling with detailed logging and user-friendly messages
- **Security Best Practices**: Encrypted API tokens, secure password hashing, CORS configuration
- **Database Integration**: SQLAlchemy-based database for session management
- **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger documentation

## Prerequisites

- Python 3.8+
- SQLite (default) or PostgreSQL/MySQL for production
- Jira instance with API access
- Valid Jira API tokens for users

## Installation

1. **Clone and navigate to the backend directory:**
   ```bash
   cd jira-secure-dashboard-a8554f3e/backend_api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database:**
   ```bash
   python -c "from src.models.database import init_database; init_database()"
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Encryption Configuration  
ENCRYPTION_KEY=your-encryption-key-for-api-tokens

# Database Configuration
DATABASE_URL=sqlite:///./jira_dashboard.db

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# Optional Configuration
LOG_LEVEL=INFO
SESSION_TIMEOUT_HOURS=24
API_TIMEOUT_SECONDS=30
```

### Security Configuration

- **JWT_SECRET_KEY**: Used for signing JWT tokens. Use a strong, random key in production.
- **ENCRYPTION_KEY**: Used for encrypting Jira API tokens before database storage.
- **ALLOWED_ORIGINS**: Configure CORS origins for your frontend domains.

## Running the Application

### Development Mode

```bash
# From the backend_api directory
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using Gunicorn with Uvicorn workers
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Authentication

- **POST /auth/login** - User login with Jira credentials
  - Body: `{"email": "user@example.com", "jira_domain": "company.atlassian.net", "api_token": "your-token"}`
  - Returns: JWT token and user information

- **POST /auth/logout** - User logout (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: Logout confirmation

- **GET /auth/me** - Get current user information (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: User information without sensitive data

### Projects

- **GET /projects/** - Get all accessible Jira projects (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: List of projects with details

- **GET /projects/{project_key}** - Get specific project details (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: Detailed project information

### Health

- **GET /** - Health check endpoint
  - Returns: API status and version information

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Database Schema

### UserSession Table

- `id`: Primary key
- `session_token`: Unique session identifier
- `email`: User's email address
- `jira_domain`: User's Jira domain
- `encrypted_api_token`: Encrypted Jira API token
- `created_at`: Session creation timestamp
- `expires_at`: Session expiration timestamp
- `is_active`: Session status (1=active, 0=inactive)

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Encrypted Storage**: Jira API tokens are encrypted before database storage
3. **Session Management**: Automatic session expiration and cleanup
4. **Input Validation**: Comprehensive request validation using Pydantic
5. **CORS Protection**: Configurable CORS origins
6. **Rate Limiting**: Built-in FastAPI rate limiting capabilities
7. **Secure Headers**: Security headers for production deployment

## Error Handling

The API provides consistent error responses:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": "Additional error details (optional)"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (access denied)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error
- `502`: Bad Gateway (Jira API errors)

## Logging

The application uses Python's built-in logging with the following levels:
- `INFO`: General information about requests and operations
- `WARNING`: Non-critical issues
- `ERROR`: Error conditions that need attention
- `DEBUG`: Detailed debugging information (development only)

## Development

### Project Structure

```
backend_api/
├── src/
│   ├── api/
│   │   ├── routes/          # API route handlers
│   │   └── main.py          # FastAPI application
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   └── dependencies/        # Dependency injection
├── interfaces/              # OpenAPI specifications
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

### Code Quality

The project follows Python best practices:
- Type hints throughout the codebase
- Comprehensive docstrings for all public functions
- Pydantic models for data validation
- SQLAlchemy for database operations
- Logging for debugging and monitoring

### Testing

Run tests using pytest:

```bash
pytest tests/ -v
```

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .env

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

- Set strong, unique values for `JWT_SECRET_KEY` and `ENCRYPTION_KEY`
- Use a production database (PostgreSQL recommended)
- Configure appropriate `ALLOWED_ORIGINS`
- Enable HTTPS and set security headers
- Set `LOG_LEVEL=WARNING` or `LOG_LEVEL=ERROR` for production

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify Jira domain format (without http/https prefix)
   - Check API token validity
   - Ensure user has appropriate Jira permissions

2. **Database Connection Issues**
   - Check `DATABASE_URL` format
   - Ensure database is initialized: `python -c "from src.models.database import init_database; init_database()"`

3. **CORS Errors**
   - Add frontend domain to `ALLOWED_ORIGINS`
   - Check protocol (http vs https) matching

4. **Token Errors**
   - Verify `JWT_SECRET_KEY` is set and consistent
   - Check token expiration settings

## Support

For issues and questions:
1. Check the logs for detailed error information
2. Verify environment configuration
3. Test Jira connectivity independently
4. Review the API documentation at `/docs`
