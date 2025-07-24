"""
Application configuration settings.
Manages environment variables and application configuration.
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Provides type-safe configuration management.
    """
    
    # Application settings
    app_name: str = Field(default="Jira Dashboard Backend API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Encryption Configuration
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./jira_dashboard.db", env="DATABASE_URL")
    
    # CORS Configuration
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    
    # Session Configuration
    session_timeout_hours: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    max_sessions_per_user: int = Field(default=5, env="MAX_SESSIONS_PER_USER")
    
    # API Configuration
    api_timeout_seconds: int = Field(default=30, env="API_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Security Configuration
    secure_cookies: bool = Field(default=True, env="SECURE_COOKIES")
    https_only: bool = Field(default=False, env="HTTPS_ONLY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins

# Global settings instance
settings = Settings()
