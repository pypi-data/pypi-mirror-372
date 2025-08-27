"""
Contains graph building utilities for the flow agent.
"""

from typing import Callable, Dict, Any, Optional
from importlib import import_module

from langgraph.graph import StateGraph

from kapso.runner.core.tool_generator import (
    generate_standard_tools_for_node_type,
    tool_requires_interrupt,
    get_interrupt_handler,
)
from kapso.runner.core.tools.handlers.generic_handler import generic_tool_handler


# Registry of handler modules and their functions
HANDLER_REGISTRY = {
    "ask_user_for_input": "kapso.runner.core.tools.handlers.messaging_handlers",
    "enter_idle_state": "kapso.runner.core.tools.handlers.messaging_handlers",
    "wait_for_user": "kapso.runner.core.tools.handlers.messaging_handlers",
    "send_whatsapp_template_message": "kapso.runner.core.tools.handlers.messaging_handlers",
    "handle_user_message": "kapso.runner.core.tools.handlers.messaging_handlers",
    "stop_execution": "kapso.runner.core.tools.handlers.messaging_handlers",
}


def get_handler_function(handler_name: str) -> Optional[Callable]:
    """
    Dynamically imports and returns a handler function by name.
    
    Args:
        handler_name: Name of the handler function
        
    Returns:
        Handler function or None if not found
    """
    if handler_name not in HANDLER_REGISTRY:
        return None
        
    module_path = HANDLER_REGISTRY[handler_name]
    try:
        module = import_module(module_path)
        return getattr(module, handler_name, None)
    except (ImportError, AttributeError):
        return None


def add_generic_node(
    builder: StateGraph, name: str, func: Callable, tools: list, node_type: str = "DefaultNode", agent_version: int = 1
):
    """
    Add a generic node to the graph with appropriate edges and tool nodes.

    Args:
        builder: The StateGraph builder
        name: The name of the node
        func: The function to execute for this node
        tools: List of tools available to this node
        node_type: The type of the node (DefaultNode, WebhookNode, etc.)
    """
    # Add the main node
    builder.add_node(name, func)

    # Add generic tool node for handling non-interrupt tool calls
    builder.add_node(f"generic_tool_node_{name}", generic_tool_handler)
    builder.add_edge(f"generic_tool_node_{name}", name)

    # Generate tools for this node type to find interrupt tools
    node_tools = generate_standard_tools_for_node_type(node_type, agent_version)

    # Add interrupt tool nodes based on the tools available to this node type
    for tool in node_tools:
        # Check if this tool requires an interrupt
        if tool_requires_interrupt(tool):
            # Get the handler for this tool
            handler_name = get_interrupt_handler(tool)

            # Skip if no handler is defined
            if not handler_name:
                continue

            # Get the tool name
            if hasattr(tool, "metadata") and hasattr(tool.metadata, "name"):
                tool_name = tool.metadata.name
            else:
                continue

            # Skip MoveToNextNode as it's handled separately
            if tool_name == "MoveToNextNode":
                continue

            # Convert CamelCase to snake_case for the tool name
            snake_case_tool_name = "".join(
                ["_" + c.lower() if c.isupper() else c for c in tool_name]
            ).lstrip("_")

            # Get the handler function dynamically
            handler = get_handler_function(handler_name)
            if not handler:
                continue

            handler_node_name = f"{snake_case_tool_name}_{name}"
            builder.add_node(handler_node_name, handler)
            builder.add_edge(handler_node_name, name)
