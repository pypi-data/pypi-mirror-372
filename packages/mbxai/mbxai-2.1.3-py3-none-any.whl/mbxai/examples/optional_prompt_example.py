"""
Example demonstrating optional prompt functionality with existing agent sessions.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, AnswerList, Answer


class ConversationResponse(BaseModel):
    """A general conversation response."""
    response: str = Field(description="The response to the conversation")
    context_used: str = Field(description="How previous conversation history was used")
    continuation_type: str = Field(description="Type of continuation (new topic, follow-up, etc.)")


class StoryResponse(BaseModel):
    """A story response."""
    story_continuation: str = Field(description="The next part of the story")
    character_development: str = Field(description="How characters developed in this part")
    plot_advancement: str = Field(description="How the plot advanced")


def demonstrate_optional_prompt():
    """Demonstrate using agent with optional prompts for existing sessions."""
    print("🎭 DEMO: Optional Prompt with Existing Agent Sessions")
    print("=" * 60)
    
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # First interaction - establish a story context
    print("\n1️⃣ First interaction - establishing story context:")
    response1 = agent.agent(
        prompt="Let's create a story about a detective solving a mystery in a small town",
        final_response_structure=StoryResponse,
        ask_questions=False
    )
    
    agent_id = response1.agent_id
    print(f"Agent ID: {agent_id}")
    
    if response1.is_complete():
        story1 = response1.final_response
        print(f"Story start: {story1.story_continuation[:150]}...")
        print(f"Characters: {story1.character_development}")
    
    # Second interaction - continue with explicit prompt
    print(f"\n2️⃣ Second interaction - continue with explicit prompt:")
    response2 = agent.agent(
        prompt="The detective finds a mysterious letter. What does it say?",
        agent_id=agent_id,
        ask_questions=False
    )
    
    if response2.is_complete():
        story2 = response2.final_response
        print(f"Story continuation: {story2.story_continuation[:150]}...")
        print(f"Plot advancement: {story2.plot_advancement}")
    
    # Third interaction - continue WITHOUT explicit prompt (using only history)
    print(f"\n3️⃣ Third interaction - continue WITHOUT explicit prompt (history-based):")
    try:
        response3 = agent.agent(
            agent_id=agent_id,  # Only provide agent_id, no prompt
            ask_questions=False
        )
        
        if response3.is_complete():
            story3 = response3.final_response
            print(f"History-based continuation: {story3.story_continuation[:150]}...")
            print(f"Character development: {story3.character_development}")
            print(f"Plot advancement: {story3.plot_advancement}")
        
    except Exception as e:
        print(f"Error with history-based continuation: {e}")
    
    # Fourth interaction - switch response format but use same session
    print(f"\n4️⃣ Fourth interaction - switch to conversation format:")
    response4 = agent.agent(
        prompt="What do you think about this story so far?",
        final_response_structure=ConversationResponse,
        agent_id=agent_id,
        ask_questions=False
    )
    
    if response4.is_complete():
        conv4 = response4.final_response
        print(f"Analysis: {conv4.response[:150]}...")
        print(f"Context used: {conv4.context_used}")
        print(f"Continuation type: {conv4.continuation_type}")
    
    # Fifth interaction - continue conversation without prompt
    print(f"\n5️⃣ Fifth interaction - continue conversation analysis without prompt:")
    try:
        response5 = agent.agent(
            agent_id=agent_id,
            ask_questions=False
        )
        
        if response5.is_complete():
            conv5 = response5.final_response
            print(f"Continued analysis: {conv5.response[:150]}...")
            print(f"Context used: {conv5.context_used}")
            print(f"Continuation type: {conv5.continuation_type}")
        
    except Exception as e:
        print(f"Error with continued conversation: {e}")
    
    # Show final session state
    session_info = agent.get_session_info(agent_id)
    print(f"\n📊 Final session state:")
    print(f"   - Total messages: {session_info['conversation_length']}")
    print(f"   - Session step: {session_info.get('step', 'unknown')}")
    print(f"   - Has final_response_structure: {'final_response_structure' in session_info}")
    
    # Cleanup
    agent.delete_session(agent_id)


def demonstrate_error_cases():
    """Demonstrate error cases with optional prompt."""
    print("\n🚨 DEMO: Error Cases with Optional Prompt")
    print("=" * 50)
    
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # Error case 1: No prompt and no existing session
    print("\n❌ Error case 1: No prompt, no existing session")
    try:
        response = agent.agent(ask_questions=False)
        print("This should have failed!")
    except ValueError as e:
        print(f"Expected error: {e}")
    
    # Error case 2: No prompt and no final_response_structure for new session
    print("\n❌ Error case 2: No final_response_structure for new session")
    try:
        response = agent.agent(prompt="Test", ask_questions=False)
        print("This should have failed!")
    except ValueError as e:
        print(f"Expected error: {e}")
    
    # Error case 3: Unknown agent_id without prompt
    print("\n❌ Error case 3: Unknown agent_id without prompt")
    try:
        response = agent.agent(agent_id="unknown-id", ask_questions=False)
        print("This should have failed!")
    except ValueError as e:
        print(f"Expected error: {e}")
    
    print("\n✅ All error cases handled correctly!")


if __name__ == "__main__":
    try:
        demonstrate_optional_prompt()
        demonstrate_error_cases()
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
