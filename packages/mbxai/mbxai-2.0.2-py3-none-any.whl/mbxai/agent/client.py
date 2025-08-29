"""
Agent client implementation for MBX AI.
"""

from typing import Any, Union, Type, Callable
import logging
import json
from pydantic import BaseModel

from ..openrouter import OpenRouterClient
from ..tools import ToolClient
from ..mcp import MCPClient
from .models import AgentResponse, Question, QuestionList, AnswerList, Result, QualityCheck

logger = logging.getLogger(__name__)


class AgentClient:
    """
    Agent client that wraps other AI clients with a dialog-based thinking process.
    
    The agent follows a multi-step process:
    1. Analyze the prompt and generate clarifying questions (if ask_questions=True)
    2. Wait for user answers or auto-answer questions
    3. Process the prompt with available information
    4. Quality check the result and iterate if needed
    5. Generate final response in the requested format
    
    Requirements:
    - The wrapped AI client MUST have a 'parse' method for structured responses
    - All AI interactions use structured Pydantic models for reliable parsing
    - Supports OpenRouterClient, ToolClient, and MCPClient (all have parse methods)
    
    Tool Registration:
    - Provides proxy methods for tool registration when supported by the underlying client
    - register_tool(): Available with ToolClient and MCPClient
    - register_mcp_server(): Available with MCPClient only
    - Throws AttributeError for unsupported clients (e.g., OpenRouterClient)
    
    Configuration:
    - max_iterations: Controls how many times the agent will iterate to improve results (default: 2)
    - Set to 0 to disable quality improvement iterations
    """

    def __init__(
        self, 
        ai_client: Union[OpenRouterClient, ToolClient, MCPClient],
        max_iterations: int = 2
    ) -> None:
        """
        Initialize the AgentClient.

        Args:
            ai_client: The underlying AI client (OpenRouterClient, ToolClient, or MCPClient)
            max_iterations: Maximum number of quality improvement iterations (default: 2)
            
        Raises:
            ValueError: If the client doesn't support structured responses (no parse method)
        """
        if not hasattr(ai_client, 'parse'):
            raise ValueError(
                f"AgentClient requires a client with structured response support (parse method). "
                f"The provided client {type(ai_client).__name__} does not have a parse method."
            )
        
        if max_iterations < 0:
            raise ValueError("max_iterations must be non-negative")
        
        self._ai_client = ai_client
        self._max_iterations = max_iterations
        self._agent_sessions: dict[str, dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable[..., Any],
        schema: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a new tool with the underlying AI client.
        
        This method proxies to the register_tool method of ToolClient or MCPClient.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            function: The function to call when the tool is used
            schema: The JSON schema for the tool's parameters. If None or empty,
                   will be automatically generated from the function signature.
            
        Raises:
            AttributeError: If the underlying client doesn't support tool registration (e.g., OpenRouterClient)
        """
        if hasattr(self._ai_client, 'register_tool'):
            self._ai_client.register_tool(name, description, function, schema)
            logger.debug(f"Registered tool '{name}' with {type(self._ai_client).__name__}")
        else:
            raise AttributeError(
                f"Tool registration is not supported by {type(self._ai_client).__name__}. "
                f"Use ToolClient or MCPClient to register tools."
            )

    def register_mcp_server(self, name: str, base_url: str) -> None:
        """
        Register an MCP server and load its tools.
        
        This method proxies to the register_mcp_server method of MCPClient.
        
        Args:
            name: The name of the MCP server
            base_url: The base URL of the MCP server
            
        Raises:
            AttributeError: If the underlying client doesn't support MCP server registration (e.g., OpenRouterClient, ToolClient)
        """
        if hasattr(self._ai_client, 'register_mcp_server'):
            self._ai_client.register_mcp_server(name, base_url)
            logger.debug(f"Registered MCP server '{name}' at {base_url} with {type(self._ai_client).__name__}")
        else:
            raise AttributeError(
                f"MCP server registration is not supported by {type(self._ai_client).__name__}. "
                f"Use MCPClient to register MCP servers."
            )

    def _call_ai_parse(self, messages: list[dict[str, Any]], response_format: Type[BaseModel]) -> Any:
        """Call the parse method on the AI client."""
        return self._ai_client.parse(messages, response_format)

    def _extract_parsed_content(self, response: Any, response_format: Type[BaseModel]) -> BaseModel:
        """Extract the parsed content from the AI response."""
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice.message, 'parsed') and choice.message.parsed:
                return choice.message.parsed
            elif hasattr(choice.message, 'content'):
                # Try to parse the content as JSON
                try:
                    content_dict = json.loads(choice.message.content)
                    return response_format(**content_dict)
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, create a default response
                    if response_format == QuestionList:
                        return QuestionList(questions=[])
                    elif response_format == Result:
                        return Result(result=choice.message.content)
                    elif response_format == QualityCheck:
                        return QualityCheck(is_good=True, feedback="")
                    else:
                        # For other formats, try to create with content
                        return response_format(result=choice.message.content)
        
        # Fallback - create empty/default response
        if response_format == QuestionList:
            return QuestionList(questions=[])
        elif response_format == Result:
            return Result(result="No response generated")
        elif response_format == QualityCheck:
            return QualityCheck(is_good=True, feedback="")
        else:
            return response_format()

    def agent(
        self,
        prompt: str,
        final_response_structure: Type[BaseModel],
        ask_questions: bool = True
    ) -> AgentResponse:
        """
        Process a prompt through the agent's thinking process.

        Args:
            prompt: The initial prompt from the user
            final_response_structure: Pydantic model defining the expected final response format
            ask_questions: Whether to ask clarifying questions (default: True)

        Returns:
            AgentResponse containing either questions to ask or the final response
        """
        logger.debug(f"Starting agent process with prompt: {prompt[:100]}...")
        
        # Step 1: Generate questions (if ask_questions is True)
        if ask_questions:
            questions_prompt = f"""
Understand this prompt and what the user wants to achieve by it: 
==========
{prompt}
==========

Think about useful steps and which information are required for it. First ask for required information and details to improve that process, when that is useful for the given case. When it's not useful, return an empty list of questions.
Use available tools to gather information or perform actions that would improve your response.
Analyze the prompt carefully and determine if additional information would significantly improve the quality of the response. Only ask questions that are truly necessary and would materially impact the outcome.
"""
            
            messages = [{"role": "user", "content": questions_prompt}]
            
            try:
                response = self._call_ai_parse(messages, QuestionList)
                question_list = self._extract_parsed_content(response, QuestionList)
                
                logger.debug(f"Generated {len(question_list.questions)} questions")
                
                # If we have questions, return them to the user
                if question_list.questions:
                    agent_response = AgentResponse(questions=question_list.questions)
                    # Store the session for continuation
                    self._agent_sessions[agent_response.agent_id] = {
                        "original_prompt": prompt,
                        "final_response_structure": final_response_structure,
                        "questions": question_list.questions,
                        "step": "waiting_for_answers"
                    }
                    return agent_response
                    
            except Exception as e:
                logger.warning(f"Failed to generate questions: {e}. Proceeding without questions.")
        
        # Step 2 & 3: No questions or ask_questions=False - proceed directly
        return self._process_with_answers(prompt, final_response_structure, [])

    def answer_to_agent(self, agent_id: str, answers: AnswerList) -> AgentResponse:
        """
        Continue an agent session by providing answers to questions.

        Args:
            agent_id: The agent session identifier
            answers: List of answers to the questions

        Returns:
            AgentResponse with the final result

        Raises:
            ValueError: If the agent session is not found or in wrong state
        """
        if agent_id not in self._agent_sessions:
            raise ValueError(f"Agent session {agent_id} not found")
        
        session = self._agent_sessions[agent_id]
        if session["step"] != "waiting_for_answers":
            raise ValueError(f"Agent session {agent_id} is not waiting for answers")
        
        # Convert answers to a more usable format
        answer_dict = {answer.key: answer.answer for answer in answers.answers}
        
        # Process with the provided answers
        result = self._process_with_answers(
            session["original_prompt"],
            session["final_response_structure"],
            answer_dict
        )
        
        # Clean up the session
        del self._agent_sessions[agent_id]
        
        return result

    def _process_with_answers(
        self,
        prompt: str,
        final_response_structure: Type[BaseModel],
        answers: Union[list, dict[str, str]]
    ) -> AgentResponse:
        """
        Process the prompt with answers through the thinking pipeline.

        Args:
            prompt: The original prompt
            final_response_structure: Expected final response structure
            answers: Answers to questions (empty if no questions were asked)

        Returns:
            AgentResponse with the final result
        """
        # Step 3: Process the prompt with thinking
        result = self._think_and_process(prompt, answers)
        
        # Step 4: Quality check and iteration
        final_result = self._quality_check_and_iterate(prompt, result, answers)
        
        # Step 5: Generate final answer in requested format
        final_response = self._generate_final_response(prompt, final_result, final_response_structure)
        
        return AgentResponse(final_response=final_response)

    def _think_and_process(self, prompt: str, answers: Union[list, dict[str, str]]) -> str:
        """
        Process the prompt with thinking.

        Args:
            prompt: The original prompt
            answers: Answers to questions

        Returns:
            The AI's result
        """
        # Format answers for the prompt
        answers_text = ""
        if isinstance(answers, dict) and answers:
            answers_text = "\n\nAdditional information provided:\n"
            for key, answer in answers.items():
                answers_text += f"- {key}: {answer}\n"
        elif isinstance(answers, list) and answers:
            answers_text = f"\n\nAdditional information: {', '.join(answers)}\n"
        
        thinking_prompt = f"""
Think about this prompt, the goal and the steps required to fulfill it: 
==========
{prompt}
==========
{answers_text}

Consider the prompt carefully, analyze what the user wants to achieve, and think through the best approach to provide a comprehensive and helpful response. Use any available tools to gather information or perform actions that would improve your response.

Provide your best result for the given prompt.
"""
        
        messages = [{"role": "user", "content": thinking_prompt}]
        
        try:
            response = self._call_ai_parse(messages, Result)
            result_obj = self._extract_parsed_content(response, Result)
            return result_obj.result
        except Exception as e:
            logger.error(f"Error in thinking process: {e}")
            raise RuntimeError(f"Failed to process prompt with AI client: {e}") from e

    def _quality_check_and_iterate(self, prompt: str, result: str, answers: Union[list, dict[str, str]]) -> str:
        """
        Check the quality of the result and iterate if needed.

        Args:
            prompt: The original prompt
            result: The current result
            answers: The answers provided

        Returns:
            The final improved result
        """
        current_result = result
        
        for iteration in range(self._max_iterations):
            quality_prompt = f"""
Given this original prompt:
==========
{prompt}
==========

And this result:
==========
{current_result}
==========

Is this result good and comprehensive, or does it need to be improved? Consider if the response fully addresses the prompt, provides sufficient detail, and would be helpful to the user.

Evaluate the quality and provide feedback if improvements are needed.
"""
            
            messages = [{"role": "user", "content": quality_prompt}]
            
            try:
                response = self._call_ai_parse(messages, QualityCheck)
                quality_check = self._extract_parsed_content(response, QualityCheck)
                
                if quality_check.is_good:
                    logger.debug(f"Quality check passed on iteration {iteration}")
                    break
                    
                logger.debug(f"Quality check failed on iteration {iteration}: {quality_check.feedback}")
                
                # Improve the result
                improvement_prompt = f"""
The original prompt was:
==========
{prompt}
==========

The current result is:
==========
{current_result}
==========

Feedback for improvement:
==========
{quality_check.feedback}
==========

Please provide an improved version that addresses the feedback while maintaining the strengths of the current result.
"""
                
                messages = [{"role": "user", "content": improvement_prompt}]
                response = self._call_ai_parse(messages, Result)
                result_obj = self._extract_parsed_content(response, Result)
                current_result = result_obj.result
                
            except Exception as e:
                logger.warning(f"Error in quality check iteration {iteration}: {e}")
                break
        
        return current_result

    def _generate_final_response(self, prompt: str, result: str, final_response_structure: Type[BaseModel]) -> BaseModel:
        """
        Generate the final response in the requested format.

        Args:
            prompt: The original prompt
            result: The processed result
            final_response_structure: The expected response structure

        Returns:
            The final response in the requested format
        """
        final_prompt = f"""
Given this original prompt:
==========
{prompt}
==========

And this processed result:
==========
{result}
==========

Generate the final answer in the exact format requested. Make sure the response is well-structured and addresses all aspects of the original prompt.
"""
        
        messages = [{"role": "user", "content": final_prompt}]
        
        try:
            response = self._call_ai_parse(messages, final_response_structure)
            return self._extract_parsed_content(response, final_response_structure)
        except Exception as e:
            logger.error(f"Error generating final response: {e}")
            # Fallback - try to create a basic response
            try:
                # If the structure has a 'result' field, use that
                if hasattr(final_response_structure, 'model_fields') and 'result' in final_response_structure.model_fields:
                    return final_response_structure(result=result)
                else:
                    # Try to create with the first field
                    fields = final_response_structure.model_fields
                    if fields:
                        first_field = next(iter(fields.keys()))
                        return final_response_structure(**{first_field: result})
                    else:
                        return final_response_structure()
            except Exception as fallback_error:
                logger.error(f"Fallback response creation failed: {fallback_error}")
                # Last resort - return the structure with default values
                return final_response_structure()
