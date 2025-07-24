#!/usr/bin/env python3
"""
Startup script for the Jira Dashboard Backend API.
Initializes the database and starts the application.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.models.database import init_database
from src.config.settings import settings

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('jira_dashboard.log')
        ]
    )

def initialize_database():
    """Initialize the database with all required tables."""
    try:
        print("Initializing database...")
        init_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {str(e)}")
        return False

def check_environment():
    """Check that all required environment variables are set."""
    required_vars = [
        "JWT_SECRET_KEY",
        "ENCRYPTION_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("✗ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file based on .env.example")
        return False
    
    print("✓ Environment variables configured")
    return True

def main():
    """Main startup function."""
    print("🚀 Starting Jira Dashboard Backend API")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    
    # Setup logging
    setup_logging()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    print("\n✓ All checks passed. Ready to start the API server.")
    print("\nTo start the server, run:")
    print("  uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI Documentation will be available at:")
    print("  http://localhost:8000/docs")

if __name__ == "__main__":
    main()
