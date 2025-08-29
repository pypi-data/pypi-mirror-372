"""
Example script demonstrating how to use both parse and tools with OpenRouterClient.
"""

import os
import logging
import random
from typing import Any
from pydantic import BaseModel, Field
from mbxai.openrouter.client import OpenRouterClient, OpenRouterModel
from mbxai.tools.client import ToolClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define a Pydantic model for structured weather data
class WeatherData(BaseModel):
    """Weather data for a location."""
    location: str = Field(..., description="The city name")
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition (e.g., sunny, cloudy)")
    humidity: float = Field(..., description="Humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    precipitation_chance: float = Field(..., description="Chance of precipitation as a percentage")

# Mock weather data for demonstration
WEATHER_DATA = {
    "new york": {"temperature": 22.5, "condition": "sunny", "humidity": 65, "wind_speed": 12, "feels_like": 23.0, "precipitation_chance": 10},
    "london": {"temperature": 18.2, "condition": "cloudy", "humidity": 75, "wind_speed": 8, "feels_like": 17.5, "precipitation_chance": 40},
    "tokyo": {"temperature": 25.7, "condition": "clear", "humidity": 60, "wind_speed": 5, "feels_like": 26.0, "precipitation_chance": 5},
    "paris": {"temperature": 20.1, "condition": "partly cloudy", "humidity": 70, "wind_speed": 10, "feels_like": 19.5, "precipitation_chance": 20},
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
            "wind_speed": round(random.uniform(5, 20)),
            "feels_like": round(random.uniform(15, 30), 1),
            "precipitation_chance": round(random.uniform(0, 100))
        }
    
    # Create WeatherData instance
    weather_data = WeatherData(
        location=location.title(),
        temperature=weather["temperature"],
        condition=weather["condition"],
        humidity=weather["humidity"],
        wind_speed=weather["wind_speed"],
        feels_like=weather["feels_like"],
        precipitation_chance=weather["precipitation_chance"]
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
        model=OpenRouterModel.GPT41
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
    
    # Example 1: Get weather for a single location using tools and parse
    logger.info("Getting weather for New York using tools and parse")
    messages = [
        {
            "role": "user", 
            "content": "What's the current weather in New York? Use the get_weather tool and format the response according to the WeatherData model."
        }
    ]
    
    response = tool_client.parse(
        messages=messages,
        response_format=WeatherData,
        timeout=30.0,
    )
    
    weather_data = response.choices[0].message.parsed
    print("\nWeather data for New York:")
    print(f"Location: {weather_data.location}")
    print(f"Temperature: {weather_data.temperature}°C")
    print(f"Condition: {weather_data.condition}")
    print(f"Humidity: {weather_data.humidity}%")
    print(f"Wind Speed: {weather_data.wind_speed} km/h")
    print(f"Feels Like: {weather_data.feels_like}°C")
    print(f"Precipitation Chance: {weather_data.precipitation_chance}%")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 