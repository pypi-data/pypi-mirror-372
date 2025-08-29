"""Constants for the Jira CLI application."""

from pathlib import Path

# Configuration file paths
CONFIG_FILE_NAME = ".jit.yaml"
CACHE_FILE_NAME = ".jit_cache.yaml"
CONFIG_PATH = Path.home() / CONFIG_FILE_NAME
CACHE_PATH = Path.home() / CACHE_FILE_NAME

# Cache settings
CACHE_TTL_SECONDS = 60 * 60 * 6  # 6 hours cache TTL

# API limits
MAX_RESULTS_DEFAULT = 100
MAX_EPICS = 100
MAX_ISSUES = 100
MAX_BOARDS = 100

# Git settings
DEFAULT_BRANCH_PREFIX = "feature"
MAX_BRANCH_NAME_LENGTH = 50

# Jira field mappings (common custom fields)
COMMON_EPIC_LINK_FIELDS = [
    "customfield_10014",  # Most common epic link field
    "customfield_10006",  # Alternative epic link field
    "customfield_10008",  # Another common variant
]

# UI Messages
MESSAGES = {
    "missing_credentials": "❌ Missing Jira credentials!",
    "config_saved": "✅ Configuration saved to ~/.jit.yaml",
    "cache_cleared": "✅ Cache cleared successfully",
    "issue_created": "✅ Created {issue_key} → {url}",
    "branch_created": "✅ Created and checked out branch: {branch_name}",
    "no_git_repo": "❌ Error: Not in a Git repository",
    "git_not_found": "❌ Error: Git is not installed or not in PATH",
    "no_active_sprints": "⚠️  No active or future sprints found for this board.",
    "no_epics_found": "⚠️  No active epics found in this project.",
    "no_boards_found": "⚠️  No sprint-enabled boards (Scrum boards) found for this project.",
}

# JQL Queries
JQL_QUERIES = {
    "epics_in_project": "project = {project_key} AND issuetype = Epic AND status != Done",
    "issues_in_project": "project = {project_key} AND status NOT IN (Done, Closed, Resolved) ORDER BY updated DESC",
}

# Atlassian URLs
ATLASSIAN_TOKEN_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"

# Selection options
MANUAL_ENTRY_OPTION = "📝 Enter {item} key manually"
CREATE_NEW_OPTION = "🆕 Create new issue"
NONE_OPTION = "🚫 None ({description})"
