import logging
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from kapso.runner.core import global_nodes
from kapso.runner.core.flow_graph import add_generic_node
from kapso.runner.core.flow_nodes import new_node_agent
from kapso.runner.core.flow_state import State
from kapso.runner.core.tools.handlers.routing_handler import subgraph_router

# Create a logger for this module
logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Responsible for building a LangGraph StateGraph from a graph definition dictionary.

    This class transforms a graph definition (typically from the UI) into a compiled LangGraph
    StateGraph that can be executed by the runners.
    """

    def __init__(self, checkpointer=None):
        """
        Initialize the GraphBuilder with an optional checkpointer.

        Args:
            checkpointer: The checkpointer to use for the compiled graph
        """
        self.checkpointer = checkpointer

    def node_id_to_name(self, graph_definition: Dict) -> Dict[str, Any]:
        """
        Create a mapping from node IDs to node names.

        Args:
            graph_definition: The graph definition dictionary

        Returns:
            Dict mapping node IDs to node names
        """
        return {node["id"]: node["name"] for node in graph_definition["nodes"]}

    def nodes_by_name(self, graph_definition: Dict) -> Dict[str, Any]:
        """
        Create a dictionary of nodes indexed by name, with global node information.

        Args:
            graph_definition: The graph definition dictionary

        Returns:
            Dict of nodes by name with global node information
        """
        nodes_dict = {node["name"]: node for node in graph_definition["nodes"]}

        # Use helper functions to handle global nodes
        global_nodes_list = global_nodes.identify_global_nodes(graph_definition)
        non_global_nodes_list = global_nodes.identify_non_global_nodes(graph_definition)

        return global_nodes.enrich_nodes_by_name(
            nodes_dict, global_nodes_list, non_global_nodes_list
        )

    def node_edges(self, graph_definition: Dict) -> Dict[str, Any]:
        """
        Create a dictionary of edges for each node, with global node handling.

        Args:
            graph_definition: The graph definition dictionary

        Returns:
            Dict mapping node names to their edges
        """
        # Create edges mapping
        node_edges = {}

        # Create regular edges from the graph definition
        for edge in graph_definition["edges"]:
            from_name = self.node_id_to_name(graph_definition)[edge["from"]]
            if from_name not in node_edges:
                node_edges[from_name] = []
            node_edges[from_name].append(
                {
                    "from": from_name,
                    "to": self.node_id_to_name(graph_definition)[edge["to"]],
                    "label": edge.get("label", None),
                }
            )

        # Use helper functions to handle global nodes
        global_nodes_list = global_nodes.identify_global_nodes(graph_definition)
        non_global_nodes_list = global_nodes.identify_non_global_nodes(graph_definition)

        return global_nodes.enrich_node_edges(node_edges, non_global_nodes_list, global_nodes_list)

    def build_langgraph(self, graph_definition: Dict, agent_version: int = 1) -> CompiledStateGraph:
        """
        Build a LangGraph StateGraph from a graph definition.

        This method transforms a graph definition into a compiled LangGraph StateGraph
        that can be executed by the runners.

        Args:
            graph_definition: The graph definition dictionary

        Returns:
            A compiled LangGraph StateGraph
        """
        builder = StateGraph(State)

        # Convert ids to names for easier lookup
        id_to_name = self.node_id_to_name(graph_definition)

        # Create edges mapping
        node_edges = self.node_edges(graph_definition)

        # Identify global nodes
        global_nodes_list = global_nodes.identify_global_nodes(graph_definition)

        # Build the graph
        for node in graph_definition["nodes"]:
            if node["name"] == START:
                for edge in graph_definition["edges"]:
                    if edge["from"] == node["id"]:
                        builder.add_edge(START, id_to_name[edge["to"]])
                continue

            if node["name"] == END:
                continue

            # Get node type, default to "default" if not specified
            node_type = node.get("type", "default")

            # Skip global nodes in this loop - they'll be handled per node
            if not node.get("global", False):
                # Add normal node
                add_generic_node(
                    builder,
                    node["name"],
                    new_node_agent(node, node_edges.get(node["name"], [])),
                    [],  # tools list
                    node_type,  # Pass the node type
                    agent_version,  # Pass the agent version
                )

                # Add global node access points for this node
                global_nodes.add_global_node_access_points(
                    builder, node["name"], global_nodes_list, node_edges, agent_version
                )

        builder.add_node("subgraph_router", subgraph_router)

        return builder.compile(checkpointer=self.checkpointer)