"""Main application class for the Jira CLI."""

import typer
from typing import Optional

from .models import IssueCreationRequest, GitBranchRequest, IssueType
from .services import ConfigService, CacheService, JiraService, GitService
from .ui import PromptService, SelectorService
from .constants import MESSAGES
from .exceptions import (
    ConfigurationError, JiraConnectionError, GitError, 
    UserCancelledError, ValidationError
)
from .utils import get_logger


class JitApp:
    """Main application class for Jira CLI."""
    
    def __init__(self):
        """Initialize the application with all services."""
        self.logger = get_logger(__name__)
        
        # Initialize services
        self.config_service = ConfigService()
        self.cache_service = CacheService()
        self.jira_service = JiraService(self.cache_service)
        self.git_service = GitService()
        
        # Initialize UI services
        self.prompt_service = PromptService()
        self.selector_service = SelectorService(self.prompt_service)
    
    def ensure_jira_connection(self) -> None:
        """Ensure Jira client is initialized with valid credentials."""
        credentials = self.config_service.get_jira_credentials()
        
        if not credentials:
            typer.echo(MESSAGES["missing_credentials"], err=True)
            self._setup_credentials()
            credentials = self.config_service.get_jira_credentials()
            
            if not credentials:
                raise ConfigurationError("Failed to configure credentials")
        
        try:
            self.jira_service.initialize_client(credentials)
        except JiraConnectionError as e:
            typer.echo(f"❌ Connection failed: {e}", err=True)
            if self.prompt_service.get_confirmation("Reconfigure credentials?"):
                self._setup_credentials()
                credentials = self.config_service.get_jira_credentials()
                if credentials:
                    self.jira_service.initialize_client(credentials)
            else:
                raise
    
    def create_issue(
        self,
        project: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        issue_type: str = "Task",
        assignee: str = "me",
        labels: str = "",
        epic: Optional[str] = None,
        components: str = "",
        board: Optional[str] = None,
        sprint: Optional[str] = None,
        dry_run: bool = False,
        open_in_browser: bool = True,
    ) -> None:
        """Create a new Jira issue."""
        self.ensure_jira_connection()
        
        # Get or prompt for project
        if not project:
            projects = self.jira_service.get_all_projects()
            latest_project = self.config_service.get_preference("latest_project")
            project = self.selector_service.select_project(projects, latest_project)
            self.config_service.set_preference("latest_project", project)
        
        # Get or prompt for basic issue details
        if not summary:
            summary = self.prompt_service.get_text_input("Summary:")
        if not description:
            description = self.prompt_service.get_text_input("Description:")
        
        # Get or prompt for epic (required)
        if not epic:
            epics = self.jira_service.get_epics_for_project(project)
            if not epics:
                typer.echo(MESSAGES["no_epics_found"], err=True)
                if self.prompt_service.get_confirmation("Enter an epic key manually?"):
                    epic = self.prompt_service.get_text_input("Enter epic key:")
                else:
                    typer.echo("Epic is required for task creation.", err=True)
                    raise typer.Exit(1)
            else:
                epic = self.selector_service.select_epic(epics)
        
        # Handle board and sprint selection
        selected_sprint_id = None
        if not sprint:
            boards = self.jira_service.get_boards_for_project(project)
            if boards:
                latest_board_id = self.config_service.get_preference(f"latest_board:{project}")
                selected_board_id = self.selector_service.select_board(boards, latest_board_id)
                
                if selected_board_id:
                    self.config_service.set_preference(f"latest_board:{project}", selected_board_id)
                    sprints = self.jira_service.get_sprints_for_board(selected_board_id)
                    if sprints:
                        selected_sprint_id = self.selector_service.select_sprint(sprints)
            else:
                typer.echo(MESSAGES["no_boards_found"])
        
        # Create issue request
        request = IssueCreationRequest(
            project=project,
            summary=summary,
            description=description,
            issue_type=IssueType(issue_type),
            assignee=assignee if assignee != "me" else None,
            labels=[x.strip() for x in labels.split(",") if x.strip()] if labels else [],
            epic=epic,
            components=[x.strip() for x in components.split(",") if x.strip()] if components else [],
            sprint_id=selected_sprint_id
        )
        
        if dry_run:
            typer.echo(f"[DRY-RUN] Would create issue: {request}")
            return
        
        # Create the issue
        try:
            issue = self.jira_service.create_issue(request)
            
            # Build URL for the issue
            base_url = self.config_service.get_preference("base_url")
            if base_url:
                url = f"{base_url.rstrip('/')}/browse/{issue.key}"
                typer.echo(MESSAGES["issue_created"].format(issue_key=issue.key, url=url))
                
                if open_in_browser:
                    import webbrowser
                    webbrowser.open(url)
            else:
                typer.echo(f"✅ Created {issue.key}")
                
        except Exception as e:
            typer.echo(f"❌ Failed to create issue: {e}", err=True)
            raise typer.Exit(1)
    
    def git_checkout_from_issue(self) -> None:
        """Create a Git branch from a Jira issue."""
        typer.echo("🌿 Git Checkout from Jira Issue")
        typer.echo("")
        
        self.ensure_jira_connection()
        
        # Select project
        projects = self.jira_service.get_all_projects()
        latest_project = self.config_service.get_preference("latest_project")
        project = self.selector_service.select_project(projects, latest_project)
        self.config_service.set_preference("latest_project", project)
        
        # Select issue or create new one
        issues = self.jira_service.get_issues_for_project(project)
        selected_issue = self.selector_service.select_issue_or_create_new(issues)
        
        if selected_issue is None:
            # Create new issue
            typer.echo("🆕 Creating new issue...")
            self.create_issue(project=project, open_in_browser=False)
            # After creation, get the latest issue (this is a simplification)
            issues = self.jira_service.get_issues_for_project(project)
            if issues:
                selected_issue = issues[0]  # Get the most recent one
        
        if selected_issue:
            # Create Git branch
            try:
                request = GitBranchRequest(
                    issue_key=selected_issue.key,
                    summary=selected_issue.summary
                )
                
                if self.git_service.create_branch(request):
                    typer.echo(MESSAGES["branch_created"].format(branch_name=request.branch_name))
                    
            except GitError as e:
                if "Not in a Git repository" in str(e):
                    typer.echo(MESSAGES["no_git_repo"], err=True)
                elif "Git is not installed" in str(e):
                    typer.echo(MESSAGES["git_not_found"], err=True)
                else:
                    typer.echo(f"❌ Git error: {e}", err=True)
                raise typer.Exit(1)
        else:
            typer.echo("❌ No issue selected", err=True)
            raise typer.Exit(1)
    
    def configure_credentials(self) -> None:
        """Configure Jira credentials interactively."""
        current_credentials = self.config_service.get_jira_credentials()
        credentials = self.prompt_service.collect_jira_credentials(current_credentials)
        self.config_service.save_jira_credentials(credentials)
        typer.echo(MESSAGES["config_saved"])
    
    def manage_cache(self) -> None:
        """Manage application cache."""
        typer.echo("🗂️  Cache Management")
        typer.echo("")
        
        stats = self.cache_service.get_cache_stats()
        
        if stats["total_entries"] == 0:
            typer.echo("No cached data found.")
            return
        
        typer.echo(f"Found {stats['total_entries']} cached items:")
        for entry in stats["entries"]:
            validity = "valid" if entry["is_valid"] else "expired"
            if entry["age_minutes"] >= 0:
                typer.echo(f"  - {entry['key']}: {entry['age_minutes']} minutes old ({entry['data_type']}, {validity})")
            else:
                typer.echo(f"  - {entry['key']}: invalid cache entry")
        
        typer.echo("")
        if self.prompt_service.get_confirmation("Clear all cached data?"):
            self.cache_service.clear_cache()
            typer.echo(MESSAGES["cache_cleared"])
    
    def _setup_credentials(self) -> None:
        """Set up Jira credentials interactively."""
        try:
            credentials = self.prompt_service.collect_jira_credentials()
            self.config_service.save_jira_credentials(credentials)
            typer.echo(MESSAGES["config_saved"])
        except UserCancelledError:
            typer.echo("❌ Configuration cancelled by user", err=True)
            raise typer.Exit(1)
