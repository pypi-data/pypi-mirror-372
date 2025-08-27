"""
Definition for the webhook_request tool.
"""

import json
import logging
from typing import Annotated, Optional

import httpx
from langchain_core.tools import InjectedToolArg, tool

logger = logging.getLogger(__name__)


@tool
async def webhook_request(
    url: str,
    method: str,
    headers: Optional[dict | str] = None,
    body: Optional[dict | str] = None,
    mock_response_enabled: Annotated[bool, InjectedToolArg] = False,
    mock_response: Annotated[Optional[dict | str], InjectedToolArg] = None,
) -> dict:
    """
    Use this tool to make HTTP requests to external services when you need to fetch or send data.

    Key usage guidelines:
    - Use when external API interaction is needed
    - Provide the `url` and `method` parameters. `headers` and `body` are optional.
    - If you see a string with format #{variable_name} in the parameters, replace it with the value.
    - Headers and body are json or dicts, not strings.

    Example usage:
    - Sending data to an API (with headers and body)
    - Fetching info from a service (GET, potentially no headers or body)
    - Triggering external workflows

    Args:
        url: The complete URL of the endpoint (e.g., "https://api.example.com/data")
        method: The HTTP method in uppercase (GET, POST, PUT, DELETE, etc)
        headers: Optional dictionary of request headers (e.g., {"Authorization": "Bearer token"})
        body: Optional dictionary of data to send in request body (e.g., {"user_id": 123})
    """
    # Directly call the async function without asyncio.run()
    return await do_webhook_request(url, method, headers, body, mock_response_enabled, mock_response)


async def do_webhook_request(
    url: str,
    method: str,
    headers: Optional[dict | str] = None,
    body: Optional[dict | str] = None,
    mock_response_enabled: bool = False,
    mock_response: Optional[dict | str] = None,
) -> dict:
    """
    Asynchronously makes an HTTP request. Handles optional headers and body.
    """
    dict_headers = {}
    dict_body = {}
    # Transform headers and body to dict if they are strings
    if isinstance(headers, str):
        try:
            dict_headers = json.loads(headers)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse headers as JSON: {headers}")
    else:
        dict_headers = headers

    if isinstance(body, str):
        try:
            dict_body = json.loads(body)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse body as JSON: {body}")
    else:
        dict_body = body

    # Check if mock response is enabled
    if mock_response_enabled and mock_response is not None:
        logger.info(f"Using mock response instead of making actual request to {url}")
        logger.info(f"Mock response: {mock_response}")

        # If mock_response is a string, try to parse it as JSON
        if isinstance(mock_response, str):
            try:
                parsed_content = json.loads(mock_response)
                return {"status_code": 200, "content": parsed_content}
            except json.JSONDecodeError:
                # If parsing fails, return it as a string
                return {"status_code": 200, "content": mock_response}

        return {"status_code": 200, "content": mock_response}  # Default success status code

    try:
        # Log the request details for debugging
        logger.info(f"Making {method} request to {url}")
        logger.debug(f"Request headers: {dict_headers}")
        logger.debug(f"Request body: {dict_body}")
        
        # Create client with explicit timeout (default httpx timeout is 5 seconds)
        # Setting a longer timeout of 30 seconds for webhook requests
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Prepare request arguments, handling None for headers and body
            # Don't include json parameter if body is empty dict
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": dict_headers if dict_headers is not None else None,
            }
            
            # Only include json parameter if body is not None and not empty dict
            if dict_body is not None and dict_body != {}:
                request_kwargs["json"] = dict_body
            
            logger.debug(f"Request kwargs: {request_kwargs}")
            response = await client.request(**request_kwargs)
            logger.info(f"Received response from {url}: status_code={response.status_code}")

            try:
                json_content = response.json()
                logger.debug(f"Response JSON content: {json_content}")
            except Exception:
                # If response is not JSON, return the raw text content
                json_content = {"text": response.text}
                logger.debug(f"Response text content: {response.text}")

            return {"status_code": response.status_code, "content": json_content}
    except httpx.ConnectTimeout as e:
        logger.error(f"Webhook request failed for {url}: Connection timeout - {e}")
        return {"error": f"Connection timeout: {str(e)}"}
    except httpx.ReadTimeout as e:
        logger.error(f"Webhook request failed for {url}: Read timeout - {e}")
        return {"error": f"Read timeout: {str(e)}"}
    except httpx.WriteTimeout as e:
        logger.error(f"Webhook request failed for {url}: Write timeout - {e}")
        return {"error": f"Write timeout: {str(e)}"}
    except httpx.ConnectError as e:
        logger.error(f"Webhook request failed for {url}: Connection error - {e}")
        return {"error": f"Connection error: {str(e)}"}
    except httpx.HTTPStatusError as e:
        logger.error(f"Webhook request failed for {url}: HTTP status error {e.response.status_code} - {e}")
        return {"error": f"HTTP status error {e.response.status_code}: {str(e)}"}
    except httpx.RequestError as e:
        logger.error(f"Webhook request failed for {url}: Request error - {e}")
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        logger.error(f"Webhook request failed for {url}: Unexpected error {type(e).__name__} - {str(e)}")
        return {"error": f"Unexpected error {type(e).__name__}: {str(e)}"}
