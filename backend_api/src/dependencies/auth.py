"""
Authentication dependencies for route protection.
Provides dependency injection for authentication validation.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from ..models.database import get_database
from ..models.user_session import UserSession
from ..utils.auth import verify_token, decrypt_api_token
from ..services.jira_service import JiraService

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        Dictionary containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials)
        session_token = payload.get("session_token")
        
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user session from database
        user_session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == 1
        ).first()
        
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session is expired
        from datetime import datetime, timezone
        if user_session.expires_at < datetime.now(timezone.utc):
            # Mark session as inactive
            user_session.is_active = 0
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "email": user_session.email,
            "jira_domain": user_session.jira_domain,
            "session_token": user_session.session_token,
            "encrypted_api_token": user_session.encrypted_api_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_jira_service(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> JiraService:
    """
    Dependency to get Jira service instance for the current user.
    
    Args:
        current_user: Current authenticated user information
        
    Returns:
        Configured JiraService instance
        
    Raises:
        HTTPException: If Jira service cannot be created
    """
    try:
        # Decrypt API token
        api_token = decrypt_api_token(current_user["encrypted_api_token"])
        
        # Create Jira service instance
        jira_service = JiraService(
            jira_domain=current_user["jira_domain"],
            email=current_user["email"],
            api_token=api_token
        )
        
        return jira_service
        
    except Exception as e:
        logger.error(f"Failed to create Jira service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize Jira service"
        )

def require_authentication(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Simple authentication requirement dependency.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user
