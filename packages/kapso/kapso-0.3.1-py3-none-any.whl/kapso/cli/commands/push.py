"""
Implementation of the global push command for the Kapso CLI.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console

# Push command is registered directly in main.py, no typer app needed
console = Console()


@dataclass
class LocalResource:
    """Represents a local resource to potentially push."""
    name: str
    path: Path
    resource_type: str  # 'agent', 'flow', 'function'
    resource_id: Optional[str] = None  # From metadata
    has_changes: bool = True


@dataclass
class PushChanges:
    """Container for categorized changes."""
    new_agents: List[LocalResource]
    update_agents: List[LocalResource]
    new_flows: List[LocalResource]
    update_flows: List[LocalResource]
    functions: List[LocalResource]
    
    @property
    def total_count(self) -> int:
        return (len(self.new_agents) + len(self.update_agents) + 
                len(self.new_flows) + len(self.update_flows) + 
                len(self.functions))
    
    @property
    def is_empty(self) -> bool:
        return self.total_count == 0


@dataclass
class PushResult:
    """Result of pushing a single resource."""
    resource: LocalResource
    success: bool
    error_message: Optional[str] = None
    new_id: Optional[str] = None  # For new resources


def collect_local_agents(agents_dir: Path) -> List[LocalResource]:
    """Collect all local agents with their metadata."""
    from kapso.cli.utils.metadata import read_metadata
    
    agents = []
    
    if not agents_dir.exists():
        return agents
    
    for agent_path in agents_dir.iterdir():
        if not agent_path.is_dir():
            continue
            
        # Check if agent.py exists
        agent_file = agent_path / "agent.py"
        if not agent_file.exists():
            continue
            
        # Read metadata to get agent_id
        metadata = read_metadata(agent_path)
        agent_id = metadata.get('agent_id') if metadata else None
        
        agent = LocalResource(
            name=agent_path.name,
            path=agent_path,
            resource_type="agent",
            resource_id=agent_id
        )
        agents.append(agent)
    
    return agents


def collect_local_flows(flows_dir: Path) -> List[LocalResource]:
    """Collect all local flows with their metadata."""
    from kapso.cli.utils.metadata import read_metadata
    
    flows = []
    
    if not flows_dir.exists():
        return flows
    
    for flow_path in flows_dir.iterdir():
        if not flow_path.is_dir():
            continue
            
        # Check if flow.py exists
        flow_file = flow_path / "flow.py"
        if not flow_file.exists():
            continue
            
        # Read metadata to get flow_id
        metadata = read_metadata(flow_path)
        flow_id = metadata.get('flow_id') if metadata else None
        
        flow = LocalResource(
            name=flow_path.name,
            path=flow_path,
            resource_type="flow",
            resource_id=flow_id
        )
        flows.append(flow)
    
    return flows


def collect_local_functions(functions_dir: Path) -> List[LocalResource]:
    """Collect all local functions."""
    functions = []
    
    if not functions_dir.exists():
        return functions
    
    for function_file in functions_dir.iterdir():
        if not function_file.is_file():
            continue
            
        # Only include .js files
        if function_file.suffix != '.js':
            continue
            
        function = LocalResource(
            name=function_file.stem,  # filename without extension
            path=function_file,
            resource_type="function",
            resource_id=None  # Functions don't have persistent IDs
        )
        functions.append(function)
    
    return functions


def categorize_changes(
    local_agents: List[LocalResource],
    local_flows: List[LocalResource],
    local_functions: List[LocalResource]
) -> PushChanges:
    """Categorize resources into new and update lists."""
    new_agents = []
    update_agents = []
    new_flows = []
    update_flows = []
    
    # Categorize agents
    for agent in local_agents:
        if agent.resource_id is None:
            new_agents.append(agent)
        else:
            update_agents.append(agent)
    
    # Categorize flows
    for flow in local_flows:
        if flow.resource_id is None:
            new_flows.append(flow)
        else:
            update_flows.append(flow)
    
    # Functions are always included as-is (they handle create/update internally)
    return PushChanges(
        new_agents=new_agents,
        update_agents=update_agents,
        new_flows=new_flows,
        update_flows=update_flows,
        functions=local_functions
    )


class PushService:
    """Service class for push operations - easily mockable."""
    
    def __init__(self, api_client, console):
        self.api_client = api_client
        self.console = console
    
    def push_agent(self, agent: LocalResource) -> PushResult:
        """Push a single agent."""
        from kapso.cli.utils.agent import compile_agent_from_directory
        from kapso.cli.utils.metadata import write_metadata, create_agent_metadata, read_metadata
        from datetime import datetime, timezone
        
        try:
            # Compile agent
            agent_data = compile_agent_from_directory(agent.path)
            if not agent_data:
                return PushResult(
                    resource=agent,
                    success=False,
                    error_message="Failed to compile agent"
                )
            
            if agent.resource_id is None:
                # Create new agent
                response = self.api_client.create_agent(agent_data)
                new_id = response['data']['id']
                
                # Update metadata with new agent_id
                metadata = read_metadata(agent.path)
                if metadata:
                    metadata['agent_id'] = new_id
                    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    metadata['updated_at'] = current_time
                else:
                    metadata = create_agent_metadata(
                        name=agent_data.get('name', agent.name.replace('_', ' ').title()),
                        description=agent_data.get('description', ''),
                        agent_id=new_id
                    )
                write_metadata(agent.path, metadata)
                
                return PushResult(resource=agent, success=True, new_id=new_id)
            else:
                # Update existing agent
                response = self.api_client.update_agent(agent.resource_id, agent_data)
                
                # Update metadata timestamps
                metadata = read_metadata(agent.path)
                if metadata:
                    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    metadata['updated_at'] = current_time
                    write_metadata(agent.path, metadata)
                
                return PushResult(resource=agent, success=True)
                
        except Exception as e:
            return PushResult(
                resource=agent,
                success=False,
                error_message=str(e)
            )
    
    def push_flow(self, flow: LocalResource) -> PushResult:
        """Push a single flow."""
        from kapso.cli.utils.flow import compile_flow_from_directory
        from kapso.cli.utils.metadata import write_metadata, create_flow_metadata, read_metadata
        from datetime import datetime, timezone
        
        try:
            # Compile flow
            flow_data, error_message = compile_flow_from_directory(flow.path)
            if not flow_data:
                return PushResult(
                    resource=flow,
                    success=False,
                    error_message=error_message or "Failed to compile flow"
                )
            
            if flow.resource_id is None:
                # Create new flow
                response = self.api_client.create_flow(flow_data)
                new_id = response['data']['id']
                
                # Update metadata with new flow_id
                metadata = read_metadata(flow.path)
                if metadata:
                    metadata['flow_id'] = new_id
                    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    metadata['updated_at'] = current_time
                else:
                    metadata = create_flow_metadata(
                        name=flow_data.get('name', flow.name.replace('_', ' ').title()),
                        description=flow_data.get('description', ''),
                        flow_id=new_id
                    )
                write_metadata(flow.path, metadata)
                
                return PushResult(resource=flow, success=True, new_id=new_id)
            else:
                # Update existing flow
                response = self.api_client.update_flow(flow.resource_id, flow_data)
                
                # Update metadata timestamps
                metadata = read_metadata(flow.path)
                if metadata:
                    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    metadata['updated_at'] = current_time
                    write_metadata(flow.path, metadata)
                
                return PushResult(resource=flow, success=True)
                
        except Exception as e:
            return PushResult(
                resource=flow,
                success=False,
                error_message=str(e)
            )
    
    def push_function(self, function: LocalResource) -> PushResult:
        """Push a single function."""
        try:
            # Read function code
            with open(function.path, 'r') as f:
                code = f.read()
            
            # Functions use generic API calls - they handle create/update internally
            # Get existing functions to check if it exists
            response = self.api_client.get("functions")
            functions = response.get('data', [])
            
            existing_function = None
            for func in functions:
                if func.get('name') == function.name:
                    existing_function = func
                    break
            
            function_data = {
                "name": function.name,
                "code": code,
                "function_type": "cloudflare_worker"  # Default to cloudflare
            }
            
            if existing_function:
                # Update existing function
                response = self.api_client.patch(
                    f"functions/{existing_function['id']}", 
                    {"function": function_data}
                )
                # Deploy the function
                self.api_client.post(f"functions/{existing_function['id']}/deploy", {})
            else:
                # Create new function
                response = self.api_client.post("functions", {"function": function_data})
                function_id = response.get('data', response)['id']
                # Deploy the function
                self.api_client.post(f"functions/{function_id}/deploy", {})
            
            return PushResult(resource=function, success=True)
            
        except Exception as e:
            return PushResult(
                resource=function,
                success=False,
                error_message=str(e)
            )


def push(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be pushed without pushing")
):
    """Push all local changes to Kapso Cloud."""
    from kapso.cli.utils.project_config import get_project_id
    from kapso.cli.services.auth_service import AuthService
    from kapso.cli.services.api_service import ApiManager
    from rich.prompt import Confirm
    
    # Ensure we have a project configured
    project_id = get_project_id()
    if not project_id:
        console.print("[red]Error: No project configured.[/red]")
        console.print("Run 'kapso init' to set up a project or create a kapso.yaml file.")
        raise typer.Exit(1)
    
    # Collect all local resources
    project_root = Path.cwd()
    agents_dir = project_root / "agents"
    flows_dir = project_root / "flows"
    functions_dir = project_root / "functions"
    
    console.print("Analyzing local changes...")
    
    try:
        local_agents = collect_local_agents(agents_dir)
        local_flows = collect_local_flows(flows_dir)
        local_functions = collect_local_functions(functions_dir)
        
        changes = categorize_changes(local_agents, local_flows, local_functions)
        
        if changes.is_empty:
            console.print("No changes to push.")
            return
        
        # Display changes
        if dry_run:
            console.print("\nWould push:")
            _display_changes(changes, dry_run=True)
            console.print(f"\n{changes.total_count} resources would be pushed.")
            return
        
        console.print("\nChanges to push:")
        _display_changes(changes, dry_run=False)
        
        # Confirm unless --yes flag is used
        if not yes:
            if not Confirm.ask(f"Push {changes.total_count} resources?", default=False):
                console.print("Push cancelled.")
                return
        
        # Execute push
        console.print("Pushing changes...")
        
        # Initialize API services
        auth_service = AuthService()
        api_manager = ApiManager(auth_service)
        api_client = api_manager.project(project_id)
        
        push_service = PushService(api_client, console)
        results = _execute_push(push_service, changes)
        
        # Display results
        _display_results(results)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


def _display_changes(changes: PushChanges, dry_run: bool = False):
    """Display the changes that will be pushed."""
    prefix = "  " if dry_run else "  "
    
    for agent in changes.new_agents:
        console.print(f"{prefix}NEW: agents/{agent.name}")
    
    for agent in changes.update_agents:
        console.print(f"{prefix}UPDATE: agents/{agent.name}")
    
    for flow in changes.new_flows:
        console.print(f"{prefix}NEW: flows/{flow.name}")
    
    for flow in changes.update_flows:
        console.print(f"{prefix}UPDATE: flows/{flow.name}")
    
    for function in changes.functions:
        console.print(f"{prefix}PUSH: functions/{function.name}.js")


def _execute_push(push_service: PushService, changes: PushChanges) -> List[PushResult]:
    """Execute the push operation for all changes."""
    results = []
    
    # Push new agents
    for agent in changes.new_agents:
        console.print(f"Pushing agents/{agent.name}... ", end="")
        result = push_service.push_agent(agent)
        results.append(result)
        if result.success:
            console.print("✓")
        else:
            console.print("✗")
    
    # Push agent updates
    for agent in changes.update_agents:
        console.print(f"Pushing agents/{agent.name}... ", end="")
        result = push_service.push_agent(agent)
        results.append(result)
        if result.success:
            console.print("✓")
        else:
            console.print("✗")
    
    # Push new flows
    for flow in changes.new_flows:
        console.print(f"Pushing flows/{flow.name}... ", end="")
        result = push_service.push_flow(flow)
        results.append(result)
        if result.success:
            console.print("✓")
        else:
            console.print("✗")
    
    # Push flow updates
    for flow in changes.update_flows:
        console.print(f"Pushing flows/{flow.name}... ", end="")
        result = push_service.push_flow(flow)
        results.append(result)
        if result.success:
            console.print("✓")
        else:
            console.print("✗")
    
    # Push functions
    for function in changes.functions:
        console.print(f"Pushing functions/{function.name}.js... ", end="")
        result = push_service.push_function(function)
        results.append(result)
        if result.success:
            console.print("✓")
        else:
            console.print("✗")
    
    return results


def _display_results(results: List[PushResult]):
    """Display the final results of the push operation."""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    if successful:
        console.print(f"\nSuccessfully pushed {len(successful)} resources.")
    
    if failed:
        console.print(f"\n[red]Failed to push {len(failed)} resources:[/red]")
        for result in failed:
            console.print(f"  [red]✗ {result.resource.resource_type}s/{result.resource.name}: {result.error_message}[/red]")
        
        # Exit with error if any failures
        raise typer.Exit(1)