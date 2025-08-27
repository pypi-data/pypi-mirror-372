import typer
from rich.console import Console
from rich.progress import Progress
import time

from kapso.cli.services.auth_service import AuthService

app = typer.Typer(name="login", help="Authenticate with Kapso Cloud.")
console = Console()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force re-authentication even if already logged in."
    ),
):
    """
    Authenticate with Kapso Cloud.

    This command opens a browser window to authenticate with Kapso Cloud
    and stores the authentication token securely.
    """
    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return

    # Access common options from context
    common_options = ctx.obj
    verbose = common_options.verbose if common_options else False

    auth_service = AuthService()

    if verbose:
        console.print("Verbose mode enabled")

    # Check if already authenticated
    if not force:
        auth_status = auth_service.is_authenticated()
        if auth_status and isinstance(auth_status, dict):
            console.print(f"[green]Already logged in as {auth_status.get('email', 'unknown')}[/green]")
            console.print("Use --force to re-authenticate if needed.")
            return

    # Start authentication flow
    console.print("Starting authentication with Kapso...")

    try:
        # Get authentication URL and code
        auth_data = auth_service.request_auth_token()
        
        # Check the keys in auth_data
        auth_url = auth_data.get("url") or auth_data.get("auth_url")
        auth_code = auth_data.get("code") or auth_data.get("auth_code")
        
        if not auth_url or not auth_code:
            console.print("[red]Error: Missing URL or code in authentication data[/red]")
            return

        # Display URL and code to user
        console.print(f"Authentication URL: [blue]{auth_url}[/blue]")
        console.print("Opening browser for authentication...")

        # Open browser
        auth_service.open_browser(auth_url)

        # Variables for authentication status
        success = False
        token_data = None
        error_message = None

        # Wait for authentication with progress bar
        with Progress() as progress:
            task = progress.add_task("Waiting for authentication...", total=None)
            
            # Poll for token exchange
            try:
                token_data = auth_service.poll_for_token_exchange(auth_code)
                success = bool(token_data and token_data.get("token"))
                
                if success:
                    # Store the token
                    auth_service.store_token(token_data["token"])
            except Exception as e:
                error_message = str(e)
                
            # Complete and remove the task
            progress.update(task, completed=True)
            progress.stop()
        
        # Display results after progress bar is done
        if success:
            console.print("\n[green]Authentication successful![/green]")
            verify_data = auth_service.verify_token()
            console.print(f"Logged in as {verify_data.get('email', 'unknown')}")
        else:
            console.print("\n[red]Authentication failed or timed out.[/red]")
            if error_message:
                console.print(f"Error: {error_message}")
            console.print("Please try again.")

    except Exception as e:
        console.print(f"[red]Error during authentication: {str(e)}[/red]")
        return