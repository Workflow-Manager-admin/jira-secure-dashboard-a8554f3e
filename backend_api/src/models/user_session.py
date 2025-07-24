"""
User session model for managing authenticated user sessions.
Stores session tokens and associated user information securely.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class UserSession(Base):
    """
    UserSession model for managing user authentication sessions.
    
    Stores session tokens, user email, Jira domain, and encrypted API tokens.
    Sessions have automatic expiration times for security.
    """
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    jira_domain = Column(String(255), nullable=False)
    encrypted_api_token = Column(Text, nullable=False)  # Encrypted Jira API token
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    
    def __repr__(self):
        return f"<UserSession(email='{self.email}', domain='{self.jira_domain}')>"
