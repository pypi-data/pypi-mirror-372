"""
Example demonstrating AgentClient tool registration proxy methods.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, ToolClient
from mbxai.mcp import MCPClient


class WeatherResponse(BaseModel):
    """Response for weather queries."""
    location: str = Field(description="The location")
    temperature: str = Field(description="Current temperature")
    conditions: str = Field(description="Weather conditions")
    recommendations: list[str] = Field(description="Recommendations based on weather")


class CalculationResponse(BaseModel):
    """Response for calculations."""
    operation: str = Field(description="The operation performed")
    result: float = Field(description="The calculation result")
    explanation: str = Field(description="Step-by-step explanation")


def get_weather(location: str) -> dict:
    """Get weather information for a location."""
    # Mock weather service
    weather_data = {
        "New York": {"temp": "72°F", "conditions": "Sunny"},
        "London": {"temp": "15°C", "conditions": "Cloudy"},
        "Tokyo": {"temp": "25°C", "conditions": "Rainy"},
    }
    
    data = weather_data.get(location, {"temp": "20°C", "conditions": "Unknown"})
    return {
        "location": location,
        "temperature": data["temp"],
        "conditions": data["conditions"]
    }


def calculate(operation: str, a: float, b: float) -> dict:
    """Perform mathematical calculations."""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else None
    }
    
    result = operations.get(operation.lower())
    if result is None:
        return {"error": "Invalid operation or division by zero"}
    
    return {
        "operation": f"{a} {operation} {b}",
        "result": result,
        "explanation": f"Calculated {a} {operation} {b} = {result}"
    }


def demo_tool_registration_with_tool_client():
    """Demonstrate tool registration with ToolClient via AgentClient."""
    print("=== Tool Registration with ToolClient ===")
    
    # Initialize clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "test-token"))
    tool_client = ToolClient(openrouter_client)
    agent = AgentClient(tool_client)
    
    # Register tools through the agent proxy
    try:
        agent.register_tool(
            name="get_weather",
            description="Get current weather for a location",
            function=get_weather,
            schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for"
                    }
                },
                "required": ["location"]
            }
        )
        print("✅ Successfully registered weather tool via AgentClient")
        
        agent.register_tool(
            name="calculate",
            description="Perform mathematical calculations",
            function=calculate,
            schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The mathematical operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        )
        print("✅ Successfully registered calculator tool via AgentClient")
        
    except Exception as e:
        print(f"❌ Tool registration failed: {e}")
    
    # Test agent with tools (mock example)
    print("\n📝 Example usage:")
    print('agent.agent("What\'s the weather in New York?", WeatherResponse)')
    print('agent.agent("Calculate 15 + 25", CalculationResponse)')


def demo_tool_registration_with_mcp_client():
    """Demonstrate tool registration with MCPClient via AgentClient."""
    print("\n=== Tool Registration with MCPClient ===")
    
    # Initialize clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "test-token"))
    mcp_client = MCPClient(openrouter_client)
    agent = AgentClient(mcp_client)
    
    # Register individual tools
    try:
        agent.register_tool(
            name="get_weather",
            description="Get current weather for a location",
            function=get_weather,
            schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for"
                    }
                },
                "required": ["location"]
            }
        )
        print("✅ Successfully registered tool with MCPClient via AgentClient")
        
    except Exception as e:
        print(f"❌ Tool registration failed: {e}")
    
    # Register MCP server (mock - would normally connect to real server)
    try:
        # Note: This would fail in real usage without a running MCP server
        # agent.register_mcp_server("example_server", "http://localhost:8000")
        print("📝 MCP server registration available via: agent.register_mcp_server(name, url)")
        
    except Exception as e:
        print(f"⚠️  MCP server registration example: {e}")


def demo_tool_registration_errors():
    """Demonstrate error handling when trying to register tools with unsupported clients."""
    print("\n=== Error Handling for Unsupported Clients ===")
    
    # Try with OpenRouterClient (doesn't support tool registration)
    try:
        openrouter_client = OpenRouterClient(token="test-token")
        agent = AgentClient(openrouter_client)
        
        agent.register_tool(
            name="test_tool",
            description="A test tool",
            function=lambda x: x,
            schema={"type": "object", "properties": {}}
        )
        print("❌ This should not be reached - OpenRouterClient doesn't support tools")
        
    except AttributeError as e:
        print(f"✅ Correctly handled unsupported client: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Try MCP server registration with non-MCP client
    try:
        openrouter_client = OpenRouterClient(token="test-token")
        tool_client = ToolClient(openrouter_client)
        agent = AgentClient(tool_client)
        
        agent.register_mcp_server("test_server", "http://localhost:8000")
        print("❌ This should not be reached - ToolClient doesn't support MCP servers")
        
    except AttributeError as e:
        print(f"✅ Correctly handled unsupported MCP registration: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demo_client_capabilities():
    """Show which clients support which registration methods."""
    print("\n=== Client Capabilities Summary ===")
    
    capabilities = {
        "OpenRouterClient": {
            "parse": "✅",
            "register_tool": "❌",
            "register_mcp_server": "❌"
        },
        "ToolClient": {
            "parse": "✅", 
            "register_tool": "✅",
            "register_mcp_server": "❌"
        },
        "MCPClient": {
            "parse": "✅",
            "register_tool": "✅", 
            "register_mcp_server": "✅"
        }
    }
    
    print("Client capabilities for AgentClient:")
    print("┌─────────────────┬───────┬──────────────┬─────────────────────┐")
    print("│ Client          │ parse │ register_tool│ register_mcp_server │")
    print("├─────────────────┼───────┼──────────────┼─────────────────────┤")
    
    for client, caps in capabilities.items():
        print(f"│ {client:<15} │ {caps['parse']:>5} │ {caps['register_tool']:>12} │ {caps['register_mcp_server']:>19} │")
    
    print("└─────────────────┴───────┴──────────────┴─────────────────────┘")


if __name__ == "__main__":
    print("AgentClient Tool Registration Examples\n")
    print("=" * 60)
    
    demo_tool_registration_with_tool_client()
    demo_tool_registration_with_mcp_client()
    demo_tool_registration_errors()
    demo_client_capabilities()
    
    print("\n" + "=" * 60)
    print("All examples completed! 🎉")
