"""
Factory for creating and configuring LLM instances.
"""
import os
import logging
from dotenv import load_dotenv
from typing import Any, Dict, Optional, Literal, Iterator, AsyncIterator
from langchain_core.outputs.chat_generation import ChatGenerationChunk
from langchain_core.outputs.chat_result import ChatResult

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

# Create a logger for this module
logger = logging.getLogger(__name__)


def initialize_llm(llm_config: Optional[Dict[str, Any]] = None):
    """
    Initialize the LLM based on the provided configuration.

    Args:
        llm_config: Optional configuration for the LLM

    Returns:
        The LLM without tools bound
    """
    # Use default configuration if none provided
    if not llm_config:
        return _create_default_llm()

    # Determine which provider to use
    provider_name = llm_config.get("provider_name", "Anthropic")

    if provider_name == "OpenAI":
        return _create_openai_llm(llm_config)
    elif provider_name == "OpenRouter":
        return _create_openrouter_llm(llm_config)
    elif provider_name == "Google":
        return _create_google_llm(llm_config)
    else:
        return _create_anthropic_llm(llm_config)


def _create_default_llm():
    """Create the default Anthropic LLM"""
    return ChatAnthropic(
        model="claude-3-7-sonnet-latest",
        timeout=120,
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        temperature=0.0,
        max_retries=5,
        streaming=True,
        max_tokens_to_sample=8096,
    )

def _create_google_llm(llm_config: Dict[str, Any]):
    """Create a Google LLM with the given configuration"""
    api_key = llm_config.get("api_key")

    return ChatGoogleGenerativeAI(
        model=llm_config.get("provider_model_name", "gemini-2.5-pro-exp-03-25"),
        google_api_key=api_key,
        temperature=llm_config.get("temperature", 0.1),
        max_retries=5,
        max_tokens_to_sample=llm_config.get("max_tokens", 2048),
    )


def _create_openai_llm(llm_config: Dict[str, Any]):
    """Create an OpenAI LLM with the given configuration"""
    api_key = llm_config.get("api_key")

    is_reasoning_model = llm_config.get("reasoning_model", True)

    kwargs = {
        "model": llm_config.get("provider_model_name", "gpt-4o"),
        "timeout": 120,
        "api_key": api_key,
        "max_retries": 5,
        "streaming": True,
        "max_tokens": llm_config.get("max_tokens", 2048),
        "stream_usage": True,
    }

    # Only add temperature if not a reasoning model
    if not is_reasoning_model:
        kwargs["temperature"] = llm_config.get("temperature", 0.0)

    # Only OpenAI supports reasoning_effort
    if is_reasoning_model:
        kwargs["reasoning_effort"] = llm_config.get("reasoning_effort", "low")

    return ChatOpenAI(**kwargs)


def _create_anthropic_llm(llm_config: Dict[str, Any]):
    """Create an Anthropic LLM with the given configuration"""
    api_key = llm_config.get("api_key")

    return ChatAnthropic(
        model=llm_config.get("provider_model_name", "claude-3-5-sonnet-latest"),
        timeout=120,
        api_key=api_key,
        temperature=llm_config.get("temperature", 0.1),
        max_retries=5,
        streaming=True,
        max_tokens_to_sample=llm_config.get("max_tokens", 2048),
    )


def _create_openrouter_llm(llm_config: Dict[str, Any]):
    """Create an OpenRouter LLM with the given configuration"""
    api_key = llm_config.get("api_key")
    is_reasoning_model = llm_config.get("reasoning_model", True)

    kwargs = {
        "model": llm_config.get("provider_model_name", "gpt-4o"),
        "timeout": 120,
        "max_retries": 5,
        "max_tokens": llm_config.get("max_tokens", 2048),
        "base_url": os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1",
        "api_key": api_key,
    }

    # Only add temperature if not a reasoning model
    if not is_reasoning_model:
        kwargs["temperature"] = llm_config.get("temperature", 0.0)

    # Only OpenAI supports reasoning_effort
    if is_reasoning_model:
        kwargs["reasoning"] = {
            "effort": llm_config.get("reasoning_effort", "low"),
        }

    return ChatOpenRouter(**kwargs)

from typing import Any, Optional, List, Dict, Union, Sequence, Mapping
from pydantic import Field, SecretStr, root_validator

import os
import json
import requests
import httpx

from langchain_core.language_models.chat_models import BaseChatModel, generate_from_stream, agenerate_from_stream
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk
from langchain_core.messages.tool import ToolCall
from langchain_core.utils.function_calling import convert_to_openai_tool

class ChatOpenRouter(BaseChatModel):
    """ChatOpenRouter is a chat model wrapper for the OpenRouter API.

    This class extends LangChain's BaseChatModel to interface with OpenRouter, 
    a unified API that supports multiple model providers (e.g., OpenAI GPT, Anthropic Claude, Mistral, etc.). 
    It matches the interface of ChatOpenAI, providing synchronous and async invocation, 
    tool (function) calling via `bind_tools`, and streaming support.

    Attributes:
        openrouter_api_key (SecretStr): The OpenRouter API key (reads from env `OPENROUTER_API_KEY` if not provided).
        openrouter_base_url (str): Base URL for the OpenRouter API (env `OPENROUTER_API_URL` or `OPENROUTER_BASE_URL`, default "https://openrouter.ai/api/v1").
        model (str): Identifier of the model to use (e.g., "openai/gpt-4", "anthropic/claude-2", "mistral/7B").
        max_tokens (int, optional): Maximum number of tokens in the generated response.
        temperature (float, optional): Sampling temperature for the model.
        top_p (float, optional): Nucleus sampling parameter.
        top_k (int, optional): Top-k sampling parameter (for models that support it).
        top_a (float, optional): Alternate nucleus sampling parameter (for certain models).
        min_p (float, optional): Minimum probability threshold for token selection.
        frequency_penalty (float, optional): Frequency penalty (OpenAI-style).
        presence_penalty (float, optional): Presence penalty (OpenAI-style).
        repetition_penalty (float, optional): Repetition penalty (for models that support it).
        seed (int, optional): Random seed for deterministic generation (if supported).
        logit_bias (Dict[str, float], optional): Biases for specific tokens (by token ID).
        disable_streaming (bool or 'tool_calling'): Controls streaming behavior.
            - If False (default), streaming is used when available.
            - If True, streaming is always disabled (the response is gathered fully before returning).
            - If "tool_calling", streaming is disabled only when a tool call is expected (i.e., when tools are provided).
        stream_usage (bool): Whether to collect usage tokens during streaming (defaults to True).
        http_client (Any, optional): Custom HTTP client for synchronous requests (e.g., `requests.Session` or similar).
        http_async_client (Any, optional): Custom HTTP client for async requests (e.g., an `httpx.AsyncClient`).
        timeout (float, optional): Request timeout in seconds (defaults to 120.0).
    """
    openrouter_api_key: SecretStr = Field(None, alias="api_key", env="OPENROUTER_API_KEY")
    openrouter_base_url: Optional[str] = Field(None, alias="base_url")
    model: str = "openai/gpt-3.5-turbo"
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    top_a: Optional[float] = None
    min_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    repetition_penalty: Optional[float] = None
    seed: Optional[int] = None
    logit_bias: Optional[Dict[str, float]] = None
    disable_streaming: Union[bool, Literal["tool_calling"]] = True
    stream_usage: bool = True
    http_client: Any = None
    http_async_client: Any = None
    timeout: Optional[float] = Field(120.0, description="Request timeout in seconds")

    @root_validator(pre=True)
    def set_default_base_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Configure base URL using environment variables or default."""
        base_url = values.get("openrouter_base_url") or os.getenv("OPENROUTER_API_URL") or os.getenv("OPENROUTER_BASE_URL")
        if base_url is None:
            base_url = "https://openrouter.ai/api/v1"
        values["openrouter_base_url"] = base_url.rstrip("/")
        return values

    def _get_request_payload(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Create the JSON payload for an OpenRouter chat completions request."""
        # Convert messages to OpenAI/OpenRouter format
        msg_dicts: List[Dict[str, Any]] = []
        for msg in messages:
            if hasattr(msg, "to_dict"):
                # If BaseMessage provides a serialization method
                msg_payload = msg.to_dict()
            else:
                # Construct basic message dict
                role = getattr(msg, "role", None) or ("system" if msg.__class__.__name__ == "SystemMessage" else "user")
                content = msg.content if hasattr(msg, "content") else str(msg)
                msg_payload = {"role": role, "content": content}
                # Include name for function/tool messages
                if hasattr(msg, "name") and role in ("function", "tool"):
                    msg_payload["name"] = msg.name
                if hasattr(msg, "tool_call_id"):
                    msg_payload["tool_call_id"] = msg.tool_call_id
            msg_dicts.append(msg_payload)
        payload: Dict[str, Any] = {"model": self.model, "messages": msg_dicts}
        # Core model parameters
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.top_k is not None:
            payload["top_k"] = self.top_k
        if self.top_a is not None:
            payload["top_a"] = self.top_a
        if self.min_p is not None:
            payload["min_p"] = self.min_p
        if self.frequency_penalty is not None:
            payload["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty is not None:
            payload["presence_penalty"] = self.presence_penalty
        if self.repetition_penalty is not None:
            payload["repetition_penalty"] = self.repetition_penalty
        if self.seed is not None:
            payload["seed"] = self.seed
        if self.logit_bias is not None:
            payload["logit_bias"] = self.logit_bias
        # Add stop sequences if specified
        if stop is not None:
            payload["stop"] = stop
        # Tool calling support: attach tools and function_call directives if present
        if "tools" in kwargs:
            payload["tools"] = kwargs.pop("tools")
        if "function_call" in kwargs:
            payload["function_call"] = kwargs.pop("function_call")
        # Include any extra fields passed in **kwargs (e.g., default_query params)
        payload.update(kwargs)
        return payload

    def _make_request(self, payload: Dict[str, Any], stream: bool = False) -> Any:
        """Send a synchronous HTTP request to the OpenRouter Chat Completions endpoint."""
        # Determine URL (append path if not already included)
        url = self.openrouter_base_url
        if not url.endswith("/chat/completions"):
            url = url.rstrip("/") + "/chat/completions"
        # Prepare headers
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.openrouter_api_key.get_secret_value()}" if self.openrouter_api_key else "",
            "Content-Type": "application/json",
        }
        # If default_headers provided (e.g., in model_kwargs), include them
        if hasattr(self, "default_headers") and isinstance(self.default_headers, Mapping):
            headers.update(self.default_headers)
        # Use custom client if provided, else requests
        timeout_value = self.timeout or 120.0
        if not stream:
            if self.http_client:
                # Assume http_client has a compatible post method
                response = self.http_client.post(url, json=payload, headers=headers)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=timeout_value)
            response.raise_for_status()
            return response.json()
        else:
            if self.http_client:
                response = self.http_client.post(url, json=payload, headers=headers, stream=True)
            else:
                response = requests.post(url, json=payload, headers=headers, stream=True, timeout=timeout_value)
            response.raise_for_status()
            return response

    async def _make_async_request(self, payload: Dict[str, Any], stream: bool = False) -> Any:
        """Send an asynchronous HTTP request to OpenRouter (for async calls)."""
        url = self.openrouter_base_url
        if not url.endswith("/chat/completions"):
            url = url.rstrip("/") + "/chat/completions"
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.openrouter_api_key.get_secret_value()}" if self.openrouter_api_key else "",
            "Content-Type": "application/json",
        }
        if hasattr(self, "default_headers") and isinstance(self.default_headers, Mapping):
            headers.update(self.default_headers)
        # Use provided AsyncClient or create a temporary one
        client: httpx.AsyncClient
        client_created = False
        if self.http_async_client:
            client = self.http_async_client
        else:
            # Configure timeout like webhook_request does
            timeout = httpx.Timeout(self.timeout or 120.0, connect=10.0)
            client = httpx.AsyncClient(timeout=timeout)
            client_created = True
        
        try:
            if not stream:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                return resp.json()
            else:
                # Use stream interface for SSE
                # For streaming, we need to ensure the client stays alive for the duration of the stream
                # The caller (_astream) is responsible for entering the async context
                resp = client.stream("POST", url, json=payload, headers=headers)
                # Store the client info on the response object so _astream can clean it up if needed
                resp._client_created = client_created
                resp._client = client if client_created else None
                return resp
        finally:
            # Clean up client if we created it and not streaming
            if client_created and not stream:
                await client.aclose()

    def _format_response(self, data: Dict[str, Any]) -> BaseMessage:
        """Parse a raw API JSON response into an AIMessage (with tool call info if present)."""
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices found in OpenRouter response")
        choice = choices[0]
        msg_dict = choice.get("message", {})
        finish_reason = choice.get("finish_reason")
        # Base content and role
        role = msg_dict.get("role", "assistant")
        content = msg_dict.get("content", None)
        ai_msg: BaseMessage
        # Check for tool/function calls in output
        tool_calls_data = msg_dict.get("tool_calls")
        if finish_reason == "tool_calls" or tool_calls_data is not None or msg_dict.get("function_call"):
            # Model decided to call a tool (one or multiple calls)
            tool_calls: List[ToolCall] = []
            if tool_calls_data:
                # OpenRouter's tool_calls array
                for tc in tool_calls_data:
                    func = tc.get("function", {})
                    name = func.get("name")
                    args_json = func.get("arguments", "{}")
                    
                    # Clean up OpenRouter's tool call end marker if present
                    if "<｜tool▁call▁end｜>" in args_json:
                        args_json = args_json.replace("<｜tool▁call▁end｜>", "")
                    
                    try:
                        args = json.loads(args_json)
                    except json.JSONDecodeError:
                        args = args_json
                    call_id = tc.get("id")
                    tool_calls.append(ToolCall(name=name, args=args or {}, id=call_id))
            elif msg_dict.get("function_call"):
                # OpenAI-compatible single function call
                func_call = msg_dict["function_call"]
                name = func_call.get("name")
                args_json = func_call.get("arguments", "{}")
                
                # Clean up OpenRouter's tool call end marker if present
                if "<｜tool▁call▁end｜>" in args_json:
                    args_json = args_json.replace("<｜tool▁call▁end｜>", "")
                
                try:
                    args = json.loads(args_json)
                except json.JSONDecodeError:
                    args = args_json
                tool_calls.append(ToolCall(name=name, args=args or {}))
            # Create an AIMessage with tool_calls attached (content could include reasoning if provided)
            ai_msg = AIMessage(content=content or "", role="assistant", tool_calls=tool_calls)
        else:
            # Standard response with content
            ai_msg = AIMessage(content=content, role=role)
        # Include token usage metadata if present
        usage = data.get("usage") or choice.get("usage")
        if usage:
            token_usage: Dict[str, int] = {}
            # OpenAI style
            if "prompt_tokens" in usage:
                token_usage["prompt_tokens"] = usage["prompt_tokens"]
                token_usage["input_tokens"] = usage["prompt_tokens"]
            if "completion_tokens" in usage:
                token_usage["completion_tokens"] = usage["completion_tokens"]
                token_usage["output_tokens"] = usage["completion_tokens"]
            # Anthropic style
            if "input_tokens" in usage:
                token_usage["prompt_tokens"] = usage["input_tokens"]
                token_usage["input_tokens"] = usage["input_tokens"]
            if "output_tokens" in usage:
                token_usage["completion_tokens"] = usage["output_tokens"]
                token_usage["output_tokens"] = usage["output_tokens"]
            # Total
            total = usage.get("total_tokens") or (token_usage.get("prompt_tokens", 0) + token_usage.get("completion_tokens", 0))
            token_usage["total_tokens"] = total
            # Attach to message metadata
            setattr(ai_msg, "response_metadata", {"token_usage": token_usage})
            setattr(ai_msg, "usage_metadata", token_usage)
        # Attach model name if provided
        if data.get("model"):
            if not hasattr(ai_msg, "response_metadata"):
                ai_msg.response_metadata = {}
            ai_msg.response_metadata["model_name"] = data["model"]
        return ai_msg

    def bind_tools(
        self, 
        tools: Sequence[Union[Dict[str, Any], type, callable, Any]], 
        *, 
        tool_choice: Optional[Union[dict, str, Literal["auto", "none", "any", "required"], bool]] = None, 
        strict: Optional[bool] = None, 
        **kwargs: Any
    ) -> BaseChatModel:
        """Bind tool-like objects to this model, enabling OpenRouter tool calling.

        Args:
            tools: List of tools (could be dicts, Pydantic classes, functions, or BaseTool instances) to provide to the model.
            tool_choice: Directive for tool usage. Can be:
                - A specific tool name (string) to force the model to call that tool.
                - "auto" or None to let the model decide (default OpenRouter behavior).
                - "none" to prevent tool use.
                - "any" or True to require at least one tool call (best-effort; not guaranteed by API).
            strict: If True, enforce exact JSON schema in tool inputs (if supported).
            **kwargs: Additional parameters to bind to the model.
        Returns:
            A new Runnable (ChatOpenRouter with tools bound) that can be invoked.
        """
        # Convert tools to OpenAI/OpenRouter function schema
        formatted_tools = [convert_to_openai_tool(tool, strict=strict) for tool in tools]
        bind_params: Dict[str, Any] = {"tools": formatted_tools}
        # Map tool_choice to OpenRouter's function_call parameter
        if tool_choice is not None and tool_choice is not False:
            if isinstance(tool_choice, dict):
                # If already a function call spec dict
                bind_params["function_call"] = tool_choice.get("function", tool_choice)
            elif isinstance(tool_choice, str):
                if tool_choice in {"auto", "none"}:
                    bind_params["function_call"] = tool_choice
                else:
                    # Treat as specific tool name
                    bind_params["function_call"] = {"name": tool_choice}
            elif tool_choice in {True, "any", "required"}:
                # Force at least one tool use (OpenRouter has no explicit flag; use "auto")
                bind_params["function_call"] = "auto"
        return self.bind(**bind_params, **kwargs)

    def _generate(
        self, 
        messages: List[BaseMessage], 
        stop: Optional[List[str]] = None, 
        run_manager: Optional[Any] = None, 
        **kwargs: Any
    ) -> "ChatResult":
        """Synchronously generate a response for the given chat messages."""
        # Decide on streaming based on settings
        use_stream = (self.disable_streaming is False) or (self.disable_streaming == "tool_calling" and "tools" not in kwargs)
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        if use_stream:
            # Stream the response and aggregate the final result
            stream_iter = self._stream(messages, stop=stop, run_manager=run_manager, **kwargs)
            return generate_from_stream(stream_iter)
        else:
            # Regular API call
            data = self._make_request(payload, stream=False)
            ai_msg = self._format_response(data)
            from langchain_core.language_models.chat_models import ChatGeneration, ChatResult
            return ChatResult(generations=[ChatGeneration(message=ai_msg)], llm_output={})

    async def _agenerate(
        self, 
        messages: List[BaseMessage], 
        stop: Optional[List[str]] = None, 
        run_manager: Optional[Any] = None, 
        **kwargs: Any
    ) -> "ChatResult":
        """Asynchronously generate a response for the given chat messages."""
        use_stream = (self.disable_streaming is False) or (self.disable_streaming == "tool_calling" and "tools" not in kwargs)
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        if use_stream:
            stream_aiter = self._astream(messages, stop=stop, run_manager=run_manager, **kwargs)
            return await agenerate_from_stream(stream_aiter)
        else:
            data = await self._make_async_request(payload, stream=False)
            ai_msg = self._format_response(data)
            from langchain_core.language_models.chat_models import ChatGeneration, ChatResult
            return ChatResult(generations=[ChatGeneration(message=ai_msg)], llm_output={})

    def _stream(
        self, 
        messages: List[BaseMessage], 
        stop: Optional[List[str]] = None, 
        run_manager: Optional[Any] = None, 
        **kwargs: Any
    ) -> Iterator["ChatGenerationChunk"]:
        """Synchronously stream the response as it is generated (yields chunks)."""
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        payload["stream"] = True
        response = self._make_request(payload, stream=True)
        # Read Server-Sent Event stream
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8").strip()
            if not decoded or not decoded.startswith("data:"):
                continue
            data_str = decoded[len("data:"):].strip()
            if data_str == "[DONE]":
                break
            try:
                event = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            # Each event contains a partial delta
            if "choices" in event and event["choices"]:
                choice = event["choices"][0]
                if "delta" in choice:
                    delta = choice["delta"]
                    # Role appears in first delta
                    if delta.get("role"):
                        msg_chunk = AIMessageChunk(content="", role=delta["role"])
                    else:
                        text = delta.get("content", "")
                        msg_chunk = AIMessageChunk(content=text)
                    # Wrap into a ChatGenerationChunk for yielding
                    chunk_obj = ChatGenerationChunk(message=msg_chunk)
                    # Emit token callback if applicable
                    if run_manager and isinstance(msg_chunk.content, str):
                        run_manager.on_llm_new_token(msg_chunk.content, chunk=chunk_obj)
                    yield chunk_obj
                # If the model triggers a function call mid-stream, we can break out (finish_reason "function_call")
                if choice.get("finish_reason") == "function_call":
                    break

    async def _astream(
        self, 
        messages: List[BaseMessage], 
        stop: Optional[List[str]] = None, 
        run_manager: Optional[Any] = None, 
        **kwargs: Any
    ) -> AsyncIterator["ChatGenerationChunk"]:
        """Asynchronously stream the response (yields chunks)."""
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        payload["stream"] = True
        # Open the streaming response
        resp = await self._make_async_request(payload, stream=True)
        
        # Check if we need to clean up the client after streaming
        client_to_close = getattr(resp, '_client', None)
        
        try:
            async with resp as response:
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    decoded = line.strip()
                    if not decoded or not decoded.startswith("data:"):
                        continue
                    data_str = decoded[len("data:"):].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    if "choices" in event and event["choices"]:
                        choice = event["choices"][0]
                        if "delta" in choice:
                            delta = choice["delta"]
                            if delta.get("role"):
                                msg_chunk = AIMessageChunk(content="", role=delta["role"])
                            else:
                                text = delta.get("content", "")
                                msg_chunk = AIMessageChunk(content=text)
                            chunk_obj = ChatGenerationChunk(message=msg_chunk)
                            if run_manager and isinstance(msg_chunk.content, str):
                                await run_manager.on_llm_new_token(msg_chunk.content, chunk=chunk_obj)
                            yield chunk_obj
                        if choice.get("finish_reason") == "function_call":
                            break
        finally:
            # Clean up the client if we created it
            if client_to_close:
                await client_to_close.aclose()

    @property
    def _llm_type(self) -> str:            # noqa: D401 (“_llm_type” must be a property)
        """Constant identifier used by LangChain for serialization."""
        return "chat-openrouter"
