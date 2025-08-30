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
from .models import AgentResponse, Question, QuestionList, AnswerList, Result, QualityCheck, TokenUsage, TokenSummary

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

    def _call_ai_parse(self, messages: list[dict[str, Any]], response_format: Type[BaseModel], conversation_history: list[dict[str, Any]] = None) -> Any:
        """Call the parse method on the AI client with optional conversation history."""
        # Combine conversation history with new messages
        if conversation_history:
            full_messages = conversation_history + messages
            logger.debug(f"🔗 AI call with {len(conversation_history)} history messages + {len(messages)} new messages = {len(full_messages)} total")
        else:
            full_messages = messages
            logger.debug(f"🔗 AI call with {len(messages)} messages (no history)")
        return self._ai_client.parse(full_messages, response_format)

    def _validate_answers(self, answers: Any) -> bool:
        """
        Validate that answers parameter is a proper AnswerList with content.
        
        Args:
            answers: The answers parameter to validate
            
        Returns:
            True if answers is valid and has content, False otherwise
        """
        # Check if answers is the correct type
        if not isinstance(answers, AnswerList):
            logger.warning(f"Invalid answers type: {type(answers)}. Expected AnswerList, treating as no answers.")
            return False
        
        # Check if answers has content
        if not hasattr(answers, 'answers') or not answers.answers:
            logger.info(f"Empty answers list provided, proceeding without answers processing.")
            return False
        
        # Check if answers list contains valid Answer objects
        for answer in answers.answers:
            if not hasattr(answer, 'key') or not hasattr(answer, 'answer'):
                logger.warning(f"Invalid answer object in list: {answer}. Treating as no answers.")
                return False
        
        logger.debug(f"Validated {len(answers.answers)} answers")
        return True

    def _extract_token_usage(self, response: Any) -> TokenUsage:
        """Extract token usage information from an AI response."""
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                return TokenUsage(
                    prompt_tokens=getattr(usage, 'prompt_tokens', 0),
                    completion_tokens=getattr(usage, 'completion_tokens', 0),
                    total_tokens=getattr(usage, 'total_tokens', 0)
                )
        except (AttributeError, TypeError) as e:
            logger.debug(f"Could not extract token usage: {e}")
        
        return TokenUsage()  # Return empty usage if extraction fails

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
        prompt: str = None,
        final_response_structure: Type[BaseModel] = None,
        ask_questions: bool = True,
        agent_id: str = None,
        answers: AnswerList | None = None
    ) -> AgentResponse:
        """
        Process a prompt through the agent's thinking process.

        Args:
            prompt: The prompt from the user (optional if agent_id exists with history)
            final_response_structure: Pydantic model defining the expected final response format (required for new sessions)
            ask_questions: Whether to ask clarifying questions (default: True)
            agent_id: Optional agent session ID to continue an existing conversation
            answers: Optional answers to questions (when continuing a conversation with questions)

        Returns:
            AgentResponse containing either questions to ask or the final response
            
        Raises:
            ValueError: If neither prompt nor agent_id with history is provided, or if final_response_structure is missing for new sessions
        """
        # Validate inputs and determine session type
        is_existing_session = agent_id is not None and agent_id in self._agent_sessions
        existing_session = self._agent_sessions.get(agent_id, {}) if agent_id else {}
        conversation_history = existing_session.get("conversation_history", []).copy()
        
        # Validation logic
        if not is_existing_session:
            # New session - both prompt and final_response_structure are required
            if not prompt:
                raise ValueError("Prompt is required when starting a new agent session")
            if not final_response_structure:
                raise ValueError("final_response_structure is required when starting a new agent session")
            
            # Create new agent_id if not provided
            if agent_id is None:
                agent_id = str(__import__("uuid").uuid4())
            logger.info(f"🚀 Starting new agent process (ID: {agent_id}) with prompt: {prompt[:100]}...")
        else:
            # Existing session - use previous final_response_structure if not provided
            if not final_response_structure:
                final_response_structure = existing_session.get("final_response_structure")
                if not final_response_structure:
                    raise ValueError("final_response_structure not found in existing session and not provided")
            
            # Handle optional prompt for existing sessions
            if not prompt:
                # Use conversation history to continue without explicit prompt
                prompt = "[Continue conversation based on history]"
                logger.info(f"🔄 Continuing agent process (ID: {agent_id}) without explicit prompt (using history)")
            else:
                logger.info(f"🔄 Continuing agent process (ID: {agent_id}) with prompt: {prompt[:100]}...")
        
        # Initialize token summary
        token_summary = TokenSummary()
        
        if conversation_history:
            logger.info(f"📜 Agent {agent_id}: Loaded conversation history with {len(conversation_history)} messages")
        
        # Store conversation history for AI calls (don't include current prompt yet)
        history_for_ai = conversation_history.copy()
        
        # Add current prompt to full conversation history for session storage
        conversation_history.append({"role": "user", "content": prompt})
        
        # Handle answers provided (skip question generation and process directly)
        if answers is not None:
            if self._validate_answers(answers):
                logger.info(f"📝 Agent {agent_id}: Processing with provided answers, skipping question generation")
                return self._process_answers_directly(agent_id, prompt, final_response_structure, answers, token_summary, history_for_ai)
            else:
                logger.info(f"📝 Agent {agent_id}: Invalid or empty answers provided, proceeding with normal flow")
        
        # Step 1: Generate questions (if ask_questions is True)
        if ask_questions:
            logger.info(f"❓ Agent {agent_id}: Analyzing prompt and generating clarifying questions")
            questions_prompt = f"""
Understand this prompt and what the user wants to achieve by it: 
==========
{prompt}
==========

Think about useful steps and which information are required for it. First ask for required information and details to improve that process, when that is useful for the given case. When it's not useful, return an empty list of questions.
Use available tools to gather information or perform actions that would improve your response.
Analyze the prompt carefully and determine if additional information would significantly improve the quality of the response. Only ask questions that are truly necessary and would materially impact the outcome.

IMPORTANT: For each question, provide a technical key identifier that:
- Uses only alphanumeric characters and underscores
- Starts with a letter
- Is descriptive but concise (e.g., "user_name", "email_address", "preferred_genre", "budget_range")
- Contains no spaces, hyphens, or special characters like ?, !, @, etc.
"""
            
            messages = [{"role": "user", "content": questions_prompt}]
            
            try:
                response = self._call_ai_parse(messages, QuestionList, history_for_ai)
                question_list = self._extract_parsed_content(response, QuestionList)
                
                # Extract token usage for question generation
                token_summary.question_generation = self._extract_token_usage(response)
                
                logger.info(f"❓ Agent {agent_id}: Generated {len(question_list.questions)} questions (tokens: {token_summary.question_generation.total_tokens})")
                
                # If we have questions, return them to the user
                if question_list.questions:
                    agent_response = AgentResponse(agent_id=agent_id, questions=question_list.questions, token_summary=token_summary)
                    # Store the session for continuation
                    self._agent_sessions[agent_response.agent_id] = {
                        "original_prompt": prompt,
                        "final_response_structure": final_response_structure,
                        "questions": question_list.questions,
                        "step": "waiting_for_answers",
                        "token_summary": token_summary,
                        "conversation_history": history_for_ai  # Include history without current prompt
                    }
                    logger.info(f"📋 Agent {agent_id}: Waiting for user answers to {len(question_list.questions)} questions")
                    return agent_response
                    
            except Exception as e:
                logger.warning(f"Failed to generate questions: {e}. Proceeding without questions.")
        
        # Step 2 & 3: No questions or ask_questions=False - proceed directly
        logger.info(f"⚡ Agent {agent_id}: No questions needed, proceeding directly to processing")
        return self._process_with_answers(prompt, final_response_structure, [], agent_id, token_summary, history_for_ai)

    def _process_answers_directly(
        self,
        agent_id: str,
        prompt: str,
        final_response_structure: Type[BaseModel],
        answers: AnswerList,
        token_summary: TokenSummary,
        conversation_history: list[dict[str, Any]]
    ) -> AgentResponse:
        """
        Process answers directly without going through question generation.
        
        Args:
            agent_id: The agent session identifier
            prompt: The current prompt
            final_response_structure: Expected response structure
            answers: Provided answers
            token_summary: Current token usage summary
            conversation_history: Conversation history
            
        Returns:
            AgentResponse with the final result
        """
        # Check if we have a session with questions to match against
        session = self._agent_sessions.get(agent_id, {})
        questions = session.get("questions", [])
        
        if not questions:
            # No previous questions - treat as simple additional context
            logger.info(f"📝 Agent {agent_id}: No previous questions found, treating answers as additional context")
            answer_dict = {answer.key: answer.answer for answer in answers.answers}
            qa_pairs = []
            for answer in answers.answers:
                qa_pairs.append({
                    "question": f"Information about {answer.key}",
                    "key": answer.key,
                    "answer": answer.answer,
                    "required": True
                })
        else:
            # Match answers with previous questions
            logger.info(f"📝 Agent {agent_id}: Matching {len(answers.answers)} answers with previous questions")
            answer_dict = {answer.key: answer.answer for answer in answers.answers}
            
            # Create question-answer pairs for better context
            qa_pairs = []
            for question in questions:
                answer_text = answer_dict.get(question.key, "No answer provided")
                qa_pairs.append({
                    "question": question.question,
                    "key": question.key,
                    "answer": answer_text,
                    "required": question.required
                })
        
        # Process with the provided answers and question context
        result = self._process_with_answers(
            prompt,
            final_response_structure,
            qa_pairs,
            agent_id,
            token_summary,
            conversation_history
        )
        
        # Note: History management is now handled in _process_with_answers
        # No need to duplicate history management here
        return result

    def _format_qa_context_for_quality_check(self, answers: Union[list, dict[str, str]]) -> str:
        """
        Format question-answer context for quality check and improvement prompts.
        
        Args:
            answers: Question-answer pairs or simple answers
            
        Returns:
            Formatted context text
        """
        if not answers:
            return ""
            
        if isinstance(answers, list) and answers:
            # Check if it's a list of question-answer pairs (enhanced format)
            if isinstance(answers[0], dict) and "question" in answers[0]:
                context_text = "\nContext Information (Questions & Answers):\n"
                context_text += "The response was generated with the following additional context:\n\n"
                for i, qa_pair in enumerate(answers, 1):
                    question = qa_pair.get("question", "Unknown question")
                    answer = qa_pair.get("answer", "No answer provided")
                    required = qa_pair.get("required", True)
                    
                    status_marker = "🔴 REQUIRED" if required else "🟡 OPTIONAL"
                    context_text += f"{i}. {status_marker} Q: {question}\n"
                    context_text += f"   A: {answer}\n\n"
                return context_text
            else:
                # Legacy format - simple list
                return f"\nAdditional context: {', '.join(str(a) for a in answers)}\n\n"
        elif isinstance(answers, dict) and answers:
            # Legacy format - simple dict
            context_text = "\nAdditional context provided:\n"
            for key, answer in answers.items():
                context_text += f"- {key}: {answer}\n"
            return context_text + "\n"
        
        return ""

    def _process_with_answers(
        self,
        prompt: str,
        final_response_structure: Type[BaseModel],
        answers: Union[list, dict[str, str]],
        agent_id: str,
        token_summary: TokenSummary,
        conversation_history: list[dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process the prompt with answers through the thinking pipeline.

        Args:
            prompt: The original prompt
            final_response_structure: Expected final response structure
            answers: Question-answer pairs or simple answers (empty if no questions were asked)
            agent_id: The agent session identifier
            token_summary: Current token usage summary
            conversation_history: Optional conversation history for dialog context

        Returns:
            AgentResponse with the final result
        """
        if conversation_history is None:
            conversation_history = []
            
        # Step 3: Process the prompt with thinking
        logger.info(f"🧠 Agent {agent_id}: Processing prompt and generating initial response")
        result = self._think_and_process(prompt, answers, agent_id, token_summary, conversation_history)
        
        # Step 4: Quality check and iteration
        final_result = self._quality_check_and_iterate(prompt, result, answers, agent_id, token_summary, conversation_history)
        
        # Step 5: Generate final answer in requested format
        logger.info(f"📝 Agent {agent_id}: Generating final structured response")
        final_response = self._generate_final_response(prompt, final_result, final_response_structure, agent_id, token_summary, conversation_history)
        
        # Update session with the final response in conversation history
        if agent_id in self._agent_sessions:
            # Update conversation history with assistant response
            updated_history = conversation_history.copy()
            updated_history.append({"role": "assistant", "content": str(final_response)})
            
            self._agent_sessions[agent_id]["conversation_history"] = updated_history
            self._agent_sessions[agent_id]["step"] = "completed"
            self._agent_sessions[agent_id]["token_summary"] = token_summary
            self._agent_sessions[agent_id]["final_response_structure"] = final_response_structure
            logger.info(f"💾 Agent {agent_id}: Updated session with conversation history ({len(updated_history)} messages)")
        else:
            # Create new session if it doesn't exist
            updated_history = conversation_history.copy()
            updated_history.append({"role": "assistant", "content": str(final_response)})
            
            self._agent_sessions[agent_id] = {
                "step": "completed",
                "conversation_history": updated_history,
                "token_summary": token_summary,
                "final_response_structure": final_response_structure
            }
            logger.info(f"💾 Agent {agent_id}: Created new session with conversation history ({len(updated_history)} messages)")
        
        # Log final token summary
        logger.info(f"📊 Agent {agent_id}: Token usage summary - Total: {token_summary.total_tokens} "
                   f"(Prompt: {token_summary.total_prompt_tokens}, Completion: {token_summary.total_completion_tokens})")
        
        return AgentResponse(agent_id=agent_id, final_response=final_response, token_summary=token_summary)

    def _think_and_process(self, prompt: str, answers: Union[list, dict[str, str]], agent_id: str, token_summary: TokenSummary, conversation_history: list[dict[str, Any]] = None) -> str:
        """
        Process the prompt with thinking.

        Args:
            prompt: The original prompt
            answers: Question-answer pairs or simple answers
            agent_id: The agent session identifier
            token_summary: Current token usage summary
            conversation_history: Optional conversation history for dialog context

        Returns:
            The AI's result
        """
        if conversation_history is None:
            conversation_history = []
        # Format answers for the prompt with enhanced context
        answers_text = ""
        if isinstance(answers, list) and answers:
            # Check if it's a list of question-answer pairs (enhanced format)
            if answers and isinstance(answers[0], dict) and "question" in answers[0]:
                answers_text = "\n\nQuestion-Answer Context:\n"
                answers_text += "The following questions were asked to gather more information, along with the answers provided:\n\n"
                for i, qa_pair in enumerate(answers, 1):
                    question = qa_pair.get("question", "Unknown question")
                    answer = qa_pair.get("answer", "No answer provided")
                    key = qa_pair.get("key", "")
                    required = qa_pair.get("required", True)
                    
                    status_marker = "🔴 REQUIRED" if required else "🟡 OPTIONAL"
                    answers_text += f"{i}. {status_marker} Question: {question}\n"
                    answers_text += f"   Answer: {answer}\n"
                    if key:
                        answers_text += f"   (Key: {key})\n"
                    answers_text += "\n"
            else:
                # Legacy format - simple list
                answers_text = f"\n\nAdditional information: {', '.join(str(a) for a in answers)}\n"
        elif isinstance(answers, dict) and answers:
            # Legacy format - simple dict
            answers_text = "\n\nAdditional information provided:\n"
            for key, answer in answers.items():
                answers_text += f"- {key}: {answer}\n"
        
        thinking_prompt = f"""
Think about this prompt, the goal and the steps required to fulfill it: 
==========
{prompt}
==========
{answers_text}

Consider the prompt carefully, analyze what the user wants to achieve, and think through the best approach to provide a comprehensive and helpful response. 

IMPORTANT: When formulating your response, take into account both the original prompt AND the specific questions that were asked along with their answers. The questions reveal what additional information was deemed necessary, and the answers provide crucial context that should inform your response.

Use any available tools to gather information or perform actions that would improve your response.

Provide your best result for the given prompt, incorporating all the context from the question-answer pairs.
"""
        
        messages = [{"role": "user", "content": thinking_prompt}]
        
        try:
            response = self._call_ai_parse(messages, Result, conversation_history)
            result_obj = self._extract_parsed_content(response, Result)
            
            # Track token usage for thinking process
            token_summary.thinking_process = self._extract_token_usage(response)
            logger.info(f"🧠 Agent {agent_id}: Thinking completed (tokens: {token_summary.thinking_process.total_tokens})")
            
            return result_obj.result
        except Exception as e:
            logger.error(f"Error in thinking process: {e}")
            raise RuntimeError(f"Failed to process prompt with AI client: {e}") from e

    def _quality_check_and_iterate(self, prompt: str, result: str, answers: Union[list, dict[str, str]], agent_id: str, token_summary: TokenSummary, conversation_history: list[dict[str, Any]] = None) -> str:
        """
        Check the quality of the result and iterate if needed.

        Args:
            prompt: The original prompt
            result: The current result
            answers: Question-answer pairs or simple answers
            agent_id: The agent session identifier
            token_summary: Current token usage summary
            conversation_history: Optional conversation history for dialog context

        Returns:
            The final improved result
        """
        if conversation_history is None:
            conversation_history = []
            
        current_result = result
        
        if self._max_iterations == 0:
            logger.info(f"✅ Agent {agent_id}: Skipping quality check (max_iterations=0)")
            return current_result
        
        logger.info(f"🔍 Agent {agent_id}: Starting quality check and improvement process (max iterations: {self._max_iterations})")
        
        # Format context information for quality checks
        context_text = self._format_qa_context_for_quality_check(answers)
        
        for iteration in range(self._max_iterations):
            quality_prompt = f"""
Given this original prompt:
==========
{prompt}
==========
{context_text}
And this result:
==========
{current_result}
==========

Is this result good and comprehensive, or does it need to be improved? Consider if the response fully addresses the prompt, provides sufficient detail, and would be helpful to the user.

IMPORTANT: Also evaluate whether the result properly incorporates and addresses the information provided through the question-answer pairs above. The response should demonstrate that it has taken this additional context into account.

Evaluate the quality and provide feedback if improvements are needed.
"""
            
            messages = [{"role": "user", "content": quality_prompt}]
            
            try:
                response = self._call_ai_parse(messages, QualityCheck, conversation_history)
                quality_check = self._extract_parsed_content(response, QualityCheck)
                
                # Track token usage for quality check
                quality_check_tokens = self._extract_token_usage(response)
                token_summary.quality_checks.append(quality_check_tokens)
                
                if quality_check.is_good:
                    logger.info(f"✅ Agent {agent_id}: Quality check passed on iteration {iteration + 1} (tokens: {quality_check_tokens.total_tokens})")
                    break
                    
                logger.info(f"🔄 Agent {agent_id}: Quality check iteration {iteration + 1} - Improvements needed: {quality_check.feedback[:100]}... (tokens: {quality_check_tokens.total_tokens})")
                
                # Improve the result
                improvement_prompt = f"""
The original prompt was:
==========
{prompt}
==========
{context_text}
The current result is:
==========
{current_result}
==========

Feedback for improvement:
==========
{quality_check.feedback}
==========

Please provide an improved version that addresses the feedback while maintaining the strengths of the current result. Make sure to incorporate all the context from the question-answer pairs above.
"""
                
                messages = [{"role": "user", "content": improvement_prompt}]
                improvement_response = self._call_ai_parse(messages, Result, conversation_history)
                result_obj = self._extract_parsed_content(improvement_response, Result)
                current_result = result_obj.result
                
                # Track token usage for improvement
                improvement_tokens = self._extract_token_usage(improvement_response)
                token_summary.improvements.append(improvement_tokens)
                
                logger.info(f"⚡ Agent {agent_id}: Improvement iteration {iteration + 1} completed (tokens: {improvement_tokens.total_tokens})")
                
            except Exception as e:
                logger.warning(f"Error in quality check iteration {iteration}: {e}")
                break
        
        total_quality_tokens = sum(usage.total_tokens for usage in token_summary.quality_checks)
        total_improvement_tokens = sum(usage.total_tokens for usage in token_summary.improvements)
        logger.info(f"🏁 Agent {agent_id}: Quality check completed - {len(token_summary.quality_checks)} checks, {len(token_summary.improvements)} improvements (Quality tokens: {total_quality_tokens}, Improvement tokens: {total_improvement_tokens})")
        
        return current_result

    def _generate_final_response(self, prompt: str, result: str, final_response_structure: Type[BaseModel], agent_id: str, token_summary: TokenSummary, conversation_history: list[dict[str, Any]] = None) -> BaseModel:
        """
        Generate the final response in the requested format.

        Args:
            prompt: The original prompt
            result: The processed result
            final_response_structure: The expected response structure
            agent_id: The agent session identifier
            token_summary: Current token usage summary
            conversation_history: Optional conversation history for dialog context

        Returns:
            The final response in the requested format
        """
        if conversation_history is None:
            conversation_history = []
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
            response = self._call_ai_parse(messages, final_response_structure, conversation_history)
            final_response = self._extract_parsed_content(response, final_response_structure)
            
            # Track token usage for final response generation
            token_summary.final_response = self._extract_token_usage(response)
            logger.info(f"📝 Agent {agent_id}: Final structured response generated (tokens: {token_summary.final_response.total_tokens})")
            
            return final_response
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

    def get_session_info(self, agent_id: str) -> dict[str, Any]:
        """
        Get information about an agent session.
        
        Args:
            agent_id: The agent session identifier
            
        Returns:
            Session information dictionary
            
        Raises:
            ValueError: If the agent session is not found
        """
        if agent_id not in self._agent_sessions:
            raise ValueError(f"Agent session {agent_id} not found")
        
        session = self._agent_sessions[agent_id].copy()
        # Remove sensitive information and add summary
        session["conversation_length"] = len(session.get("conversation_history", []))
        return session

    def delete_session(self, agent_id: str) -> bool:
        """
        Delete an agent session.
        
        Args:
            agent_id: The agent session identifier
            
        Returns:
            True if session was deleted, False if it didn't exist
        """
        if agent_id in self._agent_sessions:
            del self._agent_sessions[agent_id]
            logger.info(f"🗑️ Deleted agent session {agent_id}")
            return True
        return False

    def list_sessions(self) -> list[str]:
        """
        List all active agent session IDs.
        
        Returns:
            List of agent session IDs
        """
        return list(self._agent_sessions.keys())
