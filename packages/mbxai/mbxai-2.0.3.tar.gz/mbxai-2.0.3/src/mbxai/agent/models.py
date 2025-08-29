"""
Pydantic models for the agent client.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid


class Question(BaseModel):
    """A question for the user to provide more information."""
    question: str = Field(description="The question to ask the user")
    key: str = Field(description="A unique and short technical key identifier to identify this question don't use spaces or special characters")
    required: bool = Field(default=True, description="Whether this question is required")


class Result(BaseModel):
    """A simple result wrapper containing just text."""
    result: str = Field(description="The result text from the AI")


class AgentResponse(BaseModel):
    """Response from the agent that can contain questions or a final result."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this agent session")
    questions: list[Question] = Field(default_factory=list, description="List of questions for the user")
    final_response: Optional[Any] = Field(default=None, description="The final response if processing is complete")
    
    def has_questions(self) -> bool:
        """Check if this response has questions that need to be answered."""
        return len(self.questions) > 0
    
    def is_complete(self) -> bool:
        """Check if this response contains a final result."""
        return self.final_response is not None


class QuestionList(BaseModel):
    """A list of questions to ask the user."""
    questions: list[Question] = Field(description="List of questions to ask the user")


class Answer(BaseModel):
    """An answer to a question."""
    key: str = Field(description="The key of the question being answered")
    answer: str = Field(description="The answer to the question")


class AnswerList(BaseModel):
    """A list of answers from the user."""
    answers: list[Answer] = Field(description="List of answers to questions")


class QualityCheck(BaseModel):
    """Result of quality checking the AI response."""
    is_good: bool = Field(description="Whether the result is good enough")
    feedback: str = Field(description="Feedback on what could be improved if not good")
