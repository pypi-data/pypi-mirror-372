"""
Example script demonstrating how to use the parse function with OpenRouterClient.
"""

import os
import logging
from typing import Any
from pydantic import BaseModel, Field
from mbxai.openrouter.client import OpenRouterClient, OpenRouterModel

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

async def main():
    # Get API token from environment variable
    token = os.getenv("OPENROUTER_API_KEY")
    if not token:
        raise ValueError("Please set the OPENROUTER_API_KEY environment variable")

    # Initialize the OpenRouter client
    logger.info("Initializing OpenRouter client")
    client = OpenRouterClient(
        token=token,
        model=OpenRouterModel.GPT41
    )
    
    # Example 1: Parse weather data for a single location
    logger.info("Parsing weather data for New York")
    messages = [
        {
            "role": "user", 
            "content": "What's the current weather in New York? Please provide temperature, condition, humidity, wind speed, feels like temperature, and precipitation chance."
        }
    ]
    
    response = client.parse(
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
    
    # Example 2: Parse weather data for multiple locations
    logger.info("\nParsing weather data for multiple locations")
    messages = [
        {
            "role": "user", 
            "content": "Compare the weather in London and Tokyo. For each city, provide temperature, condition, humidity, wind speed, feels like temperature, and precipitation chance."
        }
    ]
    
    class MultiLocationWeather(BaseModel):
        """Weather data for multiple locations."""
        locations: list[WeatherData] = Field(..., description="List of weather data for different locations")
    
    response = client.parse(
        messages=messages,
        response_format=MultiLocationWeather,
        timeout=30.0,
    )
    
    multi_weather = response.choices[0].message.parsed
    print("\nWeather comparison:")
    for location_data in multi_weather.locations:
        print(f"\n{location_data.location}:")
        print(f"Temperature: {location_data.temperature}°C")
        print(f"Condition: {location_data.condition}")
        print(f"Humidity: {location_data.humidity}%")
        print(f"Wind Speed: {location_data.wind_speed} km/h")
        print(f"Feels Like: {location_data.feels_like}°C")
        print(f"Precipitation Chance: {location_data.precipitation_chance}%")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 