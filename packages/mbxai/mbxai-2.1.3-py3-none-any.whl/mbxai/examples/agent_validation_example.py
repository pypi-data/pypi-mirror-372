"""
Example demonstrating AgentClient validation and error handling.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, ToolClient
from mbxai.mcp import MCPClient


class SimpleResponse(BaseModel):
    """A simple response for testing."""
    message: str = Field(description="The response message")


class MockClientWithoutParse:
    """Mock client that doesn't have a parse method."""
    def create(self, messages, **kwargs):
        return "This client doesn't support structured responses"


def demo_client_validation():
    """Demonstrate AgentClient validation of client capabilities."""
    
    print("=== AgentClient Validation Examples ===\n")
    
    # Example 1: Valid clients
    print("1. Testing valid clients with parse method:")
    
    try:
        # OpenRouterClient - has parse method
        openrouter_client = OpenRouterClient(token="test-token")
        agent1 = AgentClient(openrouter_client)
        print("✅ OpenRouterClient: Successfully created AgentClient")
    except Exception as e:
        print(f"❌ OpenRouterClient: {e}")
    
    try:
        # ToolClient - has parse method (inherits from OpenRouterClient functionality)
        openrouter_client = OpenRouterClient(token="test-token")
        tool_client = ToolClient(openrouter_client)
        agent2 = AgentClient(tool_client)
        print("✅ ToolClient: Successfully created AgentClient")
    except Exception as e:
        print(f"❌ ToolClient: {e}")
    
    try:
        # MCPClient - has parse method (inherits from ToolClient)
        openrouter_client = OpenRouterClient(token="test-token")
        mcp_client = MCPClient(openrouter_client)
        agent3 = AgentClient(mcp_client)
        print("✅ MCPClient: Successfully created AgentClient")
    except Exception as e:
        print(f"❌ MCPClient: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Invalid client
    print("2. Testing invalid client without parse method:")
    
    try:
        mock_client = MockClientWithoutParse()
        agent_invalid = AgentClient(mock_client)
        print("❌ This should not be reached - validation failed!")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid client: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Demonstrate why parse method is required
    print("3. Why structured responses are essential for AgentClient:")
    print("""
The AgentClient requires structured responses because it:
- Generates questions as QuestionList objects
- Performs quality checks as QualityCheck objects  
- Processes intermediate results as Result objects
- Returns final responses as user-defined Pydantic models

Without structured parsing, the agent cannot reliably:
- Extract questions to ask users
- Determine if results need improvement
- Format final responses correctly
- Handle the multi-step thinking process
    """)


def demo_agent_workflow():
    """Demonstrate the complete agent workflow."""
    print("4. Complete AgentClient workflow example:")
    
    # Note: This would require a real API token to run
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  Set OPENROUTER_API_KEY environment variable to run live examples")
        return
    
    try:
        # Initialize with real client
        openrouter_client = OpenRouterClient(token=api_key)
        agent = AgentClient(openrouter_client)
        
        # Test without questions
        response = agent.agent(
            prompt="Explain the benefits of structured AI responses", 
            final_response_structure=SimpleResponse,
            ask_questions=False
        )
        
        if response.is_complete():
            print(f"✅ Agent response: {response.final_response.message}")
        else:
            print("❌ Expected complete response but got questions")
            
    except Exception as e:
        print(f"❌ Agent workflow error: {e}")


if __name__ == "__main__":
    demo_client_validation()
    print("\n" + "="*70 + "\n")
    demo_agent_workflow()
