"""
Utility functions for agent operations.
"""

import os
import sys
import re
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import yaml
from kapso.builder.agent.agent import Agent
from kapso.builder.serialization.yaml import serialize_to_yaml

def compile_agent(
    agent_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> Optional[Path]:
    """
    Compile an agent from Python code to YAML without output messages.
    
    Args:
        agent_file: Path to the Python file defining the agent.
        output_file: Output file path (defaults to agent.yaml in the current directory).
        verbose: Whether to print verbose messages.
        
    Returns:
        Path to the compiled file, or None if compilation failed.
    """
    # Resolve file path
    file_path = Path(agent_file).resolve()
    
    # Check if file exists
    if not file_path.exists():
        if verbose:
            print(f"Error: File not found: {file_path}")
        return None
    
    # Default output file
    if not output_file:
        output_file = "agent.yaml"
    
    try:
        # Add the current directory to the path
        sys.path.insert(0, os.getcwd())
        
        # If file is not a Python file, error out
        if not str(file_path).endswith(".py"):
            if verbose:
                print(f"Error: File must be a Python file (.py): {file_path}")
            return None
        
        # Import the agent
        spec = importlib.util.spec_from_file_location("agent_module", file_path)
        if not spec or not spec.loader:
            if verbose:
                print(f"Error: Failed to load module: {file_path}")
            return None
            
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)
        
        # Find the agent in the module
        agent = None
        
        # First, look for default/agent variables by convention
        if hasattr(agent_module, "default"):
            agent = getattr(agent_module, "default")
        elif hasattr(agent_module, "agent"):
            agent = getattr(agent_module, "agent")
        else:
            # Scan all variables in the module for Agent instances
            for name, obj in vars(agent_module).items():
                if isinstance(obj, Agent):
                    agent = obj
                    break
        
        if not agent or not isinstance(agent, Agent):
            if verbose:
                print("Error: No agent found in the specified file.")
                print("The file must contain an Agent instance, either named 'agent', 'default', or any variable name.")
            return None
        
        # Serialize to YAML
        yaml_content = serialize_to_yaml(agent)
        
        # Write to file
        output_path = Path(output_file).resolve()
        with open(output_path, "w") as f:
            f.write(yaml_content)
            
        return output_path
        
    except ImportError as e:
        if verbose:
            import traceback
            print(f"Error importing agent: {str(e)}")
            print("\nFull traceback:")
            traceback.print_exc()
        else:
            print(f"Import error: {str(e)}")
        return None
    except Exception as e:
        if verbose:
            import traceback
            print(f"Error compiling agent: {str(e)}")
            print("\nFull traceback:")
            traceback.print_exc()
        else:
            print(f"Compilation error: {str(e)}")
        return None

def load_agent_graph(agent_path: Optional[Path] = None) -> Tuple[Optional[Dict[str, Any]], bool]:
    """
    Load and process the agent graph from agent.yaml.
    
    This function loads the agent definition from agent.yaml,
    extracts the graph, and ensures all nodes and edges have proper IDs.
    
    Args:
        agent_path: Path to the agent YAML file (defaults to agent.yaml in current directory)
        
    Returns:
        Tuple of (processed graph, success flag)
    """
    try:
        # Use default path if not provided
        if not agent_path:
            agent_path = Path.cwd() / "agent.yaml"
            
        # Check if file exists
        if not agent_path.exists():
            return None, False
            
        # Load YAML file
        with open(agent_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Extract the graph if it exists
        if not config.get("graph"):
            return None, True  # No graph but successful load
            
        # Work with a copy to avoid modifying the original
        graph = config["graph"]
        
        # Ensure all nodes in graph have an ID (use name as ID if not present)
        if "nodes" in graph and isinstance(graph["nodes"], list):
            for node in graph["nodes"]:
                if not node.get("id") and node.get("name"):
                    node["id"] = node["name"]
        
        # Ensure all edges have an ID (use "from_to_to" pattern if not present)
        if "edges" in graph and isinstance(graph["edges"], list):
            for edge in graph["edges"]:
                if not edge.get("id"):
                    # Get node names for from and to nodes for more readable IDs
                    from_node = next((n for n in graph["nodes"] if n.get("id") == edge["from"] or n.get("name") == edge["from"]), None)
                    to_node = next((n for n in graph["nodes"] if n.get("id") == edge["to"] or n.get("name") == edge["to"]), None)
                    
                    from_name = from_node.get("name") if from_node else edge["from"]
                    to_name = to_node.get("name") if to_node else edge["to"]
                    
                    # Create an ID using the from and to node names
                    edge["id"] = f"{from_name}_to_{to_name}"
        
        return graph, True
        
    except Exception as e:
        return None, False


def find_agent_directory(agent_name: str, project_root: Optional[Path] = None) -> Optional[Path]:
    """
    Find an agent directory by name.
    
    Args:
        agent_name: Name of the agent to find.
        project_root: Root directory to search from (defaults to current directory).
        
    Returns:
        Path to the agent directory if found, None otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()
    
    agents_dir = project_root / "agents"
    if not agents_dir.exists():
        return None
    
    agent_dir = agents_dir / agent_name
    if agent_dir.exists() and agent_dir.is_dir():
        return agent_dir
    
    return None


def get_agent_name_from_cwd() -> Optional[str]:
    """
    Get the agent name from the current working directory.
    
    Returns:
        Agent name if currently inside an agent directory, None otherwise.
    """
    cwd = Path.cwd()
    
    # Check if we're in an agents/<name> directory
    if cwd.parent.name == "agents" and cwd.name != "agents":
        return cwd.name
    
    return None


def validate_agent_name(name: str) -> bool:
    """
    Validate an agent name.
    
    Args:
        name: Agent name to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    if not name:
        return False
    
    # Must start with a letter or underscore, then letters, numbers, underscores, and hyphens
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_-]*$'
    return bool(re.match(pattern, name))


def compile_agent_from_directory(agent_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Compile an agent from its directory structure.
    
    Args:
        agent_dir: Path to the agent directory containing agent.py.
        
    Returns:
        Compiled agent data as dictionary, or None if compilation failed.
    """
    agent_file = agent_dir / "agent.py"
    if not agent_file.exists():
        return None
    
    try:
        # Add the agent directory to the path so imports work
        sys.path.insert(0, str(agent_dir))
        
        # Import the agent module
        spec = importlib.util.spec_from_file_location("agent_module", agent_file)
        if not spec or not spec.loader:
            return None
            
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)
        
        # Find the agent instance
        agent = None
        if hasattr(agent_module, "default"):
            agent = getattr(agent_module, "default")
        elif hasattr(agent_module, "agent"):
            agent = getattr(agent_module, "agent")
        else:
            # Scan for Agent instances
            for name, obj in vars(agent_module).items():
                if isinstance(obj, Agent):
                    agent = obj
                    break
        
        if not agent or not isinstance(agent, Agent):
            return None
        
        # Serialize to dictionary (not YAML)
        yaml_content = serialize_to_yaml(agent)
        # Parse the YAML back to a dictionary
        return yaml.safe_load(yaml_content)
        
    except Exception:
        return None
    finally:
        # Remove the added path
        if str(agent_dir) in sys.path:
            sys.path.remove(str(agent_dir))