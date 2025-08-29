"""Jira API service."""

import os
from typing import List, Optional, Dict, Any
from jira import JIRA

from ..models import (
    JiraCredentials, ProjectInfo, EpicInfo, BoardInfo, 
    SprintInfo, IssueInfo, IssueCreationRequest
)
from ..constants import (
    MAX_RESULTS_DEFAULT, COMMON_EPIC_LINK_FIELDS, 
    JQL_QUERIES, MAX_EPICS, MAX_ISSUES, MAX_BOARDS
)
from ..exceptions import JiraConnectionError, ValidationError
from .cache_service import CacheService


class JiraService:
    """Service for interacting with Jira API."""
    
    def __init__(self, cache_service: CacheService):
        """Initialize the Jira service."""
        self.cache_service = cache_service
        self._client: Optional[JIRA] = None
    
    def initialize_client(self, credentials: JiraCredentials) -> None:
        """Initialize the Jira client with credentials."""
        try:
            # Check for environment variable override
            base_url = os.environ.get("JIRA_BASE_URL") or credentials.base_url
            
            self._client = JIRA(
                server=base_url,
                basic_auth=(credentials.email, credentials.token)
            )
        except Exception as e:
            raise JiraConnectionError(f"Failed to connect to Jira: {e}")
    
    @property
    def client(self) -> JIRA:
        """Get the Jira client instance."""
        if self._client is None:
            raise JiraConnectionError("Jira client not initialized")
        return self._client
    
    def get_all_projects(self) -> List[ProjectInfo]:
        """Get all projects with caching."""
        cache_key = self.cache_service.get_cache_key("projects")
        
        # Try to get from cache first
        cached_projects = self.cache_service.get_cached_data_safe(cache_key)
        if cached_projects is not None:
            return [ProjectInfo(**project) for project in cached_projects]
        
        # Fetch from API if not in cache
        try:
            projects = self.client.projects()
            project_data = [
                ProjectInfo(key=project.key, name=project.name)
                for project in projects
            ]
            
            # Cache the result as dictionaries
            cache_data = [{"key": p.key, "name": p.name} for p in project_data]
            self.cache_service.set_cached_data(cache_key, cache_data)
            
            return project_data
        except Exception as e:
            raise JiraConnectionError(f"Could not fetch projects: {e}")
    
    def get_epics_for_project(self, project_key: str) -> List[EpicInfo]:
        """Get epics for a specific project with caching."""
        cache_key = self.cache_service.get_cache_key("epics", project_key)
        
        # Try to get from cache first
        cached_epics = self.cache_service.get_cached_data_safe(cache_key)
        if cached_epics is not None:
            return [EpicInfo(**epic) for epic in cached_epics]
        
        # Fetch from API if not in cache
        jql = JQL_QUERIES["epics_in_project"].format(project_key=project_key)
        try:
            issues = self.client.search_issues(jql, maxResults=MAX_EPICS)
            epic_data = [
                EpicInfo(
                    key=issue.key,
                    summary=issue.fields.summary,
                    display=f"{issue.key} - {issue.fields.summary}"
                )
                for issue in issues
            ]
            
            # Cache the result as dictionaries
            cache_data = [
                {"key": e.key, "summary": e.summary, "display": e.display}
                for e in epic_data
            ]
            self.cache_service.set_cached_data(cache_key, cache_data)
            
            return epic_data
        except Exception as e:
            raise JiraConnectionError(f"Could not fetch epics: {e}")
    
    def get_boards_for_project(self, project_key: str) -> List[BoardInfo]:
        """Get all boards for a specific project with caching."""
        cache_key = self.cache_service.get_cache_key("boards", project_key)
        
        # Try to get from cache first
        cached_boards = self.cache_service.get_cached_data_safe(cache_key)
        if cached_boards is not None:
            return [BoardInfo(**board) for board in cached_boards]
        
        # Fetch from API if not in cache
        project_boards = []
        try:
            boards = self.client.boards(maxResults=MAX_BOARDS, projectKeyOrID=project_key)
            
            for board in boards:
                try:
                    # Only include boards that support sprints (Scrum boards)
                    if hasattr(board, 'type') and board.type.lower() != 'scrum':
                        continue
                    
                    # Check if board belongs to this project
                    if self._board_belongs_to_project(board, project_key):
                        board_type = getattr(board, 'type', 'unknown')
                        project_boards.append(BoardInfo(
                            id=board.id,
                            name=board.name,
                            type=board_type,
                            display=f"{board.name} (ID: {board.id}, {board_type})"
                        ))
                except:
                    continue
            
            # Cache the result as dictionaries
            cache_data = [
                {
                    "id": b.id, "name": b.name, 
                    "type": b.type, "display": b.display
                }
                for b in project_boards
            ]
            self.cache_service.set_cached_data(cache_key, cache_data)
            
        except Exception as e:
            raise JiraConnectionError(f"Could not fetch boards: {e}")
        
        return project_boards
    
    def get_sprints_for_board(self, board_id: int) -> List[SprintInfo]:
        """Get active and future sprints for a specific board with caching."""
        cache_key = self.cache_service.get_cache_key("sprints", board_id)
        
        # Try to get from cache first
        cached_sprints = self.cache_service.get_cached_data_safe(cache_key)
        if cached_sprints is not None:
            return [SprintInfo(**sprint) for sprint in cached_sprints]
        
        # Fetch from API if not in cache
        try:
            sprints = self.client.sprints(board_id, state="active,future")
            sprint_data = [
                SprintInfo(
                    id=sprint.id,
                    name=sprint.name,
                    state=sprint.state,
                    display=f"{sprint.name} ({sprint.state})"
                )
                for sprint in sprints
            ]
            
            # Cache the result as dictionaries
            cache_data = [
                {
                    "id": s.id, "name": s.name,
                    "state": s.state, "display": s.display
                }
                for s in sprint_data
            ]
            self.cache_service.set_cached_data(cache_key, cache_data)
            
            return sprint_data
        except Exception as e:
            raise JiraConnectionError(f"Could not fetch sprints: {e}")
    
    def get_issues_for_project(self, project_key: str) -> List[IssueInfo]:
        """Get all issues for a specific project with caching."""
        cache_key = self.cache_service.get_cache_key("issues", project_key)
        
        # Try to get from cache first
        cached_issues = self.cache_service.get_cached_data_safe(cache_key)
        if cached_issues is not None:
            return [IssueInfo(**issue) for issue in cached_issues]
        
        # Fetch from API if not in cache
        try:
            jql = JQL_QUERIES["issues_in_project"].format(project_key=project_key)
            issues = self.client.search_issues(jql, maxResults=MAX_ISSUES)
            issue_data = [
                IssueInfo(
                    key=issue.key,
                    summary=issue.fields.summary,
                    status=issue.fields.status.name,
                    type=issue.fields.issuetype.name,
                    display=f"{issue.key} - {issue.fields.summary} ({issue.fields.status.name})"
                )
                for issue in issues
            ]
            
            # Cache the result as dictionaries
            cache_data = [
                {
                    "key": i.key, "summary": i.summary,
                    "status": i.status, "type": i.type, "display": i.display
                }
                for i in issue_data
            ]
            self.cache_service.set_cached_data(cache_key, cache_data)
            
            return issue_data
        except Exception as e:
            raise JiraConnectionError(f"Could not fetch issues: {e}")
    
    def create_issue(self, request: IssueCreationRequest) -> Any:
        """Create a new Jira issue."""
        fields = {
            "project": {"key": request.project},
            "summary": request.summary,
            "issuetype": {"name": request.issue_type.value},
            "description": request.description,
        }
        
        # Set assignee
        if request.assignee == "me":
            fields["assignee"] = {"accountId": self.client.current_user()}
        elif request.assignee:
            fields["assignee"] = {"name": request.assignee}
        
        # Set labels
        if request.labels:
            fields["labels"] = request.labels
        
        # Set components
        if request.components:
            fields["components"] = [{"name": comp} for comp in request.components]
        
        # Set epic link
        if request.epic:
            epic_field = self._find_epic_link_field()
            if epic_field:
                fields[epic_field] = request.epic
        
        try:
            issue = self.client.create_issue(fields=fields)
            
            # Add to sprint if specified
            if request.sprint_id:
                self.client.add_issues_to_sprint(request.sprint_id, [issue.key])
            
            return issue
        except Exception as e:
            raise JiraConnectionError(f"Failed to create issue: {e}")
    
    def get_current_user(self) -> str:
        """Get current user account ID."""
        return self.client.current_user()
    
    def get_server_url(self) -> str:
        """Get Jira server URL."""
        return self.client.server_url
    
    def _board_belongs_to_project(self, board: Any, project_key: str) -> bool:
        """Check if board belongs to the specified project."""
        # Check if board belongs to this project
        if hasattr(board, 'location') and hasattr(board.location, 'projectKey'):
            return board.location.projectKey == project_key
        
        # Fallback: check board configuration
        try:
            board_config = self.client.board_config(board.id)
            return (hasattr(board_config, 'project') and 
                   board_config.project.key == project_key)
        except:
            return False
    
    def _find_epic_link_field(self) -> Optional[str]:
        """Find the epic link field dynamically."""
        try:
            for field in self.client.fields():
                if 'epic' in field['name'].lower() and 'link' in field['name'].lower():
                    return field['id']
        except Exception:
            pass
        
        # Fallback to common epic link fields
        return COMMON_EPIC_LINK_FIELDS[0]
