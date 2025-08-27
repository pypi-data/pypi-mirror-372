"""
Implementation of the SubagentNode type.
"""

import json
import logging
from typing import Any, Dict, List, cast

from langchain_core.messages import AIMessage, SystemMessage, trim_messages
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel

from kapso.runner.core.flow_state import State
from kapso.runner.core.node_types.base import NodeType
from kapso.runner.core.tools.knowledge_base.kb_utils import list_available_knowledge_bases

# Create a logger for this module
logger = logging.getLogger(__name__)


class SubagentNodeType(NodeType):
    """Node type for delegating tasks to specialized subagents with access to multiple tools."""

    @property
    def name(self) -> str:
        """Return the name of the node type."""
        return "SubagentNode"

    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with subagent-specific information.

        Args:
            prompt: The base step prompt
            node_config: Configuration for this node

        Returns:
            Enhanced prompt with subagent configuration
        """
        enhanced_prompt = prompt

        # Process subagent configuration if present
        if "subagent" in node_config:
            subagent_config = node_config["subagent"]
            logger.info(f"Adding subagent configuration to prompt.")

            enhanced_prompt += f"\n\nYou are acting as a specialized subagent with multiple capabilities."

            # Process knowledge base configuration if present
            if "knowledge_bases" in subagent_config and subagent_config["knowledge_bases"]:
                # List all available knowledge bases for this node
                available_kbs = list_available_knowledge_bases(node_config)

                if available_kbs:
                    # Enhance the prompt with knowledge base information
                    enhanced_prompt += f"\n\n<knowledge_bases>\nYou have access to the following knowledge base(s): {', '.join(available_kbs)}\nYou can use the kb_retrieval tool to search for relevant information in these knowledge bases.\n</knowledge_bases>"

            # Add WhatsApp template configuration if present
            if "whatsapp_templates" in subagent_config and subagent_config["whatsapp_templates"]:
                templates = subagent_config["whatsapp_templates"]

                # Format templates for prompt
                template_info = []
                for template in templates:
                    template_info.append({
                        "template_name": template.get("template_name", ""),
                        "parameters": template.get("template_parameters", {}),
                        "phone_number": template.get("phone_number", ""),
                        "description": template.get("description", "")
                    })

                templates_json = json.dumps(template_info, indent=2)
                enhanced_prompt += f"""
<whatsapp_template_config>
The WhatsApp template configuration for this node is:

{templates_json}

Use the SendWhatsappTemplateMessage tool with this information to send these templates.
</whatsapp_template_config>
"""
        return enhanced_prompt

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
        Execute the subagent node's action.

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

        # Store current node in state for tools to access
        state["current_node"] = node_config

        # Generate the system prompt
        system_prompt = self.generate_system_prompt(configurable)

        # Invoke the LLM with the enhanced prompts
        response = await llm.ainvoke(
            trim_messages(
                [SystemMessage(content=system_prompt)] + state["full_history"],
                max_tokens=40,
                token_counter=len,
                include_system=True,
                start_on=AIMessage,
            )
        )

        return response