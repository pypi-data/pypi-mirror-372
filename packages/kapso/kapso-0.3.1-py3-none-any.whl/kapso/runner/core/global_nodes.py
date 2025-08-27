"""
Helper functions for handling global nodes in the flow agent.
"""

from typing import Any, Dict, List

from langgraph.graph import END, START, StateGraph

from kapso.runner.core.flow_nodes import new_node_agent
from kapso.runner.core.flow_graph import add_generic_node


def identify_global_nodes(graph_definition: Dict) -> List[Dict[str, Any]]:
    """
    Identify global nodes in the graph definition.

    Args:
        graph_definition: The graph definition dictionary

    Returns:
        List of global node configurations
    """
    return [
        node
        for node in graph_definition["nodes"]
        if node.get("global", False) and node["name"] != START and node["name"] != END
    ]


def identify_non_global_nodes(graph_definition: Dict) -> List[str]:
    """
    Identify non-global nodes in the graph definition.

    Args:
        graph_definition: The graph definition dictionary

    Returns:
        List of non-global node names
    """
    return [
        node["name"]
        for node in graph_definition["nodes"]
        if not node.get("global", False) and node["name"] != START and node["name"] != END
    ]


def get_global_node_access_name(global_node_name: str, node_name: str) -> str:
    """
    Generate the access name for a global node from a specific node.

    Args:
        global_node_name: The name of the global node
        node_name: The name of the node accessing the global node

    Returns:
        The access name for the global node
    """
    return f"use_{global_node_name}__at__{node_name}"


def add_global_node_access_points(
    builder: StateGraph,
    node_name: str,
    global_nodes: List[Dict[str, Any]],
    node_edges: Dict[str, List[Dict[str, Any]]],
    agent_version: int = 1,
) -> None:
    """
    Add global node access points for a specific node.

    Args:
        builder: The StateGraph builder
        node_name: The name of the node
        global_nodes: List of global node configurations
        node_edges: Dictionary of edges for each node
    """
    for global_node in global_nodes:
        global_node_name = global_node["name"]
        global_node_access_name = get_global_node_access_name(global_node_name, node_name)

        # Get node type, default to "DefaultNode" if not specified
        node_type = global_node.get("type", "DefaultNode")

        # Add the global node with proper agent version
        add_generic_node(
            builder,
            global_node_access_name,
            new_node_agent(global_node, node_edges.get(global_node_name, [])),
            [],  # tools list
            node_type,  # Pass the node type
            agent_version,  # Pass the agent version
        )

        # Add edge back to the original node
        builder.add_edge(global_node_access_name, node_name)


def enrich_node_edges(
    node_edges: Dict[str, List[Dict[str, Any]]],
    non_global_nodes: List[str],
    global_nodes: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Enrich node edges with edges to global nodes.

    Args:
        node_edges: The existing node edges dictionary
        non_global_nodes: List of non-global node names
        global_nodes: List of global node configurations

    Returns:
        Updated node edges dictionary
    """
    # First add edges from regular nodes to global nodes
    for node_name in non_global_nodes:
        if node_name not in node_edges:
            node_edges[node_name] = []

        for global_node in global_nodes:
            global_node_name = global_node["name"]
            global_node_access_name = get_global_node_access_name(global_node_name, node_name)

            node_edges[node_name].append(
                {
                    "from": node_name,
                    "to": global_node_access_name,
                    "label": global_node.get(
                        "global_condition", f"Access global node: {global_node_name}"
                    ),
                }
            )
    
    # Add return edges from global node access points to their triggering nodes
    for node_name in non_global_nodes:
        for global_node in global_nodes:
            global_node_name = global_node["name"]
            global_node_access_name = get_global_node_access_name(global_node_name, node_name)
            
            # Create edges list for this global node access point if it doesn't exist
            if global_node_access_name not in node_edges:
                node_edges[global_node_access_name] = []
                
            # Add edge back to the triggering node with return information
            node_edges[global_node_access_name].append(
                {
                    "from": global_node_access_name,
                    "to": node_name,
                    "label": f"Return to the triggering node '{node_name}' after global node execution is complete",
                    "is_return_path": True,
                    "triggering_node": node_name
                }
            )

    return node_edges


def enrich_nodes_by_name(
    nodes_dict: Dict[str, Any], global_nodes: List[Dict[str, Any]], non_global_nodes: List[str]
) -> Dict[str, Any]:
    """
    Enrich nodes dictionary with global node access points.

    Args:
        nodes_dict: The existing nodes dictionary
        global_nodes: List of global node configurations
        non_global_nodes: List of non-global node names

    Returns:
        Updated nodes dictionary
    """
    for global_node in global_nodes:
        for node_name in non_global_nodes:
            global_node_access_name = get_global_node_access_name(global_node["name"], node_name)

            # Create a copy of the global node with a modified name
            access_node = global_node.copy()
            access_node["name"] = global_node_access_name
            access_node["original_name"] = global_node["name"]
            # Preserve the global attribute from the original node
            access_node["global"] = global_node.get("global", False)
            # Add the triggering node information
            access_node["triggering_node"] = node_name
            nodes_dict[global_node_access_name] = access_node

    return nodes_dict
