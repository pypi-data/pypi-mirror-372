"""
Flow utility functions for the Kapso CLI.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from kapso.builder.flows.flow import Flow
from kapso.builder.compilation.flow_compiler import compile_flow
from kapso.builder.serialization.flow_yaml import deserialize_from_dict


def find_flow_directory(flow_name: str, project_root: Optional[Path] = None) -> Optional[Path]:
    """
    Find a flow directory by name.
    
    Args:
        flow_name: Name of the flow to find.
        project_root: Root directory to search from (defaults to current directory).
        
    Returns:
        Path to the flow directory if found, None otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()
    
    flows_dir = project_root / "flows"
    if not flows_dir.exists():
        return None
    
    flow_dir = flows_dir / flow_name
    if flow_dir.exists() and flow_dir.is_dir():
        return flow_dir
    
    return None


def get_flow_name_from_cwd() -> Optional[str]:
    """
    Get the flow name from the current working directory.
    
    Returns:
        Flow name if currently inside a flow directory, None otherwise.
    """
    cwd = Path.cwd()
    
    # Check if we're in a flows/<name> directory
    if cwd.parent.name == "flows" and cwd.name != "flows":
        return cwd.name
    
    return None


def validate_flow_name(name: str) -> bool:
    """
    Validate a flow name.
    
    Args:
        name: Flow name to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    if not name:
        return False
    
    # Must start with a letter or underscore, then letters, numbers, underscores, and hyphens
    import re
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_-]*$'
    return bool(re.match(pattern, name))


def compile_flow_from_directory(flow_dir: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Compile a flow from its directory structure.
    
    Args:
        flow_dir: Path to the flow directory containing flow.py.
        
    Returns:
        Tuple of (compiled flow data as dictionary, error message).
        If successful, returns (flow_data, None).
        If failed, returns (None, error_message).
    """
    flow_file = flow_dir / "flow.py"
    if not flow_file.exists():
        return None, f"flow.py file not found in {flow_dir}"
    
    try:
        # Add the flow directory to the path so imports work
        sys.path.insert(0, str(flow_dir))
        
        # Import the flow module
        spec = importlib.util.spec_from_file_location("flow_module", flow_file)
        if not spec or not spec.loader:
            return None, "Failed to load flow.py module - check for syntax errors"
            
        flow_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(flow_module)
        
        # Find the flow instance
        flow = None
        if hasattr(flow_module, "flow"):
            flow = getattr(flow_module, "flow")
        else:
            # Scan for Flow instances
            for name, obj in vars(flow_module).items():
                if isinstance(obj, Flow):
                    flow = obj
                    break
        
        if not flow:
            return None, "No Flow instance found in flow.py - make sure you have a 'flow = Flow(...)' variable"
        
        if not isinstance(flow, Flow):
            return None, f"Variable 'flow' is not a Flow instance (found {type(flow).__name__})"
        
        # Compile flow to dictionary
        try:
            return compile_flow(flow), None
        except Exception as e:
            return None, f"Flow validation failed: {str(e)}"
        
    except ImportError as e:
        return None, f"Import error in flow.py: {str(e)}"
    except SyntaxError as e:
        return None, f"Syntax error in flow.py at line {e.lineno}: {str(e)}"
    except Exception as e:
        return None, f"Error compiling flow: {str(e)}"
    finally:
        # Remove the added path
        if str(flow_dir) in sys.path:
            sys.path.remove(str(flow_dir))


def convert_flow_to_python(flow_data: Dict[str, Any]) -> str:
    """
    Convert flow data from API to Python Flow Builder SDK code.
    
    Args:
        flow_data: Flow data from the API.
        
    Returns:
        Python code string defining the flow.
    """
    name = flow_data.get('name', 'Unnamed Flow')
    description = flow_data.get('description', '')
    nodes = flow_data.get('nodes', [])
    edges = flow_data.get('edges', [])
    
    # Start building the Python code
    lines = [
        "from kapso.builder.flows import Flow",
        "from kapso.builder.flows.nodes import (",
        "    SendTextNode,",
        "    WaitForResponseNode, ",
        "    DecideNode,",
        "    AgentNode,",
        "    SendTemplateNode,",
        "    SendInteractiveNode,",
        "    FunctionNode",
        ")",
        "from kapso.builder.flows.edges import Edge",
        "",
        f"# {description}" if description else "",
        f"flow = Flow(",
        f"    name=\"{name}\",",
        f"    description=\"{description}\"" if description else "    description=None",
        ")"
    ]
    
    # Remove empty description comment line if no description
    if not description:
        lines = [line for line in lines if line != "# "]
    
    lines.append("")
    
    # Add nodes
    if nodes:
        lines.append("# Add nodes")
        for node in nodes:
            node_type = node.get('type', 'SendTextNode')
            node_id = node.get('id', 'node')
            node_config = node.get('config', {})
            
            # Create node based on type
            if node_type == 'send_text':
                # Support both 'message' and 'text' fields for backward compatibility
                message = node_config.get('message') or node_config.get('text', 'Hello!')
                lines.append(f"{node_id} = SendTextNode(id=\"{node_id}\", text=\"{message}\")")
            elif node_type == 'wait_for_response':
                lines.append(f"{node_id} = WaitForResponseNode(id=\"{node_id}\")")
            elif node_type == 'decide':
                conditions_str = "[]"  # Simplified for now
                lines.append(f"{node_id} = DecideNode(id=\"{node_id}\", conditions={conditions_str})")
            elif node_type == 'agent':
                agent_id = node_config.get('agent_id', '')
                lines.append(f"{node_id} = AgentNode(id=\"{node_id}\", agent_id=\"{agent_id}\")")
            elif node_type == 'send_template':
                template = node_config.get('template', '')
                lines.append(f"{node_id} = SendTemplateNode(id=\"{node_id}\", template=\"{template}\")")
            elif node_type == 'send_interactive':
                lines.append(f"{node_id} = SendInteractiveNode(id=\"{node_id}\")")
            elif node_type == 'function':
                function_id = node_config.get('function_id', '')
                lines.append(f"{node_id} = FunctionNode(id=\"{node_id}\", function_id=\"{function_id}\")")
            else:
                lines.append(f"{node_id} = SendTextNode(id=\"{node_id}\", text=\"Node: {node_type}\")")
            
            lines.append(f"flow.add_node({node_id})")
        
        lines.append("")
    
    # Add edges
    if edges:
        lines.append("# Add edges")
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            label = edge.get('label', 'next')
            lines.append(f"flow.add_edge(\"{source}\", \"{target}\", \"{label}\")")
    
    return "\n".join(lines)