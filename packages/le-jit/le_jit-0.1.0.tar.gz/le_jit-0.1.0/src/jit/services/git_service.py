"""Git operations service."""

import subprocess
from typing import Optional

from ..models import GitBranchRequest
from ..exceptions import GitError


class GitService:
    """Service for Git operations."""
    
    def __init__(self):
        """Initialize the Git service."""
        pass
    
    def is_git_repository(self) -> bool:
        """Check if current directory is a Git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'], 
                check=True, 
                capture_output=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def is_git_installed(self) -> bool:
        """Check if Git is installed and available."""
        try:
            subprocess.run(
                ['git', '--version'], 
                check=True, 
                capture_output=True
            )
            return True
        except FileNotFoundError:
            return False
    
    def create_branch(self, request: GitBranchRequest) -> bool:
        """Create and checkout a new Git branch."""
        if not self.is_git_installed():
            raise GitError("Git is not installed or not in PATH")
        
        if not self.is_git_repository():
            raise GitError("Not in a Git repository")
        
        branch_name = request.branch_name
        
        try:
            # Create and checkout the new branch
            subprocess.run(
                ['git', 'checkout', '-b', branch_name], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True
            
        except subprocess.CalledProcessError as e:
            if 'already exists' in str(e.stderr):
                # Branch already exists, try to checkout
                return self._checkout_existing_branch(branch_name)
            else:
                raise GitError(f"Failed to create branch: {e.stderr}")
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout an existing branch."""
        if not self.is_git_installed():
            raise GitError("Git is not installed or not in PATH")
        
        if not self.is_git_repository():
            raise GitError("Not in a Git repository")
        
        try:
            subprocess.run(
                ['git', 'checkout', branch_name], 
                check=True, 
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to checkout branch {branch_name}: {e.stderr}")
    
    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current Git branch."""
        if not self.is_git_repository():
            return None
        
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        if not self.is_git_repository():
            return False
        
        try:
            subprocess.run(
                ['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{branch_name}'], 
                check=True, 
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _checkout_existing_branch(self, branch_name: str) -> bool:
        """Checkout an existing branch when creation fails."""
        try:
            subprocess.run(
                ['git', 'checkout', branch_name], 
                check=True, 
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise GitError(f"Could not checkout existing branch {branch_name}: {e.stderr}")
