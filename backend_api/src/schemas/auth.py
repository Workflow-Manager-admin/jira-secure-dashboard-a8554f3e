"""
Pydantic schemas for authentication requests and responses.
Defines data models for login, logout, and authentication validation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """
    Schema for user login request.
    Validates Jira credentials including email, domain, and API token.
    """
    email: EmailStr = Field(..., description="User's Jira email address")
    jira_domain: str = Field(..., min_length=3, max_length=255, description="Jira instance domain (e.g., company.atlassian.net)")
    api_token: str = Field(..., min_length=10, max_length=500, description="Jira API token")
    
    @validator('jira_domain')
    def validate_domain(cls, v):
        """Validate and clean domain format."""
        v = v.strip().lower()
        # Remove protocol if present
        if v.startswith(('http://', 'https://')):
            v = v.split('://', 1)[1]
        # Remove trailing slash
        v = v.rstrip('/')
        return v
    
    @validator('api_token')
    def validate_api_token(cls, v):
        """Validate API token format."""
        v = v.strip()
        if not v:
            raise ValueError('API token cannot be empty')
        return v

class LoginResponse(BaseModel):
    """
    Schema for successful login response.
    Returns authentication token and user information.
    """
    access_token: str = Field(..., description="JWT access token for authenticated requests")
    token_type: str = Field(default="bearer", description="Token type")
    user_email: str = Field(..., description="Authenticated user's email")
    jira_domain: str = Field(..., description="User's Jira domain")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    message: str = Field(default="Login successful", description="Success message")

class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    Provides consistent error message format.
    """
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")

class LogoutResponse(BaseModel):
    """
    Schema for logout response.
    Confirms successful session termination.
    """
    message: str = Field(default="Logout successful", description="Logout confirmation message")

class TokenValidationResponse(BaseModel):
    """
    Schema for token validation response.
    Returns user information for valid tokens.
    """
    valid: bool = Field(..., description="Whether the token is valid")
    user_email: Optional[str] = Field(None, description="User email if token is valid")
    jira_domain: Optional[str] = Field(None, description="Jira domain if token is valid")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
