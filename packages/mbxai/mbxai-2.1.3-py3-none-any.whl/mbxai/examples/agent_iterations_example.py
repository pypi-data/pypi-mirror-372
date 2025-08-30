"""
Example demonstrating AgentClient max_iterations configuration.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient


class DetailedAnalysis(BaseModel):
    """A detailed analysis response."""
    topic: str = Field(description="The topic being analyzed")
    key_points: list[str] = Field(description="Key points of the analysis")
    depth_score: int = Field(description="Depth score from 1-10")
    recommendations: list[str] = Field(description="Recommendations based on analysis")
    conclusion: str = Field(description="Overall conclusion")


def demo_different_iteration_settings():
    """Demonstrate how max_iterations affects response quality."""
    
    print("=== AgentClient max_iterations Configuration Demo ===\n")
    
    # Complex prompt that benefits from iteration
    complex_prompt = """
    Analyze the impact of artificial intelligence on modern education systems. 
    Consider both positive and negative aspects, provide specific examples, 
    and suggest practical implementation strategies for educational institutions.
    """
    
    # Test with different iteration settings
    iteration_configs = [
        {"iterations": 0, "description": "No quality iterations (fastest)"},
        {"iterations": 1, "description": "Single quality check"},
        {"iterations": 2, "description": "Default - two quality iterations"},
        {"iterations": 3, "description": "Enhanced quality with three iterations"},
    ]
    
    for config in iteration_configs:
        print(f"🔄 Testing with {config['iterations']} iterations - {config['description']}")
        print("-" * 60)
        
        try:
            # Initialize client with specific iteration count
            openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "test-token"))
            agent = AgentClient(openrouter_client, max_iterations=config['iterations'])
            
            print(f"Agent configured with max_iterations={config['iterations']}")
            
            # Mock the response since we can't actually call the API
            print("📝 Example response would be generated with this configuration:")
            print(f"   - Quality improvement cycles: {config['iterations']}")
            print(f"   - Expected processing time: {'Low' if config['iterations'] <= 1 else 'Medium' if config['iterations'] <= 2 else 'High'}")
            print(f"   - Expected response quality: {'Basic' if config['iterations'] == 0 else 'Good' if config['iterations'] <= 2 else 'Excellent'}")
            
            # In real usage, you would call:
            # response = agent.agent(complex_prompt, DetailedAnalysis, ask_questions=False)
            
        except Exception as e:
            print(f"❌ Error with {config['iterations']} iterations: {e}")
        
        print()


def demo_iteration_validation():
    """Demonstrate validation of max_iterations parameter."""
    
    print("=== max_iterations Validation ===\n")
    
    test_cases = [
        {"value": -1, "should_pass": False, "description": "Negative value"},
        {"value": 0, "should_pass": True, "description": "Zero (no iterations)"},
        {"value": 1, "should_pass": True, "description": "Single iteration"},
        {"value": 5, "should_pass": True, "description": "High iteration count"},
    ]
    
    openrouter_client = OpenRouterClient(token="test-token")
    
    for test in test_cases:
        try:
            agent = AgentClient(openrouter_client, max_iterations=test["value"])
            if test["should_pass"]:
                print(f"✅ {test['description']}: max_iterations={test['value']} accepted")
            else:
                print(f"❌ {test['description']}: Should have failed but didn't")
        except ValueError as e:
            if not test["should_pass"]:
                print(f"✅ {test['description']}: Correctly rejected - {e}")
            else:
                print(f"❌ {test['description']}: Unexpectedly rejected - {e}")
        except Exception as e:
            print(f"❌ {test['description']}: Unexpected error - {e}")


def demo_performance_considerations():
    """Show performance implications of different iteration settings."""
    
    print("\n=== Performance Considerations ===\n")
    
    print("max_iterations Impact Analysis:")
    print("┌─────────────┬─────────────────┬─────────────────┬─────────────────┐")
    print("│ Iterations  │ API Calls       │ Processing Time │ Quality Level   │")
    print("├─────────────┼─────────────────┼─────────────────┼─────────────────┤")
    print("│ 0           │ 2 calls         │ Fastest         │ Basic           │")
    print("│ 1           │ 4 calls         │ Fast            │ Good            │")
    print("│ 2 (default) │ 6 calls         │ Moderate        │ Very Good       │")
    print("│ 3           │ 8 calls         │ Slower          │ Excellent       │")
    print("│ 4+          │ 10+ calls       │ Slowest         │ Diminishing     │")
    print("└─────────────┴─────────────────┴─────────────────┴─────────────────┘")
    
    print("\nRecommendations:")
    print("• Use max_iterations=0 for: Quick responses, simple queries, real-time applications")
    print("• Use max_iterations=1 for: Balanced performance and quality")
    print("• Use max_iterations=2 for: Default - good balance (recommended)")
    print("• Use max_iterations=3+ for: Complex analysis, critical applications, maximum quality")
    
    print("\nAPI Call Breakdown per agent() call:")
    print("• Question generation: 1 call")
    print("• Initial processing: 1 call")  
    print("• Quality check + improvement: 2 calls per iteration")
    print("• Final formatting: 1 call")
    print("• Total = 3 + (2 × max_iterations) calls")


def demo_use_cases():
    """Show appropriate use cases for different iteration settings."""
    
    print("\n=== Use Case Examples ===\n")
    
    use_cases = [
        {
            "scenario": "Chatbot Quick Responses",
            "iterations": 0,
            "reasoning": "Speed is critical, basic quality acceptable"
        },
        {
            "scenario": "Content Summarization",
            "iterations": 1,
            "reasoning": "Some quality improvement needed, moderate speed"
        },
        {
            "scenario": "Business Report Generation",
            "iterations": 2,
            "reasoning": "Default balanced approach for professional content"
        },
        {
            "scenario": "Academic Research Analysis",
            "iterations": 3,
            "reasoning": "High quality required, processing time less critical"
        },
        {
            "scenario": "Legal Document Review",
            "iterations": 4,
            "reasoning": "Maximum accuracy needed, time not a constraint"
        }
    ]
    
    for case in use_cases:
        print(f"📋 {case['scenario']}")
        print(f"   Recommended max_iterations: {case['iterations']}")
        print(f"   Reasoning: {case['reasoning']}")
        print(f"   Example: agent = AgentClient(client, max_iterations={case['iterations']})")
        print()


if __name__ == "__main__":
    demo_different_iteration_settings()
    demo_iteration_validation()
    demo_performance_considerations()
    demo_use_cases()
    
    print("=" * 60)
    print("max_iterations configuration demo completed! 🎉")
