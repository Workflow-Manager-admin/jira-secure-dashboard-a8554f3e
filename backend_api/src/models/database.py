"""
Database configuration and session management for the Jira Dashboard backend.
Handles SQLAlchemy setup and database connection management.
"""
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for all database models
Base = declarative_base()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jira_dashboard.db")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata for database operations
metadata = MetaData()

def get_database():
    """
    Dependency function to get database session.
    This function creates a database session that is automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize the database by creating all tables.
    This function should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
