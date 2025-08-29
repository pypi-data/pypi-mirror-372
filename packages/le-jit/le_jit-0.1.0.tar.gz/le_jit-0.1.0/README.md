# Jit - Lightning-Fast Jira CLI

A blazing-fast command-line interface for creating Jira tasks and seamlessly integrating with your local Git workflow. Built for developers who want to minimize context switching between Jira and their development environment.

## 🚀 Project Intention

**Jit** solves the common developer pain point of slow, repetitive Jira task creation and Git branch management by providing:

- **⚡ Lightning-Fast Task Creation**: Create Jira issues in seconds with intelligent caching and fuzzy search
- **🌿 Seamless Git Integration**: Automatically create properly named Git branches from Jira issues
- **🧠 Smart Workflow**: Remember your preferences, cache frequently used data, and provide context-aware suggestions
- **🎯 Developer-Focused**: Built by developers, for developers who live in the terminal

### The Problem Jit Solves

Before Jit, creating a new task meant:
1. Opening Jira in browser (slow)
2. Navigating through multiple dropdowns and forms
3. Manually copying the issue key
4. Switching to terminal
5. Creating a Git branch with proper naming convention
6. Manually typing the branch name

With Jit, this becomes:
```bash
jit checkout  # One command, complete workflow
```

## 🛠 Installation

### Prerequisites
- Python 3.13+
- Git (for branch creation features)
- Active Jira account with API access

### Install from Source
```bash
git clone <repository-url>
cd jit
poetry install

# Or with pip
pip install -e .
```

## ⚡ Quick Start

### 1. First-Time Setup
```bash
jit config
```
This launches an interactive setup wizard that:
- Guides you to create a Jira API token
- Saves your credentials securely
- Tests the connection

### 2. Create Your First Issue
```bash
# Interactive mode (recommended for first use)
jit

# Or specify details directly
jit --project MYPROJ --summary "Fix login bug" --epic MYPROJ-123
```

### 3. Create Issue + Git Branch in One Command
```bash
jit checkout
```
This will:
- Let you select an existing issue OR create a new one
- Automatically create a Git branch like `feature/MYPROJ-456-fix-login-bug`
- Check out the new branch
- You're ready to code!

## 📖 Command Reference

### `jit` (Default Command)
**Purpose**: Create a new Jira issue

**Usage**:
```bash
# Interactive mode (recommended)
jit

# Command-line mode
jit [OPTIONS]
```

**Options**:
| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--project` | `-p` | Project key | `--project MYPROJ` |
| `--summary` | `-s` | Issue title/summary | `--summary "Fix login bug"` |
| `--description` | `-d` | Issue description | `--description "Users can't login on mobile"` |
| `--issue-type` | | Issue type | `--issue-type Bug` (default: Task) |
| `--assignee` | | Assign to user | `--assignee me` (default: me) |
| `--labels` | | Comma-separated labels | `--labels "frontend,urgent"` |
| `--epic` | | Epic key to link | `--epic MYPROJ-100` |
| `--components` | | Comma-separated components | `--components "API,Frontend"` |
| `--board` | | Board name or ID | `--board "My Team Board"` |
| `--sprint` | | Sprint name, ID, or 'current' | `--sprint current` |
| `--dry-run` | | Preview without creating | `--dry-run` |
| `--open/--no-open` | | Open in browser after creation | `--no-open` |

**Examples**:
```bash
# Quick task creation
jit --project MYPROJ --summary "Update documentation"

# Full issue with epic and sprint
jit -p MYPROJ -s "Implement OAuth" -d "Add OAuth 2.0 support" --epic MYPROJ-50 --sprint current

# Bug report
jit --project MYPROJ --issue-type Bug --summary "Login fails on Safari" --labels "browser-bug,urgent"
```

### `jit checkout`
**Purpose**: Create a Git branch from a Jira issue (with optional issue creation)

**Usage**:
```bash
jit checkout
```

**Interactive Flow**:
1. **Select Project**: Choose from your recent projects or search all available
2. **Select Issue**: 
   - Choose "🆕 Create new issue" to create and branch in one flow
   - Or select an existing issue from the list
3. **Auto-Branch Creation**: Creates branch like `feature/PROJ-123-issue-summary`

**Example Branch Names**:
- `feature/MYPROJ-456-implement-user-authentication`
- `feature/MYPROJ-789-fix-mobile-responsive-layout`
- `feature/MYPROJ-101-add-dark-mode-support`

### `jit config`
**Purpose**: Configure Jira credentials and settings

**Usage**:
```bash
jit config
```

**What it configures**:
- Jira base URL (e.g., `https://mycompany.atlassian.net`)
- Email address
- API token (with guided creation)
- Tests connection and saves securely

### `jit cache`
**Purpose**: Manage application cache for better performance

**Usage**:
```bash
jit cache
```

**Features**:
- View cached data and age
- Clear expired or corrupted cache
- Cache includes: projects, epics, boards, sprints, issues

## 🎯 Usage Patterns

### Daily Development Workflow
```bash
# Start new feature
jit checkout
# → Creates issue + branch, ready to code

# Need a quick bug fix?
jit --project MYPROJ --issue-type Bug --summary "Fix header alignment"
# → Quick issue creation

# Planning session?
jit --project MYPROJ --epic MYPROJ-200 --summary "User profile page"
# → Link to epic for better organization
```

### Team Workflows

**For Product Owners**:
```bash
# Create multiple issues for a feature
jit --project MYPROJ --epic MYPROJ-100 --summary "Design user dashboard"
jit --project MYPROJ --epic MYPROJ-100 --summary "Implement dashboard API"
jit --project MYPROJ --epic MYPROJ-100 --summary "Add dashboard tests"
```

**For Developers**:
```bash
# Pick up work and start coding immediately
jit checkout
# → Browse backlog, select issue, create branch, start coding
```

**For DevOps/Release Management**:
```bash
# Create deployment issues
jit --project MYPROJ --issue-type Task --summary "Deploy v2.1 to staging" --assignee devops-team
```

## 🧠 Smart Features

### Intelligent Caching
- **6-hour TTL**: Cached data stays fresh but reduces API calls
- **Safe Fallback**: Corrupted cache is automatically cleared
- **Selective Caching**: Only caches frequently accessed data

### Context Awareness
- **Remembers Preferences**: Latest project, board selections
- **Fuzzy Search**: Type partial names to find projects/epics quickly
- **Smart Defaults**: Assigns issues to you, suggests recent epics

### Git Integration
- **Branch Naming Convention**: Automatic `feature/ISSUE-KEY-summary` format
- **Collision Handling**: Handles existing branches gracefully
- **Repository Detection**: Only works in Git repositories

## 🔧 Configuration

### Config File Location
`~/.jit.yaml`

### Example Configuration
```yaml
base_url: https://mycompany.atlassian.net
email: developer@mycompany.com
token: ATATT3xFfGF0123...  # Your API token
latest_project: MYPROJ
latest_board:MYPROJ: 42
```

### Cache File
`~/.jit_cache.yaml` - Automatically managed, can be safely deleted

## 🚨 Troubleshooting

### Common Issues

**"Missing Jira credentials"**
```bash
jit config  # Run setup wizard
```

**"Not in a Git repository"**
```bash
cd /path/to/your/git/project
jit checkout
```

**Slow performance / stale data**
```bash
jit cache  # Clear cache to refresh data
```

**Connection issues**
- Verify your Jira URL is correct
- Ensure API token hasn't expired
- Check network connectivity

### Debug Mode
```bash
export JIT_LOG_LEVEL=DEBUG
jit --project MYPROJ --summary "Test issue"
```

## 🏗 Architecture

Built with clean architecture principles:
- **Services Layer**: Jira API, Git operations, configuration, caching
- **UI Layer**: Interactive prompts, fuzzy search, selections  
- **Models**: Type-safe data classes for all entities
- **Error Handling**: Comprehensive exception handling

## 🤝 Contributing

1. Follow existing code patterns
2. Add type hints to all new code
3. Include comprehensive error handling
4. Update documentation for new features
5. Test with real Jira instances

## 📄 License

[Add your license here]

---

**Made with ❤️ for developers who value speed and efficiency**