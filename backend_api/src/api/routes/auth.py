"""
Authentication API routes for login, logout, and session management.
Handles user authentication with Jira credentials and JWT token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import logging

from ...models.database import get_database
from ...models.user_session import UserSession
from ...schemas.auth import LoginRequest, LoginResponse, ErrorResponse, LogoutResponse
from ...services.jira_service import JiraService
from ...utils.auth import create_access_token, encrypt_api_token, generate_session_token
from ...dependencies.auth import require_authentication

logger = logging.getLogger(__name__)

# Create router with authentication tag
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication failed"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

# PUBLIC_INTERFACE
@router.post("/login", response_model=LoginResponse, summary="User Login")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_database)
):
    """
    Authenticate user with Jira credentials and create session.
    
    This endpoint validates user credentials against Jira API,
    creates a secure session, and returns a JWT token for subsequent requests.
    
    Args:
        login_data: User login credentials (email, domain, API token)
        db: Database session
        
    Returns:
        LoginResponse with JWT token and user information
        
    Raises:
        HTTPException: For authentication failures or validation errors
    """
    try:
        # Create Jira service to validate credentials
        jira_service = JiraService(
            jira_domain=login_data.jira_domain,
            email=login_data.email,
            api_token=login_data.api_token
        )
        
        # Validate credentials with Jira API
        if not jira_service.validate_credentials():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Jira credentials"
            )
        
        # Generate session token and encrypt API token
        session_token = generate_session_token()
        encrypted_api_token = encrypt_api_token(login_data.api_token)
        
        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24 hour session
        
        # Deactivate any existing sessions for this user
        existing_sessions = db.query(UserSession).filter(
            UserSession.email == login_data.email,
            UserSession.jira_domain == login_data.jira_domain,
            UserSession.is_active == 1
        ).all()
        
        for session in existing_sessions:
            session.is_active = 0
        
        # Create new user session
        user_session = UserSession(
            session_token=session_token,
            email=login_data.email,
            jira_domain=login_data.jira_domain,
            encrypted_api_token=encrypted_api_token,
            expires_at=expires_at,
            is_active=1
        )
        
        db.add(user_session)
        db.commit()
        db.refresh(user_session)
        
        # Create JWT token
        token_data = {
            "session_token": session_token,
            "email": login_data.email,
            "jira_domain": login_data.jira_domain
        }
        
        access_token = create_access_token(data=token_data)
        
        logger.info(f"Successful login for user: {login_data.email}")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_email=login_data.email,
            jira_domain=login_data.jira_domain,
            expires_in=86400,  # 24 hours in seconds
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

# PUBLIC_INTERFACE
@router.post("/logout", response_model=LogoutResponse, summary="User Logout")
async def logout(
    current_user: dict = Depends(require_authentication),
    db: Session = Depends(get_database)
):
    """
    Logout user and invalidate session.
    
    This endpoint invalidates the current user session,
    making the JWT token unusable for future requests.
    
    Args:
        current_user: Current authenticated user information
        db: Database session
        
    Returns:
        LogoutResponse confirming successful logout
    """
    try:
        # Find and deactivate user session
        user_session = db.query(UserSession).filter(
            UserSession.session_token == current_user["session_token"],
            UserSession.is_active == 1
        ).first()
        
        if user_session:
            user_session.is_active = 0
            db.commit()
            logger.info(f"User logged out: {current_user['email']}")
        
        return LogoutResponse(message="Logout successful")
        
    except Exception as e:
        logger.error(f"Logout error for {current_user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )

# PUBLIC_INTERFACE
@router.get("/me", summary="Get Current User")
async def get_current_user_info(
    current_user: dict = Depends(require_authentication)
):
    """
    Get current authenticated user information.
    
    Returns information about the currently authenticated user
    without sensitive data like API tokens.
    
    Args:
        current_user: Current authenticated user information
        
    Returns:
        User information (email, domain)
    """
    return {
        "email": current_user["email"],
        "jira_domain": current_user["jira_domain"],
        "authenticated": True
    }
