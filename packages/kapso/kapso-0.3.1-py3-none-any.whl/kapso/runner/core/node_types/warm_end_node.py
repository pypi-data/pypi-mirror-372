"""
Implementation of the WarmEndNode type.
"""

import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, SystemMessage, trim_messages
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel

from kapso.runner.core.flow_state import State
from kapso.runner.core.node_types.base import NodeType

# Create a logger for this module
logger = logging.getLogger(__name__)


class WarmEndNodeType(NodeType):
    """Warm end node type with basic functionality."""

    @property
    def name(self) -> str:
        """Return the name of the node type."""
        return "WarmEndNode"

    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with node type-specific information.

        Args:
            prompt: The base step prompt
            node_config: Configuration for this node

        Returns:
            Enhanced prompt with node type-specific information
        """
        # Warm end node doesn't need to enhance the prompt
        return prompt

    @NodeType.retry_on_overloaded
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
        Execute the warm end node's action.

        Args:
            state: The current state
            node_config: Configuration for this node
            node_edges: The edges for the current node
            llm: The LLM with tools bound
            llm_without_tools: The LLM without tools bound
            config: The runnable configuration

        Returns:
            The result of the node execution
        """
        configurable = config.get("configurable", {})

        system_prompt = self.generate_system_prompt(configurable)

        response = await llm.ainvoke(
            trim_messages(
                [SystemMessage(content=system_prompt)] + state["full_history"],
                max_tokens=40,
                token_counter=len,
                include_system=True,
                start_on=AIMessage,
            )
        )

        # Log the LLM response
        logger.info("LLM Response:")
        if hasattr(response, "content") and response.content:
            logger.info(f"  Content: {response.content}")
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"  Tool calls: {response.tool_calls}")

        return response
