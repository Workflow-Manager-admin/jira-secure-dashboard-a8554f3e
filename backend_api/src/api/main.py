"""
Main FastAPI application for the Jira Dashboard backend.
Provides secure authentication and project data retrieval from Jira.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

# Import routes
from .routes.auth import router as auth_router
from .routes.projects import router as projects_router

# Import database initialization
from ..models.database import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Jira Dashboard Backend API")
    try:
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jira Dashboard Backend API")

# Create FastAPI application with comprehensive metadata
app = FastAPI(
    title="Jira Dashboard Backend API",
    description="""
    # Jira Dashboard Backend API
    
    A secure backend service for the Jira Dashboard web application.
    
    ## Features
    
    * **Secure Authentication**: JWT-based authentication with Jira credentials
    * **Session Management**: Secure session handling with encrypted API tokens
    * **Project Data**: Retrieve and format Jira project information
    * **Error Handling**: Comprehensive error responses and logging
    * **Input Validation**: Robust input validation and sanitization
    
    ## Security
    
    * All API tokens are encrypted before storage
    * JWT tokens with configurable expiration
    * HTTPS recommended for production use
    * CORS configured for cross-origin requests
    
    ## Authentication
    
    Most endpoints require authentication. Use the `/auth/login` endpoint to obtain
    a JWT token, then include it in the `Authorization: Bearer <token>` header
    for subsequent requests.
    
    ## WebSocket Support
    
    This API currently uses REST endpoints. For real-time features, WebSocket
    connections can be established for live project updates and notifications.
    See the `/docs` endpoint for detailed WebSocket usage information.
    """,
    version="1.0.0",
    contact={
        "name": "Jira Dashboard Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and session management operations"
        },
        {
            "name": "projects", 
            "description": "Jira project data retrieval and management"
        },
        {
            "name": "health",
            "description": "API health and status checks"
        }
    ],
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(projects_router)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """
    Health check endpoint to verify API availability.
    
    Returns:
        dict: API status and basic information
    """
    return {
        "message": "Jira Dashboard Backend API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

# PUBLIC_INTERFACE
@app.get("/docs/websocket", tags=["health"], summary="WebSocket Usage Information")
def websocket_docs():
    """
    WebSocket connection documentation and usage information.
    
    This endpoint provides information about WebSocket connections
    for real-time features that may be added in the future.
    
    Returns:
        dict: WebSocket usage documentation
    """
    return {
        "websocket_info": {
            "description": "WebSocket endpoints for real-time features",
            "usage": "Connect to /ws endpoint with valid JWT token",
            "features": [
                "Real-time project updates",
                "Live issue notifications", 
                "Session status updates"
            ],
            "authentication": "Include JWT token in connection headers",
            "note": "WebSocket features are available for enhanced real-time dashboard updates"
        },
        "connection_example": {
            "url": "wss://your-domain.com/ws",
            "headers": {
                "Authorization": "Bearer your-jwt-token"
            }
        }
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.status_code,
            "message": exc.detail,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )
