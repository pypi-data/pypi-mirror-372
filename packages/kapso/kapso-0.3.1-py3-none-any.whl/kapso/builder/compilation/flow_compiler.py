"""
Flow compilation functionality for converting Python Flow objects to backend-compatible JSON.
"""

import json
from typing import Dict, Any

from kapso.builder.flows.flow import Flow


def compile_flow(flow: Flow) -> Dict[str, Any]:
    """
    Compile a Flow object to a dictionary structure compatible with the backend.
    
    This function converts a Python Flow definition into the JSON structure
    expected by UpdateFlowWithDefinitionJob and other backend processing.
    
    Args:
        flow: The Flow object to compile
        
    Returns:
        Dictionary representation ready for backend consumption
    """
    return {
        "name": flow.name,
        "description": flow.description,
        "definition": {
            "nodes": [node.to_dict() for node in flow.nodes],
            "edges": [edge.to_dict() for edge in flow.edges]
        }
    }


def compile_to_json(flow: Flow, indent: int = None) -> str:
    """
    Compile a Flow object to a JSON string.
    
    Args:
        flow: The Flow object to compile
        indent: JSON indentation for pretty printing (None for compact)
        
    Returns:
        JSON string representation of the flow
    """
    flow_dict = compile_flow(flow)
    return json.dumps(flow_dict, indent=indent, ensure_ascii=False)