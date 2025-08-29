"""User prompt service for collecting input."""

import webbrowser
from typing import Optional, List
from InquirerPy import inquirer

from ..models import JiraCredentials
from ..constants import ATLASSIAN_TOKEN_URL, MESSAGES
from ..exceptions import UserCancelledError


class PromptService:
    """Service for prompting user input."""
    
    def __init__(self):
        """Initialize the prompt service."""
        pass
    
    def get_text_input(self, message: str, default: Optional[str] = None) -> str:
        """Get text input from user."""
        try:
            return inquirer.text(message, default=default or "").execute()
        except KeyboardInterrupt:
            raise UserCancelledError("Operation cancelled by user")
    
    def get_secret_input(self, message: str) -> str:
        """Get secret input from user (hidden)."""
        try:
            return inquirer.secret(message).execute()
        except KeyboardInterrupt:
            raise UserCancelledError("Operation cancelled by user")
    
    def get_confirmation(self, message: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user."""
        try:
            return inquirer.confirm(message, default=default).execute()
        except KeyboardInterrupt:
            raise UserCancelledError("Operation cancelled by user")
    
    def get_fuzzy_selection(
        self, 
        message: str, 
        choices: List[str], 
        default: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> str:
        """Get selection from user using fuzzy search."""
        try:
            return inquirer.fuzzy(
                message,
                choices=choices,
                default=default,
                instruction=instruction or "Use arrows to navigate, type to filter"
            ).execute()
        except KeyboardInterrupt:
            raise UserCancelledError("Operation cancelled by user")
    
    def collect_jira_credentials(
        self, 
        current_credentials: Optional[JiraCredentials] = None
    ) -> JiraCredentials:
        """Collect Jira credentials from user with guided setup."""
        print("🔧 Setting up Jira credentials")
        print("")
        
        if current_credentials:
            print(f"Current configuration:")
            print(f"  Base URL: {current_credentials.base_url}")
            print(f"  Email: {current_credentials.email}")
            print(f"  Token: {'Set' if current_credentials.token else 'Not set'}")
            print("")
            
            if not self.get_confirmation("Update configuration?"):
                return current_credentials
        
        # Get base URL
        base_url = self.get_text_input(
            "Enter your Jira base URL (e.g., https://yourcompany.atlassian.net):",
            default=current_credentials.base_url if current_credentials else None
        )
        
        # Get email
        email = self.get_text_input(
            "Enter your email address:",
            default=current_credentials.email if current_credentials else None
        )
        
        # Get token with guidance
        need_token = (
            not current_credentials or 
            not current_credentials.token or 
            self.get_confirmation("Update API token?")
        )
        
        if need_token:
            self._show_token_creation_guide()
            token = self.get_secret_input("Enter your API token:")
        else:
            token = current_credentials.token
        
        return JiraCredentials(
            base_url=base_url,
            email=email,
            token=token
        )
    
    def collect_issue_details(self) -> tuple[str, str]:
        """Collect basic issue details from user."""
        summary = self.get_text_input("Summary:")
        description = self.get_text_input("Description:")
        return summary, description
    
    def _show_token_creation_guide(self) -> None:
        """Show guidance for creating API token."""
        print("")
        print("🔑 To create an API token:")
        print("1. Open: " + ATLASSIAN_TOKEN_URL)
        print("2. Click 'Create API token'")
        print("3. Give it a name (e.g., 'Jira CLI')")
        print("4. Copy the generated token")
        print("")
        
        if self.get_confirmation("Open token creation page in browser?"):
            webbrowser.open(ATLASSIAN_TOKEN_URL)
        
        print("")
