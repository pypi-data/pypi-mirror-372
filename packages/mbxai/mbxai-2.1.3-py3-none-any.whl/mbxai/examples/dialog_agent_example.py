"""
Example usage of the AgentClient with persistent dialog sessions.
"""

import os
from pydantic import BaseModel, Field
from mbxai import AgentClient, OpenRouterClient, AnswerList, Answer


class ChatResponse(BaseModel):
    """A general chat response."""
    response: str = Field(description="The response to the user's message")
    context_awareness: str = Field(description="How this response relates to previous conversation")


class BookRecommendation(BaseModel):
    """A book recommendation response."""
    title: str = Field(description="The title of the recommended book")
    author: str = Field(description="The author of the book")
    genre: str = Field(description="The genre of the book")
    reason: str = Field(description="Why this book is recommended based on conversation")
    connection_to_previous: str = Field(description="How this recommendation connects to our previous conversation")


def demonstrate_dialog_conversation():
    """Demonstrate persistent dialog functionality."""
    print("🔄 DEMO: Persistent Dialog Agent")
    print("=" * 50)
    
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # First conversation - start new session
    print("\n1️⃣ Starting new conversation:")
    prompt1 = "Hi, I'm looking for a good book to read. I love science fiction."
    response1 = agent.agent(prompt1, ChatResponse, ask_questions=False)
    
    if response1.is_complete():
        agent_id = response1.agent_id
        chat_resp = response1.final_response
        print(f"Agent ID: {agent_id}")
        print(f"Response: {chat_resp.response}")
        print(f"Context awareness: {chat_resp.context_awareness}")
        
        # Second conversation - continue same session
        print(f"\n2️⃣ Continuing conversation with agent {agent_id}:")
        prompt2 = "Actually, I also enjoy fantasy novels. What would you recommend that combines both genres?"
        response2 = agent.agent(prompt2, BookRecommendation, ask_questions=False, agent_id=agent_id)
        
        if response2.is_complete():
            book_rec = response2.final_response
            print(f"Book: {book_rec.title} by {book_rec.author}")
            print(f"Genre: {book_rec.genre}")
            print(f"Reason: {book_rec.reason}")
            print(f"Connection to previous: {book_rec.connection_to_previous}")
            
            # Third conversation - continue same session
            print(f"\n3️⃣ Continuing conversation with agent {agent_id}:")
            prompt3 = "That sounds great! Can you recommend something similar but from a different author?"
            response3 = agent.agent(prompt3, BookRecommendation, ask_questions=False, agent_id=agent_id)
            
            if response3.is_complete():
                book_rec2 = response3.final_response
                print(f"Book: {book_rec2.title} by {book_rec2.author}")
                print(f"Genre: {book_rec2.genre}")
                print(f"Reason: {book_rec2.reason}")
                print(f"Connection to previous: {book_rec2.connection_to_previous}")
        
        # Show session info
        print(f"\n📊 Session Information:")
        try:
            session_info = agent.get_session_info(agent_id)
            print(f"Conversation length: {session_info['conversation_length']} messages")
            print(f"Session step: {session_info.get('step', 'unknown')}")
        except Exception as e:
            print(f"Error getting session info: {e}")
        
        # List all sessions
        print(f"\n📝 Active sessions: {agent.list_sessions()}")
        
        # Cleanup - optional
        print(f"\n🗑️ Cleaning up session...")
        deleted = agent.delete_session(agent_id)
        print(f"Session deleted: {deleted}")
        print(f"Active sessions after cleanup: {agent.list_sessions()}")


def demonstrate_dialog_with_questions():
    """Demonstrate dialog with question-answer flow."""
    print("\n🔄 DEMO: Dialog Agent with Questions")
    print("=" * 50)
    
    # Initialize the clients
    openrouter_client = OpenRouterClient(token=os.getenv("OPENROUTER_API_KEY", "your-token-here"))
    agent = AgentClient(openrouter_client, max_iterations=1)
    
    # First conversation with questions
    print("\n1️⃣ Starting conversation with questions:")
    prompt1 = "I want a personalized book recommendation"
    response1 = agent.agent(prompt1, BookRecommendation, ask_questions=True)
    
    agent_id = response1.agent_id
    print(f"Agent ID: {agent_id}")
    
    if response1.has_questions():
        print(f"\n📋 Agent generated {len(response1.questions)} questions:")
        for i, question in enumerate(response1.questions, 1):
            print(f"  {i}. {question.question} (key: {question.key})")
        
        # Simulate answering questions
        answers = AnswerList(answers=[
            Answer(key="genre_preference", answer="I love science fiction and fantasy"),
            Answer(key="reading_level", answer="I prefer complex, adult novels"),
            Answer(key="recent_books", answer="I recently read and loved Dune and The Name of the Wind")
        ])
        
        print(f"\n📝 Providing answers...")
        final_response = agent.agent("Continue with answers", BookRecommendation, ask_questions=False, agent_id=agent_id, answers=answers)
        
        if final_response.is_complete():
            book_rec = final_response.final_response
            print(f"Book: {book_rec.title} by {book_rec.author}")
            print(f"Genre: {book_rec.genre}")
            print(f"Reason: {book_rec.reason}")
            
            # Continue conversation - this should remember the previous interaction
            print(f"\n2️⃣ Continuing conversation with agent {agent_id}:")
            prompt2 = "Thank you! Can you also recommend something by a female author in the same genres?"
            response2 = agent.agent(prompt2, BookRecommendation, ask_questions=False, agent_id=agent_id)
            
            if response2.is_complete():
                book_rec2 = response2.final_response
                print(f"Book: {book_rec2.title} by {book_rec2.author}")
                print(f"Genre: {book_rec2.genre}")
                print(f"Reason: {book_rec2.reason}")
                print(f"Connection to previous: {book_rec2.connection_to_previous}")
            
            # Continue WITHOUT explicit prompt - using only conversation history
            print(f"\n3️⃣ Continuing conversation WITHOUT explicit prompt (history-based):")
            try:
                response3 = agent.agent(agent_id=agent_id, ask_questions=False)  # No prompt provided
                
                if response3.is_complete():
                    book_rec3 = response3.final_response
                    print(f"History-based recommendation:")
                    print(f"Book: {book_rec3.title} by {book_rec3.author}")
                    print(f"Genre: {book_rec3.genre}")
                    print(f"Reason: {book_rec3.reason}")
                    print(f"Connection to previous: {book_rec3.connection_to_previous}")
            except Exception as e:
                print(f"Error with history-based continuation: {e}")
        
        # Session cleanup
        print(f"\n🗑️ Session cleanup...")
        agent.delete_session(agent_id)


if __name__ == "__main__":
    print("=== Dialog Agent Examples ===\n")
    
    try:
        demonstrate_dialog_conversation()
    except Exception as e:
        print(f"Error in dialog conversation demo: {e}")
    
    print("\n" + "="*80 + "\n")
    
    try:
        demonstrate_dialog_with_questions()
    except Exception as e:
        print(f"Error in dialog with questions demo: {e}")
