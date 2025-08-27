"""
Implementation of the WebhookNode type.
"""

import json
import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, SystemMessage, trim_messages
from langchain_core.runnables.config import RunnableConfig

from kapso.runner.core.flow_state import State
from kapso.runner.core.node_types.base import NodeType

# Create a logger for this module
logger = logging.getLogger(__name__)


class WebhookNodeType(NodeType):
    """Node type for making webhook requests."""

    @property
    def name(self) -> str:
        """Return the name of the node type."""
        return "WebhookNode"

    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with node type-specific information.

        Args:
            prompt: The base step prompt
            node_config: Configuration for this node

        Returns:
            Enhanced prompt with node type-specific information
        """
        # Process webhook configuration if present
        if "webhook" in node_config:
            webhook_config = node_config["webhook"]
            logger.info(f"Adding webhook configuration to prompt: {webhook_config}")

            # Format the webhook configuration as a readable string
            webhook_info = json.dumps(webhook_config, indent=2)

            # Add webhook configuration to the prompt
            enhanced_prompt = f"""
            {prompt}

            The webhook configuration for this node is:
            <webhook_config>
            {webhook_info}
            </webhook_config>
            """
            return enhanced_prompt

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
        Execute the webhook node's action.

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

        # 3. Return the response
        return response
