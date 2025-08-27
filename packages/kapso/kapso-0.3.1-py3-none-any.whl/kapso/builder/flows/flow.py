"""
Flow class for creating deterministic workflows.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set

from .nodes.base import Node
from .edges.edge import Edge

logger = logging.getLogger(__name__)


@dataclass
class Flow:
    """Main Flow class for building deterministic workflows."""
    
    name: str
    description: Optional[str] = None
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    
    def add_node(self, node: Node) -> "Flow":
        """Add a node to the flow."""
        self.nodes.append(node)
        return self
    
    def add_edge(self, source: str, target: str, label: str = "next") -> "Flow":
        """Add an edge between nodes."""
        edge = Edge(source=source, target=target, label=label)
        self.edges.append(edge)
        return self

    def validate(self) -> None:
        """Validate the flow configuration."""
        if not self.nodes:
            raise ValueError("Flow must have at least one node")

        # Get all node IDs
        node_ids = {node.id for node in self.nodes}
        
        # Check for duplicate node IDs
        seen_ids = []
        for node in self.nodes:
            if node.id in seen_ids:
                raise ValueError(f"Duplicate node ID: {node.id}. Node IDs must be unique.")
            seen_ids.append(node.id)

        # Find StartNodes
        start_nodes = [node for node in self.nodes if node.node_type == "start"]
        if len(start_nodes) == 0:
            raise ValueError("Flow must have exactly one StartNode")
        if len(start_nodes) > 1:
            raise ValueError(f"Flow must have exactly one StartNode, found {len(start_nodes)}")

        start_node = start_nodes[0]

        # Validate all edges reference existing nodes
        for edge in self.edges:
            if edge.source not in node_ids:
                raise ValueError(f"Edge references non-existent source node: {edge.source}")
            if edge.target not in node_ids:
                raise ValueError(f"Edge references non-existent target node: {edge.target}")

        # Check StartNode has outgoing edges
        start_has_outgoing = any(edge.source == start_node.id for edge in self.edges)
        if not start_has_outgoing:
            logger.warning(f"StartNode '{start_node.id}' has no outgoing edges - flow cannot progress")

        # Find all reachable nodes from StartNode
        reachable_nodes = self._get_reachable_nodes(start_node.id)
        
        # Warn about unreachable nodes
        for node in self.nodes:
            if node.id not in reachable_nodes:
                logger.warning(f"Node '{node.id}' is not reachable from StartNode")

        # Find nodes with no outgoing edges (potential dead ends)
        nodes_with_outgoing = {edge.source for edge in self.edges}
        for node in self.nodes:
            if node.id not in nodes_with_outgoing and node.node_type != "start":
                # This could be a terminal node, so just warn
                logger.warning(f"Node '{node.id}' has no outgoing edges - potential flow termination point")

    def _get_reachable_nodes(self, start_id: str) -> Set[str]:
        """Get all nodes reachable from a starting node via depth-first search."""
        reachable = set()
        stack = [start_id]
        
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            
            reachable.add(current)
            
            # Add all targets from current node to stack
            for edge in self.edges:
                if edge.source == current and edge.target not in reachable:
                    stack.append(edge.target)
        
        return reachable