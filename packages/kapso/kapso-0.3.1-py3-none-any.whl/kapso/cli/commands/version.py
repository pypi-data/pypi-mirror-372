"""
Implementation of the version command for the Kapso CLI.
"""
import typer
from rich.console import Console

from kapso.cli.utils.version_check import get_current_version, check_for_update

app = typer.Typer(name="version", help="Display version information")
console = Console()


@app.callback(invoke_without_command=True)
def version(
    ctx: typer.Context,
    check: bool = typer.Option(
        False, 
        "--check", 
        "-c",
        help="Check for available updates"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f", 
        help="Force check for updates (ignore cache)"
    )
):
    """Display CLI version and optionally check for updates."""
    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return
        
    current = get_current_version()
    console.print(f"Kapso CLI version: [cyan]{current}[/cyan]")
    
    if check or force:
        console.print("\n[cyan]Checking for updates...[/cyan]")
        update_info = check_for_update(force=force)
        
        if update_info:
            console.print(
                f"\n[yellow]📦 Update available: {update_info['latest']}[/yellow]"
            )
            console.print(f"Run: [cyan]{update_info['command']}[/cyan]")
        else:
            console.print("[green]✅ You're using the latest version![/green]")