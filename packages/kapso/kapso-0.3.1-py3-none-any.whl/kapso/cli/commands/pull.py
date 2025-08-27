"""
Implementation of the pull command for the Kapso CLI.
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
import inquirer
import yaml

from kapso.cli.services.auth_service import AuthService
from kapso.cli.services.api_service import ApiManager
from kapso.cli.services.project import ProjectService
from kapso.cli.utils.formatting import print_error, print_warning, print_info

console = Console()


def fetch_project_data(api_manager: ApiManager, project_id: str) -> Dict[str, Any]:
    """
    Fetch project data from the API.
    
    Args:
        api_manager: API manager instance
        project_id: ID of the project to fetch
        
    Returns:
        Project data dictionary
    """
    projects = api_manager.user().list_projects()
    for project in projects:
        if project['id'] == project_id:
            return project
    raise ValueError(f"Project with ID {project_id} not found")


def fetch_all_agents(api_manager: ApiManager, project_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all agents for a project from the API.
    
    Args:
        api_manager: API manager instance
        project_id: ID of the project
        
    Returns:
        List of agent dictionaries
    """
    try:
        response = api_manager.project(project_id).list_agents()
        agents = response.get('data', response) if isinstance(response, dict) else response
        
        # Fetch detailed agent data with graphs
        detailed_agents = []
        for agent in agents:
            try:
                detailed_response = api_manager.project(project_id).get_agent_with_graph(agent['id'])
                detailed_data = detailed_response.get('data', detailed_response)
                detailed_agents.append(detailed_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch details for agent {agent['name']}: {e}[/yellow]")
                detailed_agents.append(agent)
        
        return detailed_agents
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch agents: {e}[/yellow]")
        return []


def fetch_all_flows(api_manager: ApiManager, project_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all flows for a project from the API.
    
    Args:
        api_manager: API manager instance
        project_id: ID of the project
        
    Returns:
        List of flow dictionaries
    """
    try:
        response = api_manager.project(project_id).list_flows()
        flows = response.get('data', response) if isinstance(response, dict) else response
        
        # Fetch detailed flow data with definitions
        detailed_flows = []
        for flow in flows:
            try:
                detailed_response = api_manager.project(project_id).get_flow_with_definition(flow['id'])
                detailed_data = detailed_response.get('data', detailed_response)
                detailed_flows.append(detailed_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch details for flow {flow['name']}: {e}[/yellow]")
                detailed_flows.append(flow)
        
        return detailed_flows
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch flows: {e}[/yellow]")
        return []


def fetch_all_functions(api_manager: ApiManager, project_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all functions for a project from the API.
    
    Args:
        api_manager: API manager instance
        project_id: ID of the project
        
    Returns:
        List of function dictionaries
    """
    try:
        response = api_manager.project(project_id).get("functions")
        functions = response.get('data', [])
        return functions
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch functions: {e}[/yellow]")
        return []


def sanitize_filename(name: str) -> str:
    """
    Sanitize a name to be used as a filename or directory name.
    
    Args:
        name: The name to sanitize
        
    Returns:
        Sanitized name safe for filesystem use
    """
    # Replace spaces and hyphens with underscores
    sanitized = name.lower().replace(' ', '_').replace('-', '_')
    # Remove any characters that aren't alphanumeric or underscore
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
    # Remove consecutive underscores
    sanitized = '_'.join(part for part in sanitized.split('_') if part)
    return sanitized or 'unnamed'


def escape_python_string(s: str) -> str:
    """
    Escape a string for use in Python code.
    
    Args:
        s: The string to escape
        
    Returns:
        Escaped string safe for Python code
    """
    # Replace backslashes first to avoid double-escaping
    s = s.replace('\\', '\\\\')
    # Replace quotes
    s = s.replace('"', '\\"')
    # Replace newlines
    s = s.replace('\n', '\\n')
    # Replace tabs
    s = s.replace('\t', '\\t')
    # Replace carriage returns
    s = s.replace('\r', '\\r')
    return s


def ensure_authenticated(auth_service: AuthService = None):
    """Ensure user is authenticated before proceeding."""
    if not auth_service:
        auth_service = AuthService()
    
    # Check if we have KAPSO_API_KEY environment variable
    if "KAPSO_API_KEY" in os.environ:
        return True
    
    if not auth_service.is_authenticated():
        console.print("[yellow]You need to be logged in to pull agents.[/yellow]")
        console.print("Run 'kapso login' first.")
        sys.exit(1)


def select_agent(api_manager: ApiManager) -> Dict[str, Any]:
    """
    Interactive agent selection: Project -> Agent
    
    Returns:
        Selected agent information including ID and project ID
    """
    # Step 1: List and select project
    projects = api_manager.user().list_projects()
    if not projects:
        console.print("[yellow]No projects found. Create one at app.kapso.ai[/yellow]")
        sys.exit(1)
    
    # Create a mapping of project names to IDs
    project_map = {p['name']: p['id'] for p in projects}
    project_names = list(project_map.keys())
    
    # Use inquirer to select project
    questions = [
        inquirer.List('project_name',
                     message="Select a project",
                     choices=project_names)
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        console.print("[yellow]No project selected. Exiting.[/yellow]")
        sys.exit(1)
    
    project_name = answers['project_name']
    project_id = project_map[project_name]
    
    # Ensure we have an API key for this project before listing agents
    auth_service = AuthService()
    api_key = auth_service.get_project_api_key(project_id)
    
    if not api_key:
        console.print(f"[cyan]Generating API key for project '{project_name}'...[/cyan]")
        try:
            # Generate a new API key using the user token
            api_key_result = api_manager.user().generate_project_api_key(project_id)
            
            if api_key_result and api_key_result.get("key"):
                api_key = api_key_result["key"]
                auth_service.store_project_api_key(project_id, api_key)
                console.print("[green]API key generated successfully.[/green]")
            else:
                console.print("[red]Failed to generate API key for this project.[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error generating API key: {str(e)}[/red]")
            sys.exit(1)
    
    # Step 2: List and select agent
    agents_response = api_manager.project(project_id).list_agents()
    agents = agents_response.get('data', agents_response) if isinstance(agents_response, dict) else agents_response
    
    if not agents:
        console.print("[yellow]No agents found in this project.[/yellow]")
        sys.exit(1)
    
    # Create a mapping of agent names to their data
    agent_map = {a['name']: a for a in agents}
    agent_names = list(agent_map.keys())
    
    # Use inquirer to select agent
    questions = [
        inquirer.List('agent_name',
                     message="Select an agent",
                     choices=agent_names)
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        console.print("[yellow]No agent selected. Exiting.[/yellow]")
        sys.exit(1)
    
    agent_name = answers['agent_name']
    selected_agent = agent_map[agent_name]
    
    return {'id': selected_agent['id'], 'project_id': project_id, 'name': selected_agent['name']}


def confirm_overwrite(path: Path, skip_confirmation: bool = False) -> bool:
    """
    Check if directory has files and confirm overwrite.
    
    Args:
        path: Directory path to check
        skip_confirmation: If True, skip confirmation prompt and always return True
    
    Returns:
        True if user confirms or directory is empty, False otherwise
    """
    if not path.exists():
        path.mkdir(parents=True)
        return True
    
    # Check for existing files
    existing_files = []
    files_to_check = ['agent.py', 'agent.yaml', 'kapso.yaml']
    
    for file in files_to_check:
        if (path / file).exists():
            existing_files.append(file)
    
    # Check for test files
    tests_dir = path / 'tests'
    if tests_dir.exists() and any(tests_dir.iterdir()):
        existing_files.append('tests/*')
    
    if existing_files:
        console.print("[yellow]Warning: The following files will be overwritten:[/yellow]")
        for file in existing_files:
            console.print(f"  - {file}")
        
        if skip_confirmation:
            console.print("[green]Proceeding with overwrite (--yes flag specified)[/green]")
            return True
        
        return typer.confirm("Continue?")
    
    return True


def download_agent_data(api_manager: ApiManager, agent_id: str, project_id: str) -> Dict[str, Any]:
    """
    Download complete agent data from API.
    
    Returns:
        Dictionary containing:
        - agent: Agent configuration with graph
        - test_suites: List of test suites with test cases
        - knowledge_bases: List of knowledge base contents
    """
    # Get agent with graph
    agent_response = api_manager.project(project_id).get_agent_with_graph(agent_id)
    agent_data = agent_response.get('data', agent_response)
    
    # Get test suites
    test_suites = []
    try:
        suites_response = api_manager.project(project_id).list_agent_test_suites(agent_id)
        suites_list = suites_response.get('data', suites_response) if isinstance(suites_response, dict) else suites_response
        
        for suite in suites_list:
            # Get the full test suite data including test cases
            suite_response = api_manager.project(project_id).get_test_suite(suite['id'])
            suite_data = suite_response.get('data', suite_response) if isinstance(suite_response, dict) else suite_response
            test_suites.append(suite_data)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch test suites: {e}[/yellow]")
    
    # TODO: Get knowledge base contents when API is available
    knowledge_bases = []
    
    return {
        'agent': agent_data,
        'test_suites': test_suites,
        'knowledge_bases': knowledge_bases
    }


def convert_agent_to_python(agent_data: Dict[str, Any]) -> str:
    """
    Convert agent JSON/YAML structure to Python code using Builder SDK.
    
    This is the reverse of the compile operation.
    """
    import json
    
    # Start building the Python code
    lines = []
    
    # Add imports
    lines.append('"""')
    agent_name_display = escape_python_string(agent_data.get("name", "Unnamed Agent"))
    lines.append(f'Agent: {agent_name_display}')
    if agent_data.get('description'):
        description_display = escape_python_string(agent_data["description"])
        lines.append(f'Description: {description_display}')
    lines.append('"""')
    lines.append('')
    lines.append('from kapso.builder import Agent')
    
    # Collect unique node types from the graph
    node_types = set()
    has_default_nodes = False
    if 'graph' in agent_data and 'nodes' in agent_data['graph']:
        for node in agent_data['graph']['nodes']:
            node_type = node.get('type', '')
            if node_type == 'DefaultNode':
                has_default_nodes = True
            elif node_type:
                node_types.add(node_type)
    
    # Add node imports
    all_node_types = list(node_types)
    if has_default_nodes:
        all_node_types.append('DefaultNode')
    
    if all_node_types:
        lines.append(f'from kapso.builder.nodes import {", ".join(sorted(all_node_types))}')
    
    # Check if we need tool imports by looking at SubagentNodes
    tool_types = set()
    if 'graph' in agent_data and 'nodes' in agent_data['graph']:
        for node in agent_data['graph']['nodes']:
            if node.get('type') == 'SubagentNode' and node.get('subagent'):
                subagent = node['subagent']
                if subagent.get('webhooks'):
                    tool_types.add('WebhookTool')
                if subagent.get('knowledge_bases'):
                    tool_types.add('KnowledgeBaseTool')
                if subagent.get('whatsapp_templates'):
                    tool_types.add('WhatsappTemplateTool')
                if subagent.get('mcp_servers'):
                    tool_types.add('McpServerTool')
    
    if tool_types:
        lines.append(f'from kapso.builder.nodes.subagent import {", ".join(sorted(tool_types))}')
    
    lines.append('from kapso.builder.agent.constants import START_NODE, END_NODE')
    lines.append('')
    lines.append('')
    
    # Create agent
    lines.append('# Create the agent')
    lines.append(f'agent = Agent(')
    agent_name = escape_python_string(agent_data.get("name", "My Agent"))
    lines.append(f'    name="{agent_name}",')
    if agent_data.get('description'):
        description = escape_python_string(agent_data['description'])
        lines.append(f'    description="{description}",')
    if agent_data.get('system_prompt'):
        # Escape system prompt
        system_prompt = escape_python_string(agent_data['system_prompt'])
        lines.append(f'    system_prompt="{system_prompt}",')
    lines.append(')')
    lines.append('')
    
    # Process nodes
    node_id_to_var = {}  # Map node IDs to variable names
    node_name_to_var = {}  # Map node names to variable names
    if 'graph' in agent_data and 'nodes' in agent_data['graph']:
        lines.append('# Define nodes')
        
        # First, add start and end nodes
        lines.append('# Add start and end nodes')
        lines.append('agent.add_node(START_NODE)')
        lines.append('agent.add_node(END_NODE)')
        lines.append('')
        
        node_counter = 1
        for node in agent_data['graph']['nodes']:
            node_id = node['id']
            node_name = node.get('name', node_id)
            node_type = node.get('type', '')
            
            # Skip start and end nodes as we've already added them
            if node_name == '__start__' or node_name == '__end__':
                continue
            
            # Create a valid Python variable name
            var_name = f"node_{node_counter}"
            node_id_to_var[node_id] = var_name
            node_name_to_var[node_name] = var_name
            node_counter += 1
            
            if node_type == 'SubagentNode':
                lines.append(f'{var_name} = SubagentNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                
                # Add prompt if available
                if node.get('prompt'):
                    # Escape prompt string
                    prompt = escape_python_string(node['prompt'])
                    lines.append(f'    prompt="{prompt}",')
                
                # Add description if available
                if node.get('description'):
                    description = escape_python_string(node['description'])
                    lines.append(f'    description="{description}",')
                
                # Add global attributes
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                
                lines.append(')')
                
                # Add tools from the subagent field
                if node.get('subagent'):
                    subagent = node['subagent']
                    lines.append('')
                    
                    # Add webhook tools
                    for webhook in subagent.get('webhooks', []):
                        lines.append(f'{var_name}.add_tool(WebhookTool(')
                        webhook_name = escape_python_string(webhook["name"])
                        lines.append(f'    name="{webhook_name}",')
                        webhook_url = escape_python_string(webhook["url"])
                        lines.append(f'    url="{webhook_url}",')
                        if webhook.get('description'):
                            description = escape_python_string(webhook['description'])
                            lines.append(f'    description="{description}",')
                        http_method = escape_python_string(webhook.get("http_method", "POST"))
                        lines.append(f'    http_method="{http_method}",')
                        
                        # Parse headers from string to dict if needed
                        if webhook.get('headers'):
                            try:
                                headers = json.loads(webhook['headers']) if isinstance(webhook['headers'], str) else webhook['headers']
                                lines.append(f'    headers={repr(headers)},')
                            except:
                                pass
                        
                        # Parse body schema
                        if webhook.get('body_schema'):
                            try:
                                body_schema = json.loads(webhook['body_schema']) if isinstance(webhook['body_schema'], str) else webhook['body_schema']
                                lines.append(f'    body_schema={repr(body_schema)},')
                            except:
                                pass
                                
                        if webhook.get('jmespath_query'):
                            jmespath_query = escape_python_string(webhook['jmespath_query'])
                            lines.append(f'    jmespath_query="{jmespath_query}",')
                            
                        lines.append('))')
                        lines.append('')
                    
                    # Add knowledge base tools
                    for kb in subagent.get('knowledge_bases', []):
                        lines.append(f'{var_name}.add_tool(KnowledgeBaseTool(')
                        kb_name = escape_python_string(kb["name"])
                        lines.append(f'    name="{kb_name}",')
                        if kb.get('description'):
                            description = escape_python_string(kb['description'])
                            lines.append(f'    description="{description}",')
                        # Escape the knowledge text
                        kb_text = escape_python_string(kb.get('knowledge_base_text', ''))
                        lines.append(f'    knowledge_base_text="{kb_text}"')
                        lines.append('))')
                        lines.append('')
                    
                    # Add WhatsApp template tools
                    for wt in subagent.get('whatsapp_templates', []):
                        lines.append(f'{var_name}.add_tool(WhatsappTemplateTool(')
                        wt_name = escape_python_string(wt["name"])
                        lines.append(f'    name="{wt_name}",')
                        template_name = escape_python_string(wt.get("template_name", wt["name"]))
                        lines.append(f'    template_name="{template_name}",')
                        phone_number = escape_python_string(wt.get("phone_number", ""))
                        lines.append(f'    phone_number="{phone_number}",')
                        if wt.get('description'):
                            description = escape_python_string(wt['description'])
                            lines.append(f'    description="{description}",')
                        if wt.get('wait_for_response'):
                            lines.append(f'    wait_for_response={wt["wait_for_response"]},')
                        lines.append('))')
                        lines.append('')
                    
                    # Add MCP server tools
                    for mcp in subagent.get('mcp_servers', []):
                        lines.append(f'{var_name}.add_tool(McpServerTool(')
                        mcp_name = escape_python_string(mcp["name"])
                        lines.append(f'    name="{mcp_name}",')
                        mcp_url = escape_python_string(mcp["url"])
                        lines.append(f'    url="{mcp_url}",')
                        if mcp.get('description'):
                            description = escape_python_string(mcp['description'])
                            lines.append(f'    description="{description}",')
                        if mcp.get('transport_kind'):
                            transport_kind = escape_python_string(mcp["transport_kind"])
                            lines.append(f'    transport_kind="{transport_kind}",')
                        lines.append('))')
                        lines.append('')
                
                # Add the SubagentNode to the agent
                lines.append(f'agent.add_node({var_name})')
            elif node_type == 'HandoffNode':
                lines.append(f'{var_name} = HandoffNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                lines.append(')')
                lines.append(f'agent.add_node({var_name})')
            elif node_type == 'WarmEndNode':
                lines.append(f'{var_name} = WarmEndNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                if node.get('warm_end', {}).get('timeout_minutes'):
                    lines.append(f'    timeout_minutes={node["warm_end"]["timeout_minutes"]},')
                if node.get('prompt'):
                    prompt = escape_python_string(node['prompt'])
                    lines.append(f'    prompt="{prompt}",')
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                lines.append(')')
                lines.append(f'agent.add_node({var_name})')
            elif node_type == 'WebhookNode':
                webhook = node.get('webhook', {})
                lines.append(f'{var_name} = WebhookNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                webhook_url = escape_python_string(webhook.get("url", ""))
                lines.append(f'    url="{webhook_url}",')
                http_method = escape_python_string(webhook.get("http_method", "POST"))
                lines.append(f'    http_method="{http_method}",')
                if node.get('prompt'):
                    prompt = escape_python_string(node['prompt'])
                    lines.append(f'    prompt="{prompt}",')
                if webhook.get('headers'):
                    lines.append(f'    headers={repr(webhook.get("headers"))},')
                if webhook.get('body'):
                    lines.append(f'    body={repr(webhook.get("body"))},')
                if webhook.get('body_schema'):
                    lines.append(f'    body_schema={repr(webhook.get("body_schema"))},')
                if webhook.get('jmespath_query'):
                    jmespath_query = escape_python_string(webhook['jmespath_query'])
                    lines.append(f'    jmespath_query="{jmespath_query}",')
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                lines.append(')')
                lines.append(f'agent.add_node({var_name})')
            elif node_type == 'KnowledgeBaseNode':
                kb = node.get('knowledge_base', {})
                lines.append(f'{var_name} = KnowledgeBaseNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                if node.get('prompt'):
                    prompt = escape_python_string(node['prompt'])
                    lines.append(f'    prompt="{prompt}",')
                if kb.get('knowledge_base_text'):
                    kb_text = escape_python_string(kb['knowledge_base_text'])
                    lines.append(f'    knowledge_base_text="{kb_text}",')
                if kb.get('knowledge_base_file'):
                    kb_file = escape_python_string(kb["knowledge_base_file"])
                    lines.append(f'    knowledge_base_file="{kb_file}",')
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                lines.append(')')
                lines.append(f'agent.add_node({var_name})')
            elif node_type == 'WhatsAppTemplateNode':
                wt = node.get('whatsapp_template', {})
                lines.append(f'{var_name} = WhatsAppTemplateNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                template_name = escape_python_string(wt.get("template_name", ""))
                lines.append(f'    template_name="{template_name}",')
                phone_number = escape_python_string(wt.get("phone_number", ""))
                lines.append(f'    phone_number="{phone_number}",')
                if wt.get('template_parameters'):
                    lines.append(f'    template_parameters={repr(wt["template_parameters"])},')
                if wt.get('wait_for_response') is not None:
                    lines.append(f'    wait_for_response={wt["wait_for_response"]},')
                if node.get('prompt'):
                    prompt = escape_python_string(node['prompt'])
                    lines.append(f'    prompt="{prompt}",')
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                lines.append(')')
                lines.append(f'agent.add_node({var_name})')
            else:
                # Handle DefaultNode or any unrecognized node type
                lines.append(f'{var_name} = DefaultNode(')
                node_name_escaped = escape_python_string(node_name)
                lines.append(f'    name="{node_name_escaped}",')
                if node.get('prompt'):
                    prompt = escape_python_string(node['prompt'])
                    lines.append(f'    prompt="{prompt}",')
                if node.get('global'):
                    lines.append(f'    global_={node["global"]},')
                if node.get('global_condition'):
                    global_condition = escape_python_string(node['global_condition'])
                    lines.append(f'    global_condition="{global_condition}",')
                lines.append(')')
                lines.append(f'agent.add_node({var_name})')
            
            lines.append('')
    
    # Process edges
    if 'graph' in agent_data and 'edges' in agent_data['graph']:
        lines.append('# Define edges')
        
        # Create a map of node IDs to node names for start/end detection
        node_id_to_name = {}
        for node in agent_data['graph']['nodes']:
            node_id_to_name[node['id']] = node.get('name', node['id'])
        
        for edge_data in agent_data['graph']['edges']:
            source_ref = edge_data['from']  # Could be node ID or name
            target_ref = edge_data['to']    # Could be node ID or name
            
            # Check if source is start node (by ID or name)
            source_node_name = node_id_to_name.get(source_ref, source_ref)
            if source_ref == '__start__' or source_node_name == '__start__':
                source = 'START_NODE'
            elif source_ref in node_id_to_var:
                # It's a node ID, use the variable directly
                source = node_id_to_var[source_ref]
            elif source_ref in node_name_to_var:
                # It's a node name, use the variable directly
                source = node_name_to_var[source_ref]
            else:
                # It's a string node name, quote it
                source = f'"{source_ref}"'
                
            # Check if target is end node (by ID or name)
            target_node_name = node_id_to_name.get(target_ref, target_ref)
            if target_ref == '__end__' or target_node_name == '__end__':
                target = 'END_NODE'
            elif target_ref in node_id_to_var:
                # It's a node ID, use the variable directly
                target = node_id_to_var[target_ref]
            elif target_ref in node_name_to_var:
                # It's a node name, use the variable directly
                target = node_name_to_var[target_ref]
            else:
                # It's a string node name, quote it
                target = f'"{target_ref}"'
            
            # Use 'label' instead of 'condition'
            if edge_data.get('label'):
                condition = escape_python_string(edge_data['label'])
                lines.append(f'agent.add_edge({source}, {target}, condition="{condition}")')
            else:
                lines.append(f'agent.add_edge({source}, {target})')
        lines.append('')
    
    # Add simple edges if no edges defined
    if 'graph' not in agent_data or 'edges' not in agent_data['graph'] or len(agent_data['graph']['edges']) == 0:
        lines.append('# Define a simple flow')
        lines.append('agent.add_edge(START_NODE, END_NODE)')
        lines.append('')
    
    # Add validation at the end
    lines.append('# Validate the agent configuration')
    lines.append('agent.validate()')
    lines.append('')
    
    return '\n'.join(lines)


def create_project_structure(project_path: Path, project_data: Dict[str, Any]) -> None:
    """
    Create the basic project directory structure and kapso.yaml.
    
    Args:
        project_path: Path to the project directory
        project_data: Project data from API
    """
    # Create directory structure
    (project_path / "agents").mkdir(exist_ok=True)
    (project_path / "flows").mkdir(exist_ok=True)
    (project_path / "functions").mkdir(exist_ok=True)
    
    # Create project-level kapso.yaml
    kapso_config = {
        'project_id': project_data['id'],
        'name': project_data['name'],
        'version': '0.1.0'
    }
    
    # Custom YAML dumper for better formatting
    def str_representer(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    class LiteralDumper(yaml.SafeDumper):
        pass
    
    LiteralDumper.add_representer(str, str_representer)
    
    with open(project_path / 'kapso.yaml', 'w') as f:
        yaml.dump(kapso_config, f, Dumper=LiteralDumper, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)
    
    # Create .env.example
    with open(project_path / '.env.example', 'w') as f:
        f.write('# Kapso API Key - get yours from app.kapso.ai\n')
        f.write('KAPSO_API_KEY=your_api_key_here\n')


def create_agent_files(project_path: Path, agents: List[Dict[str, Any]]) -> None:
    """
    Create agent directories and files from agent data.
    
    Args:
        project_path: Path to the project directory
        agents: List of agent data dictionaries
    """
    for agent in agents:
        # Sanitize agent name for directory
        agent_dir_name = sanitize_filename(agent['name'])
        agent_dir = project_path / "agents" / agent_dir_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert agent to Python code
        python_code = convert_agent_to_python(agent)
        
        # Create agent.py
        with open(agent_dir / 'agent.py', 'w') as f:
            f.write(python_code)
        
        # Create metadata.yaml
        from datetime import datetime
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        metadata = {
            'agent_id': agent['id'],
            'name': agent['name'],
            'description': agent.get('description', ''),
            'created_at': agent.get('created_at', current_time),
            'updated_at': agent.get('updated_at', current_time)
        }
        
        # Custom YAML dumper
        def str_representer(dumper, data):
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        
        class LiteralDumper(yaml.SafeDumper):
            pass
        
        LiteralDumper.add_representer(str, str_representer)
        
        with open(agent_dir / 'metadata.yaml', 'w') as f:
            yaml.dump(metadata, f, Dumper=LiteralDumper, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)


def create_flow_files(project_path: Path, flows: List[Dict[str, Any]]) -> None:
    """
    Create flow directories and files from flow data.
    
    Args:
        project_path: Path to the project directory
        flows: List of flow data dictionaries
    """
    for flow in flows:
        # Sanitize flow name for directory
        flow_dir_name = sanitize_filename(flow['name'])
        flow_dir = project_path / "flows" / flow_dir_name
        flow_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert flow to Python code using Flow Builder SDK
        python_code = convert_flow_to_python(flow)
        
        # Create flow.py
        with open(flow_dir / 'flow.py', 'w') as f:
            f.write(python_code)
        
        # Create metadata.yaml
        from datetime import datetime
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        metadata = {
            'flow_id': flow['id'],
            'name': flow['name'],
            'description': flow.get('description', ''),
            'created_at': flow.get('created_at', current_time),
            'updated_at': flow.get('updated_at', current_time)
        }
        
        # Custom YAML dumper
        def str_representer(dumper, data):
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        
        class LiteralDumper(yaml.SafeDumper):
            pass
        
        LiteralDumper.add_representer(str, str_representer)
        
        with open(flow_dir / 'metadata.yaml', 'w') as f:
            yaml.dump(metadata, f, Dumper=LiteralDumper, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)


def create_function_files(project_path: Path, functions: List[Dict[str, Any]]) -> None:
    """
    Create function files from function data.
    
    Args:
        project_path: Path to the project directory
        functions: List of function data dictionaries
    """
    functions_dir = project_path / "functions"
    functions_dir.mkdir(exist_ok=True)
    
    for function in functions:
        # Create function file
        function_name = sanitize_filename(function['name'])
        function_file = functions_dir / f"{function_name}.js"
        
        # Use the function code from API or generate basic template
        function_code = function.get('code', f'function {function_name}() {{ /* TODO: Implement */ }}')
        
        with open(function_file, 'w') as f:
            f.write(function_code)


def convert_flow_to_python(flow_data: Dict[str, Any]) -> str:
    """
    Convert flow JSON/YAML structure to Python code using Flow Builder SDK.
    
    Args:
        flow_data: Flow data dictionary from API
        
    Returns:
        Python code string
    """
    # Import the flow converter
    from kapso.cli.utils.flow_converter import convert_flow_to_python as convert_flow
    return convert_flow(flow_data)


def select_project_interactive(api_manager: ApiManager) -> Dict[str, Any]:
    """
    Interactive project selection.
    
    Args:
        api_manager: API manager instance
        
    Returns:
        Selected project data
    """
    projects = api_manager.user().list_projects()
    if not projects:
        console.print("[yellow]No projects found. Create one at app.kapso.ai[/yellow]")
        sys.exit(1)
    
    # Create a mapping of project names to project data
    project_map = {p['name']: p for p in projects}
    project_names = list(project_map.keys())
    
    # Use inquirer to select project
    questions = [
        inquirer.List('project_name',
                     message="Select a project",
                     choices=project_names)
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        console.print("[yellow]No project selected. Exiting.[/yellow]")
        sys.exit(1)
    
    project_name = answers['project_name']
    selected_project = project_map[project_name]
    
    # Ensure we have an API key for this project
    auth_service = AuthService()
    api_key = auth_service.get_project_api_key(selected_project['id'])
    
    if not api_key:
        console.print(f"[cyan]Generating API key for project '{project_name}'...[/cyan]")
        try:
            # Generate a new API key using the user token
            api_key_result = api_manager.user().generate_project_api_key(selected_project['id'])
            
            if api_key_result and api_key_result.get("key"):
                api_key = api_key_result["key"]
                auth_service.store_project_api_key(selected_project['id'], api_key)
                console.print("[green]API key generated successfully.[/green]")
            else:
                console.print("[red]Failed to generate API key for this project.[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error generating API key: {str(e)}[/red]")
            sys.exit(1)
    
    return selected_project


def pull_entire_project(project_id: Optional[str], yes: bool) -> None:
    """
    Pull entire project from Kapso Cloud.
    
    Args:
        project_id: Optional project ID. If None, will prompt for selection
        yes: Skip confirmation prompts
    """
    project_path = Path.cwd()
    
    # Check authentication
    auth_service = AuthService()
    ensure_authenticated(auth_service)
    api_manager = ApiManager(auth_service)
    
    # Get project ID if not provided
    if not project_id:
        project_data = select_project_interactive(api_manager)
        project_id = project_data['id']
        console.print(f"Selected project: {project_data['name']}")
    else:
        project_data = fetch_project_data(api_manager, project_id)
        console.print(f"Using project: {project_data['name']}")
    
    # Ensure we have an API key for this project before fetching resources
    api_key = auth_service.get_project_api_key(project_id)
    
    if not api_key:
        console.print(f"[cyan]Generating API key for project '{project_data['name']}'...[/cyan]")
        try:
            # Generate a new API key using the user token
            api_key_result = api_manager.user().generate_project_api_key(project_id)
            
            if api_key_result and api_key_result.get("key"):
                api_key = api_key_result["key"]
                auth_service.store_project_api_key(project_id, api_key)
                console.print("[green]API key generated successfully.[/green]")
            else:
                console.print("[red]Failed to generate API key for this project.[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error generating API key: {str(e)}[/red]")
            sys.exit(1)
    
    # Confirm overwrite if directory has files
    if not confirm_overwrite_project(project_path, skip_confirmation=yes):
        console.print("[yellow]Pull cancelled.[/yellow]")
        sys.exit(0)
    
    # Fetch all project resources
    with Progress() as progress:
        task = progress.add_task("Pulling project...", total=5)
        
        # project_data already fetched above
        progress.update(task, advance=1)
        
        # Fetch agents
        agents = fetch_all_agents(api_manager, project_id)
        progress.update(task, advance=1)
        
        # Fetch flows
        flows = fetch_all_flows(api_manager, project_id)
        progress.update(task, advance=1)
        
        # Fetch functions
        functions = fetch_all_functions(api_manager, project_id)
        progress.update(task, advance=1)
        
        # Create project structure
        create_project_structure(project_path, project_data)
        progress.update(task, advance=1)
        
        # Create resource files
        create_agent_files(project_path, agents)
        create_flow_files(project_path, flows)
        create_function_files(project_path, functions)
        progress.update(task, advance=1)
    
    # Show summary
    agent_count = len(agents)
    flow_count = len(flows)
    function_count = len(functions)
    
    console.print(f"[green]Successfully pulled project: {project_data['name']}[/green]")
    console.print(f"✓ Pulled {agent_count} agents, {flow_count} flows, {function_count} functions")
    
    if agent_count > 0:
        console.print("\nTo start developing:")
        console.print("  cd agents/<agent_name>")
        console.print("  # Edit agent.py")


def confirm_overwrite_project(path: Path, skip_confirmation: bool = False) -> bool:
    """
    Check if directory has project files and confirm overwrite.
    
    Args:
        path: Directory path to check
        skip_confirmation: If True, skip confirmation prompt
        
    Returns:
        True if user confirms or directory is clean, False otherwise
    """
    if not path.exists():
        path.mkdir(parents=True)
        return True
    
    # Check for existing project structure
    existing_items = []
    
    if (path / 'kapso.yaml').exists():
        existing_items.append('kapso.yaml')
    if (path / 'agents').exists() and any((path / 'agents').iterdir()):
        existing_items.append('agents/*')
    if (path / 'flows').exists() and any((path / 'flows').iterdir()):
        existing_items.append('flows/*')
    if (path / 'functions').exists() and any((path / 'functions').iterdir()):
        existing_items.append('functions/*')
    
    if existing_items:
        console.print("[yellow]Warning: The following will be overwritten:[/yellow]")
        for item in existing_items:
            console.print(f"  - {item}")
        
        if skip_confirmation:
            console.print("[green]Proceeding with overwrite (--yes flag specified)[/green]")
            return True
        
        return typer.confirm("Continue?")
    
    return True


def create_project_files(
    path: Path, 
    agent_data: Dict[str, Any],
    python_code: str,
    project_id: str
):
    """Create all project files in the specified directory."""
    # Create directories
    (path / 'knowledge').mkdir(exist_ok=True)
    (path / 'tests').mkdir(exist_ok=True)
    
    # Create agent.py
    with open(path / 'agent.py', 'w') as f:
        f.write(python_code)
    
    # Create kapso.yaml with agent_id and project_id
    # Note: project_id comes from the pull command context, not the agent data
    kapso_config = {
        'agent_id': agent_data['agent']['id'],
        'project_id': project_id,
        'name': agent_data['agent'].get('name', 'My Agent')
    }
    
    # Custom YAML dumper for better formatting
    def str_representer(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    class LiteralDumper(yaml.SafeDumper):
        pass
    
    LiteralDumper.add_representer(str, str_representer)
    
    with open(path / 'kapso.yaml', 'w') as f:
        yaml.dump(kapso_config, f, Dumper=LiteralDumper, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)
    
    # Create test suite directories and files
    for suite in agent_data.get('test_suites', []):
        # Sanitize suite name for directory
        suite_dir_name = sanitize_filename(suite['name'])
        suite_dir = path / 'tests' / suite_dir_name
        suite_dir.mkdir(exist_ok=True)
        
        # Create test-suite.yaml
        suite_metadata = {
            'id': suite['id'],
            'name': suite['name'],
            'description': suite.get('description', '')
        }
        
        with open(suite_dir / 'test-suite.yaml', 'w') as f:
            yaml.dump(suite_metadata, f, Dumper=LiteralDumper, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)
        
        # Create test case files
        for test_case in suite.get('test_cases', []):
            test_file_name = sanitize_filename(test_case['name']) + '.yaml'
            test_data = {
                'id': test_case.get('id'),  # Add the test case ID
                'name': test_case['name'],
                'description': test_case.get('description', ''),
                'script': test_case.get('script', ''),
                'rubric': test_case.get('rubric', '')
            }
            
            with open(suite_dir / test_file_name, 'w') as f:
                yaml.dump(test_data, f, Dumper=LiteralDumper, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)
    
    # Create .env.example
    with open(path / '.env.example', 'w') as f:
        f.write('# Kapso API Key - get yours from app.kapso.ai\n')
        f.write('KAPSO_API_KEY=your_api_key_here\n')


def pull(
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="Project ID to pull"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
):
    """
    Pull entire project from Kapso Cloud to create local development environment.
    
    Downloads all agents, flows, and functions into proper directory structure.
    If no project ID provided, will prompt for project selection.
    """
    pull_entire_project(project_id, yes)