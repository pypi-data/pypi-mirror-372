"""
Implementation of the flow commands for the Kapso CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from kapso.cli.services.auth_service import AuthService
from kapso.cli.services.api_service import ApiManager
from kapso.cli.services.project import ProjectService
from kapso.cli.utils.flow import (
    find_flow_directory,
    get_flow_name_from_cwd,
    validate_flow_name,
    compile_flow_from_directory,
    convert_flow_to_python
)
from kapso.cli.utils.metadata import (
    read_metadata,
    write_metadata,
    create_flow_metadata,
    update_metadata_timestamps
)
from datetime import datetime, timezone
from kapso.cli.utils.project_config import get_project_id

app = typer.Typer(name="flow", help="Manage flows")
console = Console()


def ensure_flows_directory() -> Path:
    """
    Ensure flows directory exists in current project.
    
    Returns:
        Path to flows directory.
        
    Raises:
        SystemExit: If flows directory doesn't exist and can't be created.
    """
    flows_dir = Path.cwd() / "flows"
    
    if not flows_dir.exists():
        console.print("[red]Error: No flows/ directory found.[/red]")
        console.print("Run 'kapso init' first to set up a project.")
        raise typer.Exit(1)
    
    return flows_dir


@app.command()
def init(
    name: str = typer.Argument(..., help="Name of the flow to create")
):
    """
    Create a new flow locally.
    
    Creates flows/<name>/ directory with flow.py and metadata.yaml files.
    """
    # Validate flow name
    if not validate_flow_name(name):
        console.print("[red]Error: Invalid flow name.[/red]")
        console.print("Use letters, numbers, underscores, and hyphens only. Must start with letter or underscore.")
        raise typer.Exit(1)
    
    # Ensure flows directory exists
    flows_dir = ensure_flows_directory()
    
    # Check if flow already exists
    flow_dir = flows_dir / name
    if flow_dir.exists():
        console.print(f"[red]Error: Flow '{name}' already exists at {flow_dir}[/red]")
        raise typer.Exit(1)
    
    try:
        # Create flow directory and files
        project_service = ProjectService()
        project_service.create_flow_directory(Path.cwd(), name)
        
        console.print(f"[green]✓ Created flows/{name}/flow.py[/green]")
        console.print(f"[green]✓ Created flows/{name}/metadata.yaml[/green]")
        console.print(f"\nFlow '{name}' created successfully!")
            
    except Exception as e:
        console.print(f"[red]Error creating flow: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def pull(
    name: str = typer.Argument(..., help="Name of the flow to pull"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite local changes")
):
    """
    Pull specific flow from cloud.
    
    Fetches flow by name from current project and updates local files.
    """
    # Ensure we have a project configured
    project_id = get_project_id()
    if not project_id:
        console.print("[red]Error: No project configured.[/red]")
        console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
        raise typer.Exit(1)
    
    # Ensure flows directory exists
    flows_dir = ensure_flows_directory()
    
    try:
        # Initialize API services
        auth_service = AuthService()
        api_manager = ApiManager(auth_service)
        api_client = api_manager.project(project_id)
        
        # Find flow by name in the project
        console.print(f"Looking for flow '{name}' in project...")
        flows_response = api_client.list_flows()
        flows = flows_response.get('data', [])
        
        # Find flow by name (case-insensitive matching)
        target_flow = None
        for flow in flows:
            if flow['name'].lower().replace(' ', '_') == name.lower():
                target_flow = flow
                break
        
        if not target_flow:
            console.print(f"[red]Error: Flow '{name}' not found in project.[/red]")
            console.print("Available flows:")
            for flow in flows:
                flow_name = flow['name'].lower().replace(' ', '_')
                console.print(f"  - {flow_name}")
            raise typer.Exit(1)
        
        # Get full flow data with definition
        console.print(f"Fetching flow '{target_flow['name']}'...")
        flow_response = api_client.get_flow_with_definition(target_flow['id'])
        flow_data = flow_response.get('data', {})
        
        # Convert flow name to directory format
        flow_dir_name = name.lower()
        flow_dir = flows_dir / flow_dir_name
        
        # Check if flow already exists locally
        is_update = flow_dir.exists()
        action = "Updated" if is_update else "Pulled"
        
        # Convert flow data to Python code
        python_code = convert_flow_to_python(flow_data)
        
        # Create/update flow directory
        flow_dir.mkdir(exist_ok=True)
        
        # Write flow.py file
        flow_file = flow_dir / "flow.py"
        with open(flow_file, 'w') as f:
            f.write(python_code)
        
        # Write metadata.yaml file
        metadata = create_flow_metadata(
            name=flow_data.get('name', name.replace('_', ' ').title()),
            description=flow_data.get('description', ''),
            flow_id=flow_data['id']
        )
        write_metadata(flow_dir, metadata)
        
        console.print(f"[green]✓ {action} flow '{name}' from cloud[/green]")
        console.print(f"[green]  - {flow_file}[/green]")
        console.print(f"[green]  - {flow_dir / 'metadata.yaml'}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error pulling flow: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def push(
    name: str = typer.Argument(..., help="Name of the flow to push"),
    force: bool = typer.Option(False, "--force", "-f", help="Force push without confirmation")
):
    """
    Push flow to cloud (create or update).
    
    Compiles flow.py and pushes to Kapso Cloud, creating or updating as needed.
    """
    # Ensure we have a project configured
    project_id = get_project_id()
    if not project_id:
        console.print("[red]Error: No project configured.[/red]")
        console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
        raise typer.Exit(1)
    
    # Ensure flows directory exists
    flows_dir = ensure_flows_directory()
    
    # Find flow directory
    flow_dir = find_flow_directory(name, Path.cwd())
    if not flow_dir:
        console.print(f"[red]Error: Flow '{name}' not found.[/red]")
        console.print("Available flows:")
        for flow_path in flows_dir.iterdir():
            if flow_path.is_dir():
                console.print(f"  - {flow_path.name}")
        raise typer.Exit(1)
    
    # Check if flow.py exists
    flow_file = flow_dir / "flow.py"
    if not flow_file.exists():
        console.print(f"[red]Error: flow.py not found in {flow_dir}[/red]")
        console.print("Create a flow.py file to define your flow.")
        raise typer.Exit(1)
    
    try:
        # Compile flow from directory
        console.print(f"Compiling flow '{name}'...")
        flow_data, error_message = compile_flow_from_directory(flow_dir)
        if not flow_data:
            console.print(f"[red]Error: Failed to compile flow '{name}'[/red]")
            if error_message:
                console.print(f"[red]{error_message}[/red]")
            else:
                console.print("Check your flow.py file for syntax errors.")
            raise typer.Exit(1)
        
        # Read existing metadata to check for flow_id
        metadata = read_metadata(flow_dir)
        existing_flow_id = metadata.get('flow_id') if metadata else None
        
        # Initialize API services
        auth_service = AuthService()
        api_manager = ApiManager(auth_service)
        api_client = api_manager.project(project_id)
        
        if existing_flow_id:
            # Update existing flow
            console.print(f"Updating existing flow (ID: {existing_flow_id})...")
            response = api_client.update_flow(existing_flow_id, flow_data)
            action = "Updated"
        else:
            # Create new flow
            console.print("Creating new flow in cloud...")
            response = api_client.create_flow(flow_data)
            action = "Created new"
            
            # Update metadata with new flow_id
            flow_id = response['data']['id']
            if metadata:
                metadata['flow_id'] = flow_id
                update_metadata_timestamps(flow_dir, 
                    datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
            else:
                # Create new metadata if it doesn't exist
                metadata = create_flow_metadata(
                    name=flow_data.get('name', name.replace('_', ' ').title()),
                    description=flow_data.get('description', ''),
                    flow_id=flow_id
                )
            write_metadata(flow_dir, metadata)
        
        flow_id = response['data']['id']
        console.print(f"[green]✓ {action} flow in cloud[/green]")
        console.print(f"[green]  Flow ID: {flow_id}[/green]")
        console.print(f"[green]  Name: {response['data']['name']}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error pushing flow: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    remote: bool = typer.Option(False, "--remote", "-r", help="Show remote flows from cloud")
):
    """
    List flows (local and/or remote).
    
    Shows local flows from the flows/ directory and optionally remote flows.
    """
    try:
        # Get local flows
        local_flows = []
        flows_dir = Path.cwd() / "flows"
        
        if flows_dir.exists():
            for flow_path in flows_dir.iterdir():
                if flow_path.is_dir() and (flow_path / "flow.py").exists():
                    metadata = read_metadata(flow_path)
                    if metadata:
                        local_flows.append({
                            'directory': flow_path.name,
                            'name': metadata.get('name', flow_path.name.replace('_', ' ').title()),
                            'description': metadata.get('description', ''),
                            'flow_id': metadata.get('flow_id'),
                            'created_at': metadata.get('created_at'),
                            'updated_at': metadata.get('updated_at')
                        })
        
        # Display local flows
        console.print("[cyan]Local flows:[/cyan]")
        if not local_flows:
            console.print("  [dim]No local flows found[/dim]")
            console.print("  Run 'kapso flow init <name>' to create a flow")
        else:
            for flow in local_flows:
                status = ""
                if flow['flow_id']:
                    status = "[green](pushed)[/green]"
                else:
                    status = "[yellow](local only)[/yellow]"
                
                console.print(f"  • [bold]{flow['directory']}[/bold] - {flow['name']} {status}")
                if flow['description']:
                    console.print(f"    [dim]{flow['description']}[/dim]")
        
        # Get remote flows if requested
        if remote:
            project_id = get_project_id()
            if not project_id:
                console.print("\n[red]Error: No project configured for remote flows.[/red]")
                console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
                raise typer.Exit(1)
            
            console.print("\n[cyan]Remote flows:[/cyan]")
            try:
                # Initialize API services
                auth_service = AuthService()
                api_manager = ApiManager(auth_service)
                api_client = api_manager.project(project_id)
                
                # Fetch remote flows
                response = api_client.list_flows()
                remote_flows = response.get('data', [])
                
                if not remote_flows:
                    console.print("  [dim]No remote flows found[/dim]")
                else:
                    # Create mapping of remote flow IDs to local flows
                    local_flow_ids = {flow['flow_id']: flow for flow in local_flows if flow['flow_id']}
                    
                    for remote_flow in remote_flows:
                        remote_id = remote_flow['id']
                        remote_name = remote_flow['name']
                        remote_desc = remote_flow.get('description', '')
                        
                        # Check if this remote flow exists locally
                        local_match = local_flow_ids.get(remote_id)
                        if local_match:
                            status = f"[green](local: {local_match['directory']})[/green]"
                        else:
                            status = "[blue](remote only)[/blue]"
                        
                        console.print(f"  • [bold]{remote_name}[/bold] {status}")
                        if remote_desc:
                            console.print(f"    [dim]{remote_desc}[/dim]")
                        console.print(f"    [dim]ID: {remote_id}[/dim]")
                        
            except Exception as e:
                console.print(f"  [red]Error fetching remote flows: {str(e)}[/red]")
        
        # Show helpful commands
        console.print("\n[dim]Commands:[/dim]")
        console.print("  [dim]kapso flow init <name>  - Create a new flow[/dim]")
        console.print("  [dim]kapso flow pull <name>  - Pull flow from cloud[/dim]")
        console.print("  [dim]kapso flow push <name>  - Push flow to cloud[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing flows: {str(e)}[/red]")
        raise typer.Exit(1)