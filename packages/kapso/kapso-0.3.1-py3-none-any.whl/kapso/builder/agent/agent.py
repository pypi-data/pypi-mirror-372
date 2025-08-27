"""
Agent definition for the Kapso SDK.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

from kapso.builder.nodes.base import Node
from kapso.builder.edges.edge import Edge, create_edge
from kapso.builder.agent.constants import START_NODE, END_NODE
from kapso.builder.nodes.factory import DefaultNode

logger = logging.getLogger(__name__)
@dataclass
class Agent:
    """
    Agent definition in the Kapso SDK.

    An agent consists of nodes connected by edges, forming a directed graph.
    """
    name: str
    system_prompt: Optional[str] = None
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    message_debounce_seconds: Optional[int] = None

    def add_node(self, node: Union[Node, str]) -> "Agent":
        """Add a node to the agent.
        
        Args:
            node: Either a Node object or a string (START_NODE or END_NODE)
        
        Returns:
            The Agent instance for method chaining
        """
        # Handle special string constants
        if isinstance(node, str):
            if node == START_NODE:
                node = DefaultNode(name=START_NODE, prompt="")
            elif node == END_NODE:
                node = DefaultNode(name=END_NODE, prompt="")
            else:
                raise ValueError(f"Invalid string node: {node}. Only {START_NODE} and {END_NODE} are allowed as string nodes.")
        
        # Check for duplicate node names
        if any(n.name == node.name for n in self.nodes):
            raise ValueError(f"Duplicate node name: {node.name}. Node names must be unique.")

        self.nodes.append(node)
        return self

    def add_edge(self, source: Union[str, Node], target: Union[str, Node], condition: Optional[str] = None) -> "Agent":
        """Add an edge between two nodes.
        
        Args:
            source: Source node (can be a Node object or node name string)
            target: Target node (can be a Node object or node name string)
            condition: Optional condition for the edge
        """
        # Extract node names if Node objects are passed
        source_name = source.name if isinstance(source, Node) else source
        target_name = target.name if isinstance(target, Node) else target
        
        edge = Edge(source=source_name, target=target_name, condition=condition)
        self.edges.append(edge)
        return self

    def validate(self) -> None:
        """Validate the agent configuration."""
        if not self.nodes:
            raise ValueError("Agent must have at least one node")

        node_names = {node.name for node in self.nodes}

        for edge in self.edges:
            if edge.source not in node_names and edge.source != START_NODE:
                raise ValueError(f"Edge references non-existent source node: {edge.source}")

            if edge.target not in node_names and edge.target != END_NODE:
                raise ValueError(f"Edge references non-existent target node: {edge.target}")

        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)

        for node in self.nodes:
            # Skip connectivity check for global nodes as they can be triggered from any state
            if not node.global_ and node.name not in connected_nodes:
                logger.warning(f"Node '{node.name}' is not connected to any other node.")

        has_start_edge = any(edge.source == START_NODE for edge in self.edges)
        has_end_edge = any(edge.target == END_NODE for edge in self.edges)

        if not has_start_edge:
            logger.warning(f"No edge from {START_NODE} found in the agent graph.")

        if not has_end_edge:
            logger.warning(f"No edge to {END_NODE} found in the agent graph.")


def create_agent(
    name: str,
    system_prompt: Optional[str] = None,
    nodes: Optional[List[Union[Node, str]]] = None,
    edges: Optional[List[Dict[str, str]]] = None,
    message_debounce_seconds: Optional[int] = None
) -> Agent:
    """
    Create an agent with the specified configuration.

    Args:
        name: The name of the agent
        system_prompt: System prompt for the agent
        nodes: List of nodes in the agent graph (can include START_NODE and END_NODE strings)
        edges: List of edges connecting nodes
        message_debounce_seconds: Message debounce time in seconds

    Returns:
        An Agent instance
    """
    agent = Agent(
        name=name,
        system_prompt=system_prompt,
        message_debounce_seconds=message_debounce_seconds
    )
    
    # Add nodes using add_node method to handle string constants
    if nodes:
        for node in nodes:
            agent.add_node(node)

    if edges:
        for edge in edges:
            agent.add_edge(
                source=edge["source"],
                target=edge["target"],
                condition=edge.get("condition")
            )

    return agent
