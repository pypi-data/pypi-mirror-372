"""Jira CLI - Create and manage Jira issues from the command line."""

import typer
from typing import Optional

from .app import JitApp
from .exceptions import ConfigurationError, JiraConnectionError, GitError, UserCancelledError

# Initialize the Typer app
app = typer.Typer(add_completion=False)

# Initialize the main application
jit_app = JitApp()


@app.callback(invoke_without_command=True)
def create(
    ctx: typer.Context,
    project: str = typer.Option(None, "--project", "-p", help="Project key"),
    summary: str = typer.Option(None, "--summary", "-s", help="Issue summary"),
    description: str = typer.Option(None, "--description", "-d", help="Issue description"),
    issue_type: str = typer.Option("Task", "--issue-type", help="Issue type"),
    assignee: str = typer.Option("me", "--assignee", help="Assignee"),
    labels: str = typer.Option("", "--labels", help="Comma-separated labels"),
    epic: str = typer.Option(None, "--epic", help="Epic key"),
    components: str = typer.Option("", "--components", help="Comma-separated components"),
    board: str = typer.Option(None, "--board", help="Board name or ID"),
    sprint: str = typer.Option(None, "--sprint", help="Sprint name, ID, or 'current'"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be created"),
    open_in_browser: bool = typer.Option(True, "--open/--no-open", help="Open issue in browser"),
):
    """Jira CLI - Create and manage Jira issues from the command line."""
    if ctx.invoked_subcommand is not None:
        return
    
    try:
        jit_app.create_issue(
            project=project,
            summary=summary,
            description=description,
            issue_type=issue_type,
            assignee=assignee,
            labels=labels,
            epic=epic,
            components=components,
            board=board,
            sprint=sprint,
            dry_run=dry_run,
            open_in_browser=open_in_browser,
        )
    except (ConfigurationError, JiraConnectionError, GitError, UserCancelledError) as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)

@app.command("co")
@app.command()
def checkout():
    """Git checkout - Create branch from Jira issue."""
    try:
        jit_app.git_checkout_from_issue()
    except (ConfigurationError, JiraConnectionError, GitError, UserCancelledError) as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def config():
    """Configure Jira credentials."""
    try:
        jit_app.configure_credentials()
    except (ConfigurationError, UserCancelledError) as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def cache():
    """Manage cache - clear cached data to force refresh."""
    try:
        jit_app.manage_cache()
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)

