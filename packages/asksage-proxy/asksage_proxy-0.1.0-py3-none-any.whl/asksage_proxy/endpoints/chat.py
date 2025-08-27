"""Chat completions endpoint for AskSage Proxy."""

import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from aiohttp import web
from loguru import logger

from ..client import AskSageClient
from ..config import AskSageConfig
from ..types import (
    FINISH_REASONS,
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    CompletionUsage,
    Function,
    NonStreamChoice,
    StreamChoice,
)

DEFAULT_MODEL = "gpt-4o"


def parse_tool_calls_from_response(
    response_content: str,
) -> Optional[List[ChatCompletionMessageToolCall]]:
    """Parse tool calls from AskSage response content.

    AskSage may return tool calls in various formats. This function attempts to
    detect and parse them into OpenAI format.

    Args:
        response_content: The response content from AskSage

    Returns:
        List of tool calls if found, None otherwise
    """
    if not response_content:
        return None

    tool_calls = []

    # Try to detect function call patterns in the response
    # This is a heuristic approach since we need to see actual AskSage tool call responses

    # Pattern 1: JSON-like function calls
    import re

    # Look for function call patterns like: function_name(arguments)
    function_pattern = r"(\w+)\s*\(\s*([^)]*)\s*\)"
    matches = re.findall(function_pattern, response_content)

    for i, (func_name, args_str) in enumerate(matches):
        # Skip common words that aren't function names
        if func_name.lower() in [
            "get",
            "set",
            "is",
            "has",
            "can",
            "will",
            "should",
            "would",
        ]:
            continue

        try:
            # Try to parse arguments as JSON
            if args_str.strip():
                # Simple argument parsing - in real implementation you'd want more robust parsing
                arguments = args_str.strip()
                if not arguments.startswith("{"):
                    # Convert simple arguments to JSON format
                    arguments = f'{{"query": "{arguments}"}}'
            else:
                arguments = "{}"

            tool_call = ChatCompletionMessageToolCall(
                id=f"call_{uuid.uuid4().hex[:8]}",
                function=Function(name=func_name, arguments=arguments),
                type="function",
            )
            tool_calls.append(tool_call)

        except Exception:
            # Skip invalid function calls
            continue

    # Pattern 2: Look for explicit tool call JSON in response
    try:
        # Try to find JSON objects that look like tool calls
        json_pattern = r'\{[^}]*"name"\s*:\s*"[^"]+"\s*[^}]*\}'
        json_matches = re.findall(json_pattern, response_content)

        for json_str in json_matches:
            try:
                parsed = json.loads(json_str)
                if "name" in parsed:
                    tool_call = ChatCompletionMessageToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        function=Function(
                            name=parsed["name"],
                            arguments=json.dumps(parsed.get("arguments", {})),
                        ),
                        type="function",
                    )
                    tool_calls.append(tool_call)
            except json.JSONDecodeError:
                continue

    except Exception:
        pass

    return tool_calls if tool_calls else None


async def transform_openai_to_asksage(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform OpenAI chat completion request to AskSage query format.

    Args:
        data: OpenAI chat completion request data

    Returns:
        AskSage query payload
    """
    # Extract messages and convert to AskSage format
    messages = data.get("messages", [])

    # Find system message and user messages
    system_prompt = None
    user_messages = []

    for message in messages:
        role = message.get("role")
        content = message.get("content", "")

        if role == "system":
            system_prompt = content
        elif role == "user":
            user_messages.append(content)
        elif role == "assistant":
            # For conversation history, we might need to handle this differently
            # For now, we'll include it in the message context
            user_messages.append(f"Assistant: {content}")

    # Combine user messages into a single message
    if len(user_messages) == 1:
        message = user_messages[0]
    else:
        message = "\n\n".join(user_messages)

    # Build AskSage payload
    asksage_payload = {
        "message": message,
        "model": data.get("model", DEFAULT_MODEL),
        "temperature": data.get("temperature", 0.0),
        "persona": "default",
        "dataset": "all",
        "live": 0,
        "limit_references": 0,  # Remove references to avoid problematic content
    }

    # Add system prompt if present
    if system_prompt:
        asksage_payload["system_prompt"] = system_prompt

    # Handle max_tokens -> limit_references mapping (approximate)
    if "max_tokens" in data:
        # AskSage doesn't have direct max_tokens, but we can use limit_references
        # as a rough approximation for controlling response length
        max_tokens = data["max_tokens"]
        if max_tokens <= 100:
            asksage_payload["limit_references"] = 1
        elif max_tokens <= 500:
            asksage_payload["limit_references"] = 3
        else:
            asksage_payload["limit_references"] = 5

    # Handle tools (function calling)
    if "tools" in data:
        asksage_payload["tools"] = json.dumps(data["tools"])

    if "tool_choice" in data:
        tool_choice = data["tool_choice"]
        # Handle different tool_choice formats
        if isinstance(tool_choice, str):
            # "auto", "none", or function name
            asksage_payload["tool_choice"] = tool_choice
        else:
            # Object format like {"type": "function", "function": {"name": "get_weather"}}
            asksage_payload["tool_choice"] = json.dumps(tool_choice)

    # Handle reasoning effort (o1 models)
    if "reasoning_effort" in data:
        asksage_payload["reasoning_effort"] = data["reasoning_effort"]

    return asksage_payload


async def transform_asksage_to_openai(
    asksage_response: Dict[str, Any],
    *,
    model_name: str,
    create_timestamp: int,
    prompt_tokens: int = 0,
    is_streaming: bool = False,
) -> Dict[str, Any]:
    """Transform AskSage response to OpenAI chat completion format.

    Args:
        asksage_response: Response from AskSage API
        model_name: Model name to include in response
        create_timestamp: Timestamp for the response
        prompt_tokens: Number of tokens in the prompt
        is_streaming: Whether this is a streaming response

    Returns:
        OpenAI-compatible response
    """
    # Handle AskSage API response format
    # Based on ANL testing, the real content is in the "message" field
    # The "response" field often contains just "OK" or status info

    response_content = ""

    # First try to get content from "message" field (this is where real content is)
    response_content = asksage_response.get("message", "")

    # If message field is empty, fall back to response field
    if not response_content:
        if "response" in asksage_response:
            response_data = asksage_response["response"]
            if isinstance(response_data, dict):
                # Nested response format - extract the actual message
                response_content = response_data.get(
                    "message", ""
                ) or response_data.get("response", "")
            else:
                # Direct response format
                response_content = str(response_data)

    # Final fallback to empty string
    if not response_content:
        response_content = ""

    # Parse tool calls from response
    tool_calls = parse_tool_calls_from_response(response_content)

    # Determine finish reason
    finish_reason = "tool_calls" if tool_calls else "stop"

    # Calculate token usage (simplified - in real implementation you'd want proper tokenization)
    completion_tokens = len(response_content.split()) if response_content else 0
    total_tokens = prompt_tokens + completion_tokens

    usage = CompletionUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )

    if is_streaming:
        # Create streaming response chunk
        delta = ChoiceDelta(content=response_content)
        if tool_calls:
            # Convert tool calls to streaming format
            delta.tool_calls = [
                ChoiceDeltaToolCall(
                    index=i,
                    id=tool_call.id,
                    function=tool_call.function,
                    type=tool_call.type,
                )
                for i, tool_call in enumerate(tool_calls)
            ]

        openai_response = ChatCompletionChunk(
            id=str(uuid.uuid4().hex),
            created=create_timestamp,
            model=model_name,
            choices=[
                StreamChoice(
                    index=0,
                    delta=delta,
                    finish_reason=finish_reason,
                )
            ],
        )
    else:
        # Create non-streaming response
        message = ChatCompletionMessage(content=response_content)
        if tool_calls:
            message.tool_calls = tool_calls

        openai_response = ChatCompletion(
            id=str(uuid.uuid4().hex),
            created=create_timestamp,
            model=model_name,
            choices=[
                NonStreamChoice(
                    index=0,
                    message=message,
                    finish_reason=finish_reason,
                )
            ],
            usage=usage,
        )

    return openai_response.model_dump()


async def handle_non_streaming_request(
    client: AskSageClient,
    asksage_payload: Dict[str, Any],
    model_name: str,
    create_timestamp: int,
) -> web.Response:
    """Handle non-streaming chat completion request.

    Args:
        client: AskSage client instance
        asksage_payload: Transformed payload for AskSage API
        model_name: Model name for response
        create_timestamp: Timestamp for response

    Returns:
        JSON response with chat completion
    """
    try:
        # Log the payload being sent to AskSage
        logger.info(f"Sending to AskSage: {json.dumps(asksage_payload, indent=2)}")

        # Send query to AskSage
        asksage_response = await client.query(asksage_payload)

        # Log the response from AskSage
        logger.info(f"AskSage response: {json.dumps(asksage_response, indent=2)}")

        # Transform response to OpenAI format
        openai_response = await transform_asksage_to_openai(
            asksage_response,
            model_name=model_name,
            create_timestamp=create_timestamp,
            prompt_tokens=0,  # TODO: Calculate actual prompt tokens
            is_streaming=False,
        )

        return web.json_response(
            openai_response,
            status=200,
            content_type="application/json",
        )

    except Exception as e:
        logger.error(f"Error in non-streaming request: {e}")
        return web.json_response(
            {
                "error": {
                    "message": f"Internal server error: {str(e)}",
                    "type": "internal_server_error",
                    "code": "internal_error",
                }
            },
            status=500,
        )


async def handle_streaming_request(
    client: AskSageClient,
    asksage_payload: Dict[str, Any],
    model_name: str,
    create_timestamp: int,
    request: web.Request,
) -> web.StreamResponse:
    """Handle streaming chat completion request.

    Args:
        client: AskSage client instance
        asksage_payload: Transformed payload for AskSage API
        model_name: Model name for response
        create_timestamp: Timestamp for response
        request: Original web request

    Returns:
        Streaming response with SSE events
    """
    response = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

    response.enable_chunked_encoding()
    await response.prepare(request)

    try:
        # Log the payload being sent to AskSage
        logger.info(
            f"Streaming - Sending to AskSage: {json.dumps(asksage_payload, indent=2)}"
        )

        # For now, we'll simulate streaming by getting the full response
        # and sending it in chunks. In a real implementation, you'd want
        # to handle actual streaming from AskSage if available.
        asksage_response = await client.query(asksage_payload)

        # Log the response from AskSage
        logger.info(
            f"Streaming - AskSage response: {json.dumps(asksage_response, indent=2)}"
        )

        # Extract response content using the same logic as transform_asksage_to_openai
        # Prioritize "message" field where real content is located
        response_content = asksage_response.get("message", "")

        # Fall back to response field if message is empty
        if not response_content:
            if "response" in asksage_response:
                response_data = asksage_response["response"]
                if isinstance(response_data, dict):
                    response_content = response_data.get(
                        "message", ""
                    ) or response_data.get("response", "")
                else:
                    response_content = str(response_data)

        # Send response in chunks
        if response_content:
            # Split into words for chunked streaming
            words = response_content.split()
            current_content = ""

            for word in words:
                current_content += word + " "

                # Create streaming chunk
                chunk_data = await transform_asksage_to_openai(
                    {"response": word + " "},
                    model_name=model_name,
                    create_timestamp=create_timestamp,
                    is_streaming=True,
                )

                # Send SSE event
                sse_data = f"data: {json.dumps(chunk_data)}\n\n"
                await response.write(sse_data.encode())

                # Small delay to simulate streaming
                await asyncio.sleep(0.05)

        # Send final chunk with finish_reason
        final_chunk = ChatCompletionChunk(
            id=str(uuid.uuid4().hex),
            created=create_timestamp,
            model=model_name,
            choices=[
                StreamChoice(
                    index=0,
                    delta=ChoiceDelta(content=None),
                    finish_reason="stop",
                )
            ],
        )

        sse_data = f"data: {json.dumps(final_chunk.model_dump())}\n\n"
        await response.write(sse_data.encode())

        # Send done signal
        await response.write(b"data: [DONE]\n\n")

    except Exception as e:
        logger.error(f"Error in streaming request: {e}")
        error_data = {
            "error": {
                "message": f"Internal server error: {str(e)}",
                "type": "internal_server_error",
                "code": "internal_error",
            }
        }
        sse_data = f"data: {json.dumps(error_data)}\n\n"
        await response.write(sse_data.encode())

    await response.write_eof()
    return response


async def chat_completions(
    request: web.Request,
) -> Union[web.Response, web.StreamResponse]:
    """Handle chat completions endpoint.

    Args:
        request: The incoming HTTP request

    Returns:
        Either a JSON response or streaming response
    """
    config: AskSageConfig = request.app["config"]

    try:
        # Parse request data
        data = await request.json()

        if not data:
            return web.json_response(
                {
                    "error": {
                        "message": "Invalid request: empty JSON data",
                        "type": "invalid_request_error",
                        "code": "invalid_request",
                    }
                },
                status=400,
            )

        # Check for required fields
        if "messages" not in data:
            return web.json_response(
                {
                    "error": {
                        "message": "Missing required field: messages",
                        "type": "invalid_request_error",
                        "code": "missing_required_field",
                    }
                },
                status=400,
            )

        # Transform OpenAI request to AskSage format
        asksage_payload = await transform_openai_to_asksage(data)

        model_name = data.get("model", DEFAULT_MODEL)
        create_timestamp = int(time.time())
        stream = data.get("stream", False)

        # Create AskSage client
        async with AskSageClient(config) as client:
            if stream:
                return await handle_streaming_request(
                    client, asksage_payload, model_name, create_timestamp, request
                )
            else:
                return await handle_non_streaming_request(
                    client, asksage_payload, model_name, create_timestamp
                )

    except json.JSONDecodeError:
        return web.json_response(
            {
                "error": {
                    "message": "Invalid JSON in request body",
                    "type": "invalid_request_error",
                    "code": "invalid_json",
                }
            },
            status=400,
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat_completions: {e}")
        return web.json_response(
            {
                "error": {
                    "message": "Internal server error",
                    "type": "internal_server_error",
                    "code": "internal_error",
                }
            },
            status=500,
        )
