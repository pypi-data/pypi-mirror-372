"""Example usage of MCP client and server."""

import asyncio
from typing import Any
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from ..openrouter import OpenRouterClient
from .client import MCPClient
from .server import MCPServer


# Create a FastMCP instance for this module
mcp = FastMCP("weather-service")


# Define input/output models
class WeatherInput(BaseModel):
    location: str
    units: str = "celsius"  # Default to celsius, can be "fahrenheit" or "celsius"


class WeatherOutput(BaseModel):
    location: str
    temperature: float
    units: str
    condition: str
    humidity: float


@mcp.tool()
async def get_weather(input: WeatherInput) -> dict[str, Any]:
    """Get weather information for a location.
    
    Args:
        input: WeatherInput model containing location and units preference
    """
    # This is a mock implementation
    temperature = 20 if input.units == "celsius" else 68  # Convert to fahrenheit if needed
    
    return {
        "location": input.location,
        "temperature": temperature,
        "units": input.units,
        "condition": "sunny",
        "humidity": 65,
    }


async def main():
    # Create and start the MCP server
    server = MCPServer("weather-service")
    
    # Register the tool with the MCP server
    server.mcp_server.add_tool(get_weather)
    
    # Create the OpenRouter client
    openrouter_client = OpenRouterClient(token="your-api-key")
    
    # Create the MCP client
    mcp_client = MCPClient(openrouter_client)
    
    # Register the MCP server
    await mcp_client.register_mcp_server(
        name="weather-service",
        base_url="http://localhost:8000"
    )
    
    # Use the tool in a chat
    messages = [{"role": "user", "content": "What's the weather like in New York?"}]
    response = await mcp_client.chat(messages)
    print(response.choices[0].message.content)
    
    # Use the tool with structured output
    response = await mcp_client.parse(messages, WeatherOutput)
    weather_info = response.choices[0].message.parsed
    print(f"Location: {weather_info.location}")
    print(f"Temperature: {weather_info.temperature}°{weather_info.units.upper()}")
    print(f"Condition: {weather_info.condition}")
    print(f"Humidity: {weather_info.humidity}%")


if __name__ == "__main__":
    asyncio.run(main()) 