import typer
from rich.console import Console

from kapso.cli.services.auth_service import AuthService

app = typer.Typer(name="logout", help="Log out from Kapso Cloud.")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Log out from Kapso Cloud.
    
    This command clears your authentication tokens.
    """
    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return
        
    common_options = ctx.obj
    verbose = common_options.verbose if common_options else False
    
    auth_service = AuthService()
    
    if verbose:
        console.print("Verbose mode enabled")
    
    auth_status = auth_service.is_authenticated()
    if auth_status and isinstance(auth_status, dict):
        email = auth_status.get("email", "unknown")
        
        try:
            auth_service.revoke_token()
            console.print(f"[green]Successfully logged out.[/green]")
        except Exception as e:
            console.print(f"[red]Error logging out: {str(e)}[/red]")
    else:
        console.print("[yellow]You are not logged in.[/yellow]") 