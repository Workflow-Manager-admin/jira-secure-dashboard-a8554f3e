"""
Projects API routes for retrieving Jira project data.
Handles fetching and formatting project information for authenticated users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from ...schemas.projects import ProjectsResponse, ProjectsErrorResponse
from ...schemas.auth import ErrorResponse
from ...services.jira_service import JiraService
from ...dependencies.auth import get_jira_service, require_authentication

logger = logging.getLogger(__name__)

# Create router with projects tag
router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(require_authentication)],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access forbidden"},
        502: {"model": ProjectsErrorResponse, "description": "Jira API error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

# PUBLIC_INTERFACE
@router.get("/", response_model=ProjectsResponse, summary="Get User Projects")
async def get_projects(
    jira_service: JiraService = Depends(get_jira_service),
    current_user: dict = Depends(require_authentication)
):
    """
    Retrieve all Jira projects accessible to the authenticated user.
    
    This endpoint fetches all projects that the user has access to
    from their Jira instance, including project details, issue types,
    and metadata needed for the dashboard display.
    
    Args:
        jira_service: Configured Jira service instance
        current_user: Current authenticated user information
        
    Returns:
        ProjectsResponse containing list of projects and metadata
        
    Raises:
        HTTPException: For Jira API errors or authentication issues
    """
    try:
        logger.info(f"Fetching projects for user: {current_user['email']}")
        
        # Get projects from Jira API
        projects = jira_service.get_user_projects()
        
        logger.info(f"Retrieved {len(projects)} projects for user: {current_user['email']}")
        
        return ProjectsResponse(
            projects=projects,
            total_count=len(projects),
            message="Projects retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching projects for {current_user['email']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

# PUBLIC_INTERFACE
@router.get("/{project_key}", summary="Get Project Details")
async def get_project_details(
    project_key: str,
    jira_service: JiraService = Depends(get_jira_service),
    current_user: dict = Depends(require_authentication)
):
    """
    Get detailed information for a specific project.
    
    This endpoint retrieves detailed information for a single project,
    including issue types, statuses, and other metadata.
    
    Args:
        project_key: The project key to retrieve details for
        jira_service: Configured Jira service instance
        current_user: Current authenticated user information
        
    Returns:
        Detailed project information
        
    Raises:
        HTTPException: For project not found or access errors
    """
    try:
        logger.info(f"Fetching details for project {project_key} for user: {current_user['email']}")
        
        # Get all projects and find the specific one
        projects = jira_service.get_user_projects()
        project = next((p for p in projects if p["key"] == project_key), None)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_key}' not found or access denied"
            )
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_key} for {current_user['email']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project details for {project_key}"
        )
