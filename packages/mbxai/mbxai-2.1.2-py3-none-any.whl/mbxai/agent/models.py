"""
Pydantic models for the agent client.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
import re


class Question(BaseModel):
    """A question for the user to provide more information."""
    question: str = Field(description="The question to ask the user")
    key: str = Field(description="A unique and short technical key identifier using only alphanumeric characters and underscores (e.g., user_name, email_address, age)")
    required: bool = Field(default=True, description="Whether this question is required")
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Ensure the key contains only alphanumeric characters and underscores."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            # Convert invalid key to valid format
            # Remove special characters and replace spaces with underscores
            cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', v)
            # Ensure it starts with a letter
            if not cleaned or not cleaned[0].isalpha():
                cleaned = 'key_' + cleaned
            # Remove consecutive underscores
            cleaned = re.sub(r'_+', '_', cleaned)
            # Remove trailing underscores
            cleaned = cleaned.rstrip('_')
            # Ensure it's not empty
            if not cleaned:
                cleaned = 'key'
            return cleaned
        return v


class Result(BaseModel):
    """A simple result wrapper containing just text."""
    result: str = Field(description="The result text from the AI")


class AgentResponse(BaseModel):
    """Response from the agent that can contain questions or a final result."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this agent session")
    questions: list[Question] = Field(default_factory=list, description="List of questions for the user")
    final_response: Optional[Any] = Field(default=None, description="The final response if processing is complete")
    token_summary: Optional["TokenSummary"] = Field(default=None, description="Summary of token usage for this agent process")
    
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


class TokenUsage(BaseModel):
    """Token usage information for a single API call."""
    prompt_tokens: int = Field(default=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(default=0, description="Number of tokens in the completion")
    total_tokens: int = Field(default=0, description="Total number of tokens used")


class TokenSummary(BaseModel):
    """Summary of token usage across all API calls in an agent process."""
    question_generation: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for question generation")
    thinking_process: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for thinking/processing")
    quality_checks: list[TokenUsage] = Field(default_factory=list, description="Tokens used for each quality check iteration")
    improvements: list[TokenUsage] = Field(default_factory=list, description="Tokens used for each improvement iteration")
    final_response: TokenUsage = Field(default_factory=TokenUsage, description="Tokens used for final response generation")
    
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens used across all operations."""
        total = (
            self.question_generation.total_tokens +
            self.thinking_process.total_tokens +
            sum(usage.total_tokens for usage in self.quality_checks) +
            sum(usage.total_tokens for usage in self.improvements) +
            self.final_response.total_tokens
        )
        return total
    
    @property
    def total_prompt_tokens(self) -> int:
        """Calculate total prompt tokens used across all operations."""
        total = (
            self.question_generation.prompt_tokens +
            self.thinking_process.prompt_tokens +
            sum(usage.prompt_tokens for usage in self.quality_checks) +
            sum(usage.prompt_tokens for usage in self.improvements) +
            self.final_response.prompt_tokens
        )
        return total
    
    @property
    def total_completion_tokens(self) -> int:
        """Calculate total completion tokens used across all operations."""
        total = (
            self.question_generation.completion_tokens +
            self.thinking_process.completion_tokens +
            sum(usage.completion_tokens for usage in self.quality_checks) +
            sum(usage.completion_tokens for usage in self.improvements) +
            self.final_response.completion_tokens
        )
        return total
