"""
Implementation of the WhatsappTemplateNode type.
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


class WhatsappTemplateNodeType(NodeType):
    """Node type for sending WhatsApp templates."""

    @property
    def name(self) -> str:
        """Return the name of the node type."""
        return "WhatsappTemplateNode"

    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with node type-specific information.

        Args:
            prompt: The base step prompt
            node_config: Configuration for this node

        Returns:
            Enhanced prompt with node type-specific information
        """
        # Process WhatsApp template configuration if present
        if "whatsapp_template" in node_config:
            template_config = node_config["whatsapp_template"]
            logger.info(f"Adding WhatsApp template configuration to prompt: {template_config}")
            # Format the template configuration as a readable string
            template_info = json.dumps(template_config, indent=2)

            # Add template configuration to the prompt
            enhanced_prompt = f"""
{prompt}

<whatsapp_template_config>
The WhatsApp template configuration for this node is:

{template_info}

Use the SendWhatsappTemplateMessage tool with these parameters to complete this step.
</whatsapp_template_config>
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
        Execute the WhatsApp template node's action.

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

        # Return the response
        return response
