"""
Specialized runner for standard and streaming conversation execution.
"""

import logging
from typing import Dict, Any, Optional, AsyncGenerator

from langgraph.types import Command
from kapso.runner.runners.base import BaseRunner
from kapso.runner.runners.types import ErrorCallback
from kapso.runner.utils.interrupt_utils import is_redundant_retry_input
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

class ExecutionRunner(BaseRunner):
    """
    Runner for standard and streaming conversation execution.

    This runner handles both synchronous and streaming conversations,
    with support for interrupts and retries.
    """

    def __init__(self, debug: bool = False, on_error: Optional[ErrorCallback] = None):
        super().__init__(debug=debug)
        self.on_error = on_error

    async def run(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message_input: Optional[Dict[str, Any]] = None,
        contact_information: Optional[Dict[str, Any]] = None,
        is_new_conversation: bool = False,
        test_mode: bool = False,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        channel_config: Optional[Dict[str, Any]] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        agent_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a conversation synchronously.

        Args:
            graph_definition: The graph definition dictionary
            thread_id: Optional thread ID for the conversation
            message_input: Optional message payload as a dictionary
            contact_information: Optional contact information (phone, name, metadata)
            is_new_conversation: Flag indicating if this is a new conversation
            test_mode: Flag indicating if test mode is enabled
            agent_prompt: Optional agent prompt
            llm_config: Optional LLM configuration
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming
            channel_config: Optional channel configuration

        Returns:
            Dict[str, Any]: The processed conversation state
        """
        thread_id = self._get_thread_id(thread_id)
        
        # Set thread context for all logs in this execution
        set_thread_context(thread_id)
        
        try:
            # For logging, extract phone_number from contact_information if available
            phone_number = None
            if contact_information and "phone_number" in contact_information:
                phone_number = contact_information["phone_number"]

            logger.info(
                "Processing conversation - Phone: %s, New: %s, Test Mode: %s, Agent Prompt: %s",
                phone_number,
                is_new_conversation,
                test_mode,
                agent_prompt,
            )
            if message_input:
                logger.debug("Received message payload: %s", message_input)

            # Configure the channel adapter if channel_config is provided
            if channel_config and "type" in channel_config:
                channel_type = channel_config.get("type")
                try:
                    configure_adapter(
                        MessageChannelType(channel_type),
                        channel_config.get("settings", {})
                    )
                    logger.info(f"Configured channel adapter: {channel_type}")
                except Exception as e:
                    logger.error(f"Failed to configure channel adapter {channel_type}: {str(e)}")

            graph = self.graph_builder.build_langgraph(graph_definition, agent_version=agent_version or 1)
            config = await self._prepare_config(
                graph_definition,
                thread_id,
                test_mode,
                agent_prompt,
                contact_information=contact_information,
                llm_config=llm_config,
                last_interrupt_tool_call_id=last_interrupt_tool_call_id,
                channel_config=channel_config,
                execution_metadata=execution_metadata,
                agent_version=agent_version or 1,
            )

            agent_version = config.get("configurable", {}).get("agent_version", 1)
            input_state = self._prepare_input_state(is_new_conversation, message_input, agent_version)


            # Invoke the graph
            await graph.ainvoke(input_state, config=config)

            logger.info("Graph execution completed")

            state = await graph.aget_state(config)
            return self._format_state_response(state, thread_id)
        except Exception as e:
            # If we have an error callback, prepare context and call it
            if self.on_error:
                try:
                    # Build error context with available information
                    node_info = {}
                    try:
                        # Try to get the current state to extract node info
                        state = await graph.aget_state(config) if 'graph' in locals() else None
                        if state and state.values:
                            current_node = state.values.get("current_node", {})
                            node_info = {
                                "id": current_node.get("id"),
                                "type": current_node.get("type"),
                                "name": current_node.get("name"),
                            }
                    except Exception:
                        pass  # Ignore errors getting node info
                    
                    context = {
                        "message_input": message_input,
                        "contact_information": contact_information,
                        "is_new_conversation": is_new_conversation,
                        "node_info": node_info,
                        "agent_execution_id": None,  # Could be extracted from config if available
                    }
                    
                    # Call the error callback
                    await self.on_error(thread_id, e, 1, context)  # delivery_attempt=1 for run method
                except Exception as callback_error:
                    logger.error(f"Error callback failed: {str(callback_error)}")
            
            # Re-raise the original error
            raise
        finally:
            # Clear thread context when done
            clear_thread_context()

    async def _determine_stream_input(
        self,
        graph,
        config,
        thread_id: str,
        message_input: Optional[Dict[str, Any]] = None,
        is_new_conversation: bool = False,
        delivery_attempt: int = 1,
        last_interrupt_tool_call_id: Optional[str] = None,
        resume_interrupt_id: Optional[str] = None,
    ) -> Any:
        """
        Determine the appropriate input for graph streaming execution.

        Args:
            graph: The graph instance
            config: The graph configuration
            thread_id: Thread ID for the conversation
            message_input: Optional message payload as a dictionary
            is_new_conversation: Flag indicating if this is a new conversation
            delivery_attempt: The delivery attempt counter
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming
            resume_interrupt_id: Optional ID of the interrupt we're resuming

        Returns:
            The appropriate input for graph streaming
        """
        if delivery_attempt > 1:
            # This is a retry attempt, check for redundancy using interrupt-based checks
            is_redundant = await is_redundant_retry_input(graph, config, resume_interrupt_id, is_new_conversation)
            if is_redundant:
                # Use None to signal resumption from checkpoint without new input
                logger.info(
                    "Retry handling: Input is redundant, resuming from checkpoint."
                )
                return None
            else:
                # Retry but not redundant, prepare normal input
                # If we're resuming an interrupt, use the Command syntax
                if last_interrupt_tool_call_id:
                    logger.debug(
                        f"Retry handling: Resuming interrupt {resume_interrupt_id}."
                    )
                    # Filter out message_contexts from resume command
                    if message_input and isinstance(message_input, dict):
                        filtered_input = message_input.copy()
                        if "content" in filtered_input and isinstance(filtered_input["content"], dict):
                            filtered_content = filtered_input["content"].copy()
                            filtered_content.pop("message_contexts", None)
                            filtered_content.pop("template_contexts", None)  # Also remove old field for compatibility
                            filtered_input["content"] = filtered_content
                        return Command(resume=filtered_input)
                    return Command(resume=message_input)
                else:
                    logger.debug(
                        "Retry handling: Preparing standard input."
                    )
                    agent_version = config.get("configurable", {}).get("agent_version", 1)
                    return self._prepare_input_state(is_new_conversation, message_input, agent_version)
        else:
            # First attempt, prepare normal input
            # If we're resuming an interrupt, use the Command syntax
            if last_interrupt_tool_call_id:
                logger.debug(
                    f"First attempt, resuming interrupt {resume_interrupt_id}."
                )
                # Filter out message_contexts from resume command
                if message_input and isinstance(message_input, dict):
                    filtered_input = message_input.copy()
                    if "content" in filtered_input and isinstance(filtered_input["content"], dict):
                        filtered_content = filtered_input["content"].copy()
                        filtered_content.pop("message_contexts", None)
                        filtered_content.pop("template_contexts", None)  # Also remove old field for compatibility
                        filtered_input["content"] = filtered_content
                    return Command(resume=filtered_input)
                return Command(resume=message_input)
            else:
                logger.debug("First attempt, preparing standard input.")
                agent_version = config.get("configurable", {}).get("agent_version", 1)
                return self._prepare_input_state(is_new_conversation, message_input, agent_version)

    async def stream(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message_input: Optional[Dict[str, Any]] = None,
        contact_information: Optional[Dict[str, Any]] = None,
        is_new_conversation: bool = False,
        test_mode: bool = False,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        resume_interrupt_id: Optional[str] = None,
        delivery_attempt: int = 1,
        channel_config: Optional[Dict[str, Any]] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        agent_version: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a conversation with streaming output.

        This method provides a streaming interface to process conversations,
        yielding intermediate states and handling interrupts.

        Args:
            graph_definition: The graph definition dictionary
            thread_id: Optional thread ID for the conversation
            message_input: Optional message payload as a dictionary
            contact_information: Optional contact information (phone, name, metadata)
            is_new_conversation: Flag indicating if this is a new conversation
            test_mode: Flag indicating if test mode is enabled
            agent_prompt: Optional agent prompt
            llm_config: Optional LLM configuration
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming
            resume_interrupt_id: Optional ID of the interrupt we're resuming
            delivery_attempt: The delivery attempt counter
            channel_config: Optional channel configuration

        Yields:
            Dict[str, Any]: Intermediate conversation states
        """
        thread_id = self._get_thread_id(thread_id)
        
        # Set thread context for all logs in this execution
        set_thread_context(thread_id)

        try:
            # For logging, extract phone_number from contact_information if available
            phone_number = None
            if contact_information and "phone_number" in contact_information:
                phone_number = contact_information["phone_number"]

            # --- Prepare Graph and Config ---
            graph = self.graph_builder.build_langgraph(graph_definition, agent_version=agent_version or 1)
            
            # Initialize token tracker if available
            token_tracker = TokenUsageTracker() if HAS_TOKEN_TRACKING else None

            # Configure the channel adapter if channel_config is provided
            if channel_config and "type" in channel_config:
                channel_type = channel_config.get("type")
                try:
                    configure_adapter(
                        MessageChannelType(channel_type),
                        channel_config.get("settings", {})
                    )
                    logger.info(f"Configured channel adapter: {channel_type}")
                except Exception as e:
                    logger.error(f"Failed to configure channel adapter {channel_type}: {str(e)}")

            config = await self._prepare_config(
                graph_definition,
                thread_id,
                test_mode,
                agent_prompt,
                contact_information=contact_information,
                llm_config=llm_config,
                last_interrupt_tool_call_id=last_interrupt_tool_call_id,
                channel_config=channel_config,
                execution_metadata=execution_metadata,
                agent_version=agent_version or 1,
            )
            
            # Add token tracker to callbacks
            if "callbacks" not in config:
                config["callbacks"] = []
            if token_tracker:
                config["callbacks"].append(token_tracker)
            logger.info(
                "Streaming conversation - Phone: %s, NewConv: %s, ResumeInterruptID: %s",
                phone_number,
                is_new_conversation,
                last_interrupt_tool_call_id,
            )
            if message_input:
                # Log a truncated version of the message
                message_str = str(message_input)
                logger.debug(
                    "Message content (truncated): %s...",
                    message_str[:100] if len(message_str) > 100 else message_str,
                )

            # --- Determine Input for Graph Execution ---
            input_for_astream = await self._determine_stream_input(
                graph,
                config,
                thread_id,
                message_input,
                is_new_conversation,
                delivery_attempt,
                last_interrupt_tool_call_id,
                resume_interrupt_id,
            )

            # --- Stream the Graph Execution with Interrupt Processing Loop ---
            # Initial graph execution
            async for event in graph.astream(input_for_astream, config=config, stream_mode="updates"):
                state_after_step = await graph.aget_state(config)
                yield self._format_state_response(state_after_step, thread_id, is_update=True)

            state = await graph.aget_state(config)
            final_response = self._format_state_response(state, thread_id, is_update=False)
            
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

        except Exception as e:
            logger.error(
                f"Error during graph execution (Attempt {delivery_attempt}): {str(e)}",
                exc_info=True,
            )
            
            # If we have an error callback and this is a retryable attempt
            if self.on_error and delivery_attempt <= 5:
                try:
                    # Build error context with available information
                    node_info = {}
                    try:
                        # Try to get the current state to extract node info
                        state = await graph.aget_state(config) if 'graph' in locals() else None
                        if state and state.values:
                            current_node = state.values.get("current_node", {})
                            node_info = {
                                "id": current_node.get("id"),
                                "type": current_node.get("type"),
                                "name": current_node.get("name"),
                            }
                    except Exception:
                        pass  # Ignore errors getting node info
                    
                    context = {
                        "message_input": message_input,
                        "contact_information": contact_information,
                        "is_new_conversation": is_new_conversation,
                        "node_info": node_info,
                        "agent_execution_id": None,  # Could be extracted from config if available
                    }
                    
                    # Call the error callback
                    await self.on_error(thread_id, e, delivery_attempt, context)
                except Exception as callback_error:
                    logger.error(f"Error callback failed: {str(callback_error)}")
            
            # Re-raise the original error
            raise
        finally:
            # Clear thread context when done
            clear_thread_context()