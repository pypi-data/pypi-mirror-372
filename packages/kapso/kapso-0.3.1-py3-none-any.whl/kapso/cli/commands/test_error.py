"""
Hidden test command to verify Sentry integration.
"""

import typer
from rich.console import Console

from kapso.cli.utils.error_tracking import capture_exception

app = typer.Typer(hidden=True)
console = Console()


@app.command()
def error():
    """Trigger a test error for Sentry verification."""
    console.print("[yellow]Triggering test error for Sentry...[/yellow]")
    
    try:
        # This will cause an error
        data = {"key": "value"}
        result = data["missing_key"]
    except KeyError as e:
        console.print("[red]Error triggered successfully![/red]")
        capture_exception(e, {
            "command": "test-error",
            "purpose": "sentry_verification"
        })
        console.print("\n✅ Error sent to Sentry. Check your dashboard.")
        console.print("Look for KeyError in 'cli-production' or 'cli-development' environment.")
        return
    
    console.print("[red]Error: Test failed to trigger[/red]")