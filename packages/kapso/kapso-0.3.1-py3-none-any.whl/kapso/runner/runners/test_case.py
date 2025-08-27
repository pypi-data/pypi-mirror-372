"""
Specialized runner for test cases.
"""

import logging
from typing import Dict, Any, Optional, List

from langgraph.types import Command

from kapso.runner.runners.base import BaseRunner
from kapso.runner.utils.message_utils import recursively_convert_messages_to_openai_format
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

class TestCaseRunner(BaseRunner):
    """
    Runner for test cases.
    """

    def __init__(self, debug: bool = False):
        """Initialize the test chat runner."""
        super().__init__(debug=debug)

    async def run(
        self,
        graph_definition: Dict[str, Any],
        test_case: Dict[str, Any],
        thread_id: Optional[str] = None,
        contact_information: Optional[Dict[str, Any]] = None,
        phone_number: Optional[str] = None,  # For backward compatibility
        agent_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        judge_llm_config: Optional[Dict[str, Any]] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        agent_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a test case by automatically responding to user input requests.

        Args:
            graph_definition: The graph definition
            thread_id: Optional thread ID
            test_case: The test case with script and rubric
            contact_information: Optional contact information (phone, name, metadata)
            phone_number: Optional phone number (deprecated, use contact_information)
            agent_prompt: Optional system prompt for the agent
            llm_config: Optional LLM configuration
            judge_llm_config: Optional LLM configuration for the judge
        Returns:
            Dict[str, Any]: The test result with score and conversation
        """
        thread_id = self._get_thread_id(thread_id)
        
        # Set thread context for all logs in this execution
        set_thread_context(thread_id)
        
        try:
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
                "Processing test case - Test: %s, Phone: %s",
                test_case.get("name", "Unknown"),
                log_phone,
            )

            configure_adapter(
                MessageChannelType.WHATSAPP,
                { "mock": True }
            )

            # Set up test mode by default for tests
            test_mode = True

            # Build the graph and prepare the config
            graph = self.graph_builder.build_langgraph(graph_definition, agent_version=agent_version or 1)
            
            # Initialize token tracker
            token_tracker = TokenUsageTracker() if HAS_TOKEN_TRACKING else None
            
            config = await self._prepare_config(
                graph_definition, 
                thread_id, 
                test_mode, 
                agent_prompt, 
                contact_information=contact_information,
                llm_config=llm_config, 
                last_interrupt_tool_call_id=None,
                execution_metadata=execution_metadata,
                agent_version=agent_version or 1,
            )
            
            # Add token tracker to callbacks
            if "callbacks" not in config:
                config["callbacks"] = []
            if token_tracker:
                config["callbacks"].append(token_tracker)

            # Store any errors encountered during execution
            error = None
            execution_completed = True
            # Generate a realistic first message from the user based on the test script
            first_message = await self._simulate_first_message(
                test_case.get("script", ""), llm_config
            )

            logger.info("First simulated user message: %s", first_message)

            # Start with a new conversation including the simulated first message
            is_new_conversation = True
            agent_version = config.get("configurable", {}).get("agent_version", 1)
            input_state = self._prepare_input_state(is_new_conversation, first_message, agent_version)

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
                            "Test case execution completed normally"
                        )
                        break

                    # Check if we have an interrupt tool call
                    interrupt_tool_call = self._get_interrupt_tool_call(state)

                    if not interrupt_tool_call:
                        logger.warning(
                            "Test case execution paused without interrupt tool call"
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
                        if simulated_response.get("content", {}).get("text") == "CONVERSATION_ENDED":
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
                    logger.error(f"Error in test case execution: {str(e)}")
                    error = {"message": str(e), "type": type(e).__name__}
                    execution_completed = False
                    break

            # Get the final state for evaluation
            try:
                state = await graph.aget_state(config)

                # Evaluate the conversation against the rubric
                evaluation_result = await self._evaluate_test_result(
                    state.values.get("conversation", []),
                    state.values.get("full_history", []),
                    test_case.get("rubric", ""),
                    judge_llm_config
                )

                # Prepare the message history from state
                message_history = self._select_message_history_from_state(state.values)
                full_history = message_history.get("full_history", [])
                conversation = message_history.get("conversation", [])

            except Exception as e:
                logger.error(
                    f"Error retrieving state or evaluating test: {str(e)}"
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
            
            # Add token usage to test result
            usage_summary = token_tracker.get_usage_summary() if token_tracker else {}
            if usage_summary and usage_summary.get("total_tokens", 0) > 0:
                test_result["token_usage"] = {
                    "provider": llm_config.get("provider_name", "Anthropic") if llm_config else "Anthropic",
                    "model": llm_config.get("provider_model_name", "unknown") if llm_config else "unknown",
                    "input_tokens": usage_summary["input_tokens"],
                    "output_tokens": usage_summary["output_tokens"],
                    "total_tokens": usage_summary["total_tokens"],
                    "cache_creation_tokens": usage_summary["cache_creation_tokens"],
                    "cache_read_tokens": usage_summary["cache_read_tokens"]
                }
                logger.info(f"Token usage tracked: {usage_summary}")

            return test_result
        except Exception as e:
            logger.error(f"Error in test case setup: {str(e)}")
            # Return minimal error result
            return {
                "thread_id": thread_id,
                "test_case_id": test_case.get("id"),
                "test_case_name": test_case.get("name"),
                "score": 0.0,
                "feedback": f"Test setup failed: {str(e)}",
                "full_history": [],
                "conversation": [],
                "execution_completed": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }
        finally:
            # Clear thread context when done
            clear_thread_context()

    async def _simulate_first_message(
        self, test_script: str, llm_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate a realistic first message from a user initiating a conversation.

        Args:
            test_script: Instructions on how the simulated user should behave
            llm_config: Optional LLM configuration

        Returns:
            Dict[str, Any]: The simulated first user message
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
            return { "type": "user_input", "content": { "text": match.group(1).strip() } }
        else:
            # Fallback if XML parsing fails
            logger.warning(
                f"Failed to extract first message from XML, using raw content: {content[:100]}..."
            )
            return { "type": "user_input", "content": { "text": str(content).strip() } }

    async def _simulate_user_response(
        self,
        question: str,
        test_script: str,
        conversation: List,
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Use LLM to simulate a user response based on the test script and conversation.

        Args:
            question: The question being asked by the agent
            test_script: Instructions on how the simulated user should respond
            conversation: The conversation history from state
            llm_config: Optional LLM configuration

        Returns:
            Dict[str, Any]: The simulated user response, or "CONVERSATION_ENDED" if no response is required
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
            return { "type": "user_input", "content": { "text": match.group(1).strip() } }
        else:
            # Fallback if XML parsing fails
            logger.warning(
                f"Failed to extract message from XML, using raw content: {content[:100]}..."
            )
            return { "type": "user_input", "content": { "text": str(content).strip() } }

    async def _evaluate_test_result(
        self,
        conversation: List,
        full_history: List,
        rubric: str,
        llm_config: Optional[Dict[str, Any]] = None,
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
Evaluate the conversation and the internal execution details of the agent thoroughly and provide:
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
<conversation>
{formatted_conversation}
</conversation>

Here is the internal execution details of the agent:
<agent_internal_execution>
{full_history}
</agent_internal_execution>

Evaluate the agent's performance according to this rubric:

<rubric>
{rubric}
</rubric>

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
