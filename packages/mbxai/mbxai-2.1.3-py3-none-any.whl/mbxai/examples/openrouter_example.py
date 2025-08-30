"""
Example script demonstrating basic usage of the OpenRouterClient.
"""

import os
import logging
from mbxai.openrouter.client import OpenRouterClient, OpenRouterModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Get API token from environment variable
    token = os.getenv("OPENROUTER_API_KEY")
    if not token:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        raise ValueError("Please set the OPENROUTER_API_KEY environment variable")

    logger.info("Initializing OpenRouterClient with GPT-4 Turbo")
    # Initialize the client
    client = OpenRouterClient(
        token=token,
        model=OpenRouterModel.GPT4_TURBO  # Using GPT-4 Turbo as default
    )

    # Example messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]

    logger.info("Sending request to OpenRouter API")
    # Send the request
    response = client.create(messages=messages)

    # Log the response
    logger.info("Received response from OpenRouter API")
    logger.info(f"Response: {response}")

if __name__ == "__main__":
    main() 