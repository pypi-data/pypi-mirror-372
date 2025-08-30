"""
Example demonstrating the new unified agent interface.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, AnswerList, Answer


class SimpleResponse(BaseModel):
    """A simple response."""
    response: str = Field(description="The response text")
    context_used: str = Field(description="How context was used in this response")


def demonstrate_unified_interface():
    """Demonstrate the unified agent interface with and without questions."""
    print("🔧 DEMO: Unified Agent Interface")
    print("=" * 50)
    
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # Example 1: Start conversation with questions
    print("\n1️⃣ Starting conversation that generates questions:")
    response1 = agent.agent("I need help planning a trip", SimpleResponse, ask_questions=True)
    
    agent_id = response1.agent_id
    print(f"Agent ID: {agent_id}")
    
    if response1.has_questions():
        print(f"📋 Generated {len(response1.questions)} questions:")
        for q in response1.questions:
            print(f"  - {q.question} (key: {q.key})")
        
        # Example 2: Provide answers using the unified interface
        print(f"\n2️⃣ Providing answers using unified interface:")
        answers = AnswerList(answers=[
            Answer(key="destination", answer="Japan"),
            Answer(key="duration", answer="10 days"),
            Answer(key="budget", answer="$3000"),
            Answer(key="interests", answer="culture, food, temples")
        ])
        
        response2 = agent.agent(
            "Now help me plan the trip", 
            SimpleResponse, 
            ask_questions=False, 
            agent_id=agent_id, 
            answers=answers
        )
        
        if response2.is_complete():
            trip_plan = response2.final_response
            print(f"Response: {trip_plan.response}")
            print(f"Context used: {trip_plan.context_used}")
    
    # Example 3: Continue the conversation
    print(f"\n3️⃣ Continuing conversation without questions:")
    response3 = agent.agent(
        "What about transportation within Japan?", 
        SimpleResponse, 
        ask_questions=False, 
        agent_id=agent_id
    )
    
    if response3.is_complete():
        transport_info = response3.final_response
        print(f"Response: {transport_info.response}")
        print(f"Context used: {transport_info.context_used}")
    
    # Example 4: Using answers without previous questions (new session)
    print(f"\n4️⃣ Starting new session with direct answers (no questions):")
    new_answers = AnswerList(answers=[
        Answer(key="city", answer="Tokyo"),
        Answer(key="travel_style", answer="luxury"),
        Answer(key="group_size", answer="2 people")
    ])
    
    response4 = agent.agent(
        "Recommend restaurants",
        SimpleResponse,
        ask_questions=False,
        answers=new_answers  # New session, no agent_id provided
    )
    
    if response4.is_complete():
        restaurant_info = response4.final_response
        print(f"New Agent ID: {response4.agent_id}")
        print(f"Response: {restaurant_info.response}")
        print(f"Context used: {restaurant_info.context_used}")
    
    # Show active sessions
    print(f"\n📊 Active Sessions: {agent.list_sessions()}")
    
    # Cleanup
    print(f"\n🗑️ Cleaning up sessions...")
    agent.delete_session(agent_id)
    if response4.agent_id != agent_id:
        agent.delete_session(response4.agent_id)
    print(f"Active Sessions after cleanup: {agent.list_sessions()}")


if __name__ == "__main__":
    try:
        demonstrate_unified_interface()
    except Exception as e:
        print(f"Error: {e}")
