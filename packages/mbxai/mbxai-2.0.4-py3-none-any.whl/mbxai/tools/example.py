"""
Example usage of the ToolClient.
"""

from pydantic import BaseModel
from ..openrouter import OpenRouterClient, OpenRouterModel
from .client import ToolClient

# Define a Pydantic model for structured output
class WeatherInfo(BaseModel):
    """Weather information for a location."""
    location: str
    temperature: float
    conditions: str
    humidity: float

# Example tool function
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: The location to get weather for
        
    Returns:
        A string describing the current weather
    """
    # In a real implementation, this would call a weather API
    return f"The weather in {location} is sunny with a temperature of 25°C and 60% humidity."

def main() -> None:
    # Initialize the OpenRouter client
    client = OpenRouterClient(token="your-api-key")
    
    # Initialize the ToolClient
    tool_client = ToolClient(client)
    
    # Register the weather tool
    tool_client.register_tool(
        name="get_weather",
        description="Get the current weather for a location",
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
    
    # Example 1: Simple chat with tool usage
    messages = [
        {"role": "user", "content": "What's the weather like in New York?"}
    ]
    
    response = tool_client.chat(messages)
    print(response.choices[0].message.content)
    
    # Example 2: Structured output with tool usage
    messages = [
        {"role": "user", "content": "Get the weather in London and format it as structured data"}
    ]
    
    response = tool_client.parse(messages, WeatherInfo)
    weather_info = response.choices[0].message.parsed
    print(f"Location: {weather_info.location}")
    print(f"Temperature: {weather_info.temperature}°C")
    print(f"Conditions: {weather_info.conditions}")
    print(f"Humidity: {weather_info.humidity}%")

if __name__ == "__main__":
    main() 