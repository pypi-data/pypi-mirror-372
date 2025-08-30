"""
Script to send a request to AI using OpenRouterClient by reading request.json.
"""

import os
import json
import logging
from pathlib import Path
from mbxai.openrouter.client import OpenRouterClient
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PageStructureValidator(BaseModel):
    """Model representing a validator to check if an HTML page matches a known structure."""

    name: str = Field(description="Name of the validator")
    xpath_selector: str = Field(
        description="XPath selector to check if the structure matches"
    )
    description: str = Field(
        description="Description of what this validator checks for"
    )


class ProductSelector(BaseModel):
    """Model representing a selector for extracting specific product data."""

    field_name: str = Field(description="Name of the product field to extract")
    xpath_selector: str = Field(description="XPath selector to extract the data")
    description: str = Field(description="Description of what this selector extracts")
    is_list: bool = Field(description="Whether this selector should extract a list of values or a single value")


class PageStructureAnalysis(BaseModel):
    """Model representing the analysis of a product page structure."""

    structure_id: str = Field(description="Unique identifier for this page structure")
    store_name: str = Field(description="Name of the store/website")
    structure_description: str = Field(description="Description of the page structure")
    validators: list[PageStructureValidator] = Field(
        description="Validators to check if HTML matches this structure"
    )
    selectors: list[ProductSelector] = Field(
        description="Selectors to extract product data"
    )


def read_request_json() -> dict:
    """Read and parse the request.json file.
    
    Returns:
        dict: The parsed JSON data
    """
    current_dir = Path(__file__).parent
    request_file = current_dir / "request.json"
    
    try:
        with open(request_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"request.json not found at {request_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing request.json: {e}")
        raise

def format_response(response) -> dict:
    """Format the ChatCompletion response into a JSON-serializable dictionary.
    
    Args:
        response: The ChatCompletion response from OpenAI
        
    Returns:
        dict: A JSON-serializable dictionary containing the response data
    """
    # Format choices with tool calls if present
    choices = []
    for choice in response.choices:
        choice_data = {
            'index': choice.index,
            'message': {
                'role': choice.message.role,
                'content': choice.message.content
            },
            'finish_reason': choice.finish_reason
        }
        
        # Add tool calls if they exist
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
            choice_data['message']['tool_calls'] = [
                {
                    'id': tool_call.id,
                    'type': tool_call.type,
                    'function': {
                        'name': tool_call.function.name,
                        'arguments': tool_call.function.arguments
                    }
                }
                for tool_call in choice.message.tool_calls
            ]
        
        choices.append(choice_data)

    return {
        'id': response.id,
        'created': response.created,
        'model': response.model,
        'choices': choices,
        'usage': {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    }

def write_response_json(response_data: dict):
    """Write the response data to response.json file.
    
    Args:
        response_data: The formatted response dictionary to write
    """
    current_dir = Path(__file__).parent
    response_file = current_dir / "response.json"
    
    try:
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2)
        logger.info(f"Response written to {response_file}")
    except IOError as e:
        logger.error(f"Error writing response.json: {e}")
        raise

def main():
    # Get API token from environment variable
    token = os.getenv("OPENROUTER_API_KEY")
    if not token:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        raise ValueError("Please set the OPENROUTER_API_KEY environment variable")

    # Read request configuration
    logger.info("Reading request.json")
    request_data = read_request_json()

    # Initialize the OpenRouter client
    logger.info("Initializing OpenRouterClient")
    client = OpenRouterClient(token=token)

    # Extract request parameters
    model = request_data.get("model")
    messages = request_data.get("messages", [])
    tools = request_data.get("tools", [])

    # Send the request
    logger.info(f"Sending request to model: {model}")
    response = client.parse(
        model=model,
        response_format=PageStructureAnalysis,
        messages=messages,
        tools=tools
    )

    # Format and save the response
    logger.info("Received response from OpenRouter API")
    formatted_response = format_response(response)
    write_response_json(formatted_response)
    
    # Print summary
    print("\nResponse summary:")
    print(f"- Model: {formatted_response['model']}")
    print(f"- Total tokens: {formatted_response['usage']['total_tokens']}")
    print(f"- Response saved to: {Path(__file__).parent / 'response.json'}")

if __name__ == "__main__":
    main() 