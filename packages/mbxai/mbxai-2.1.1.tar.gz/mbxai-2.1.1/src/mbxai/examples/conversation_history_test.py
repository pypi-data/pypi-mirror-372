"""
Test example demonstrating conversation history persistence across multiple interactions.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, AnswerList, Answer


class StoryResponse(BaseModel):
    """A story response that should reference previous conversation."""
    story_part: str = Field(description="The current part of the story")
    references_to_previous: str = Field(description="How this connects to our previous conversation")
    conversation_context: str = Field(description="Summary of what was discussed before")


class ChatResponse(BaseModel):
    """A general chat response."""
    response: str = Field(description="The response to the user's message")
    context_awareness: str = Field(description="What the AI remembers from our conversation")


def test_conversation_history_persistence():
    """Test that conversation history persists and is used across multiple interactions."""
    print("🧪 TESTING: Conversation History Persistence")
    print("=" * 60)
    
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # First interaction - establish context
    print("\n1️⃣ First interaction - setting up story context:")
    prompt1 = "I want to tell a collaborative story about a space explorer named Luna who discovers an ancient alien artifact on Mars."
    response1 = agent.agent(prompt1, StoryResponse, ask_questions=False)
    
    agent_id = response1.agent_id
    print(f"Agent ID: {agent_id}")
    
    if response1.is_complete():
        story1 = response1.final_response
        print(f"Story Part 1: {story1.story_part[:200]}...")
        print(f"Context awareness: {story1.context_awareness}")
        
        # Check session info
        session_info = agent.get_session_info(agent_id)
        print(f"📊 Session after first interaction: {session_info['conversation_length']} messages")
    
    # Second interaction - continue story, should reference Luna and the artifact
    print(f"\n2️⃣ Second interaction - continuing story (should remember Luna and artifact):")
    prompt2 = "Luna touches the artifact and something amazing happens. Continue the story."
    response2 = agent.agent(prompt2, StoryResponse, ask_questions=False, agent_id=agent_id)
    
    if response2.is_complete():
        story2 = response2.final_response
        print(f"Story Part 2: {story2.story_part[:200]}...")
        print(f"References to previous: {story2.references_to_previous}")
        print(f"Conversation context: {story2.conversation_context}")
        
        # Check session info
        session_info = agent.get_session_info(agent_id)
        print(f"📊 Session after second interaction: {session_info['conversation_length']} messages")
    
    # Third interaction - change topic but should still remember story context
    print(f"\n3️⃣ Third interaction - changing topic (should still remember our story):")
    prompt3 = "Actually, let's pause the story. What do you think Luna's personality is like based on our story so far?"
    response3 = agent.agent(prompt3, ChatResponse, ask_questions=False, agent_id=agent_id)
    
    if response3.is_complete():
        chat3 = response3.final_response
        print(f"Response: {chat3.response}")
        print(f"Context awareness: {chat3.context_awareness}")
        
        # Check session info
        session_info = agent.get_session_info(agent_id)
        print(f"📊 Session after third interaction: {session_info['conversation_length']} messages")
    
    # Fourth interaction - return to story, should remember everything
    print(f"\n4️⃣ Fourth interaction - returning to story (should remember all previous context):")
    prompt4 = "Great! Now let's continue Luna's story from where we left off. What happens next with the artifact?"
    response4 = agent.agent(prompt4, StoryResponse, ask_questions=False, agent_id=agent_id)
    
    if response4.is_complete():
        story4 = response4.final_response
        print(f"Story Part 4: {story4.story_part[:200]}...")
        print(f"References to previous: {story4.references_to_previous}")
        print(f"Conversation context: {story4.conversation_context}")
        
        # Final session info
        session_info = agent.get_session_info(agent_id)
        print(f"📊 Final session state: {session_info['conversation_length']} messages")
        print(f"Session step: {session_info.get('step', 'unknown')}")
    
    # Display full conversation history
    print(f"\n💬 FULL CONVERSATION HISTORY:")
    session_info = agent.get_session_info(agent_id)
    history = session_info.get('conversation_history', [])
    for i, msg in enumerate(history, 1):
        role = msg['role'].upper()
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"{i:2d}. {role}: {content}")
    
    # Cleanup
    print(f"\n🗑️ Cleaning up session {agent_id}")
    agent.delete_session(agent_id)


def test_with_questions_and_history():
    """Test conversation history with questions and answers."""
    print("\n🧪 TESTING: Questions + Answers + History")
    print("=" * 60)
    
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # Start with questions
    print("\n1️⃣ Starting conversation with questions:")
    response1 = agent.agent("I want a personalized workout plan", ChatResponse, ask_questions=True)
    
    agent_id = response1.agent_id
    print(f"Agent ID: {agent_id}")
    
    if response1.has_questions():
        print(f"📋 Generated {len(response1.questions)} questions:")
        for q in response1.questions:
            print(f"  - {q.question}")
        
        # Answer questions
        answers = AnswerList(answers=[
            Answer(key="fitness_level", answer="Beginner"),
            Answer(key="goals", answer="Weight loss and muscle building"),
            Answer(key="time_available", answer="30 minutes per day, 4 days a week"),
            Answer(key="equipment", answer="Home gym with dumbbells and resistance bands")
        ])
        
        print(f"\n2️⃣ Providing answers:")
        response2 = agent.agent("Here are my answers", ChatResponse, ask_questions=False, agent_id=agent_id, answers=answers)
        
        if response2.is_complete():
            workout_plan = response2.final_response
            print(f"Workout plan: {workout_plan.response[:200]}...")
            print(f"Context awareness: {workout_plan.context_awareness}")
        
        # Continue conversation
        print(f"\n3️⃣ Follow-up question (should remember all previous context):")
        response3 = agent.agent("Can you modify this plan to focus more on cardio?", ChatResponse, ask_questions=False, agent_id=agent_id)
        
        if response3.is_complete():
            modified_plan = response3.final_response
            print(f"Modified plan: {modified_plan.response[:200]}...")
            print(f"Context awareness: {modified_plan.context_awareness}")
        
        # Show history
        session_info = agent.get_session_info(agent_id)
        print(f"\n💬 Conversation had {session_info['conversation_length']} messages")
        
        # Cleanup
        agent.delete_session(agent_id)


if __name__ == "__main__":
    try:
        test_conversation_history_persistence()
        print("\n" + "="*80 + "\n")
        test_with_questions_and_history()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
