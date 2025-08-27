"""
Main entry point for the Kapso CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from kapso.cli.commands.init import app as init_app
from kapso.cli.commands.login import app as login_app
from kapso.cli.commands.logout import app as logout_app
from kapso.cli.commands.compile import app as compile_app
from kapso.cli.commands.deploy import app as deploy_app
from kapso.cli.commands.run import app as run_app
from kapso.cli.commands.test import test_command
from kapso.cli.commands.pull import pull
from kapso.cli.commands.version import app as version_app
from kapso.cli.commands.test_error import app as test_error_app
from kapso.cli.commands.functions import app as functions_app
from kapso.cli.commands.agent import app as agent_app
from kapso.cli.commands.flow import app as flow_app
from kapso.cli.commands.push import push
from kapso.cli.utils.version_check import check_for_update, get_current_version
from kapso.cli.utils.error_tracking import init_error_tracking, capture_exception, set_user_context

# Define version
__version__ = "0.1.0"

# Initialize error tracking
init_error_tracking(__version__)

app = typer.Typer(
    name="kapso",
    help="Command line interface for the Kapso SDK.",
    add_completion=False,
)
console = Console()

class CommonOptions:
    """Common options shared across commands."""
    def __init__(
        self,
        verbose: bool = False,
        config_file: Optional[str] = None,
    ):
        self.verbose = verbose
        self.config_file = config_file or "kapso.yaml"

def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"Kapso CLI Version: {get_current_version()}")
        raise typer.Exit()

@app.callback()
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output."
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file."
    ),
    version: bool = typer.Option(
        None, 
        "--version", 
        callback=version_callback,
        help="Show version and exit."
    ),
):
    """
    Kapso CLI - Command line interface for building, testing, and deploying
    conversational agents with the Kapso SDK.
    """
    ctx.obj = CommonOptions(verbose=verbose, config_file=config_file)
    
    # Check for updates on startup (except for version command)
    if ctx.invoked_subcommand != 'version':
        update_info = check_for_update()
        if update_info:
            console.print(
                f"[yellow]📦 Update available: {update_info['latest']} "
                f"(current: {update_info['current']})[/yellow]\n"
                f"Run [cyan]{update_info['command']}[/cyan] to update.\n"
            )

app.add_typer(init_app, name="init")
app.add_typer(login_app, name="login")
app.add_typer(logout_app, name="logout")
app.add_typer(compile_app, name="compile")
app.add_typer(deploy_app, name="deploy")
app.add_typer(run_app, name="run")
app.command(name="test")(test_command)
app.command(name="pull")(pull)
app.add_typer(version_app, name="version")
app.add_typer(test_error_app, name="test-error", hidden=True)
app.add_typer(functions_app, name="functions")
app.add_typer(agent_app, name="agent")
app.add_typer(flow_app, name="flow")
app.command(name="push")(push)

def main():
    """Entry point for the CLI."""
    try:
        app(prog_name="kapso", obj={})
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
