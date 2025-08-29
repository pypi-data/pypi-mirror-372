"""
Example demonstrating automatic schema generation from function signatures.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from mbxai import AgentClient, ToolClient, OpenRouterClient


class WeatherResponse(BaseModel):
    """Response for weather queries."""
    location: str = Field(description="The location")
    temperature: str = Field(description="Current temperature")
    conditions: str = Field(description="Weather conditions")
    recommendations: list[str] = Field(description="Recommendations based on weather")


def get_weather(location: str, unit: str = "fahrenheit") -> dict:
    """Get weather information for a location.
    
    Args:
        location: The city or location name
        unit: Temperature unit (fahrenheit or celsius)
    
    Returns:
        Weather information dictionary
    """
    # Mock weather service
    temp = "72°F" if unit == "fahrenheit" else "22°C"
    return {
        "location": location,
        "temperature": temp,
        "conditions": "Sunny"
    }


def calculate_tip(bill_amount: float, tip_percentage: float = 18.0, split_count: int = 1) -> dict:
    """Calculate tip and split the bill.
    
    Args:
        bill_amount: Total bill amount in dollars
        tip_percentage: Tip percentage (default 18%)
        split_count: Number of people to split between (default 1)
    
    Returns:
        Calculation results
    """
    tip_amount = bill_amount * (tip_percentage / 100)
    total_amount = bill_amount + tip_amount
    per_person = total_amount / split_count
    
    return {
        "bill_amount": bill_amount,
        "tip_amount": tip_amount,
        "total_amount": total_amount,
        "per_person": per_person,
        "split_count": split_count
    }


def search_knowledge(query: str, category: Optional[str] = None, max_results: int = 5) -> dict:
    """Search knowledge base for information.
    
    Args:
        query: Search query string
        category: Optional category filter
        max_results: Maximum number of results to return
    
    Returns:
        Search results
    """
    # Mock search results
    return {
        "query": query,
        "category": category,
        "results": [f"Result {i+1} for '{query}'" for i in range(min(max_results, 3))],
        "total_found": max_results
    }


def demo_automatic_schema_generation():
    """Demonstrate automatic schema generation from function signatures."""
    
    print("=== Automatic Schema Generation Example ===\n")
    
    # Initialize clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "test-token"))
    tool_client = ToolClient(openrouter_client)
    agent = AgentClient(tool_client)
    
    print("Registering tools with automatic schema generation...\n")
    
    # Register tools WITHOUT providing schemas - they'll be auto-generated
    tools_to_register = [
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "function": get_weather
        },
        {
            "name": "calculate_tip", 
            "description": "Calculate tip and split bill between people",
            "function": calculate_tip
        },
        {
            "name": "search_knowledge",
            "description": "Search knowledge base for information",
            "function": search_knowledge
        }
    ]
    
    for tool_info in tools_to_register:
        try:
            # Register without schema - will be auto-generated
            agent.register_tool(
                name=tool_info["name"],
                description=tool_info["description"],
                function=tool_info["function"]
                # Note: No schema parameter - it will be auto-generated!
            )
            print(f"✅ Registered '{tool_info['name']}' with auto-generated schema")
            
        except Exception as e:
            print(f"❌ Failed to register '{tool_info['name']}': {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Show what schemas were generated
    print("Generated Tool Schemas:")
    print("-" * 25)
    
    # Access the registered tools to show their schemas
    if hasattr(tool_client, '_tools'):
        for tool_name, tool in tool_client._tools.items():
            print(f"\n🔧 Tool: {tool_name}")
            print(f"   Description: {tool.description}")
            print(f"   Schema keys: {list(tool.schema.get('properties', {}).keys())}")
            print(f"   Required params: {tool.schema.get('required', [])}")
            
            # Show a few key properties
            properties = tool.schema.get('properties', {})
            for prop_name, prop_schema in list(properties.items())[:3]:  # Show first 3
                prop_type = prop_schema.get('type', 'unknown')
                prop_desc = prop_schema.get('description', 'No description')
                print(f"   - {prop_name}: {prop_type} - {prop_desc}")
    
    print("\n" + "="*50 + "\n")
    
    # Demonstrate usage examples
    print("Example usage with auto-generated schemas:")
    print('agent.agent("What\'s the weather in Tokyo?", WeatherResponse)')
    print('agent.agent("Calculate tip for a $85 bill split 4 ways", CalculationResponse)')
    print('agent.agent("Search for Python tutorials", SearchResponse)')


def demo_manual_vs_automatic():
    """Compare manual schema vs automatic generation."""
    
    print("\n=== Manual vs Automatic Schema Comparison ===\n")
    
    openrouter_client = OpenRouterClient(token="test-token")
    tool_client = ToolClient(openrouter_client)
    
    # Example function
    def example_function(name: str, age: int, active: bool = True) -> str:
        """Example function for schema comparison.
        
        Args:
            name: Person's name
            age: Person's age in years  
            active: Whether person is active
        """
        return f"{name} is {age} years old and {'active' if active else 'inactive'}"
    
    print("1. Manual Schema (traditional approach):")
    manual_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Person's name"},
            "age": {"type": "integer", "description": "Person's age in years"},
            "active": {"type": "boolean", "description": "Whether person is active"}
        },
        "required": ["name", "age"],
        "additionalProperties": False
    }
    print(f"   Properties: {list(manual_schema['properties'].keys())}")
    print(f"   Required: {manual_schema['required']}")
    
    print("\n2. Automatic Schema (from function signature):")
    try:
        # Register with auto-generation
        tool_client.register_tool(
            "example_tool",
            "Example tool with auto-generated schema", 
            example_function
            # No schema provided - will be auto-generated
        )
        
        auto_tool = tool_client._tools.get("example_tool")
        if auto_tool:
            auto_schema = auto_tool.schema
            print(f"   Properties: {list(auto_schema.get('properties', {}).keys())}")
            print(f"   Required: {auto_schema.get('required', [])}")
            print(f"   Additional Properties: {auto_schema.get('additionalProperties')}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✨ Benefits of automatic generation:")
    print("   - No manual schema writing required")
    print("   - Automatically extracts types from function signature")
    print("   - Handles default values correctly") 
    print("   - Uses existing convert_to_strict_schema pipeline")
    print("   - Reduces chance of schema/function mismatch")


if __name__ == "__main__":
    demo_automatic_schema_generation()
    demo_manual_vs_automatic()
    
    print("\n" + "="*60)
    print("Automatic schema generation demo completed! 🎉")
    print("\nKey benefits:")
    print("• Zero-config tool registration")
    print("• Type-safe schema generation")  
    print("• Leverages existing Pydantic infrastructure")
    print("• Compatible with MCPTool.to_openai_function() approach")
