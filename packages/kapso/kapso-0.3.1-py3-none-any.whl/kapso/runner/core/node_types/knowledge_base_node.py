"""
Implementation of the KnowledgeBaseNode type.
"""

import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, SystemMessage, trim_messages
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel

from kapso.runner.core.flow_state import State
from kapso.runner.core.node_types.base import NodeType
from kapso.runner.core.tools.knowledge_base.kb_utils import list_available_knowledge_bases

# Create a logger for this module
logger = logging.getLogger(__name__)


class KnowledgeBaseNodeType(NodeType):
    """Knowledge base node type with basic functionality."""

    @property
    def name(self) -> str:
        """Return the name of the node type."""
        return "KnowledgeBaseNode"

    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with node type-specific information.

        Args:
            prompt: The base step prompt
            node_config: Configuration for this node

        Returns:
            Enhanced prompt with node type-specific information
        """
        # Check if knowledge base is provided in the node_config
        if (
            "knowledge_base" in node_config
            and "knowledge_base_text" in node_config["knowledge_base"]
        ):
            kb_key = node_config["knowledge_base"].get("key", f"kb_{node_config['name']}")
            logger.info(
                f"Node '{node_config['name']}' has knowledge base with key '{kb_key}'"
            )

            # List all available knowledge bases in this node
            available_kbs = list_available_knowledge_bases(node_config)

            # Enhance the prompt with knowledge base information
            enhanced_prompt = f"""
{prompt}

<knowledge_base>
You have access to the following knowledge base(s): {', '.join(available_kbs)}
You can use the kb_retrieval tool to search for relevant information in the knowledge base.
The knowledge base contains important context that you should use to answer questions.
DO NOT make up information. If the information is not in the knowledge base, say so.
Always use tools to send messages to the user.
</knowledge_base>
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
        Execute the knowledge base node's action.

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
