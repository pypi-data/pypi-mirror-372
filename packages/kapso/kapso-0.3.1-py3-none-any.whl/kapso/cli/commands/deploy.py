"""
Implementation of the deploy command for the Kapso CLI.
"""

import os
import sys
import time
import yaml
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import typer
from rich.console import Console
from rich.progress import Progress
import inquirer

from kapso.cli.services.auth_service import AuthService
from kapso.cli.services.api_service import ApiService, ApiManager, GenerationLimitError
from kapso.cli.utils.agent import compile_agent
from kapso.cli.utils.project_config import get_project_id, set_project_id, update_env_file

app = typer.Typer(name="deploy", help="Deploy an agent to Kapso Cloud.")
console = Console()

def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Read YAML file and return parsed content.
    
    Args:
        file_path: Path to the YAML file.
        
    Returns:
        Parsed YAML content as a dictionary.
    """
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error reading YAML file: {str(e)}[/red]")
        sys.exit(1)

def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Read JSON file and return parsed content.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        Parsed JSON content as a dictionary.
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error reading JSON file: {str(e)}[/red]")
        sys.exit(1)

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a path.
    
    Args:
        file_path: Path to get extension from.
        
    Returns:
        File extension (lowercase).
    """
    return os.path.splitext(file_path)[1].lower()

def read_data_file(file_path: str) -> Dict[str, Any]:
    """
    Read a data file (YAML or JSON) and return parsed content.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Parsed content as a dictionary.
    """
    extension = get_file_extension(file_path)
    if extension in (".yaml", ".yml"):
        return read_yaml_file(file_path)
    elif extension == ".json":
        return read_json_file(file_path)
    else:
        console.print(f"[red]Unsupported file type: {extension}[/red]")
        sys.exit(1)

def get_files_with_extension(directory: str, extension: str) -> List[str]:
    """
    Get all files with the specified extension in a directory.
    
    Args:
        directory: Directory to search in.
        extension: File extension to filter by.
        
    Returns:
        List of file paths.
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) 
            if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)]

def update_config_file(config_file: str, agent_id: str) -> None:
    """
    Update the config file with the agent ID.
    
    Args:
        config_file: Path to the config file.
        agent_id: Agent ID to add to the config.
    """
    try:
        # Load existing config or create new
        config = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = yaml.safe_load(f) or {}
        
        # Add agent ID
        config["agent_id"] = agent_id
        
        # Write updated config
        with open(config_file, "w") as f:
            yaml.dump(config, f, sort_keys=False)
            
        console.print(f"[green]Updated {config_file} with agent ID: {agent_id}[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not update config file: {str(e)}[/yellow]")

def ensure_project_api_key(project_id: str, auth_service: AuthService, api_manager: ApiManager) -> bool:
    """
    Ensure that we have an API key for the given project, generating one if needed.
    
    Args:
        project_id: ID of the project to ensure API key for.
        auth_service: Authentication service instance.
        api_manager: API manager instance.
        
    Returns:
        True if API key is available, False otherwise.
    """
    # Check if we have an API key for this project
    api_key = auth_service.get_project_api_key(project_id)
    
    # If no API key, generate one
    if not api_key:
        try:
            console.print("[cyan]Generating API key for the project...[/cyan]")
            api_key_result = api_manager.user().generate_project_api_key(project_id)
            
            if api_key_result and api_key_result.get("key"):
                # Store the API key
                api_key = api_key_result["key"]
                auth_service.store_project_api_key(project_id, api_key)
                update_env_file(project_id, api_key)
                console.print("[green]API key generated and stored successfully.[/green]")
                return True
            else:
                console.print("[red]Failed to generate API key.[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error generating API key: {str(e)}[/red]")
            return False
    
    return True

def select_project(api_manager: ApiManager) -> Optional[str]:
    """
    Let the user select a project to deploy to.
    
    Args:
        api_manager: API manager instance.
        
    Returns:
        Selected project ID if successful, None otherwise.
    """
    try:
        console.print("[cyan]Fetching available projects...[/cyan]")
        projects = api_manager.user().list_projects()
        
        if not projects:
            console.print("[yellow]No projects found. Create a project at app.kapso.ai[/yellow]")
            return None
        
        # Let user select a project if multiple
        if len(projects) == 1:
            selected_project = projects[0]
            # Ensure selected_project is a dictionary before using .get()
            if isinstance(selected_project, dict):
                console.print(f"[green]Using project: {selected_project.get('name', 'Unknown Project')}[/green]")
                return selected_project.get('id')
            else:
                # Handle the case where the single project item is not a dict
                console.print("[red]Error: Unexpected project data format.[/red]")
                return None # Or sys.exit(1)
        else:
            choices = []
            for p in projects:
                if isinstance(p, dict): # Check if p is a dictionary
                    project_id = p.get('id')
                    project_name = p.get('name', 'Unnamed Project')
                    if project_id: # Ensure project has an ID to be a valid choice
                        choices.append((f"{project_name} ({project_id})", project_id))
            
            if not choices and projects: # If there were projects but none were valid dicts with IDs
                console.print("[yellow]No valid projects found to select from.[/yellow]")
                return None
            elif not projects: # No projects at all
                 # This case is handled before by "No projects found"
                 pass


            questions = [
                inquirer.List('project_id',
                            message="Select a project to deploy to:",
                            choices=choices),
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                console.print("[yellow]Deployment cancelled.[/yellow]")
                return None
            
            project_id = answers['project_id']
            return project_id
            
    except Exception as e:
        console.print(f"[red]Error fetching projects: {str(e)}[/red]")
        return None

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    agent_file: Optional[str] = typer.Argument(
        None,
        help="Path to the agent file (Python or YAML)."
    ),
    env: str = typer.Option(
        "production",
        "--env",
        "-e",
        help="Environment to deploy to (development, staging, production)."
    ),
    project_id: Optional[str] = typer.Option(
        None,
        "--project-id",
        "-p",
        help="Project ID to deploy to."
    ),
):
    """
    Deploy an agent to Kapso Cloud.
    
    This command compiles the agent if needed and deploys it to Kapso Cloud.
    
    ⚠️  DEPRECATED: Use 'kapso agent push <name>' instead.
    """
    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return
    
    # Show deprecation warning
    console.print("[yellow]⚠️  DEPRECATED: 'kapso deploy' is deprecated.[/yellow]")
    console.print("[yellow]   Use 'kapso agent push <name>' instead for the new workflow.[/yellow]")
    console.print()
    
    # Access common options from context
    common_options = ctx.obj
    verbose = common_options.verbose if common_options else False
    config_file = common_options.config_file if common_options else "kapso.yaml"
    
    if verbose:
        console.print("Verbose mode enabled")
    
    # Check authentication status
    auth_service = AuthService()
    api_manager = ApiManager(auth_service)
    
    # Get project ID from option, config, or prompt
    if not project_id:
        project_id = get_project_id()
    
    # Check if we have an API key for the project (from env var or storage)
    has_project_api_key = False
    if project_id:
        api_key = auth_service.get_project_api_key(project_id)
        has_project_api_key = api_key is not None
    
    # Only require user authentication if we don't have a project API key
    if not has_project_api_key and not auth_service.is_authenticated():
        console.print("[yellow]You are not logged in.[/yellow]")
        if typer.confirm("Would you like to log in now?"):
            # Import the login command dynamically to avoid circular imports
            try:
                from kapso.cli.commands.login import main as login_main
                login_main(ctx, force=False)
            except ImportError:
                console.print("[red]Could not import login command. Please run 'kapso login' first.[/red]")
                sys.exit(1)
        else:
            console.print("[red]Deployment requires authentication. Aborting.[/red]")
            sys.exit(1)
    
    # If still no project ID, list projects and let user select
    if not project_id:
        project_id = select_project(api_manager)
        if not project_id:
            console.print("[red]No project selected. Aborting deployment.[/red]")
            sys.exit(1)
        
        # Save selected project ID to config
        set_project_id(project_id)
    
    # Ensure we have an API key for this project
    if not ensure_project_api_key(project_id, auth_service, api_manager):
        console.print("[red]Failed to set up project API key. Aborting deployment.[/red]")
        sys.exit(1)
    
    with Progress() as progress:
        # Step 1: Find project root and agent file
        task = progress.add_task("Finding agent file...", total=1)
        
        # Default to agent.py if no file is specified
        if not agent_file:
            # Try to get from config
            if os.path.exists(config_file):
                try:
                    config = read_yaml_file(config_file)
                    agent_file = config.get("agent_file", "agent.py")
                except Exception:
                    # If reading config fails, try common files
                    pass
            
            # Try common files
            if not agent_file or not os.path.exists(agent_file):
                if os.path.exists("agent.py"):
                    agent_file = "agent.py"
                elif os.path.exists("agent.yaml"):
                    agent_file = "agent.yaml"
                elif os.path.exists("agent.yml"):
                    agent_file = "agent.yml"
                elif os.path.exists("agent.json"):
                    agent_file = "agent.json"
                else:
                    progress.stop()
                    console.print("[red]Error: No agent file found.[/red]")
                    console.print("Please specify an agent file or create agent.py or agent.yaml.")
                    sys.exit(1)
        
        # Resolve file path
        agent_file_path = Path(agent_file).resolve()
        
        # Check if file exists
        if not agent_file_path.exists():
            progress.stop()
            console.print(f"[red]Error: Agent file not found: {agent_file_path}[/red]")
            sys.exit(1)
        
        progress.update(task, advance=1)
        
        # Step 2: Compile if it's a Python file
        task = progress.add_task("Processing agent file...", total=1)
        
        if str(agent_file_path).endswith(".py"):
            progress.update(task, description="Compiling agent...")
            
            # Use the compile_agent utility function directly instead of calling compile_main
            # Temporary prints for debugging test_deploy_python_file - REMOVED
            # print("DEBUG_DEPLOY: Entering .py compile block", file=sys.stderr)
            output_path = compile_agent(
                agent_file=str(agent_file_path),
                output_file=None,  # Use default output path
                verbose=verbose
            )
            # print(f"DEBUG_DEPLOY: compile_agent called, output_path = {output_path}", file=sys.stderr)
            # End temporary prints
            
            if output_path:
                agent_file_path = output_path
            else:
                progress.stop()
                console.print("[red]Error: Failed to compile agent.[/red]")
                sys.exit(1)
        
        progress.update(task, advance=1)
        
        # Step 3: Load the agent definition
        task = progress.add_task("Loading agent definition...", total=1)
        
        try:
            agent_definition = read_data_file(str(agent_file_path))
            agent_name = agent_definition.get("name", "Unnamed Agent")
            
            # Ensure all nodes have IDs (use name as ID if not present)
            if agent_definition.get("graph") and agent_definition["graph"].get("nodes"):
                for node in agent_definition["graph"]["nodes"]:
                    if not node.get("id") and node.get("name"):
                        node["id"] = node["name"]
            
            # Ensure all edges have IDs (use "{from}_to_{to}_{agent_name}" pattern if not present)
            if agent_definition.get("graph") and agent_definition["graph"].get("edges"):
                agent_name = agent_definition.get("name", "agent")
                nodes_map = {node.get("name"): node for node in agent_definition["graph"].get("nodes", [])}
                
                for edge in agent_definition["graph"]["edges"]:
                    if not edge.get("id"):
                        # Look for source/target or from/to fields
                        from_node = edge.get("source") or edge.get("from")
                        to_node = edge.get("target") or edge.get("to")
                        
                        # Get node names for more readable IDs
                        from_name = from_node
                        to_name = to_node
                        
                        # Create an ID using the from and to node names plus agent name
                        edge["id"] = f"{from_name}_to_{to_name}_{agent_name}"
            
            progress.update(task, advance=1)
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error loading agent definition: {str(e)}[/red]")
            sys.exit(1)
        
        # Step 4: Get the agent ID from config
        task = progress.add_task("Getting agent ID...", total=1)
        
        agent_id = None
        try:
            if os.path.exists(config_file):
                config = read_yaml_file(config_file)
                agent_id = config.get("agent_id")
        except Exception as e:
            console.print(f"[yellow]Warning: Error reading config file: {str(e)}[/yellow]")
            agent_id = None
        
        # Step 5: Initialize API service
        api_client = api_manager.project(project_id)
        
        # Step 6: If no agent ID, create a new agent after confirmation
        if not agent_id:
            progress.stop()
            console.print("[yellow]No agent ID found in configuration.[/yellow]")
            
            if typer.confirm(f"Would you like to create a new agent named '{agent_name}'?"):
                console.print(f"Creating new agent '{agent_name}'...")
                
                # Prepare agent data for creation
                create_agent_data = {
                    "name": agent_name,
                    "system_prompt": agent_definition.get("systemPrompt") or agent_definition.get("system_prompt", ""),
                }
                
                # Create the agent
                try:
                    result = api_client.create_agent(create_agent_data)
                    agent_id = result.get("data", {}).get("id")
                    
                    if not agent_id:
                        console.print("[red]Error: Failed to create agent (no ID returned).[/red]")
                        sys.exit(1)
                    
                    console.print(f"[green]Successfully created agent with ID: {agent_id}[/green]")
                    
                    # Update config file with new agent ID
                    update_config_file(config_file, agent_id)
                    
                except Exception as e:
                    console.print(f"[red]Error creating agent: {str(e)}[/red]")
                    sys.exit(1)
            else:
                console.print("[red]Deployment requires an agent ID. Aborting.[/red]")
                console.print(f"Please add agent_id to your {config_file} file.")
                sys.exit(1)
            
            # Restart progress
            with Progress() as progress:
                task = progress.add_task("Continuing deployment...", total=1)
                progress.update(task, advance=1)
        else:
            progress.update(task, advance=1)
        
        # Step 8: Update agent on server
        task = progress.add_task(f"Deploying agent to {env} environment...", total=1)
        
        try:
            # Prepare agent data
            agent_data = {
                "name": agent_definition.get("name"),
                "graph": agent_definition.get("graph"),
                "system_prompt": agent_definition.get("systemPrompt") or agent_definition.get("system_prompt"),
                "environment": env
            }
            
            # Update the agent
            result = api_client.update_agent(agent_id, agent_data)
            
            # Wait briefly to ensure the agent is updated
            time.sleep(2)
            
            # Get the updated agent definition
            updated_agent = api_client.get_agent_with_graph(agent_id)
            
            progress.update(task, advance=1)
            
            # Create a deployed agent file
            task = progress.add_task("Creating deployed agent file...", total=1)
            
            try:
                ext = get_file_extension(str(agent_file_path))
                deployed_file_path = Path(str(agent_file_path).replace(ext, f".deployed{ext}"))
                
                with open(deployed_file_path, "w") as f:
                    if ext in (".yaml", ".yml"):
                        # Custom YAML dumper for better multiline string handling
                        def str_representer(dumper, data):
                            if '\n' in data:
                                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
                            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
                        
                        class LiteralDumper(yaml.SafeDumper):
                            pass
                        
                        LiteralDumper.add_representer(str, str_representer)
                        
                        yaml.dump(
                            updated_agent.get("data", {}), 
                            f, 
                            Dumper=LiteralDumper, 
                            sort_keys=False, 
                            default_flow_style=False, 
                            width=120,
                            allow_unicode=True
                        )
                    else:
                        json.dump(updated_agent.get("data", {}), f, indent=2)
                
                progress.update(task, advance=1)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to create deployed agent file: {str(e)}[/yellow]")
                progress.update(task, advance=1)
        except GenerationLimitError as e:
            progress.stop()
            console.print(f"[red]Deployment failed: {str(e)}[/red]")
            console.print(f"[yellow]Free generations remaining: {e.free_generations_remaining}[/yellow]")
            console.print("[yellow]Upgrade your plan at app.kapso.ai to deploy more agents.[/yellow]")
            sys.exit(1)
        except Exception as e:
            progress.stop()
            console.print(f"[red]Deployment failed: {str(e)}[/red]")
            if verbose:
                import traceback
                console.print("\n[red]Full error details:[/red]")
                traceback.print_exc()
            sys.exit(1)
        
        # Step 9: Find test files
        task = progress.add_task("Finding test files...", total=1)
        
        test_files = []
        test_suite_dirs = []
        test_suite_map = {}  # Map from directory path to test suite ID
        
        try:
            tests_dir = Path("tests").resolve()
            if tests_dir.exists() and tests_dir.is_dir():
                # Check if there are subdirectories (test suites)
                subdirs = [d for d in tests_dir.iterdir() if d.is_dir()]
                
                if subdirs:
                    # If we have test suite directories, search in them
                    for suite_dir in subdirs:
                        test_suite_dirs.append(str(suite_dir))
                        # Look for YAML, YML, and JSON files
                        yaml_files = get_files_with_extension(str(suite_dir), ".yaml")
                        yml_files = get_files_with_extension(str(suite_dir), ".yml")
                        json_files = get_files_with_extension(str(suite_dir), ".json")
                        
                        # Filter out test suite metadata files
                        filtered_yaml = [f for f in yaml_files if os.path.basename(f) != "test-suite.yaml"]
                        filtered_yml = [f for f in yml_files if os.path.basename(f) != "test-suite.yml"]
                        filtered_json = [f for f in json_files if os.path.basename(f) != "test-suite.json"]
                        
                        test_files.extend(filtered_yaml + filtered_yml + filtered_json)
                else:
                    # Search directly in tests directory
                    yaml_files = get_files_with_extension(str(tests_dir), ".yaml")
                    yml_files = get_files_with_extension(str(tests_dir), ".yml")
                    json_files = get_files_with_extension(str(tests_dir), ".json")
                    
                    # Filter out test suite metadata files
                    filtered_yaml = [f for f in yaml_files if os.path.basename(f) != "test-suite.yaml"]
                    filtered_yml = [f for f in yml_files if os.path.basename(f) != "test-suite.yml"]
                    filtered_json = [f for f in json_files if os.path.basename(f) != "test-suite.json"]
                    
                    test_files.extend(filtered_yaml + filtered_yml + filtered_json)
            
            progress.update(task, advance=1)
        except Exception as e:
            console.print(f"[yellow]Warning: Error finding test files: {str(e)}[/yellow]")
            progress.update(task, advance=1)
        
        # Step 10: Get test suites from server
        task = progress.add_task("Getting test suites...", total=1)
        
        try:
            test_suites_response = api_client.list_agent_test_suites(agent_id)
            existing_test_suites = test_suites_response.get("data", [])
            
            # Get default test suite ID (use the first one if available)
            default_test_suite_id = None
            if existing_test_suites:
                default_test_suite_id = existing_test_suites[0].get("id")
            else:
                progress.stop()
                console.print("[yellow]Warning: No test suites found for this agent.[/yellow]")
                console.print("No test cases will be uploaded. Please create a test suite first.")
            
            progress.update(task, advance=1)
        except Exception as e:
            console.print(f"[yellow]Warning: Error getting test suites: {str(e)}[/yellow]")
            progress.update(task, complete=True)
            default_test_suite_id = None
        
        # Step 11: Load test suite metadata files
        task = progress.add_task("Loading test suite metadata...", total=1)
        
        if test_suite_dirs and default_test_suite_id:
            try:
                for suite_dir in test_suite_dirs:
                    # Try to find metadata files
                    metadata_json_path = os.path.join(suite_dir, "test-suite.json")
                    metadata_yaml_path = os.path.join(suite_dir, "test-suite.yaml")
                    metadata_yml_path = os.path.join(suite_dir, "test-suite.yml")
                    
                    test_suite_data = None
                    
                    if os.path.exists(metadata_json_path):
                        test_suite_data = read_json_file(metadata_json_path)
                    elif os.path.exists(metadata_yaml_path):
                        test_suite_data = read_yaml_file(metadata_yaml_path)
                    elif os.path.exists(metadata_yml_path):
                        test_suite_data = read_yaml_file(metadata_yml_path)
                    
                    if test_suite_data and test_suite_data.get("id"):
                        test_suite_map[suite_dir] = test_suite_data.get("id")
            except Exception as e:
                console.print(f"[yellow]Warning: Error loading test suite metadata: {str(e)}[/yellow]")
            
            progress.update(task, advance=1)
        else:
            progress.update(task, advance=1)
        
        # Step 12: Process test files
        updated_tests = 0
        created_tests = 0
        
        if test_files and default_test_suite_id:
            for test_file in test_files:
                test_file_name = os.path.basename(test_file)
                
                # Skip test suite metadata files
                if test_file_name.startswith("test-suite."):
                    continue
                
                task = progress.add_task(f"Processing test: {test_file_name}...", total=1)
                
                try:
                    # Read the test case
                    test_case = read_data_file(test_file)
                    
                    if test_case.get("id"):
                        # Update existing test case
                        update_data = {
                            "name": test_case.get("name", "Unnamed Test"),
                            "description": test_case.get("description", ""),
                            "rubric": test_case.get("rubric", ""),
                            "script": test_case.get("script", ""),
                        }
                        
                        api_client.update_test_case(test_case["id"], update_data)
                        updated_tests += 1
                    else:
                        # Determine which test suite to use based on the file's location
                        test_suite_id = default_test_suite_id
                        
                        # Get the directory containing the test file
                        test_file_dir = os.path.dirname(test_file)
                        
                        # Check if we have a mapping for this directory
                        if test_file_dir in test_suite_map:
                            test_suite_id = test_suite_map[test_file_dir]
                        
                        # Create new test case
                        create_data = {
                            "name": test_case.get("name", "Unnamed Test"),
                            "description": test_case.get("description", ""),
                            "rubric": test_case.get("rubric", ""),
                            "script": test_case.get("script", ""),
                        }
                        
                        response = api_client.create_test_case(test_suite_id, create_data)
                        new_test_case_data = response.get("data", {})
                        
                        if new_test_case_data and new_test_case_data.get("id"):
                            # Update the file with the new ID
                            test_case["id"] = new_test_case_data["id"]
                            
                            with open(test_file, "w") as f:
                                if get_file_extension(test_file) in (".yaml", ".yml"):
                                    yaml.dump(test_case, f, sort_keys=False)
                                else:
                                    json.dump(test_case, f, indent=2)
                            
                            created_tests += 1
                    
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"[yellow]Warning: Error processing test file {test_file_name}: {str(e)}[/yellow]")
                    progress.update(task, advance=1)
    
    # Final summary
    console.print("\n[green]Deployment completed successfully![/green]")
    console.print("\n[bold]Updated:[/bold]")
    console.print(f"- 1 agent ({agent_name})")
    console.print(f"- {updated_tests} test case(s)")
    
    console.print("\n[bold]Created:[/bold]")
    console.print(f"- {created_tests} test case(s)")
    
    console.print("\nRun 'kapso run --cloud' to try your agent.") 