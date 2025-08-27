import logging
import uuid
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, StateSnapshot

from kapso.runner.core.flow_utils import is_interrupt_active
from kapso.runner.core.persistence import create_checkpointer
from kapso.runner.utils.message_utils import recursively_convert_messages_to_openai_format
from kapso.runner.core.graph_builder import GraphBuilder

# Create a logger for this module
logger = logging.getLogger(__name__)


class ConversationService:
    async def initialize(self):
        """Initialize the service with PostgreSQL checkpointer."""
        self.checkpointer = await create_checkpointer()
        self.graph_builder = GraphBuilder(checkpointer=self.checkpointer)
        logger.info("Conversation service initialized with PostgreSQL checkpointer")

    def _prepare_input_state(self, is_new_conversation: bool, message: Optional[str]) -> Any:
        """Prepare the input state based on whether this is a new conversation."""
        if not is_new_conversation:
            return Command(resume=message)

        initial_state = {
            "full_history": [],
            "conversation": [],
        }
        if message:
            message_xml = f"This is the start of the AI agent execution. I received the following initial messages from the user: \n<messages>\n{message}\n</messages>"
            initial_state["full_history"].append(AIMessage(content=message_xml))
            initial_state["conversation"].append(HumanMessage(content=message))

        return initial_state

    def _prepare_config(
        self,
        graph_definition: Dict,
        thread_id: str,
        test_mode: bool,
        agent_prompt: Optional[str],
        phone_number: Optional[str],
        llm_config: Optional[Dict[str, Any]],
        last_interrupt_tool_call_id: Optional[str],
    ) -> Dict[str, Any]:
        """
        Prepare the configuration for graph execution.

        Args:
            graph_definition: The graph definition dictionary.
            thread_id: The thread ID for the conversation.
            test_mode: Flag indicating if test mode is enabled.
            agent_prompt: Optional agent prompt.
            phone_number: Optional phone number associated with the conversation.
            llm_config: Optional LLM configuration.
            last_interrupt_tool_call_id: Optional ID of the interrupt we're resuming.

        Returns:
            Dict[str, Any]: The configuration for the graph execution.
        """
        config = {
            "configurable": {
                "thread_id": thread_id,
                "test_mode": test_mode,
                "phone_number": phone_number,
                "nodes_by_name": self.graph_builder.nodes_by_name(graph_definition),
                "node_edges": self.graph_builder.node_edges(graph_definition),
                "llm_config": llm_config,
            },
            "recursion_limit": 50,
        }

        if last_interrupt_tool_call_id:
            config["configurable"]["resume_tool_call_id"] = last_interrupt_tool_call_id

        # Add agent prompt if provided
        if agent_prompt:
            config["configurable"]["agent_prompt"] = agent_prompt

        return config

    def _get_thread_id(self, thread_id: Optional[str]) -> str:
        """Generate a thread ID if not provided."""
        if not thread_id:
            new_thread_id = str(uuid.uuid4())
            logger.info(f"Generated new thread ID: {new_thread_id}")
            return new_thread_id
        return thread_id

    def _format_state_response(
        self, state: StateSnapshot, thread_id: str, is_update: bool = False
    ) -> Dict[str, Any]:
        """Format the state response for API consumption, including active interrupts."""

        # Determine overall status
        if is_update:
            status = "running"
        elif not state.next:
            status = "ended"
        else:
            status = "paused"

        # Extract active interrupts using new LangGraph property
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

        return result

    async def _ensure_initialized(self):
        """Ensure the checkpointer is initialized."""
        if not self.checkpointer:
            await self.initialize()

    async def _is_redundant_retry_input(
        self, graph: CompiledStateGraph, config: Dict[str, Any], resume_interrupt_id: Optional[str]
    ) -> bool:
        """
        Checks if the input for a retried message is redundant based on checkpoint state.
        Uses LangGraph's new interrupt tracking features for more precise detection.

        Args:
            graph: The compiled LangGraph application.
            config: The configuration for the current thread.
            resume_interrupt_id: The interrupt ID we're attempting to resume.

        Returns:
            bool: True if the input is redundant, False otherwise.
        """
        thread_id = config["configurable"]["thread_id"]
        logger.info(f"Performing retry check for thread {thread_id}")

        try:
            # Get the current state from the checkpointer
            state = await graph.aget_state(config)

            # If we're attempting to resume an interrupt, check if it's still active
            if resume_interrupt_id:
                # If the interrupt is NO LONGER active, the previous attempt must have
                # successfully processed it already, so this retry is redundant
                if not is_interrupt_active(state, resume_interrupt_id):
                    logger.info(
                        f"Interrupt {resume_interrupt_id} is no longer active in thread {thread_id}, "
                        "treating as redundant retry"
                    )
                    return True

            # Additional checks could be added here as needed
            return False

        except Exception as e:
            logger.error(f"Error checking for redundant retry: {str(e)}", exc_info=True)
            # Default to non-redundant if we cannot determine
            return False

    async def process_conversation(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message: Optional[str] = None,
        is_new_conversation: Optional[bool] = False,
        phone_number: Optional[str] = None,
        test_mode: Optional[bool] = False,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self._ensure_initialized()

        thread_id = self._get_thread_id(thread_id)

        logger.info(
            "Processing conversation - Thread: %s, Phone: %s, New: %s, Test Mode: %s, Agent Prompt: %s",
            thread_id,
            phone_number,
            is_new_conversation,
            test_mode,
            agent_prompt,
        )
        if message:
            logger.debug("Received message: %s", message)

        graph = self.graph_builder.build_langgraph(graph_definition)
        config = self._prepare_config(
            graph_definition,
            thread_id,
            test_mode,
            agent_prompt,
            phone_number,
            llm_config,
            last_interrupt_tool_call_id,
        )

        input_state = self._prepare_input_state(is_new_conversation, message)
        # Invoke the graph but don't need to store the result
        await graph.ainvoke(input_state, config=config)

        logger.info("Graph execution completed for thread: %s", thread_id)

        state = await graph.aget_state(config)
        return self._format_state_response(state, thread_id)

    async def process_chat(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message: Optional[str] = None,
        is_new_conversation: Optional[bool] = False,
        phone_number: Optional[str] = None,
        test_mode: Optional[bool] = False,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        agent_test_chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self._ensure_initialized()

        thread_id = self._get_thread_id(thread_id)

        logger.info(
            "Processing chat - Thread: %s, Phone: %s, New: %s, Test Mode: %s, Agent Prompt: %s",
            thread_id,
            phone_number,
            is_new_conversation,
            test_mode,
            agent_prompt,
        )
        if message:
            logger.debug("Received message: %s", message)

        graph = self.graph_builder.build_langgraph(graph_definition)
        config = self._prepare_config(
            graph_definition,
            thread_id,
            test_mode,
            agent_prompt,
            phone_number,
            llm_config,
            last_interrupt_tool_call_id,
        )

        input_state = self._prepare_input_state(is_new_conversation, message)
        # Invoke the graph but don't need to store the result
        await graph.ainvoke(input_state, config=config)

        logger.info("Graph execution completed for thread: %s", thread_id)

        state = await graph.aget_state(config)
        return self._format_state_response(state, thread_id)

    async def stream_conversation(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        message: Optional[str] = None,
        is_new_conversation: Optional[bool] = False,
        phone_number: Optional[str] = None,
        test_mode: Optional[bool] = False,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        last_interrupt_tool_call_id: Optional[str] = None,
        resume_interrupt_id: Optional[str] = None,
        delivery_attempt: Optional[int] = 1,
    ):
        """
        Process a conversation and stream the state changes, handling retries intelligently
        using LangGraph's enhanced interrupt features.

        Args:
            graph_definition: The graph definition dictionary.
            thread_id: Optional thread ID for the conversation.
            message: Optional message content.
            is_new_conversation: Flag indicating if this is a new conversation.
            phone_number: Optional phone number associated with the conversation.
            test_mode: Flag indicating if test mode is enabled.
            agent_prompt: Optional agent prompt.
            llm_config: Optional LLM configuration.
            last_interrupt_tool_call_id: Optional ID of the interrupt tool call we're resuming.
            resume_interrupt_id: Optional ID of the interrupt we're resuming.
            delivery_attempt: The Pub/Sub delivery attempt counter (1 for first attempt).

        Yields:
            Dict[str, Any]: State snapshots during conversation processing.
        """
        await self._ensure_initialized()
        thread_id = self._get_thread_id(thread_id)

        # --- Prepare Graph and Config ---
        try:
            graph = self.graph_builder.build_langgraph(graph_definition)

            config = self._prepare_config(
                graph_definition,
                thread_id,
                test_mode,
                agent_prompt,
                phone_number,
                llm_config,
                last_interrupt_tool_call_id,
            )
        except Exception as e:
            logger.error(
                f"Error preparing for conversation on thread {thread_id}: {e}", exc_info=True
            )
            raise

        logger.info(
            "Streaming conversation - Thread: %s, Attempt: %s, NewConv: %s, ResumeInterruptID: %s",
            thread_id,
            delivery_attempt,
            is_new_conversation,
            last_interrupt_tool_call_id,
        )
        if message:
            logger.debug(
                "Message content (truncated): %s...",
                message[:100] if len(message) > 100 else message,
            )

        # --- Determine Input for Graph Execution ---
        actual_input_for_astream = None
        if delivery_attempt is not None and delivery_attempt > 1:
            # This is a retry attempt, check for redundancy using new interrupt-based checks
            is_redundant = await self._is_redundant_retry_input(graph, config, resume_interrupt_id)
            if is_redundant:
                # Use None to signal resumption from checkpoint without new input
                logger.info(
                    f"Retry handling for thread {thread_id}: Input is redundant, resuming from checkpoint."
                )
                actual_input_for_astream = None
            else:
                # Retry but not redundant, prepare normal input
                # If we're resuming an interrupt, use the Command syntax
                if last_interrupt_tool_call_id and message:
                    logger.debug(
                        f"Retry handling for thread {thread_id}: Resuming interrupt {resume_interrupt_id}."
                    )
                    actual_input_for_astream = Command(resume=message)
                else:
                    logger.debug(
                        f"Retry handling for thread {thread_id}: Preparing standard input."
                    )
                    actual_input_for_astream = self._prepare_input_state(
                        is_new_conversation, message
                    )
        else:
            # First attempt, prepare normal input
            # If we're resuming an interrupt, use the Command syntax with interrupt_id
            if last_interrupt_tool_call_id and message:
                logger.debug(
                    f"First attempt for thread {thread_id}, resuming interrupt {resume_interrupt_id}."
                )
                actual_input_for_astream = Command(resume=message)
            else:
                logger.debug(f"First attempt for thread {thread_id}, preparing standard input.")
                actual_input_for_astream = self._prepare_input_state(is_new_conversation, message)

        # --- Stream Execution ---
        try:
            logger.debug(f"Starting graph execution for thread {thread_id}")
            stream_completed_normally = False

            async for event in graph.astream(
                actual_input_for_astream, config=config, stream_mode="updates"
            ):
                # Get current state after each step
                state_after_step = await graph.aget_state(config)
                yield self._format_state_response(state_after_step, thread_id, is_update=True)

            stream_completed_normally = True

            # Final snapshot if stream completed normally
            if stream_completed_normally:
                final_state = await graph.aget_state(config)
                logger.info(f"Graph execution completed successfully for thread: {thread_id}")
                yield self._format_state_response(final_state, thread_id, is_update=False)

        except Exception as e:
            logger.error(
                f"Error during graph execution for thread {thread_id} (Attempt {delivery_attempt}): {str(e)}",
                exc_info=True,
            )
            # Re-raise to ensure Pub/Sub NACKs the message
            raise

    async def cleanup(self):
        """Cleanup resources when shutting down."""
        if self.checkpointer and hasattr(self.checkpointer, "pool"):
            logger.info("Closing PostgreSQL connection pool...")
            try:
                await self.checkpointer.pool.close()
                logger.info("PostgreSQL connection pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL connection pool: {e}")

    def _select_message_history_from_state(self, state_values: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in state_values.items()
            if key in ["full_history", "conversation"]
        }

    def _select_current_node_from_state(self, state_values: Dict[str, Any]) -> Dict[str, Any]:
        current_node = state_values.get("current_node", {})

        # Remove knowledge_base_text from current_node
        current_node = {
            key: value for key, value in current_node.items() if key != "knowledge_base"
        }
        return current_node

    def _get_interrupt_tool_call(self, state: StateSnapshot) -> Optional[Dict[str, Any]]:
        tasks = state.tasks
        if not tasks or len(tasks) == 0:
            return None

        task = tasks[0]
        interrupts = task.interrupts
        if not interrupts or len(interrupts) == 0:
            return None

        return interrupts[0].value.get("tool_call")

    async def process_test_case(
        self,
        graph_definition: Dict[str, Any],
        thread_id: Optional[str] = None,
        test_case: Dict[str, Any] = None,
        phone_number: Optional[str] = None,
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        judge_llm_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a test case by automatically responding to user input requests.

        Args:
            graph_definition: The graph definition
            thread_id: Optional thread ID
            test_case: The test case with script and rubric
            phone_number: Optional phone number
            agent_prompt: Optional system prompt for the agent
            llm_config: Optional LLM configuration
            judge_llm_config: Optional LLM configuration for the judge
        Returns:
            Dict[str, Any]: The test result with score and conversation
        """
        await self._ensure_initialized()

        thread_id = self._get_thread_id(thread_id)

        logger.info(
            "Processing test case - Thread: %s, Test: %s",
            thread_id,
            test_case.get("name", "Unknown"),
        )

        # Set up test mode by default for tests
        test_mode = True

        # Build the graph and prepare the config
        graph = self.graph_builder.build_langgraph(graph_definition)
        config = self._prepare_config(
            graph_definition, thread_id, test_mode, agent_prompt, phone_number, llm_config, None
        )

        # Store any errors encountered during execution
        error = None
        execution_completed = True

        try:
            # Generate a realistic first message from the user based on the test script
            first_message = await self._simulate_first_message(
                test_case.get("script", ""), llm_config
            )

            logger.info("First simulated user message: %s", first_message)

            # Start with a new conversation including the simulated first message
            is_new_conversation = True
            input_state = self._prepare_input_state(is_new_conversation, first_message)

            # Process the conversation until it completes or needs user input
            while True:
                # Get the current state to check for interrupts and status
                try:
                    # Use either a new conversation or resume with a simulated response
                    if is_new_conversation:
                        # First execution of the graph
                        is_new_conversation = False
                        # Execute the graph and get the next state
                        await graph.ainvoke(input_state, config=config)
                    else:
                        await graph.ainvoke(Command(resume=simulated_response), config=config)

                    # Get the current state
                    state = await graph.aget_state(config)

                    # Check if conversation has ended
                    if not state.next:
                        logger.info(
                            "Test case execution completed normally for thread: %s", thread_id
                        )
                        break

                    # Check if we have an interrupt tool call
                    interrupt_tool_call = self._get_interrupt_tool_call(state)

                    if not interrupt_tool_call:
                        logger.warning(
                            "Test case execution paused without interrupt tool call for thread: %s",
                            thread_id,
                        )
                        break

                    # Check if it's AskUserForInput
                    if (
                        interrupt_tool_call.get("name") == "AskUserForInput"
                        or interrupt_tool_call.get("name") == "EnterIdleState"
                    ):
                        # Get the question being asked
                        user_question = interrupt_tool_call.get("args", {}).get("message", "")

                        # Use LLM to generate a simulated user response based on the test script
                        simulated_response = await self._simulate_user_response(
                            user_question,
                            test_case.get("script", ""),
                            state.values.get("conversation", []),
                            llm_config,
                        )

                        logger.info("Simulated user response: %s", simulated_response)

                        # Check if no response is needed
                        if simulated_response == "CONVERSATION_ENDED":
                            logger.info(
                                "Test script indicates no response needed, ending conversation"
                            )
                            break

                        # Continue with the simulated response in the next iteration
                    else:
                        # If the tool call is not AskUserForInput, we're done with the test
                        logger.info(
                            "Test case execution encountered a non-AskUserForInput tool call: %s",
                            interrupt_tool_call.get("name"),
                        )
                        break

                except Exception as e:
                    logger.error(f"Error in test case execution for thread {thread_id}: {str(e)}")
                    error = {"message": str(e), "type": type(e).__name__}
                    execution_completed = False
                    break

        except Exception as e:
            logger.error(f"Error in test case setup for thread {thread_id}: {str(e)}")
            execution_completed = False
            error = {"message": str(e), "type": type(e).__name__}

        # Get the final state for evaluation
        try:
            state = await graph.aget_state(config)

            # Evaluate the conversation against the rubric
            evaluation_result = await self._evaluate_test_result(
                state.values.get("conversation", []), test_case.get("rubric", ""), judge_llm_config
            )

            # Prepare the message history from state
            message_history = self._select_message_history_from_state(state.values)
            full_history = message_history.get("full_history", [])
            conversation = message_history.get("conversation", [])

        except Exception as e:
            logger.error(
                f"Error retrieving state or evaluating test for thread {thread_id}: {str(e)}"
            )
            error = {"message": str(e), "type": type(e).__name__}
            # Set default values when we can't get state
            full_history = []
            conversation = []
            evaluation_result = {
                "score": 0.0,
                "feedback": f"Evaluation failed due to error: {str(e)}",
            }
            execution_completed = False

        # Prepare the full test result
        test_result = {
            "thread_id": thread_id,
            "test_case_id": test_case.get("id"),
            "test_case_name": test_case.get("name"),
            "score": evaluation_result.get("score", 0.0),
            "feedback": evaluation_result.get("feedback", ""),
            "full_history": recursively_convert_messages_to_openai_format(full_history),
            "conversation": recursively_convert_messages_to_openai_format(conversation),
            "execution_completed": execution_completed,
            "error": error,
        }

        return test_result

    async def _simulate_first_message(
        self, test_script: str, llm_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Simulate a realistic first message from a user initiating a conversation.

        Args:
            test_script: Instructions on how the simulated user should behave
            llm_config: Optional LLM configuration

        Returns:
            str: The simulated first user message
        """
        import re

        from langchain_core.messages import HumanMessage, SystemMessage

        from kapso.runner.core.llm_factory import initialize_llm

        # Initialize LLM with temperature 0 for consistent responses
        simulation_llm_config = llm_config.copy() if llm_config else {}
        simulation_llm_config["temperature"] = 0.0  # Consistency for tests
        llm = initialize_llm(simulation_llm_config)

        # Create the prompt for simulating the first user message
        system_prompt = f"""You are simulating the first message a user would send to a business or service via WhatsApp or similar messaging platform.

The script below contains multiple instructions, but you MUST ONLY focus on generating the FIRST message in a conversation.

{test_script}

For example, if the script is:
<script>
1. Say 'Precio mantención'
2. Say '2019'
3. Say 'Tesla Model 3'
4. Say 'Ok, gracias'
</script>

You should ONLY use "1. Say 'Precio mantención'" to generate the first message.
And probably the message should be just 'Precio mantención'.
You will send more messages later in the conversation, but for now, just generate the first message.

Your message should be exactly what a real user would write when initiating a conversation. It should be:
1. Conversational and natural
2. Direct and to the point
3. Focused on the user's primary need or question
4. Formatted as a typical WhatsApp/text message (informal)

Your response should be structured as XML with a <message> tag.
Example: <message>Hi there</message>
"""

        user_prompt = "Generate ONLY the initial message that starts the conversation based on the instruction in the script. Return ONLY the XML response with the message tag."

        # Make the LLM call
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        response = await llm.ainvoke(messages)

        # Extract the message from XML
        content = response.content
        match = re.search(r"<message>(.*?)</message>", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # Fallback if XML parsing fails
            logger.warning(
                f"Failed to extract first message from XML, using raw content: {content[:100]}..."
            )
            return content.strip()

    async def _simulate_user_response(
        self,
        question: str,
        test_script: str,
        conversation: List,
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Use LLM to simulate a user response based on the test script and conversation.

        Args:
            question: The question being asked by the agent
            test_script: Instructions on how the simulated user should respond
            conversation: The conversation history from state
            llm_config: Optional LLM configuration

        Returns:
            str: The simulated user response, or "CONVERSATION_ENDED" if no response is required
        """
        import re

        from langchain_core.messages import HumanMessage, SystemMessage

        from kapso.runner.core.llm_factory import initialize_llm

        # Initialize LLM with temperature 0 for consistent responses
        simulation_llm_config = llm_config.copy() if llm_config else {}
        simulation_llm_config["temperature"] = 0.0  # Consistency for tests
        llm = initialize_llm(simulation_llm_config)

        # Format the conversation history for context
        formatted_history = ""
        if conversation:
            formatted_history = "\n\n".join(
                [
                    f"{'Agent' if msg.type == 'ai' else 'User'}: {msg.content}"
                    for msg in conversation
                ]
            )

        system_prompt = f"""You are simulating a realistic, natural user interacting with an AI agent based on the following script:

Script:
{test_script}

These instructions define how you behave as the user.

## IMPORTANT:

### Ending the Conversation:
You must carefully determine when the conversation naturally ends. Return exactly:
<message>CONVERSATION_ENDED</message>
when **any** of these conditions are true:

- You've completed **all instructions** explicitly listed in the script.
- The script clearly states or implies that the conversation should end (e.g., final instruction, farewell, issue resolved explicitly).
- You've explicitly indicated you have no more questions, or clearly expressed satisfaction with the agent's assistance and thanked them.
- For free-form scripts, the agent explicitly indicates the end condition mentioned (e.g., "you reached the message limit", "farewell message").

### Continuing the Conversation:
If the conversation should clearly continue according to the script instructions or agent prompts, respond concisely and naturally within a <message> tag:
Example: <message>Your concise, realistic response here</message>

Always assess script conditions carefully to determine if the conversation must end or continue.
"""

        user_prompt = f"""Here's the conversation history so far:

{formatted_history}

The AI agent just said:
{question}

Check the script instructions carefully to determine whether the conversation should continue or has reached its natural end.

- If the script is complete, the agent has resolved your question explicitly, you expressed clear satisfaction/gratitude, indicated you have no more questions, or the specified script-ending condition is met, you must respond exactly:
<message>CONVERSATION_ENDED</message>

- Otherwise, respond concisely, realistically, and naturally within a <message> tag:
Example: <message>Your response here</message>

Return ONLY the XML-formatted response as described.
"""

        # Make the LLM call
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        response = await llm.ainvoke(messages)

        # Extract the message from XML
        content = response.content
        match = re.search(r"<message>(.*?)</message>", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # Fallback if XML parsing fails
            logger.warning(
                f"Failed to extract message from XML, using raw content: {content[:100]}..."
            )
            return content.strip()

    async def _evaluate_test_result(
        self, conversation: List, rubric: str, llm_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the agent's performance using the provided rubric.

        Args:
            conversation: The conversation history
            rubric: The evaluation rubric
            llm_config: Optional LLM configuration

        Returns:
            Dict[str, Any]: Evaluation result with score and feedback
        """
        import re

        from langchain_core.messages import HumanMessage, SystemMessage

        from kapso.runner.core.llm_factory import initialize_llm

        # Initialize LLM with temperature 0 for consistent evaluation
        evaluation_llm_config = llm_config.copy() if llm_config else {}
        evaluation_llm_config["temperature"] = 0.0  # Deterministic evaluation
        llm = initialize_llm(evaluation_llm_config)

        # Format the conversation for evaluation
        formatted_conversation = ""
        if conversation:
            formatted_conversation = "\n\n".join(
                [
                    f"{'Agent' if msg.type == 'ai' else 'User'}: {msg.content}"
                    for msg in conversation
                ]
            )

        # Create the evaluation prompt
        system_prompt = """You are an objective evaluator of AI agent performance.
Your task is to assess how well the agent performed based on a specific rubric.
Evaluate the conversation thoroughly and provide:
1. A numerical score from 0.00 to 1.00 (with two decimal places)
2. Detailed feedback explaining your scoring reasoning, which must include:
   - A checklist of all evaluated items from the rubric
   - Whether each item passed or failed, marked with:
     ✅ for passed items
     ❌ for failed items
     ⚠️ for partially passed items
   - Specific examples from the conversation for each evaluation point

Your response should be structured as XML with these tags:
<score>X.XX</score>
<feedback>Your detailed feedback with the evaluation checklist in markdown format</feedback>

Be fair, consistent, and thorough in your evaluation.
Follow the rubric strictly.
"""

        user_prompt = f"""Here is the conversation between an AI agent and a user:

{formatted_conversation}

Evaluate the agent's performance according to this rubric:

{rubric}

Provide your evaluation as XML with <score> and <feedback> tags.
The score must be a number between 0.00 and 1.00 with two decimal places.
"""

        # Make the LLM call
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        response = await llm.ainvoke(messages)
        content = response.content

        # Extract score and feedback from XML
        score_match = re.search(r"<score>(.*?)</score>", content, re.DOTALL)
        feedback_match = re.search(r"<feedback>(.*?)</feedback>", content, re.DOTALL)

        result = {}

        if score_match:
            try:
                score = float(score_match.group(1).strip())
                # Ensure score is between 0 and 1
                score = max(0.0, min(1.0, score))
                # Format to two decimal places
                result["score"] = round(score, 2)
            except ValueError:
                logger.error(f"Invalid score format: {score_match.group(1)}")
                result["score"] = 0.0
        else:
            logger.error("Failed to extract score from evaluation")
            result["score"] = 0.0

        if feedback_match:
            result["feedback"] = feedback_match.group(1).strip()
        else:
            logger.error("Failed to extract feedback from evaluation")
            result["feedback"] = f"Evaluation failed to provide feedback: {content[:100]}..."

        return result
