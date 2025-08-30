"""MCP server implementation."""

from typing import Any, Callable, TypeVar
from fastapi import FastAPI, Body
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict


T = TypeVar("T", bound=BaseModel)


class Tool(BaseModel):
    """MCP tool definition."""
    model_config = ConfigDict(strict=True)
    name: str = Field(description="The name of the tool")
    description: str = Field(description="The description of what the tool does")
    inputSchema: dict[str, Any] = Field(description="The input schema for the tool")
    strict: bool = Field(default=True, description="Whether the tool response is strictly validated")
    function: Callable[..., Any] = Field(description="The tool function", exclude=True)


class MCPServer:
    """MCP server implementation."""

    def __init__(self, name: str, description: str | None = None):
        """Initialize the MCP server."""
        self.name = name
        self.description = description or f"A Model Context Protocol (MCP) tool server for {name}"
        
        # Create FastAPI app
        self.app = FastAPI(
            title=self.name,
            description=self.description,
            version="2.1.2",
        )
        
        # Initialize MCP server
        self.mcp_server = FastMCP(self.name)
        
        # Register endpoints
        self._register_endpoints()
        
        # Store registered tools
        self._tools: dict[str, Tool] = {}

    def _register_endpoints(self) -> None:
        """Register FastAPI endpoints."""
        @self.app.get("/tools", response_model=list[Tool])
        async def get_tools():
            """Get all available MCP tools."""
            return list(self._tools.values())

        @self.app.post("/tools/{tool_name}/invoke")
        async def invoke_tool(tool_name: str, arguments: dict[str, Any] = Body(...)):
            """Invoke a specific MCP tool."""
            try:
                result = await self.mcp_server.call_tool(tool_name, arguments=arguments)
                if isinstance(result, list) and len(result) == 1:
                    first_item = result[0]
                    if hasattr(first_item, "type") and first_item.type == "text":
                        return first_item.text
                elif isinstance(result, dict) and result.get("type") == "text":
                    return result["text"]
                return result
            except Exception as e:
                return {"error": f"Error invoking tool {tool_name}: {str(e)}"}

    async def add_tool(self, tool: Callable[..., Any]) -> None:
        """Add a tool to the MCP server."""
        # Add tool to MCP server
        self.mcp_server.add_tool(tool)
        
        # Get tool metadata
        tools = await self.mcp_server.list_tools()
        tool_metadata = tools[-1]
        
        # Use the raw inputSchema from FastMCP - it will be processed later by convert_to_strict_schema
        # when the tool is converted to OpenAI function format
        inputSchema = tool_metadata.inputSchema
        
        # Create and store Tool instance
        self._tools[tool_metadata.name] = Tool(
            name=tool_metadata.name,
            description=tool_metadata.description,
            inputSchema=inputSchema,
            strict=True,
            function=tool
        ) 