"""
Simple test to verify AgentClient functionality.
"""

from pydantic import BaseModel, Field
from mbxai.agent import AgentClient, AgentResponse, Question, Result
from mbxai.openrouter import OpenRouterClient


class SimpleResponse(BaseModel):
    """A simple response structure for testing."""
    message: str = Field(description="The response message")
    confidence: float = Field(description="Confidence level from 0.0 to 1.0")


def test_agent_validation():
    """Test AgentClient validation of parse method requirement."""
    
    print("=== Testing AgentClient Validation ===")
    
    # Test 1: Valid client with parse method (OpenRouterClient-like)
    class MockOpenRouterClient:
        def parse(self, messages, response_format):
            # Mock response based on the format
            class MockChoice:
                def __init__(self, content):
                    self.message = MockMessage(content)
            
            class MockMessage:
                def __init__(self, content):
                    self.content = content
                    self.parsed = None
            
            class MockResponse:
                def __init__(self, content):
                    self.choices = [MockChoice(content)]
            
            # Return appropriate mock response based on format
            if response_format.__name__ == "QuestionList":
                return MockResponse('{"questions": []}')
            elif response_format.__name__ == "Result":
                return MockResponse('{"result": "This is a test result"}')
            elif response_format.__name__ == "QualityCheck":
                return MockResponse('{"is_good": true, "feedback": ""}')
            elif response_format.__name__ == "SimpleResponse":
                return MockResponse('{"message": "Test completed successfully", "confidence": 0.95}')
            else:
                return MockResponse('{"result": "Default response"}')
    
    try:
        mock_client = MockOpenRouterClient()
        agent = AgentClient(mock_client)
        print("✅ Valid client accepted - has parse method")
        
        # Test max_iterations parameter
        agent_custom = AgentClient(mock_client, max_iterations=3)
        print("✅ Custom max_iterations parameter accepted")
        
        # Test tool registration (should fail for OpenRouterClient-like)
        try:
            agent.register_tool("test", "desc", lambda: None, {})
            print("❌ Tool registration should have failed for OpenRouterClient-like")
        except AttributeError:
            print("✅ Tool registration correctly rejected for OpenRouterClient-like")
            
    except ValueError as e:
        print(f"❌ Valid client rejected: {e}")
        return False
    
    # Test 2: Valid client with parse and register_tool (ToolClient-like)
    class MockToolClient:
        def parse(self, messages, response_format):
            return MockOpenRouterClient().parse(messages, response_format)
        
        def register_tool(self, name, description, function, schema):
            # Mock tool registration
            pass
    
    try:
        mock_tool_client = MockToolClient()
        agent = AgentClient(mock_tool_client)
        print("✅ ToolClient-like client accepted")
        
        # Test tool registration (should succeed)
        agent.register_tool("test", "desc", lambda: None, {})
        print("✅ Tool registration succeeded for ToolClient-like")
        
    except Exception as e:
        print(f"❌ ToolClient-like test failed: {e}")
    
    # Test 3: Invalid client without parse method
    class MockInvalidClient:
        def create(self, messages, **kwargs):
            return "No parse method"
    
    try:
        invalid_client = MockInvalidClient()
        agent = AgentClient(invalid_client)
        print("❌ Invalid client accepted - should have been rejected!")
        return False
    except ValueError as e:
        print(f"✅ Invalid client correctly rejected: {e}")
    
    return True


def test_agent_workflow():
    """Test the basic agent workflow without actual API calls."""
    
    # Mock OpenRouter client for testing
    class MockOpenRouterClient:
        def parse(self, messages, response_format):
            # Mock response based on the format
            class MockChoice:
                def __init__(self, content):
                    self.message = MockMessage(content)
            
            class MockMessage:
                def __init__(self, content):
                    self.content = content
                    self.parsed = None
            
            class MockResponse:
                def __init__(self, content):
                    self.choices = [MockChoice(content)]
            
            # Return appropriate mock response based on format
            if response_format.__name__ == "QuestionList":
                return MockResponse('{"questions": []}')
            elif response_format.__name__ == "Result":
                return MockResponse('{"result": "This is a test result"}')
            elif response_format.__name__ == "QualityCheck":
                return MockResponse('{"is_good": true, "feedback": ""}')
            elif response_format.__name__ == "SimpleResponse":
                return MockResponse('{"message": "Test completed successfully", "confidence": 0.95}')
            else:
                return MockResponse('{"result": "Default response"}')
    
    print("\n=== Testing Agent Workflow ===")
    
    # Test the agent
    mock_client = MockOpenRouterClient()
    agent = AgentClient(mock_client)
    
    # Test without questions
    prompt = "Test prompt"
    response = agent.agent(prompt, SimpleResponse, ask_questions=False)
    
    print("Agent Test Results:")
    print(f"Has questions: {response.has_questions()}")
    print(f"Is complete: {response.is_complete()}")
    
    if response.is_complete():
        print(f"Final response type: {type(response.final_response)}")
        print(f"Final response: {response.final_response}")
    
    return response


if __name__ == "__main__":
    # Run validation tests first
    validation_passed = test_agent_validation()
    
    if validation_passed:
        # Then run workflow test
        test_agent_workflow()
    else:
        print("❌ Validation tests failed, skipping workflow test")
