"""
Base runner for all specialized runner implementations.
"""

import logging
import uuid
import json
from typing import Dict, Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command
from langgraph.types import StateSnapshot

from kapso.runner.core.persistence import create_checkpointer
from kapso.runner.core.graph_builder import GraphBuilder
from kapso.runner.utils.message_utils import recursively_convert_messages_to_openai_format
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# Create a logger for this module
logger = logging.getLogger(__name__)

class BaseRunner:
    """
    Base class providing common functionality for all specialized runners.

    This class contains shared logic for graph building, checkpointing, and
    state management.
    """

    def __init__(self, debug: bool = False):
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    async def initialize(self, checkpointer: AsyncPostgresSaver | None = None):
        """Initialize the runner with PostgreSQL checkpointer."""
        self.checkpointer = checkpointer or await create_checkpointer()
        self.graph_builder = GraphBuilder(checkpointer=self.checkpointer)
        logger.info("Runner initialized with PostgreSQL checkpointer")

    def run(self, graph_definition: Dict[str, Any], thread_id: Optional[str] = None, message_input: Optional[Dict[str, Any]] = None, is_new_conversation: bool = False, phone_number: Optional[str] = None, test_mode: bool = False, agent_prompt: Optional[str] = None, llm_config: Optional[Dict[str, Any]] = None, last_interrupt_tool_call_id: Optional[str] = None) -> Dict[str, Any]:
        """Run the runner with the given parameters."""
        pass

    def stream(self, graph_definition: Dict[str, Any], thread_id: Optional[str] = None, message_input: Optional[Dict[str, Any]] = None, is_new_conversation: bool = False, phone_number: Optional[str] = None, test_mode: bool = False, agent_prompt: Optional[str] = None, llm_config: Optional[Dict[str, Any]] = None, last_interrupt_tool_call_id: Optional[str] = None) -> Dict[str, Any]:
        """Stream the runner with the given parameters."""
        pass

    async def _prepare_config(
        self,
        graph_definition: Dict,
        thread_id: str,
        test_mode: bool,
        agent_prompt: Optional[str],
        contact_information: Optional[Dict[str, Any]] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        channel_config: Optional[Dict[str, Any]] = None,
        phone_number: Optional[str] = None,  # For backward compatibility
        execution_metadata: Optional[Dict[str, Any]] = None,
        checkpoint_id: Optional[str] = None,
        graph = None,  # Pass the built graph when checkpoint replay is needed
        message_input: Optional[Dict[str, Any]] = None,  # Message input for replay
        agent_version: int = 1,  # Agent version parameter
    ) -> Dict[str, Any]:
        """
        Prepare the configuration for graph execution.

        Args:
            graph_definition: The graph definition dictionary
            thread_id: Thread ID for the conversation
            test_mode: Flag indicating if test mode is enabled
            agent_prompt: Optional agent prompt
            contact_information: Optional contact information (phone, name, metadata)
            llm_config: Optional LLM configuration
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming
            channel_config: Optional channel configuration
            phone_number: Optional phone number (deprecated, use contact_information)
            execution_metadata: Optional execution metadata (agent_id, execution_id, etc.)

        Returns:
            Dict[str, Any]: The prepared configuration
        """
        # If replaying from checkpoint, we need special handling
        if checkpoint_id and graph:
            # First create a base config to find the checkpoint
            base_config = {
                "configurable": {"thread_id": thread_id},
            }

            original_state = await graph.aget_state(base_config)
            next_nodes = original_state.next
            next_node = list(next_nodes)[0] if next_nodes else '__start__'
            logger.info(f"Next node: {next_node}")

            # Find the state with matching checkpoint_id
            async for state in graph.aget_state_history(base_config):
                if state.config["configurable"].get("checkpoint_id") == checkpoint_id:
                    logger.info(f"Found checkpoint {checkpoint_id}, creating new branch for replay")

                    # Prepare the state update based on the message input
                    state_update = {}

                    # If there's a message input, process it exactly like _get_state_update_from_answer
                    if message_input and last_interrupt_tool_call_id:
                        msg_type = message_input.get("type")
                        msg_content = message_input.get("content", {})

                        # Create the tool message for the interrupt response
                        tool_message = {
                            "tool_call_id": last_interrupt_tool_call_id,
                            "type": "tool",
                            "content": msg_content
                        }

                        if msg_type == "user_input":
                            user_text = msg_content.get("text", "")
                            # Update state exactly like _get_state_update_from_answer
                            state_update = {
                                "full_history": [tool_message],
                                "conversation": [HumanMessage(content=user_text)]
                            }
                        elif msg_type == "payload":
                            # Only update full_history for payloads
                            state_update = {
                                "full_history": [tool_message]
                            }
                        else:
                            logger.warning(f"Invalid message type for replay: {msg_type}")

                    # Use aupdate_state to create a new checkpoint branch
                    # This is the key to proper time travel - it creates a new checkpoint
                    # that branches from the selected one
                    new_config = await graph.aupdate_state(
                        state.config,
                        state_update if state_update else {},
                        as_node=next_node
                    )

                    logger.info(f"New checkpoint branch created: {new_config['configurable'].get('checkpoint_id')}")
                    config = new_config
                    break
            else:
                # Checkpoint not found, create normal config
                logger.error(f"Checkpoint {checkpoint_id} not found in state history")
                config = {"configurable": {}, "recursion_limit": 80}
        else:
            # Normal config preparation
            config = {"configurable": {}, "recursion_limit": 80}

        # If phone_number is provided but contact_information is not, create contact_information
        if phone_number is not None and contact_information is None:
            contact_information = {"phone_number": phone_number}
        # If contact_information is provided, extract phone_number for backward compatibility
        elif contact_information is not None and "phone_number" in contact_information:
            phone_number = contact_information["phone_number"]

        # Always update configurable with our runtime data
        config["configurable"].update({
            "thread_id": thread_id,
            "test_mode": test_mode,
            "contact_information": contact_information,
            "phone_number": phone_number,
            "nodes_by_name": self.graph_builder.nodes_by_name(graph_definition),
            "node_edges": self.graph_builder.node_edges(graph_definition),
            "llm_config": llm_config or {},
            "execution_metadata": execution_metadata or {},
            "agent_version": agent_version,  # Use the passed parameter
        })

        if last_interrupt_tool_call_id:
            config["configurable"]["resume_tool_call_id"] = last_interrupt_tool_call_id

        # Add agent prompt if provided
        if agent_prompt:
            config["configurable"]["agent_prompt"] = agent_prompt

        # Add channel_type if provided in channel_config
        if channel_config and "type" in channel_config:
            config["configurable"]["channel_type"] = channel_config.get("type")

        return config

    def _get_thread_id(self, thread_id: Optional[str]) -> str:
        """Generate a thread ID if not provided."""
        if not thread_id:
            import uuid
            new_thread_id = str(uuid.uuid4())
            logger.info(f"Generated new thread ID: {new_thread_id}")
            return new_thread_id
        return thread_id

    def _prepare_input_state(self, is_new_conversation: bool, message_input: Optional[Dict[str, Any]], agent_version: int = 1) -> Any:
        """
        Prepare the input state based on whether this is a new conversation and the message payload structure.

        Args:
            is_new_conversation: Flag indicating if this is a new conversation
            message_input: Optional message payload as a dictionary

        Returns:
            Either a Command to resume the conversation or an initial state dictionary
        """
        if not is_new_conversation:
            return Command(resume=message_input)

        if message_input is None:
            return Command(resume=None)

        # Extract message components
        msg_type = message_input.get("type")
        msg_content_dict = message_input.get("content", {})

        # Initialize state
        initial_state = {
            "full_history": [],
            "conversation": [],
            "handoff_reason": None,
        }
        
        # Set a baseline timestamp for new conversations to enable future template tracking
        from datetime import datetime, timezone
        initial_state["last_processed_timestamp"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        if msg_type == "user_input":
            user_text = msg_content_dict.get("text")
            message_contexts = msg_content_dict.get("message_contexts", [])
            
            # Track newest timestamp across all messages
            newest_timestamp = initial_state.get("last_processed_timestamp")  # Start with baseline
            
            # Inject previous messages based on direction
            for message_context in message_contexts:
                direction = message_context.get('direction', 'outbound')
                
                if agent_version == 2:
                    # V2: Add messages directly to conversation
                    if direction == 'inbound':
                        initial_state["conversation"].append(HumanMessage(content=message_context.get('content', '')))
                        initial_state["full_history"].append(HumanMessage(content=message_context.get('content', '')))
                    else:
                        initial_state["conversation"].append(AIMessage(content=message_context.get('content', '')))
                        initial_state["full_history"].append(AIMessage(content=message_context.get('content', '')))
                else:
                    # V1: Original behavior with tool calls
                    if direction == 'inbound':
                        # User message - use handle_user_message
                        tool_call_id = str(uuid.uuid4())
                        tool_call = {
                            "id": tool_call_id,
                            "name": "handle_user_message",
                            "args": {}
                        }
                        
                        ai_message = AIMessage(content="", tool_calls=[tool_call])
                        tool_response = ToolMessage(
                            content=message_context.get('content', ''),
                            tool_call_id=tool_call_id
                        )
                    else:
                        # Outbound message - use send_external_message
                        tool_call_id = str(uuid.uuid4())
                        tool_call = {
                            "id": tool_call_id,
                            "name": "send_external_message",
                            "args": { "message": message_context.get('content', '') }
                        }
                        
                        ai_message = AIMessage(content="", tool_calls=[tool_call])
                        tool_response = ToolMessage(
                            content="Message sent",
                            tool_call_id=tool_call_id
                        )
                    
                    initial_state["full_history"].extend([ai_message, tool_response])
                
                # Track the newest timestamp
                msg_timestamp = message_context.get('sent_at')
                if msg_timestamp and (not newest_timestamp or msg_timestamp > newest_timestamp):
                    newest_timestamp = msg_timestamp
            
            # Update last_processed_timestamp once after processing all messages
            if newest_timestamp:
                initial_state["last_processed_timestamp"] = newest_timestamp
            
            if agent_version == 2:
                # V2: Add user message directly
                initial_state["conversation"].append(HumanMessage(content=user_text))
                initial_state["full_history"].append(HumanMessage(content=user_text))
            else:
                # V1: Original behavior with handle_user_message
                handle_tool_call_id = str(uuid.uuid4())
                handle_tool_call = {
                    "id": handle_tool_call_id,
                    "name": "handle_user_message",
                    "args": {}
                }
                
                ai_handle_message = AIMessage(content="", tool_calls=[handle_tool_call])
                handle_tool_response = ToolMessage(
                    content=user_text,
                    tool_call_id=handle_tool_call_id
                )
                
                initial_state["full_history"].extend([ai_handle_message, handle_tool_response])
                initial_state["conversation"].append(HumanMessage(content=user_text))
            
            logger.info(f"Preparing initial state with message_contexts: {len(message_contexts)}")

        elif msg_type == "payload":
            # For system payloads, only add to full_history, not to conversation
            initial_state["full_history"].append(
                AIMessage(content=f"System Payload: {json.dumps(msg_content_dict)}")
            )

        else:
            # Unknown message type
            logger.warning(f"Unknown message type: {msg_type}")
            raise ValueError(f"Unknown message type: {msg_type}")

        # Return initial state for new conversations
        return initial_state

    async def cleanup(self):
        """Cleanup resources when shutting down."""
        if hasattr(self, 'checkpointer') and self.checkpointer and hasattr(self.checkpointer, "pool"):
            logger.info("Closing PostgreSQL connection pool...")
            try:
                await self.checkpointer.pool.close()
                logger.info("PostgreSQL connection pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL connection pool: {e}")

    def _format_state_response(
        self,
        state: StateSnapshot,
        thread_id: str,
        is_update: bool = False
    ) -> Dict[str, Any]:
        """Format the state response for API consumption, including active interrupts."""

        # Determine overall status
        if is_update:
            status = "running"
        elif not state.next:
            status = "ended"
        else:
            status = "paused"

        # Extract active interrupts using LangGraph property
        active_interrupts = []
        for interrupt in getattr(state, "interrupts", []):
            active_interrupts.append(
                {
                    "id": interrupt.interrupt_id,
                    "value": interrupt.value,
                    "resumable": interrupt.resumable,
                }
            )

        interrupt_tool_call = self._get_interrupt_tool_call(state)

        result = recursively_convert_messages_to_openai_format(
            {
                "status": status,
                "thread_id": thread_id,
                "state": {
                    "values": self._select_message_history_from_state(state.values),
                    "next_nodes": list(state.next),
                    "created_at": state.created_at,
                },
                "current_node": self._select_current_node_from_state(state.values),
                "interrupt_tool_call": interrupt_tool_call,  # Keep for backward compatibility
                "active_interrupts": active_interrupts,  # Add new interrupt information
                "is_update": is_update,
            }
        )

        # ADD: Checkpoint information
        result["checkpoint"] = {
            "checkpoint_id": state.config["configurable"].get("checkpoint_id"),
            "checkpoint_ns": state.config["configurable"].get("checkpoint_ns", ""),
            "parent_checkpoint_id": state.parent_config["configurable"].get("checkpoint_id")
                if state.parent_config else None,
        }

        return result

    def _select_message_history_from_state(self, state_values: Dict[str, Any]) -> Dict[str, Any]:
        """Extract message history from state values."""
        return {
            key: value
            for key, value in state_values.items()
            if key in ["full_history", "conversation"]
        }

    def _select_current_node_from_state(self, state_values: Dict[str, Any]) -> Dict[str, Any]:
        """Extract current node information from state values."""
        current_node = state_values.get("current_node", {})

        # Remove knowledge_base_text from current_node
        current_node = {
            key: value for key, value in current_node.items() if key != "knowledge_base"
        }

        # If global, replace name with original_name
        if current_node.get("global") and current_node.get("original_name"):
            current_node["name"] = current_node.get("original_name")

        return current_node

    def _get_interrupt_tool_call(self, state: StateSnapshot) -> Optional[Dict[str, Any]]:
        """Extract interrupt tool call from state, if any."""
        tasks = state.tasks
        if not tasks or len(tasks) == 0:
            return None

        task = tasks[0]
        interrupts = task.interrupts
        if not interrupts or len(interrupts) == 0:
            return None

        return interrupts[0].value.get("tool_call")