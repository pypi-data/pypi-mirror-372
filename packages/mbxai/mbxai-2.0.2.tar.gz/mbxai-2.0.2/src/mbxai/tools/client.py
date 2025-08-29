"""
ToolClient implementation for MBX AI.
"""

from typing import Any, Callable, TypeVar
import logging
import inspect
import json
from pydantic import BaseModel, create_model
from ..openrouter import OpenRouterClient
from .types import Tool, convert_to_strict_schema

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _generate_schema_from_function(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate JSON schema from function signature using Pydantic's model_json_schema."""
    try:
        sig = inspect.signature(func)
        
        # Extract fields for the Pydantic model
        fields = {}
        
        for param_name, param in sig.parameters.items():
            # Skip self parameter
            if param_name == 'self':
                continue
            
            # Get the parameter type annotation
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            
            # Handle default values
            if param.default != inspect.Parameter.empty:
                fields[param_name] = (param_type, param.default)
            else:
                fields[param_name] = (param_type, ...)  # Required field
        
        # Create a temporary Pydantic model
        temp_model = create_model('TempToolModel', **fields)
        
        # Generate schema using Pydantic's built-in method
        schema = temp_model.model_json_schema()
        
        logger.debug(f"Generated schema for function {func.__name__}: {json.dumps(schema, indent=2)}")
        return schema
        
    except Exception as e:
        logger.warning(f"Failed to generate schema for function {func.__name__}: {e}")
        # Return a basic schema as fallback
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }


class ToolClient:
    """Client for handling tool calls with OpenRouter."""

    def __init__(self, openrouter_client: OpenRouterClient) -> None:
        """Initialize the ToolClient.

        Args:
            openrouter_client: The OpenRouter client to use
        """
        self._client = openrouter_client
        self._tools: dict[str, Tool] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable[..., Any],
        schema: dict[str, Any] | None = None,
    ) -> None:
        """Register a new tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
            function: The function to call when the tool is used
            schema: The JSON schema for the tool's parameters. If None or empty, 
                   will be automatically generated from the function signature.
        """
        # Generate schema automatically if not provided or empty
        if not schema:
            logger.debug(f"No schema provided for tool '{name}', generating from function signature")
            raw_schema = _generate_schema_from_function(function)
            # Use the existing convert_to_strict_schema like MCPTool does
            schema = convert_to_strict_schema(raw_schema, strict=True, keep_input_wrapper=False)
            logger.debug(f"Auto-generated and converted schema for '{name}': {json.dumps(schema, indent=2)}")
        
        tool = Tool(
            name=name,
            description=description,
            function=function,
            schema=schema,
        )
        self._tools[name] = tool
        logger.debug(f"Registered tool: {name}")

    def _truncate_content(self, content: str | None, max_length: int = 100) -> str:
        """Truncate content for logging."""
        if not content:
            return "None"
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def _truncate_dict(self, data: dict[str, Any], max_length: int = 50) -> str:
        """Truncate dictionary values for logging."""
        if not data:
            return "{}"
        truncated = {}
        for k, v in data.items():
            if isinstance(v, str):
                truncated[k] = self._truncate_content(v, max_length)
            elif isinstance(v, dict):
                truncated[k] = self._truncate_dict(v, max_length)
            else:
                truncated[k] = str(v)[:max_length] + "..." if len(str(v)) > max_length else v
        return str(truncated)

    def _validate_message_sequence(self, messages: list[dict[str, Any]], validate_responses: bool = True) -> None:
        """Validate the message sequence for tool calls and responses.
        
        Args:
            messages: The message sequence to validate
            validate_responses: Whether to validate that all tool calls have responses
        """
        tool_call_ids = set()
        tool_response_ids = set()
        
        for i, msg in enumerate(messages):
            role = msg.get("role")
            if role == "assistant" and "tool_calls" in msg:
                # Track tool calls
                for tc in msg["tool_calls"]:
                    tool_call_ids.add(tc["id"])
                    logger.debug(f"Found tool call {tc['id']} for {tc['function']['name']} in message {i}")
            elif role == "tool":
                # Track tool responses
                tool_response_ids.add(msg["tool_call_id"])
                logger.debug(f"Found tool response for call ID {msg['tool_call_id']} in message {i}")
        
        # Only validate responses if requested
        if validate_responses:
            # Check for missing responses
            missing_responses = tool_call_ids - tool_response_ids
            if missing_responses:
                logger.error(f"Missing tool responses for call IDs: {missing_responses}")
                logger.error("Message sequence:")
                for i, msg in enumerate(messages):
                    role = msg.get("role", "unknown")
                    if role == "assistant" and "tool_calls" in msg:
                        logger.error(f"  Message {i} - Assistant with tool calls: {[tc['id'] for tc in msg['tool_calls']]}")
                    elif role == "tool":
                        logger.error(f"  Message {i} - Tool response for call ID: {msg['tool_call_id']}")
                    else:
                        logger.error(f"  Message {i} - {role}: {self._truncate_content(msg.get('content'))}")
                raise ValueError(f"Invalid message sequence: missing responses for tool calls {missing_responses}")

    def _log_messages(self, messages: list[dict[str, Any]], validate_responses: bool = True) -> None:
        """Log the messages being sent to OpenRouter.
        
        Args:
            messages: The messages to log
            validate_responses: Whether to validate that all tool calls have responses
        """
        logger.debug("Sending messages to OpenRouter:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = self._truncate_content(msg.get("content"))
            tool_calls = msg.get("tool_calls", [])
            tool_call_id = msg.get("tool_call_id")
            
            if tool_calls:
                tool_call_info = [
                    f"{tc['function']['name']}(id={tc['id']})"
                    for tc in tool_calls
                ]
                logger.debug(f"  Message {i} - {role}: content='{content}', tool_calls={tool_call_info}")
            elif tool_call_id:
                logger.debug(f"  Message {i} - {role}: content='{content}', tool_call_id={tool_call_id}")
            else:
                logger.debug(f"  Message {i} - {role}: content='{content}'")
        
        # Validate message sequence
        self._validate_message_sequence(messages, validate_responses)

    async def _process_tool_calls(self, message: Any, messages: list[dict[str, Any]]) -> None:
        """Process all tool calls in a message.
        
        Args:
            message: The message containing tool calls
            messages: The list of messages to add responses to
        """
        if not message.tool_calls:
            return

        # Process all tool calls first
        tool_responses = []
        for tool_call in message.tool_calls:
            tool = self._tools.get(tool_call.function.name)
            if not tool:
                raise ValueError(f"Unknown tool: {tool_call.function.name}")

            # Parse arguments if they're a string
            arguments = tool_call.function.arguments
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments: {e}")
                    raise ValueError(f"Invalid tool arguments format: {arguments}")

            # Call the tool
            logger.debug(f"Calling tool: {tool.name} with args: {self._truncate_dict(arguments)}")
            if inspect.iscoroutinefunction(tool.function):
                result = await tool.function(**arguments)
            else:
                result = tool.function(**arguments)

            # Convert result to JSON string if it's not already
            if not isinstance(result, str):
                result = json.dumps(result)

            # Create the tool response
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            tool_responses.append(tool_response)
            logger.debug(f"Created tool response for call ID {tool_call.id}")

        # Add all tool responses to the messages
        messages.extend(tool_responses)
        logger.debug(f"Message count: {len(messages)}, Added {len(tool_responses)} tool responses to messages")

        # Validate the message sequence
        self._validate_message_sequence(messages, validate_responses=True)

        # Log the messages we're about to send
        self._log_messages(messages, validate_responses=False)

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Chat with the model, handling tool calls."""
        tools = [tool.to_openai_function() for tool in self._tools.values()]
        
        if tools:
            logger.debug(f"Available tools: {[tool['function']['name'] for tool in tools]}")
            kwargs["tools"] = tools
        
        while True:
            # Get the model's response
            response = self._client.create(
                messages=messages,
                model=model,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response
            
            if not hasattr(response, 'choices'):
                raise ValueError("No choices found in response")
            
            if len(response.choices) == 0:
                raise ValueError("No choices found in response")
            
            messages.append(response.choices[0].message.dict())
            
            # Get all function calls from the output
            tool_calls = response.choices[0].message.tool_calls            
            # Process function calls if any
            if tool_calls:
                logger.debug(f"Tool calls: {len(tool_calls)} - Tools: {[tc.function.name for tc in tool_calls]}")
                
                # Process each function call
                for tool_call in tool_calls:
                    logger.debug(f"Processing tool call: {tool_call.function.name}")

                    # Get the tool
                    tool = self._tools.get(tool_call.function.name)
                    if not tool:
                        raise ValueError(f"Unknown tool: {tool_call.function.name}")

                    # Parse arguments
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool arguments: {e}")
                        raise ValueError(f"Invalid tool arguments format: {tool_call.function.arguments}")

                    # Call the tool
                    logger.debug(f"Calling tool: {tool.name} with args: {self._truncate_dict(arguments)}")
                    try:
                        result = tool.function(**arguments)
                        logger.debug(f"Tool {tool.name} completed successfully")
                    except Exception as e:
                        logger.error(f"Error calling tool {tool.name}: {str(e)}")
                        result = {"error": f"Tool execution failed: {str(e)}"}

                    # Convert result to string if needed
                    if not isinstance(result, str):
                        result = json.dumps(result)

                    # Append the function call and result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result,
                    })
                    
                    logger.debug(f"Added function call and output for {tool_call.function.name}")

                # Continue the conversation after processing all calls
                continue
            else:
                logger.debug("Final response")
                return response
            
    def parse(
        self,
        messages: list[dict[str, Any]],
        response_format: object,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Chat with the model, handling tool calls."""
        tools = [tool.to_openai_function() for tool in self._tools.values()]
        
        if tools:
            logger.debug(f"Available tools: {[tool['function']['name'] for tool in tools]}")
            kwargs["tools"] = tools
        
        while True:
            # Get the model's response
            response = self._client.parse(
                messages=messages,
                response_format=response_format,
                model=model,
                **kwargs,
            )
            
            if not hasattr(response, 'choices'):
                raise ValueError("No choices found in response")
            
            if len(response.choices) == 0:
                raise ValueError("No choices found in response")
            
            messages.append(response.choices[0].message.dict())
            
            # Get all function calls from the output
            tool_calls = response.choices[0].message.tool_calls            
            # Process function calls if any
            if tool_calls:
                logger.debug(f"Tool calls: {len(tool_calls)} - Tools: {[tc.function.name for tc in tool_calls]}")
                
                # Process each function call
                for tool_call in tool_calls:
                    logger.debug(f"Processing tool call: {tool_call.function.name}")

                    # Get the tool
                    tool = self._tools.get(tool_call.function.name)
                    if not tool:
                        raise ValueError(f"Unknown tool: {tool_call.function.name}")

                    # Parse arguments
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool arguments: {e}")
                        raise ValueError(f"Invalid tool arguments format: {tool_call.function.arguments}")

                    # Call the tool
                    logger.info(f"Calling tool: {tool.name} with args: {self._truncate_dict(arguments)}")
                    try:
                        result = tool.function(**arguments)
                        logger.debug(f"Tool {tool.name} completed successfully")
                    except Exception as e:
                        logger.error(f"Error calling tool {tool.name}: {str(e)}")
                        result = {"error": f"Tool execution failed: {str(e)}"}

                    # Convert result to string if needed
                    if not isinstance(result, str):
                        result = json.dumps(result)

                    # Append the function call and result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result,
                    })
                    
                    logger.debug(f"Added function call and output for {tool_call.function.name}")

                # Continue the conversation after processing all calls
                continue
            else:
                logger.debug("Final response")
                return response
