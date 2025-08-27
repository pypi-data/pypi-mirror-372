"""
Edge definition for the Kapso SDK.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Edge:
    """
    Edge connecting nodes in an agent graph.
    
    An edge represents a transition from one node to another,
    optionally with a condition that determines when the transition occurs.
    """
    source: str
    target: str
    condition: Optional[str] = None


def create_edge(source: str, target: str, condition: Optional[str] = None) -> Edge:
    """
    Create an edge between two nodes.
    
    Args:
        source: Source node name
        target: Target node name
        condition: Optional condition for the edge
        
    Returns:
        An Edge instance
    """
    return Edge(source=source, target=target, condition=condition)
