"""
Implementation of the HandoffNode type.
"""

import logging
from typing import Any, Dict, List

from langchain_core.runnables.config import RunnableConfig
from langgraph.types import interrupt
from pydantic import BaseModel

from kapso.runner.core.flow_state import State
from kapso.runner.core.node_types.base import NodeType

# Create a logger for this module
logger = logging.getLogger(__name__)


class HandoffNodeType(NodeType):
    """Node type for handoff operations."""

    @property
    def name(self) -> str:
        """Return the name of the node type."""
        return "HandoffNode"

    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with node type-specific information.
        HandoffNode doesn't need to enhance the prompt.
        """
        return prompt

    async def execute(
        self,
        state: State,
        node_config: Dict[str, Any],
        node_edges: List[Dict[str, Any]],
        llm,
        llm_without_tools,
        config: RunnableConfig,
    ) -> Any:
        """
        Execute the handoff node's action.
        Simply interrupts the flow to wait for user input.
        """
        logger.info("Executing handoff node")
        return interrupt({"reason": state["handoff_reason"]})
