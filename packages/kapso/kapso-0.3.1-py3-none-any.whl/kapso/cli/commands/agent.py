"""
Implementation of the agent commands for the Kapso CLI.
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
from kapso.cli.utils.agent import (
    find_agent_directory,
    get_agent_name_from_cwd,
    validate_agent_name,
    compile_agent_from_directory
)
from kapso.cli.utils.metadata import (
    read_metadata,
    write_metadata,
    create_agent_metadata,
    update_metadata_timestamps
)
from datetime import datetime, timezone
from kapso.cli.utils.project_config import get_project_id

app = typer.Typer(name="agent", help="Manage agents")
console = Console()


def ensure_agents_directory() -> Path:
    """
    Ensure agents directory exists in current project.
    
    Returns:
        Path to agents directory.
        
    Raises:
        SystemExit: If agents directory doesn't exist and can't be created.
    """
    agents_dir = Path.cwd() / "agents"
    
    if not agents_dir.exists():
        console.print("[red]Error: No agents/ directory found.[/red]")
        console.print("Run 'kapso init' first to set up a project.")
        raise typer.Exit(1)
    
    return agents_dir


@app.command()
def init(
    name: str = typer.Argument(..., help="Name of the agent to create"),
    template: str = typer.Option("default", "--template", "-t", help="Agent template to use (default, sales, support)")
):
    """
    Create a new agent locally.
    
    Creates agents/<name>/ directory with agent.py and metadata.yaml files.
    """
    # Validate agent name
    if not validate_agent_name(name):
        console.print("[red]Error: Invalid agent name.[/red]")
        console.print("Use letters, numbers, underscores, and hyphens only. Must start with letter or underscore.")
        raise typer.Exit(1)
    
    # Ensure agents directory exists
    agents_dir = ensure_agents_directory()
    
    # Check if agent already exists
    agent_dir = agents_dir / name
    if agent_dir.exists():
        console.print(f"[red]Error: Agent '{name}' already exists at {agent_dir}[/red]")
        raise typer.Exit(1)
    
    try:
        # Create agent directory and files
        project_service = ProjectService()
        project_service.create_agent_directory(Path.cwd(), name, template)
        
        console.print(f"[green]✓ Created agents/{name}/agent.py[/green]")
        console.print(f"[green]✓ Created agents/{name}/metadata.yaml[/green]")
        console.print(f"\nAgent '{name}' created successfully!")
        
        if template != "default":
            console.print(f"Used template: {template}")
            
    except Exception as e:
        console.print(f"[red]Error creating agent: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def pull(
    name: str = typer.Argument(..., help="Name of the agent to pull"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite local changes")
):
    """
    Pull specific agent from cloud.
    
    Fetches agent by name from current project and updates local files.
    """
    # Ensure we have a project configured
    project_id = get_project_id()
    if not project_id:
        console.print("[red]Error: No project configured.[/red]")
        console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
        raise typer.Exit(1)
    
    # Ensure agents directory exists
    agents_dir = ensure_agents_directory()
    
    try:
        # Initialize API services
        auth_service = AuthService()
        api_manager = ApiManager(auth_service)
        api_client = api_manager.project(project_id)
        
        # Find agent by name in the project
        console.print(f"Looking for agent '{name}' in project...")
        agents_response = api_client.list_agents()
        agents = agents_response.get('data', [])
        
        # Find agent by name (case-insensitive matching)
        target_agent = None
        for agent in agents:
            if agent['name'].lower().replace(' ', '_') == name.lower():
                target_agent = agent
                break
        
        if not target_agent:
            console.print(f"[red]Error: Agent '{name}' not found in project.[/red]")
            console.print("Available agents:")
            for agent in agents:
                agent_name = agent['name'].lower().replace(' ', '_')
                console.print(f"  - {agent_name}")
            raise typer.Exit(1)
        
        # Get full agent data with graph
        console.print(f"Fetching agent '{target_agent['name']}'...")
        agent_response = api_client.get_agent_with_graph(target_agent['id'])
        agent_data = agent_response.get('data', {})
        
        # Convert agent name to directory format
        agent_dir_name = name.lower()
        agent_dir = agents_dir / agent_dir_name
        
        # Check if agent already exists locally
        is_update = agent_dir.exists()
        action = "Updated" if is_update else "Pulled"
        
        # Convert agent data to Python code
        from kapso.cli.commands.pull import convert_agent_to_python
        python_code = convert_agent_to_python(agent_data)
        
        # Create/update agent directory
        agent_dir.mkdir(exist_ok=True)
        
        # Write agent.py file
        agent_file = agent_dir / "agent.py"
        with open(agent_file, 'w') as f:
            f.write(python_code)
        
        # Write metadata.yaml file
        metadata = create_agent_metadata(
            name=agent_data.get('name', name.replace('_', ' ').title()),
            description=agent_data.get('description', ''),
            agent_id=agent_data['id']
        )
        write_metadata(agent_dir, metadata)
        
        console.print(f"[green]✓ {action} agent '{name}' from cloud[/green]")
        console.print(f"[green]  - {agent_file}[/green]")
        console.print(f"[green]  - {agent_dir / 'metadata.yaml'}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error pulling agent: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def push(
    name: str = typer.Argument(..., help="Name of the agent to push"),
    force: bool = typer.Option(False, "--force", "-f", help="Force push without confirmation")
):
    """
    Push agent to cloud (create or update).
    
    Compiles agent.py and pushes to Kapso Cloud, creating or updating as needed.
    """
    # Ensure we have a project configured
    project_id = get_project_id()
    if not project_id:
        console.print("[red]Error: No project configured.[/red]")
        console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
        raise typer.Exit(1)
    
    # Ensure agents directory exists
    agents_dir = ensure_agents_directory()
    
    # Find agent directory
    agent_dir = find_agent_directory(name, Path.cwd())
    if not agent_dir:
        console.print(f"[red]Error: Agent '{name}' not found.[/red]")
        console.print("Available agents:")
        for agent_path in agents_dir.iterdir():
            if agent_path.is_dir():
                console.print(f"  - {agent_path.name}")
        raise typer.Exit(1)
    
    # Check if agent.py exists
    agent_file = agent_dir / "agent.py"
    if not agent_file.exists():
        console.print(f"[red]Error: agent.py not found in {agent_dir}[/red]")
        console.print("Create an agent.py file to define your agent.")
        raise typer.Exit(1)
    
    try:
        # Compile agent from directory
        console.print(f"Compiling agent '{name}'...")
        agent_data = compile_agent_from_directory(agent_dir)
        if not agent_data:
            console.print(f"[red]Error: Failed to compile agent '{name}'[/red]")
            console.print("Check your agent.py file for syntax errors.")
            raise typer.Exit(1)
        
        # Read existing metadata to check for agent_id
        metadata = read_metadata(agent_dir)
        existing_agent_id = metadata.get('agent_id') if metadata else None
        
        # Initialize API services
        auth_service = AuthService()
        api_manager = ApiManager(auth_service)
        api_client = api_manager.project(project_id)
        
        if existing_agent_id:
            # Update existing agent
            console.print(f"Updating existing agent (ID: {existing_agent_id})...")
            response = api_client.update_agent(existing_agent_id, agent_data)
            action = "Updated"
        else:
            # Create new agent
            console.print("Creating new agent in cloud...")
            response = api_client.create_agent(agent_data)
            action = "Created new"
            
            # Update metadata with new agent_id
            agent_id = response['data']['id']
            if metadata:
                metadata['agent_id'] = agent_id
                update_metadata_timestamps(agent_dir, 
                    datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
            else:
                # Create new metadata if it doesn't exist
                metadata = create_agent_metadata(
                    name=agent_data.get('name', name.replace('_', ' ').title()),
                    description=agent_data.get('description', ''),
                    agent_id=agent_id
                )
            write_metadata(agent_dir, metadata)
        
        agent_id = response['data']['id']
        console.print(f"[green]✓ {action} agent in cloud[/green]")
        console.print(f"[green]  Agent ID: {agent_id}[/green]")
        console.print(f"[green]  Name: {response['data']['name']}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error pushing agent: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def snapshot(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent name (auto-detected if in agent directory)")
):
    """
    Create a snapshot of an agent and get a test URL.
    
    Compiles agent.py and creates a snapshot for web-based testing.
    """
    # Ensure we have a project configured
    project_id = get_project_id()
    if not project_id:
        console.print("[red]Error: No project configured.[/red]")
        console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
        raise typer.Exit(1)
    
    # Determine agent name
    agent_name = agent
    if not agent_name:
        # Try to detect from current directory
        agent_name = get_agent_name_from_cwd()
        if not agent_name:
            console.print("[red]Error: Could not detect agent from current directory.[/red]")
            console.print("Run this command from inside an agent directory or use --agent flag.")
            raise typer.Exit(1)
    
    # Ensure agents directory exists
    agents_dir = ensure_agents_directory()
    
    # Find agent directory
    agent_dir = find_agent_directory(agent_name, Path.cwd())
    if not agent_dir:
        console.print(f"[red]Error: Agent '{agent_name}' not found.[/red]")
        console.print("Available agents:")
        for agent_path in agents_dir.iterdir():
            if agent_path.is_dir():
                console.print(f"  - {agent_path.name}")
        raise typer.Exit(1)
    
    # Check if agent.py exists
    agent_file = agent_dir / "agent.py"
    if not agent_file.exists():
        console.print(f"[red]Error: agent.py not found in {agent_dir}[/red]")
        console.print("Create an agent.py file to define your agent.")
        raise typer.Exit(1)
    
    try:
        # Read metadata to get agent_id
        metadata = read_metadata(agent_dir)
        if not metadata or not metadata.get('agent_id'):
            console.print(f"[red]Error: No agent_id found in metadata.[/red]")
            console.print(f"Push the agent first with: kapso agent push {agent_name}")
            raise typer.Exit(1)
        
        agent_id = metadata['agent_id']
        
        # Compile agent to get graph structure
        console.print(f"Compiling agent '{agent_name}'...")
        agent_data = compile_agent_from_directory(agent_dir)
        if not agent_data:
            console.print(f"[red]Error: Failed to compile agent '{agent_name}'[/red]")
            console.print("Check your agent.py file for syntax errors.")
            raise typer.Exit(1)
        
        # Extract graph from compiled agent data
        local_graph = agent_data.get('graph')
        
        # Initialize API services
        console.print("Creating agent snapshot...")
        auth_service = AuthService()
        api_manager = ApiManager(auth_service)
        api_client = api_manager.project(project_id)
        
        # Create agent snapshot
        snapshot_response = api_client.create_agent_snapshot(agent_id, local_graph)
        snapshot_id = snapshot_response['data']['id']
        
        # Generate web testing URL
        web_testing_url = f"https://app.kapso.ai/agent_snapshots/{snapshot_id}/canvas"
        
        console.print(f"[green]✓ Created agent snapshot successfully[/green]")
        console.print(f"[green]  Snapshot ID: {snapshot_id}[/green]")
        console.print(f"[green]  Agent: {metadata['name']}[/green]")
        console.print()
        console.print("[cyan]🌐 Test your agent in the web interface:[/cyan]")
        console.print(f"[blue]{web_testing_url}[/blue]")
        console.print()
        console.print("[dim]Click the URL above to open the agent canvas and test your agent interactively.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error creating snapshot: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    remote: bool = typer.Option(False, "--remote", "-r", help="Show remote agents from cloud")
):
    """
    List agents (local and/or remote).
    
    Shows local agents from the agents/ directory and optionally remote agents.
    """
    try:
        # Get local agents
        local_agents = []
        agents_dir = Path.cwd() / "agents"
        
        if agents_dir.exists():
            for agent_path in agents_dir.iterdir():
                if agent_path.is_dir() and (agent_path / "agent.py").exists():
                    metadata = read_metadata(agent_path)
                    if metadata:
                        local_agents.append({
                            'directory': agent_path.name,
                            'name': metadata.get('name', agent_path.name.replace('_', ' ').title()),
                            'description': metadata.get('description', ''),
                            'agent_id': metadata.get('agent_id'),
                            'created_at': metadata.get('created_at'),
                            'updated_at': metadata.get('updated_at')
                        })
        
        # Display local agents
        console.print("[cyan]Local agents:[/cyan]")
        if not local_agents:
            console.print("  [dim]No local agents found[/dim]")
            console.print("  Run 'kapso agent init <name>' to create an agent")
        else:
            for agent in local_agents:
                status = ""
                if agent['agent_id']:
                    status = "[green](pushed)[/green]"
                else:
                    status = "[yellow](local only)[/yellow]"
                
                console.print(f"  • [bold]{agent['directory']}[/bold] - {agent['name']} {status}")
                if agent['description']:
                    console.print(f"    [dim]{agent['description']}[/dim]")
        
        # Get remote agents if requested
        if remote:
            project_id = get_project_id()
            if not project_id:
                console.print("\n[red]Error: No project configured for remote agents.[/red]")
                console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
                raise typer.Exit(1)
            
            console.print("\n[cyan]Remote agents:[/cyan]")
            try:
                # Initialize API services
                auth_service = AuthService()
                api_manager = ApiManager(auth_service)
                api_client = api_manager.project(project_id)
                
                # Fetch remote agents
                response = api_client.list_agents()
                remote_agents = response.get('data', [])
                
                if not remote_agents:
                    console.print("  [dim]No remote agents found[/dim]")
                else:
                    # Create mapping of remote agent IDs to local agents
                    local_agent_ids = {agent['agent_id']: agent for agent in local_agents if agent['agent_id']}
                    
                    for remote_agent in remote_agents:
                        remote_id = remote_agent['id']
                        remote_name = remote_agent['name']
                        remote_desc = remote_agent.get('description', '')
                        
                        # Check if this remote agent exists locally
                        local_match = local_agent_ids.get(remote_id)
                        if local_match:
                            status = f"[green](local: {local_match['directory']})[/green]"
                        else:
                            status = "[blue](remote only)[/blue]"
                        
                        console.print(f"  • [bold]{remote_name}[/bold] {status}")
                        if remote_desc:
                            console.print(f"    [dim]{remote_desc}[/dim]")
                        console.print(f"    [dim]ID: {remote_id}[/dim]")
                        
            except Exception as e:
                console.print(f"  [red]Error fetching remote agents: {str(e)}[/red]")
        
        # Show helpful commands
        console.print("\n[dim]Commands:[/dim]")
        console.print("  [dim]kapso agent init <name>     - Create a new agent[/dim]")
        console.print("  [dim]kapso agent pull <name>     - Pull agent from cloud[/dim]")
        console.print("  [dim]kapso agent push <name>     - Push agent to cloud[/dim]")
        console.print("  [dim]kapso agent snapshot <name> - Create test snapshot[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing agents: {str(e)}[/red]")
        raise typer.Exit(1)