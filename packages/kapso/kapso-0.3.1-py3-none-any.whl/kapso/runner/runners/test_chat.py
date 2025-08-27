"""
Specialized runner for test chat interactions.
"""

import logging
from typing import Dict, Any, Optional, AsyncGenerator
from kapso.runner.runners.base import BaseRunner
from kapso.runner.channels.models import MessageChannelType
from kapso.runner.channels.factory import configure_adapter
from kapso.core.thread_logging import set_thread_context, clear_thread_context

# Optional token tracking - only available in cloud deployments
try:
    from app.billing.token_tracker import TokenUsageTracker
    HAS_TOKEN_TRACKING = True
except ImportError:
    HAS_TOKEN_TRACKING = False

# Create a logger for this module
logger = logging.getLogger(__name__)

class TestChatRunner(BaseRunner):
    """
    Runner for test chat interactions.

    This runner is optimized for CLI and test environments, with simple
    conversation flow.
    """

    def __init__(self, debug: bool = False):
        """Initialize the test chat runner."""
        super().__init__(debug=debug)
        self.is_first_message = True

    async def run(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message_input: Optional[Dict[str, Any]] = None,
        is_new_conversation: Optional[bool] = None,
        contact_information: Optional[Dict[str, Any]] = None,
        phone_number: Optional[str] = None,  # For backward compatibility
        test_mode: Optional[bool] = True,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        agent_test_chat_id: Optional[str] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        checkpoint_id: Optional[str] = None,
        agent_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a chat message for testing or CLI use.

        Args:
            graph_definition: The graph definition dictionary
            thread_id: Optional thread ID for the conversation
            message_input: Optional message payload as a dictionary
            is_new_conversation: Flag indicating if this is a new conversation (uses self.is_first_message if None)
            contact_information: Optional contact information (phone, name, metadata)
            phone_number: Optional phone number (deprecated, use contact_information)
            test_mode: Flag indicating if test mode is enabled (default True)
            agent_prompt: Optional agent prompt
            llm_config: Optional LLM configuration
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming
            agent_test_chat_id: Optional ID for the test chat

        Returns:
            Dict[str, Any]: The processed chat state
        """

        configure_adapter(
            MessageChannelType.WHATSAPP,
            { "mock": True }
        )
        thread_id = self._get_thread_id(thread_id)
        
        # Set thread context for all logs in this execution
        set_thread_context(thread_id)
        
        try:
            # If is_new_conversation not specified, use the first message flag
            if is_new_conversation is None:
                is_new_conversation = self.is_first_message

            # If contact_information not provided but phone_number is, create contact_information
            if contact_information is None and phone_number is not None:
                contact_information = {"phone_number": phone_number}

            # For logging, extract phone_number from contact_information if available
            log_phone = None
            if contact_information and "phone_number" in contact_information:
                log_phone = contact_information["phone_number"]
            elif phone_number:
                log_phone = phone_number

            logger.info(
                "Processing chat - Phone: %s, New: %s, Agent Prompt: %s",
                log_phone,
                is_new_conversation,
                agent_prompt,
            )
            if message_input:
                logger.debug("Received message payload: %s", message_input)

            graph = self.graph_builder.build_langgraph(graph_definition, agent_version=agent_version or 1)
            
            # Initialize token tracker
            token_tracker = TokenUsageTracker() if HAS_TOKEN_TRACKING else None
            
            # Prepare config (handles checkpoint replay if needed)
            config = await self._prepare_config(
                graph_definition,
                thread_id,
                test_mode or False,  # Ensure boolean
                agent_prompt,
                contact_information=contact_information,
                llm_config=llm_config,
                last_interrupt_tool_call_id=last_interrupt_tool_call_id,
                execution_metadata=execution_metadata,
                checkpoint_id=checkpoint_id,
                graph=graph,  # Pass graph for checkpoint handling
                message_input=message_input,  # Pass message for replay state update
                agent_version=agent_version or 1,
            )
            
            # Add token tracker to callbacks
            if "callbacks" not in config:
                config["callbacks"] = []
            if token_tracker:
                config["callbacks"].append(token_tracker)

            # Add agent_test_chat_id to config if provided
            if agent_test_chat_id:
                config["configurable"]["agent_test_chat_id"] = agent_test_chat_id

            # When replaying from checkpoint, pass None; otherwise prepare input state
            if checkpoint_id:
                # For checkpoint replay, pass None to resume from the checkpoint
                await graph.ainvoke(None, config=config)
            else:
                agent_version = config.get("configurable", {}).get("agent_version", 1)
                input_state = self._prepare_input_state(is_new_conversation, message_input, agent_version)
                await graph.ainvoke(input_state, config=config)

            logger.info("Graph execution completed")

            # After first message, set flag to False
            if self.is_first_message:
                self.is_first_message = False

            state = await graph.aget_state(config)
            return self._format_state_response(state, thread_id)
        finally:
            # Clear thread context when done
            clear_thread_context()

    async def stream(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message_input: Optional[Dict[str, Any]] = None,
        is_new_conversation: Optional[bool] = None,
        contact_information: Optional[Dict[str, Any]] = None,
        phone_number: Optional[str] = None,  # For backward compatibility
        test_mode: Optional[bool] = True,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        agent_test_chat_id: Optional[str] = None,
        delivery_attempt: int = 1,
        execution_metadata: Optional[Dict[str, Any]] = None,
        checkpoint_id: Optional[str] = None,
        agent_version: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a chat message for testing or CLI use with streaming.

        Args:
            graph_definition: The graph definition dictionary
            thread_id: Optional thread ID for the conversation
            message_input: Optional message payload as a dictionary
            is_new_conversation: Flag indicating if this is a new conversation (uses self.is_first_message if None)
            contact_information: Optional contact information (phone, name, metadata)
            phone_number: Optional phone number (deprecated, use contact_information)
            test_mode: Flag indicating if test mode is enabled (default True)
            agent_prompt: Optional agent prompt
            llm_config: Optional LLM configuration
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming
            agent_test_chat_id: Optional ID for the test chat
            delivery_attempt: The delivery attempt counter

        Yields:
            Dict[str, Any]: Intermediate conversation states
        """
        configure_adapter(
            MessageChannelType.WHATSAPP,
            { "mock": True }
        )
        thread_id = self._get_thread_id(thread_id)
        
        # Set thread context for all logs in this execution
        set_thread_context(thread_id)

        try:
            # If is_new_conversation not specified, use the first message flag
            if is_new_conversation is None:
                is_new_conversation = self.is_first_message

            # If contact_information not provided but phone_number is, create contact_information
            if contact_information is None and phone_number is not None:
                contact_information = {"phone_number": phone_number}

            # For logging, extract phone_number from contact_information if available
            log_phone = None
            if contact_information and "phone_number" in contact_information:
                log_phone = contact_information["phone_number"]
            elif phone_number:
                log_phone = phone_number

            logger.info(
                "Streaming chat - Phone: %s, New: %s, Agent Prompt: %s, Delivery Attempt: %s",
                log_phone,
                is_new_conversation,
                agent_prompt,
                delivery_attempt,
            )

            if message_input:
                message_str = str(message_input)
                logger.debug(
                    "Message content (truncated): %s...",
                    message_str[:100] if len(message_str) > 100 else message_str,
                )
            graph = self.graph_builder.build_langgraph(graph_definition, agent_version=agent_version or 1)
            
            # Initialize token tracker
            token_tracker = TokenUsageTracker() if HAS_TOKEN_TRACKING else None
            
            # Prepare config (handles checkpoint replay if needed)
            config = await self._prepare_config(
                graph_definition,
                thread_id,
                test_mode or False,  # Ensure boolean
                agent_prompt,
                contact_information=contact_information,
                llm_config=llm_config,
                last_interrupt_tool_call_id=last_interrupt_tool_call_id,
                execution_metadata=execution_metadata,
                checkpoint_id=checkpoint_id,
                graph=graph,  # Pass graph for checkpoint handling
                message_input=message_input,  # Pass message for replay state update
                agent_version=agent_version or 1,
            )
            
            # Add token tracker to callbacks
            if "callbacks" not in config:
                config["callbacks"] = []
            if token_tracker:
                config["callbacks"].append(token_tracker)

            # Add agent_test_chat_id to config if provided
            if agent_test_chat_id:
                config["configurable"]["agent_test_chat_id"] = agent_test_chat_id

            # Determine input based on whether we're replaying from checkpoint
            if checkpoint_id and message_input is None:
                # For checkpoint replay, pass None to resume from the checkpoint
                input_to_stream = None
            else:
                # Normal streaming for non-checkpoint execution
                agent_version = config.get("configurable", {}).get("agent_version", 1)
                input_to_stream = self._prepare_input_state(is_new_conversation, message_input, agent_version)

            # Stream the graph execution
            async for event in graph.astream(input_to_stream, config=config, stream_mode="updates"):
                # Create a proper deep copy of the config for aget_state
                config_copy = config.copy()
                config_copy['configurable'] = config['configurable'].copy()
                if 'checkpoint_id' in config_copy['configurable']:
                    del config_copy['configurable']['checkpoint_id']
                state_after_step = await graph.aget_state(config_copy)
                yield self._format_state_response(state_after_step, thread_id, is_update=True)

            # After streaming is complete, yield the final state
            # Create a proper deep copy for the final state check too
            final_config = config.copy()
            final_config['configurable'] = config['configurable'].copy()
            if 'checkpoint_id' in final_config['configurable']:
                del final_config['configurable']['checkpoint_id']
            final_state = await graph.aget_state(final_config)
            final_response = self._format_state_response(final_state, thread_id, is_update=False)
            
            # Add token usage to final response
            usage_summary = token_tracker.get_usage_summary() if token_tracker else {}
            if usage_summary and usage_summary.get("total_tokens", 0) > 0:
                final_response["token_usage"] = {
                    "provider": llm_config.get("provider_name", "Anthropic") if llm_config else "Anthropic",
                    "model": llm_config.get("provider_model_name", "unknown") if llm_config else "unknown",
                    "input_tokens": usage_summary["input_tokens"],
                    "output_tokens": usage_summary["output_tokens"],
                    "total_tokens": usage_summary["total_tokens"],
                    "cache_creation_tokens": usage_summary["cache_creation_tokens"],
                    "cache_read_tokens": usage_summary["cache_read_tokens"]
                }
                logger.info(f"Token usage tracked: {usage_summary}")
            
            yield final_response

            # After first message, set flag to False
            if self.is_first_message:
                self.is_first_message = False

            logger.info("Streaming completed")

        except Exception as e:
            logger.error(
                f"Error during graph execution (Attempt {delivery_attempt}): {str(e)}",
                exc_info=True,
            )
            raise
        finally:
            # Clear thread context when done
            clear_thread_context()