"""
Example usage of the AgentClient.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, AnswerList, Answer


class BookRecommendation(BaseModel):
    """A book recommendation response."""
    title: str = Field(description="The title of the recommended book")
    author: str = Field(description="The author of the book")
    genre: str = Field(description="The genre of the book")
    reason: str = Field(description="Why this book is recommended")
    summary: str = Field(description="A brief summary of the book")


class TravelPlan(BaseModel):
    """A travel plan response."""
    destination: str = Field(description="The travel destination")
    duration: str = Field(description="Duration of the trip")
    activities: list[str] = Field(description="List of recommended activities")
    budget_estimate: str = Field(description="Estimated budget for the trip")
    best_time_to_visit: str = Field(description="Best time of year to visit")


def example_with_questions():
    """Example that demonstrates the agent asking questions."""
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    # Create agent with custom max_iterations (default is 2)
    agent = AgentClient(openrouter_client, max_iterations=3)
    
    # Example 1: Book recommendation with questions
    prompt = "I want a book recommendation"
    response = agent.agent(prompt, BookRecommendation, ask_questions=True)
    
    if response.has_questions():
        print("The agent has questions for you:")
        for question in response.questions:
            print(f"- {question.question}")
        
        # Simulate answering the questions
        answers = AnswerList(answers=[
            Answer(key="genre_preference", answer="I love science fiction and fantasy"),
            Answer(key="reading_level", answer="I prefer complex, adult novels"),
            Answer(key="recent_books", answer="I recently read and loved Dune and The Name of the Wind")
        ])
        
        # Continue the agent process with answers using the unified interface
        final_response = agent.agent("Continue with previous questions", BookRecommendation, ask_questions=False, agent_id=response.agent_id, answers=answers)
        
        if final_response.is_complete():
            book_rec = final_response.final_response
            print(f"\nRecommended Book: {book_rec.title} by {book_rec.author}")
            print(f"Genre: {book_rec.genre}")
            print(f"Reason: {book_rec.reason}")
            print(f"Summary: {book_rec.summary}")
    else:
        # No questions, direct response
        book_rec = response.final_response
        print(f"Recommended Book: {book_rec.title} by {book_rec.author}")


def example_without_questions():
    """Example that demonstrates the agent without asking questions."""
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    # Create agent with no quality iterations for faster responses
    agent = AgentClient(openrouter_client, max_iterations=0)
    
    # Example 2: Travel plan without questions
    prompt = "Plan a 5-day trip to Japan for someone interested in culture and food"
    response = agent.agent(prompt, TravelPlan, ask_questions=False)
    
    if response.is_complete():
        travel_plan = response.final_response
        print(f"\nTravel Plan for {travel_plan.destination}")
        print(f"Duration: {travel_plan.duration}")
        print(f"Best time to visit: {travel_plan.best_time_to_visit}")
        print(f"Budget estimate: {travel_plan.budget_estimate}")
        print("Recommended activities:")
        for activity in travel_plan.activities:
            print(f"- {activity}")


def example_with_tool_client():
    """Example using AgentClient with ToolClient."""
    from mbxai import ToolClient
    
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    tool_client = ToolClient(openrouter_client)
    
    # Create agent with tool client
    agent = AgentClient(tool_client)
    
    # Register a simple tool via the agent (proxy method)
    def get_weather(location: str) -> str:
        """Get weather information for a location."""
        # This is a mock implementation
        return f"The weather in {location} is sunny and 72°F"
    
    # Use the agent's register_tool proxy method (schema auto-generated!)
    agent.register_tool(
        name="get_weather",
        description="Get current weather for a location",
        function=get_weather
        # No schema needed - automatically generated from function signature!
    )
    
    class WeatherResponse(BaseModel):
        location: str = Field(description="The location")
        weather: str = Field(description="Weather description")
        recommendations: list[str] = Field(description="Recommendations based on weather")
    
    prompt = "What's the weather like in San Francisco and what should I wear?"
    response = agent.agent(prompt, WeatherResponse, ask_questions=False)
    
    if response.is_complete():
        weather_info = response.final_response
        print(f"\nWeather in {weather_info.location}: {weather_info.weather}")
        print("Recommendations:")
        for rec in weather_info.recommendations:
            print(f"- {rec}")


def example_dialog_conversation():
    """Example demonstrating persistent dialog functionality."""
    print("Example of persistent dialog conversation:")
    
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # Start conversation
    response1 = agent.agent("I want a book recommendation for science fiction", BookRecommendation, ask_questions=False)
    agent_id = response1.agent_id
    
    if response1.is_complete():
        book1 = response1.final_response
        print(f"First recommendation: {book1.title} by {book1.author}")
        
        # Continue conversation with same agent_id
        response2 = agent.agent("Can you recommend something by a different author in the same genre?", BookRecommendation, ask_questions=False, agent_id=agent_id)
        
        if response2.is_complete():
            book2 = response2.final_response
            print(f"Second recommendation: {book2.title} by {book2.author}")
            print(f"Context: {book2.reason}")
    
    # Clean up session when done
    agent.delete_session(agent_id)


if __name__ == "__main__":
    print("=== Agent Client Examples ===\n")
    
    print("1. Example with questions:")
    try:
        example_with_questions()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("2. Example without questions:")
    try:
        example_without_questions()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("3. Example with ToolClient:")
    try:
        example_with_tool_client()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("4. Example with persistent dialog:")
    try:
        example_dialog_conversation()
    except Exception as e:
        print(f"Error: {e}")
