"""
Jira API service for authentication and project data retrieval.
Handles all interactions with the Jira REST API securely.
"""
import requests
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
import base64
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class JiraService:
    """
    Service class for interacting with Jira REST API.
    Handles authentication and project data retrieval.
    """
    
    def __init__(self, jira_domain: str, email: str, api_token: str):
        """
        Initialize Jira service with user credentials.
        
        Args:
            jira_domain: Jira instance domain (e.g., 'company.atlassian.net')
            email: User's email address
            api_token: User's Jira API token
        """
        self.jira_domain = jira_domain.rstrip('/')
        self.email = email
        self.api_token = api_token
        
        # Ensure domain has proper protocol
        if not self.jira_domain.startswith(('http://', 'https://')):
            self.jira_domain = f"https://{self.jira_domain}"
        
        # Create base API URL
        self.base_url = urljoin(self.jira_domain, '/rest/api/3/')
        
        # Setup authentication headers
        auth_string = f"{self.email}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def validate_credentials(self) -> bool:
        """
        Validate Jira credentials by making a test API call.
        
        Returns:
            True if credentials are valid, False otherwise
            
        Raises:
            HTTPException: If authentication fails or API is unreachable
        """
        try:
            url = urljoin(self.base_url, 'myself')
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Jira credentials. Please check your email, domain, and API token."
                )
            elif response.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. Please check your Jira permissions."
                )
            else:
                logger.error(f"Jira API validation failed with status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to connect to Jira. Please check your domain."
                )
                
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Request to Jira timed out. Please try again."
            )
        except requests.exceptions.ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Cannot connect to Jira. Please check your domain and internet connection."
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Unexpected error during Jira validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unexpected error connecting to Jira."
            )
    
    def get_user_projects(self) -> List[Dict[str, Any]]:
        """
        Retrieve all projects accessible to the authenticated user.
        
        Returns:
            List of project dictionaries with relevant information
            
        Raises:
            HTTPException: If API call fails
        """
        try:
            url = urljoin(self.base_url, 'project')
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                projects_data = response.json()
                return self._format_projects(projects_data)
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired. Please log in again."
                )
            else:
                logger.error(f"Failed to fetch projects with status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to retrieve projects from Jira."
                )
                
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Request to Jira timed out. Please try again."
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching projects: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error retrieving projects from Jira."
            )
    
    def _format_projects(self, projects_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format project data for frontend consumption.
        
        Args:
            projects_data: Raw project data from Jira API
            
        Returns:
            Formatted project data
        """
        formatted_projects = []
        
        for project in projects_data:
            # Get project lead information
            lead_info = project.get('lead', {})
            lead_name = lead_info.get('displayName', 'Unknown')
            lead_email = lead_info.get('emailAddress', '')
            
            # Get avatar URL
            avatar_urls = project.get('avatarUrls', {})
            avatar_url = avatar_urls.get('48x48', avatar_urls.get('32x32', ''))
            
            # Get project type
            project_type = project.get('projectTypeKey', 'unknown')
            
            # Format project data
            formatted_project = {
                'id': project.get('id'),
                'key': project.get('key'),
                'name': project.get('name'),
                'description': project.get('description', ''),
                'projectTypeKey': project_type,
                'lead': {
                    'name': lead_name,
                    'email': lead_email
                },
                'avatarUrl': avatar_url,
                'url': project.get('self', ''),
                'simplified': project.get('simplified', False)
            }
            
            # Try to get additional project details
            try:
                project_details = self._get_project_details(project.get('key'))
                if project_details:
                    formatted_project.update(project_details)
            except Exception as e:
                logger.warning(f"Could not fetch additional details for project {project.get('key')}: {str(e)}")
            
            formatted_projects.append(formatted_project)
        
        return formatted_projects
    
    def _get_project_details(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        Get additional project details including issue types and statuses.
        
        Args:
            project_key: Project key to fetch details for
            
        Returns:
            Additional project details or None if fetch fails
        """
        try:
            # Get project details with issue types
            url = urljoin(self.base_url, f'project/{project_key}')
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                project_data = response.json()
                
                # Extract issue types
                issue_types = []
                for issue_type in project_data.get('issueTypes', []):
                    issue_types.append({
                        'id': issue_type.get('id'),
                        'name': issue_type.get('name'),
                        'description': issue_type.get('description', ''),
                        'iconUrl': issue_type.get('iconUrl', '')
                    })
                
                return {
                    'issueTypes': issue_types,
                    'style': project_data.get('style', {}),
                    'lastUpdated': project_data.get('insight', {}).get('lastIssueUpdateTime')
                }
                
        except Exception as e:
            logger.warning(f"Failed to get project details for {project_key}: {str(e)}")
            
        return None
