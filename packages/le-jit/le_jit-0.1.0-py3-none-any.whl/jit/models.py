"""Data models for the Jira CLI application."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class IssueType(str, Enum):
    """Supported Jira issue types."""
    TASK = "Task"
    BUG = "Bug"
    STORY = "Story"
    EPIC = "Epic"
    SUBTASK = "Subtask"


class SprintState(str, Enum):
    """Sprint states."""
    ACTIVE = "active"
    FUTURE = "future"
    CLOSED = "closed"


@dataclass
class ProjectInfo:
    """Project information."""
    key: str
    name: str


@dataclass
class EpicInfo:
    """Epic information."""
    key: str
    summary: str
    display: str


@dataclass
class BoardInfo:
    """Board information."""
    id: int
    name: str
    type: str
    display: str


@dataclass
class SprintInfo:
    """Sprint information."""
    id: int
    name: str
    state: str
    display: str


@dataclass
class IssueInfo:
    """Issue information."""
    key: str
    summary: str
    status: str
    type: str
    display: str


@dataclass
class JiraCredentials:
    """Jira authentication credentials."""
    base_url: str
    email: str
    token: str


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: Any
    timestamp: float
    type: str


@dataclass
class IssueCreationRequest:
    """Request object for creating a new issue."""
    project: str
    summary: str
    description: str
    issue_type: IssueType = IssueType.TASK
    assignee: Optional[str] = None
    labels: List[str] = None
    epic: Optional[str] = None
    components: List[str] = None
    sprint_id: Optional[int] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.labels is None:
            self.labels = []
        if self.components is None:
            self.components = []


@dataclass
class GitBranchRequest:
    """Request object for creating a Git branch."""
    issue_key: str
    summary: str
    prefix: str = "feature"
    
    @property
    def branch_name(self) -> str:
        """Generate the branch name."""
        normalized_summary = self._normalize_summary()
        return f"{self.prefix}/{self.issue_key}-{normalized_summary}"
    
    def _normalize_summary(self) -> str:
        """Normalize issue summary for use in branch names."""
        import re
        # Convert to lowercase and replace spaces/special chars with hyphens
        normalized = re.sub(r'[^\w\s-]', '', self.summary.lower())
        normalized = re.sub(r'[-\s]+', '-', normalized)
        # Remove leading/trailing hyphens and limit length
        return normalized.strip('-')[:50]
