"""Custom exceptions for the Jira CLI application."""


class JitError(Exception):
    """Base exception for Jira CLI application."""
    pass


class ConfigurationError(JitError):
    """Raised when configuration is invalid or missing."""
    pass


class JiraConnectionError(JitError):
    """Raised when unable to connect to Jira."""
    pass


class CacheError(JitError):
    """Raised when cache operations fail."""
    pass


class GitError(JitError):
    """Raised when Git operations fail."""
    pass


class UserCancelledError(JitError):
    """Raised when user cancels an operation."""
    pass


class ValidationError(JitError):
    """Raised when input validation fails."""
    pass
