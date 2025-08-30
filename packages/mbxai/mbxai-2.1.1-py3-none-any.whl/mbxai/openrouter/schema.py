"""
Response formatting utilities for OpenRouter.
"""

from typing import Any
import json

def format_response(response: Any) -> dict[str, Any]:
    """Format the response into a JSON-serializable dictionary.
    
    Args:
        response: The response from OpenAI
        
    Returns:
        A JSON-serializable dictionary containing the response data
    """
    if hasattr(response, 'model_dump'):
        return response.model_dump()
    elif hasattr(response, '__dict__'):
        return response.__dict__
    return str(response) 