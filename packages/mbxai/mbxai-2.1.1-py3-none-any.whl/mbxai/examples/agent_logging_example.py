"""
Example demonstrating the enhanced logging and token tracking features of the AgentClient.
"""

import os
import logging
from pydantic import BaseModel, Field

from mbxai.openrouter import OpenRouterClient
from mbxai.agent import AgentClient

# Configure logging to see all the agent information
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class WeatherResponse(BaseModel):
    """Response format for weather information."""
    location: str = Field(description="The location requested")
    current_conditions: str = Field(description="Current weather conditions")
    temperature: str = Field(description="Current temperature")
    forecast: str = Field(description="Weather forecast")
    recommendation: str = Field(description="Clothing or activity recommendation based on weather")

class AnalysisResponse(BaseModel):
    """Response format for complex analysis."""
    summary: str = Field(description="Executive summary of the analysis")
    key_findings: list[str] = Field(description="List of key findings")
    methodology: str = Field(description="How the analysis was conducted")
    recommendations: list[str] = Field(description="Actionable recommendations")
    confidence_level: str = Field(description="Confidence level in the analysis")

def demonstrate_agent_with_questions():
    """Demonstrate agent process with question generation."""
    print("\n" + "="*60)
    print("🔍 DEMO: Agent with Question Generation")
    print("="*60)
    
    try:
        # Note: This requires a real OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ OPENROUTER_API_KEY not found. Using mock example.")
            print("Set OPENROUTER_API_KEY environment variable to run with real API calls.")
            return
        
        openrouter_client = OpenRouterClient(token=api_key)
        agent = AgentClient(openrouter_client, max_iterations=2)
        
        prompt = "I need weather information for planning my outdoor activities this weekend."
        
        print(f"📤 Sending prompt: {prompt}")
        response = agent.agent(prompt, WeatherResponse, ask_questions=True)
        
        if response.has_questions():
            print(f"\n📋 Agent generated {len(response.questions)} questions:")
            for i, question in enumerate(response.questions, 1):
                print(f"  {i}. {question.question} (key: {question.key})")
            
            if response.token_summary:
                print(f"\n📊 Token usage for question generation:")
                print(f"   - Prompt tokens: {response.token_summary.question_generation.prompt_tokens}")
                print(f"   - Completion tokens: {response.token_summary.question_generation.completion_tokens}")
                print(f"   - Total tokens: {response.token_summary.question_generation.total_tokens}")
            
            # Simulate user providing answers
            from mbxai.agent.models import AnswerList, Answer
            
            answers = AnswerList(answers=[
                Answer(key="location", answer="San Francisco, CA"),
                Answer(key="activity_type", answer="hiking and outdoor photography"),
                Answer(key="time_frame", answer="Saturday and Sunday morning")
            ])
            
            print(f"\n📝 Providing answers and continuing...")
            final_response = agent.agent("Continue with answers", WeatherResponse, ask_questions=False, agent_id=response.agent_id, answers=answers)
            
            if final_response.is_complete():
                print("\n✅ Final response received!")
                print(f"📊 Complete token summary:")
                if final_response.token_summary:
                    ts = final_response.token_summary
                    print(f"   - Question generation: {ts.question_generation.total_tokens} tokens")
                    print(f"   - Thinking process: {ts.thinking_process.total_tokens} tokens")
                    print(f"   - Quality checks: {sum(q.total_tokens for q in ts.quality_checks)} tokens ({len(ts.quality_checks)} checks)")
                    print(f"   - Improvements: {sum(i.total_tokens for i in ts.improvements)} tokens ({len(ts.improvements)} iterations)")
                    print(f"   - Final response: {ts.final_response.total_tokens} tokens")
                    print(f"   - TOTAL: {ts.total_tokens} tokens")
                
                # Access the structured response
                weather_data = final_response.final_response
                print(f"\n🌤️  Weather for {weather_data.location}:")
                print(f"   Current: {weather_data.current_conditions}")
                print(f"   Temperature: {weather_data.temperature}")
                print(f"   Recommendation: {weather_data.recommendation}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demonstrate_agent_without_questions():
    """Demonstrate agent process without question generation."""
    print("\n" + "="*60)
    print("⚡ DEMO: Agent without Question Generation (Direct Processing)")
    print("="*60)
    
    try:
        # Note: This requires a real OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ OPENROUTER_API_KEY not found. Using mock example.")
            print("Set OPENROUTER_API_KEY environment variable to run with real API calls.")
            return
        
        openrouter_client = OpenRouterClient(token=api_key)
        agent = AgentClient(openrouter_client, max_iterations=1)
        
        prompt = """
        Analyze the current state of renewable energy adoption in Europe. 
        Focus on solar and wind power, include recent statistics, challenges, 
        and future outlook for the next 5 years.
        """
        
        print(f"📤 Sending prompt: {prompt[:100]}...")
        response = agent.agent(prompt, AnalysisResponse, ask_questions=False)
        
        if response.is_complete():
            print("\n✅ Analysis completed!")
            
            if response.token_summary:
                ts = response.token_summary
                print(f"\n📊 Token usage breakdown:")
                print(f"   - Thinking process: {ts.thinking_process.total_tokens} tokens")
                print(f"   - Quality checks: {sum(q.total_tokens for q in ts.quality_checks)} tokens ({len(ts.quality_checks)} checks)")
                print(f"   - Improvements: {sum(i.total_tokens for i in ts.improvements)} tokens ({len(ts.improvements)} iterations)")
                print(f"   - Final response: {ts.final_response.total_tokens} tokens")
                print(f"   - TOTAL: {ts.total_tokens} tokens")
            
            # Access the structured response
            analysis = response.final_response
            print(f"\n📊 Analysis Results:")
            print(f"   Summary: {analysis.summary[:150]}...")
            print(f"   Key Findings: {len(analysis.key_findings)} items")
            print(f"   Recommendations: {len(analysis.recommendations)} items")
            print(f"   Confidence: {analysis.confidence_level}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demonstrate_different_iteration_settings():
    """Demonstrate different max_iterations settings and their effect on token usage."""
    print("\n" + "="*60)
    print("🔄 DEMO: Different Iteration Settings")
    print("="*60)
    
    iteration_configs = [
        {"iterations": 0, "description": "No quality checks"},
        {"iterations": 1, "description": "Basic quality check"},
        {"iterations": 3, "description": "Thorough quality improvement"}
    ]
    
    prompt = "Explain quantum computing in simple terms for a business audience."
    
    for config in iteration_configs:
        print(f"\n📋 Testing with {config['iterations']} max iterations ({config['description']})")
        print("-" * 40)
        
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                print(f"   ❌ Skipping - OPENROUTER_API_KEY not found")
                continue
            
            openrouter_client = OpenRouterClient(token=api_key)
            agent = AgentClient(openrouter_client, max_iterations=config["iterations"])
            
            print(f"   🚀 Processing with max_iterations={config['iterations']}")
            print(f"   - Description: {config['description']}")
            print(f"   - Expected processing time: {'Low' if config['iterations'] <= 1 else 'Medium' if config['iterations'] <= 2 else 'High'}")
            print(f"   - Expected response quality: {'Basic' if config['iterations'] == 0 else 'Good' if config['iterations'] <= 2 else 'Excellent'}")
            
            # In real usage, you would call:
            # response = agent.agent(prompt, AnalysisResponse, ask_questions=False)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 Agent Client Logging and Token Tracking Demo")
    print("This example demonstrates the enhanced logging and token usage tracking features.")
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n⚠️  Note: To run with real API calls, set the OPENROUTER_API_KEY environment variable.")
        print("The examples will show the logging structure but won't make actual API calls.")
    
    # Run demonstrations
    demonstrate_agent_with_questions()
    demonstrate_agent_without_questions() 
    demonstrate_different_iteration_settings()
    
    print("\n✅ Demo completed!")
    print("\nTo see the logging in action, run this script with a valid OPENROUTER_API_KEY.")
    print("You'll see detailed logs showing:")
    print("   - 🚀 Agent process start")
    print("   - ❓ Question generation")
    print("   - 🧠 Thinking process")
    print("   - 🔍 Quality checks")
    print("   - ⚡ Improvements")
    print("   - 📝 Final response generation")
    print("   - 📊 Complete token usage summary")
