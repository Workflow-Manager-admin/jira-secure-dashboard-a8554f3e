"""
Pydantic schemas for project data responses.
Defines data models for Jira project information.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProjectLead(BaseModel):
    """Schema for project lead information."""
    name: str = Field(..., description="Project lead's display name")
    email: str = Field(..., description="Project lead's email address")

class IssueType(BaseModel):
    """Schema for project issue type information."""
    id: str = Field(..., description="Issue type ID")
    name: str = Field(..., description="Issue type name")
    description: str = Field(default="", description="Issue type description")
    icon_url: str = Field(default="", description="Issue type icon URL", alias="iconUrl")

class ProjectInfo(BaseModel):
    """
    Schema for project information response.
    Contains all relevant project data for the dashboard.
    """
    id: str = Field(..., description="Project ID")
    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    description: str = Field(default="", description="Project description")
    project_type_key: str = Field(..., description="Project type (e.g., software, business)", alias="projectTypeKey")
    lead: ProjectLead = Field(..., description="Project lead information")
    avatar_url: str = Field(default="", description="Project avatar URL", alias="avatarUrl")
    url: str = Field(..., description="Project URL")
    issue_types: List[IssueType] = Field(default=[], description="List of issue types in the project", alias="issueTypes")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp", alias="lastUpdated")
    simplified: bool = Field(default=False, description="Whether this is a simplified project")
    
    class Config:
        allow_population_by_field_name = True

class ProjectsResponse(BaseModel):
    """
    Schema for projects list response.
    Returns list of projects with metadata.
    """
    projects: List[ProjectInfo] = Field(..., description="List of user's accessible projects")
    total_count: int = Field(..., description="Total number of projects")
    message: str = Field(default="Projects retrieved successfully", description="Success message")

class ProjectsErrorResponse(BaseModel):
    """
    Schema for projects retrieval error response.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
