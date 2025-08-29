"""
OpenRouter client implementation.
"""

from typing import Any, Optional, Union, Type
from openai import OpenAI, OpenAIError, RateLimitError, APITimeoutError, APIConnectionError, BadRequestError, AuthenticationError
from openai.lib._parsing import type_to_response_format_param
from .models import OpenRouterModel, OpenRouterModelRegistry
from .config import OpenRouterConfig
from .schema import format_response
from pydantic import BaseModel
import logging
import time
import asyncio
import traceback
from functools import wraps
import json

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors."""
    pass


class OpenRouterConnectionError(OpenRouterError):
    """Raised when there is a connection error."""
    pass


class OpenRouterAPIError(OpenRouterError):
    """Raised when the API returns an error."""
    pass


def with_retry(max_retries: int = 3, initial_delay: float = 1.0, max_delay: float = 10.0):
    """Decorator to add retry logic to a function.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (OpenRouterConnectionError, OpenRouterAPIError) as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise last_error
                except Exception as e:
                    # Don't retry other types of errors
                    raise e
            
            raise last_error

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OpenRouterConnectionError, OpenRouterAPIError) as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise last_error
                except Exception as e:
                    # Don't retry other types of errors
                    raise e
            
            raise last_error

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle special types."""
    def default(self, obj):
        if hasattr(obj, '__name__'):
            return obj.__name__
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    def __init__(
        self,
        token: str,
        model: Union[str, OpenRouterModel] = OpenRouterModel.GPT35_TURBO,
        base_url: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
        max_retries: int = 3,
        retry_initial_delay: float = 1.0,
        retry_max_delay: float = 10.0,
    ) -> None:
        """Initialize the OpenRouter client.

        Args:
            token: The OpenRouter API token
            model: The model to use (default: GPT35_TURBO)
            base_url: Optional custom base URL for the API
            default_headers: Optional default headers for API requests
            max_retries: Maximum number of retry attempts (default: 3)
            retry_initial_delay: Initial delay between retries in seconds (default: 1.0)
            retry_max_delay: Maximum delay between retries in seconds (default: 10.0)

        Raises:
            OpenRouterError: If initialization fails
        """
        try:
            self.config = OpenRouterConfig(
                token=token,
                model=model,
                base_url=base_url or "https://openrouter.ai/api/v1",
                default_headers=default_headers or {
                    "HTTP-Referer": "https://github.com/mibexx/mbxai",
                    "X-Title": "MBX AI",
                },
                max_retries=max_retries,
                retry_initial_delay=retry_initial_delay,
                retry_max_delay=retry_max_delay,
            )

            self._client = OpenAI(
                api_key=token,
                base_url=self.config.base_url,
                default_headers=self.config.default_headers,
            )
        except Exception as e:
            raise OpenRouterError(f"Failed to initialize client: {str(e)}")

    def _handle_api_error(self, operation: str, error: Exception) -> None:
        """Handle API errors.

        Args:
            operation: The operation being performed
            error: The error that occurred

        Raises:
            OpenRouterConnectionError: For connection issues
            OpenRouterAPIError: For API errors
            OpenRouterError: For other errors
        """
        error_msg = str(error)
        stack_trace = traceback.format_exc()
        logger.error(f"API error during {operation}: {error_msg}")
        logger.error(f"Stack trace:\n{stack_trace}")

        if isinstance(error, OpenAIError):
            raise OpenRouterAPIError(f"API error during {operation}: {error_msg}\nStack trace:\n{stack_trace}")
        elif "Connection" in error_msg:
            raise OpenRouterConnectionError(f"Connection error during {operation}: {error_msg}\nStack trace:\n{stack_trace}")
        elif "Expecting value" in error_msg and "line" in error_msg:
            # This is a JSON parsing error, likely due to a truncated or malformed response
            logger.error("JSON parsing error detected. This might be due to a large response or network issues.")
            raise OpenRouterAPIError(f"Response parsing error during {operation}. The response might be too large or malformed.\nStack trace:\n{stack_trace}")
        else:
            raise OpenRouterError(f"Error during {operation}: {error_msg}\nStack trace:\n{stack_trace}")

    @property
    def model(self) -> str:
        """Get the current model."""
        return str(self.config.model)

    @model.setter
    def model(self, value: Union[str, OpenRouterModel]) -> None:
        """Set a new model.

        Args:
            value: The new model to use
        """
        self.config.model = value

    def set_model(self, value: Union[str, OpenRouterModel]) -> None:
        """Set a new model.

        Args:
            value: The new model to use
        """
        self.model = value

    @with_retry()
    def create(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Get a chat completion from OpenRouter."""
        try:
            # Log the request details
            logger.debug(f"Sending chat completion request to OpenRouter with model: {model or self.model}")
            logger.debug(f"Message count: {len(messages)}")

            # Calculate total message size for logging
            total_size = sum(len(str(msg)) for msg in messages)
            logger.debug(f"Total message size: {total_size} bytes")

            request = {
                "model": model or self.model,
                "messages": messages,
                "stream": stream,
                **kwargs,
            }

            response = self._client.chat.completions.create(**request)

            if response is None:
                logger.error("Received None response from OpenRouter API")
                raise OpenRouterAPIError("Received None response from OpenRouter API")

            # Validate response structure
            if not hasattr(response, 'choices'):
                logger.error(f"Response missing 'choices' attribute. Available attributes: {dir(response)}")
                raise OpenRouterAPIError("Invalid response format: missing 'choices' attribute")

            if response.choices is None:
                logger.error("Response choices is None")
                raise OpenRouterAPIError("Invalid response format: choices is None")

            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            logger.debug(f"Received response from OpenRouter: {len(response.choices)} choices")

            return response

        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Error in chat completion: {str(e)}")
            logger.error(f"Stack trace:\n{stack_trace}")
            logger.error(f"Request details: model={model or self.model}, stream={stream}, kwargs={kwargs}")
            logger.error(f"Message structure: {[{'role': msg.get('role'), 'content_length': len(str(msg.get('content', '')))} for msg in messages]}")

            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                try:
                    content = e.response.text
                    logger.error(f"Response content length: {len(content)} bytes")
                    logger.error(f"Response content preview: {content[:1000]}...")
                except:
                    logger.error("Could not read response content")
            self._handle_api_error("chat completion", e)

    @with_retry()
    def parse(
        self,
        messages: list[dict[str, Any]],
        response_format: object,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Get a chat completion from OpenRouter."""

        request = {
            "model": model or self.model,
            "messages": messages,
            "response_format": response_format,
            **kwargs,
        }

        # Log the full request for debugging
        logger.debug(f"Full request: {request}")

        try:
            # Log the request details
            logger.debug(f"Sending parse request to OpenRouter with model: {model or self.model}")
            logger.debug(f"Message count: {len(messages)}")
            logger.debug(f"Response format: {response_format}")

            # Calculate total message size for logging
            total_size = sum(len(str(msg)) for msg in messages)
            logger.debug(f"Total message size: {total_size} bytes")

            try:
                response = self._client.beta.chat.completions.parse(**request)
            except RateLimitError as e:
                logger.error(f"Rate limit exceeded: {str(e)}")
                raise OpenRouterAPIError(f"Rate limit exceeded: {str(e)}")
            except APITimeoutError as e:
                logger.error(f"API timeout: {str(e)}")
                raise OpenRouterConnectionError(f"API timeout: {str(e)}")
            except APIConnectionError as e:
                logger.error(f"API connection error: {str(e)}")
                raise OpenRouterConnectionError(f"API connection error: {str(e)}")
            except AuthenticationError as e:
                logger.error(f"Authentication error: {str(e)}")
                raise OpenRouterAPIError(f"Authentication error: {str(e)}")
            except BadRequestError as e:
                logger.error(f"Bad request: {str(e)}")
                raise OpenRouterAPIError(f"Bad request: {str(e)}")
            except OpenAIError as e:
                logger.error(f"OpenAI error: {str(e)}")
                raise OpenRouterAPIError(f"OpenAI error: {str(e)}")

            # Log raw response for debugging
            logger.debug(f"Raw response: {response}")
            if hasattr(response, '__dict__'):
                logger.debug(f"Response attributes: {dir(response)}")
                logger.debug(f"Response dict: {response.__dict__}")

            if response is None:
                logger.error("Received None response from OpenRouter API")
                raise OpenRouterAPIError("Received None response from OpenRouter API")

            logger.debug(f"Received response from OpenRouter: {len(response.choices)} choices")

            return response

        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Raising error: {e}")
            logger.error(f"Error in parse completion: {str(e)}")
            logger.error(f"Stack trace:\n{stack_trace}")

            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                try:
                    content = e.response.text
                    logger.error(f"Response content length: {len(content)} bytes")
                    logger.error(f"Response content preview: {content[:1000]}...")
                except:
                    logger.error("Could not read response content")
            self._handle_api_error("parse completion", e)

    @with_retry()
    def create_parsed(
        self,
        messages: list[dict[str, Any]],
        response_format: Type[BaseModel],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Get a chat completion from OpenRouter with structured output.
        
        Args:
            messages: The messages to send to the model
            response_format: A Pydantic model defining the expected response format
            model: Optional model override
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The parsed response from the model
        """
        try:
            # Convert Pydantic model to OpenAI response format
            response_format_param = type_to_response_format_param(response_format)

            # Log the request details
            logger.debug(f"Sending parsed chat completion request to OpenRouter with model: {model or self.model}")
            logger.debug(f"Message count: {len(messages)}")
            logger.debug(f"Response format: {json.dumps(response_format_param, indent=2)}")

            # Calculate total message size for logging
            total_size = sum(len(str(msg)) for msg in messages)
            logger.debug(f"Total message size: {total_size} bytes")

            request = {
                "model": model or self.model,
                "messages": messages,
                "stream": stream,
                "response_format": response_format_param,
                **kwargs,
            }

            response = self._client.chat.completions.create(**request)

            if response is None:
                logger.error("Received None response from OpenRouter API")
                raise OpenRouterAPIError("Received None response from OpenRouter API")

            # Validate response structure
            if not hasattr(response, 'choices'):
                logger.error(f"Response missing 'choices' attribute. Available attributes: {dir(response)}")
                raise OpenRouterAPIError("Invalid response format: missing 'choices' attribute")

            if response.choices is None:
                logger.error("Response choices is None")
                raise OpenRouterAPIError("Invalid response format: choices is None")

            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            logger.debug(f"Received response from OpenRouter: {len(response.choices)} choices")

            return response

        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error(f"Error in parsed chat completion: {str(e)}")
            logger.error(f"Stack trace:\n{stack_trace}")
            logger.error(f"Request details: model={model or self.model}, stream={stream}, kwargs={kwargs}")
            logger.error(f"Message structure: {[{'role': msg.get('role'), 'content_length': len(str(msg.get('content', '')))} for msg in messages]}")

            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                try:
                    content = e.response.text
                    logger.error(f"Response content length: {len(content)} bytes")
                    logger.error(f"Response content preview: {content[:1000]}...")
                except:
                    logger.error("Could not read response content")
            self._handle_api_error("parsed chat completion", e)

    @classmethod
    def register_model(cls, name: str, value: str) -> None:
        """Register a new model.

        Args:
            name: The name of the model (e.g., "CUSTOM_MODEL")
            value: The model identifier (e.g., "provider/model-name")

        Raises:
            ValueError: If the model name is already registered.
        """
        OpenRouterModelRegistry.register_model(name, value)

    @classmethod
    def list_models(cls) -> dict[str, str]:
        """List all available models.

        Returns:
            A dictionary mapping model names to their identifiers.
        """
        return OpenRouterModelRegistry.list_models() 
