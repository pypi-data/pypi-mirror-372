"""
Base classes for node types.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Dict, List, Type, Union

from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel

from kapso.runner.core.flow_prompts import get_system_prompt, get_system_prompt_blocks
from kapso.runner.core.flow_state import State


class NodeType(ABC):
    """Base class for all node types."""

    # Default retry configuration
    DEFAULT_MAX_RETRIES = 5
    DEFAULT_BACKOFF_SECONDS = 2  # Simple fixed backoff

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the node type."""
        pass

    @abstractmethod
    def enhance_prompt(self, prompt: str, node_config: Dict[str, Any]) -> str:
        """
        Enhance the step prompt with node type-specific information.

        Args:
            prompt: The base step prompt
            node_config: Configuration for this node

        Returns:
            Enhanced prompt with node type-specific information
        """
        pass

    @abstractmethod
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
        Execute the node's action.

        Note: Subclasses should apply the @NodeType.retry_on_overloaded decorator to this method
        to enable automatic retries for Anthropic API overload errors.

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
        pass

    @staticmethod
    def retry_on_overloaded(func):
        """
        Decorator to retry functions when Anthropic API is overloaded.
        """
        logger = logging.getLogger(__name__)

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            max_retries = self.DEFAULT_MAX_RETRIES
            backoff_seconds = self.DEFAULT_BACKOFF_SECONDS

            # Get custom retry config if available in node_config
            if "node_config" in kwargs and kwargs["node_config"]:
                retry_config = kwargs["node_config"].get("retry_config", {})
                max_retries = retry_config.get("max_retries", max_retries)
                backoff_seconds = retry_config.get("backoff_seconds", backoff_seconds)

            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    # Check for interrupt objects (from langgraph.types.interrupt) which are not errors
                    error_str = str(e)
                    if "Interrupt" in error_str and "message" in error_str:
                        logger.info(f"Detected interrupt, not an error, returning: {error_str}")
                        # Re-raise so the interrupt is properly handled
                        raise

                    # Check if it's an Anthropic overload error
                    is_overloaded = False

                    # Check the error structure
                    if hasattr(e, "error"):
                        # Direct attribute access
                        if isinstance(e.error, dict) and e.error.get("type") == "overloaded_error":
                            is_overloaded = True
                    # Check the string representation for the pattern
                    if "overloaded_error" in error_str and "Overloaded" in error_str:
                        is_overloaded = True

                    # If it's not an overload error or it's the last attempt, re-raise
                    if not is_overloaded or attempt == max_retries:
                        logger.error(
                            f"Error not handled by retry (attempt {attempt + 1}/{max_retries + 1}): {str(e)}"
                        )
                        raise

                    # Log retry attempt
                    logger.warning(
                        f"Anthropic API overloaded. Retry {attempt + 1}/{max_retries} "
                        f"after {backoff_seconds}s backoff"
                    )

                    # Wait before retry
                    await asyncio.sleep(backoff_seconds)

            # This should not be reached, but just in case
            raise RuntimeError("Unexpected error: Max retries exceeded")

        return wrapper

    def generate_system_prompt(
        self, configurable: Dict[str, Any]
    ) -> Union[str, List[Dict[str, Any]]]:
        """Prepare the system prompt for the node type with optional cache control for Anthropic."""
        # Get LLM configuration
        llm_config = configurable.get("llm_config", {})
        if llm_config is None:
            llm_config = {}

        provider = llm_config.get("provider_name", "")

        # Use contact_information if available, otherwise fall back to phone_number for compatibility
        contact_information = configurable.get("contact_information", None)
        if contact_information is None and configurable.get("phone_number"):
            # Create contact_information from phone_number for backward compatibility
            contact_information = {"phone_number": configurable.get("phone_number", "")}
            
        agent_prompt = configurable.get("agent_prompt", "")
        agent_version = configurable.get("agent_version", 1)

        # Use block format with cache control for Anthropic
        if provider == "Anthropic":
            return get_system_prompt_blocks(contact_information, agent_prompt, agent_version)

        # Use string format for other providers
        return get_system_prompt(contact_information, agent_prompt, agent_version)

    def generate_base_step_prompt(
        self, node_config: Dict[str, Any], node_edges: List[Dict[str, Any]], agent_version: int = 1
    ) -> str:
        """Generate the step prompt for the node type."""
        # Format edges information
        edge_entries = []
        for edge in node_edges:
            edge_entry = "<node>\n"
            edge_entry += f"    <name>{edge['to']}</name>\n"
            if edge.get("label"):  # Only include condition if label exists
                edge_entry += f"    <condition_to_move_to_this_node>{edge['label']}</condition_to_move_to_this_node>\n"
            edge_entry += "</node>"
            edge_entries.append(edge_entry)

        edges_info = "\n".join(edge_entries) + "\n"

        # Create the base step prompt with clear structure
        if agent_version == 2:
            # V2: Task-oriented phrasing
            base_step_prompt = f"""
<current_node>
You are at node: "{node_config['name']}"
<instructions>
Your task at this node:
{node_config['prompt']}
</instructions>
</current_node>

<available_next_nodes>
The following nodes are available to move to next:
{edges_info}

You must only move to nodes that are listed above.
</available_next_nodes>

Complete the task according to the instructions.
"""
        else:
            # V1: Original first-person phrasing
            base_step_prompt = f"""
<current_node>
I am currently at node: "{node_config['name']}"
<instructions>
The instructions for this node are:
{node_config['prompt']}
</instructions>
</current_node>

<available_next_nodes>
Only the following nodes are available to move to next:
{edges_info}

Only move to nodes that are listed in the available next nodes.
</available_next_nodes>

I need to follow the instructions.
"""
        return base_step_prompt

    def generate_step_prompt(
        self, node_config: Dict[str, Any], node_edges: List[Dict[str, Any]], agent_version: int = 1
    ) -> str:
        """Generate the step prompt for the node type."""
        base_step_prompt = self.generate_base_step_prompt(node_config, node_edges, agent_version)
        enhanced_prompt = self.enhance_prompt(base_step_prompt, node_config)
        return enhanced_prompt.rstrip()


class NodeTypeRegistry:
    """Registry for node types."""

    def __init__(self):
        self._registry: Dict[str, Type[NodeType]] = {}

    def register(self, node_type_class: Type[NodeType]) -> None:
        """Register a node type class."""
        instance = node_type_class()
        self._registry[instance.name] = node_type_class

    def get(self, name: str) -> Type[NodeType]:
        """Get a node type class by name."""
        if name not in self._registry:
            raise ValueError(f"Node type '{name}' not registered")
        return self._registry[name]

    def create(self, name: str) -> NodeType:
        """Create a node type instance by name."""
        node_type_class = self.get(name)
        return node_type_class()

    def list_types(self) -> List[str]:
        """List all registered node types."""
        return list(self._registry.keys())


# Create a global registry instance
node_type_registry = NodeTypeRegistry()
