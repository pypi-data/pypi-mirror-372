"""
Example script demonstrating how to use the ToolClient with a custom Weather Tool.
"""

import os
import logging
import random
from typing import Any
from pydantic import BaseModel
from mbxai.openrouter.client import OpenRouterClient, OpenRouterModel
from mbxai.tools.client import ToolClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the weather data model
class WeatherData(BaseModel):
    """Weather data for a location."""
    location: str
    temperature: float
    condition: str
    humidity: float
    wind_speed: float

# Mock weather data for demonstration
WEATHER_DATA = {
    "new york": {"temperature": 22.5, "condition": "sunny", "humidity": 65, "wind_speed": 12},
    "london": {"temperature": 18.2, "condition": "cloudy", "humidity": 75, "wind_speed": 8},
    "tokyo": {"temperature": 25.7, "condition": "clear", "humidity": 60, "wind_speed": 5},
    "paris": {"temperature": 20.1, "condition": "partly cloudy", "humidity": 70, "wind_speed": 10},
}

def get_weather(location: str) -> dict[str, Any]:
    """Get weather information for a location.
    
    Args:
        location: The city name to get weather for
        
    Returns:
        Weather information including temperature, condition, humidity, and wind speed
    """
    logger.info(f"Getting weather for location: {location}")
    
    # Convert location to lowercase for case-insensitive matching
    location = location.lower()
    
    # Get weather data or generate random data for unknown locations
    if location in WEATHER_DATA:
        weather = WEATHER_DATA[location]
    else:
        logger.warning(f"No weather data for {location}, generating random data")
        weather = {
            "temperature": round(random.uniform(15, 30), 1),
            "condition": random.choice(["sunny", "cloudy", "clear", "partly cloudy"]),
            "humidity": round(random.uniform(50, 90)),
            "wind_speed": round(random.uniform(5, 20))
        }
    
    # Create WeatherData instance
    weather_data = WeatherData(
        location=location.title(),
        temperature=weather["temperature"],
        condition=weather["condition"],
        humidity=weather["humidity"],
        wind_speed=weather["wind_speed"]
    )
    
    logger.info(f"Weather data retrieved: {weather_data}")
    return weather_data.model_dump()

async def main():
    # Get API token from environment variable
    token = os.getenv("OPENROUTER_API_KEY")
    if not token:
        raise ValueError("Please set the OPENROUTER_API_KEY environment variable")

    # Initialize the OpenRouter client
    logger.info("Initializing OpenRouter client")
    openrouter_client = OpenRouterClient(
        token=token,
        model=OpenRouterModel.GPT35_TURBO
    )
    
    # Initialize the ToolClient
    logger.info("Initializing ToolClient")
    tool_client = ToolClient(openrouter_client)
    
    # Register the weather tool
    logger.info("Registering weather tool")
    tool_client.register_tool(
        name="get_weather",
        description="Get the current weather for a location",
        function=get_weather,
        schema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name to get weather for"
                }
            },
            "required": ["location"]
        }
    )
    
    # Example 1: Simple weather query
    logger.info("Sending weather query for New York")
    messages = [
        {"role": "user", "content": "What's the weather like in New York?"}
    ]
    
    response = tool_client.chat(
        messages,
        timeout=30.0,
    )
    logger.info("Received response from model")
    print("\nResponse for New York weather:")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 