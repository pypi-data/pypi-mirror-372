"""Example usage of the MCP client."""

import logging
import os
from mbxai.openrouter import OpenRouterClient
from mbxai.mcp import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Get API key from environment variable
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("Please set the OPENROUTER_API_KEY environment variable")
        return

    try:
        # Initialize the OpenRouter client (required by MCPClient)
        openrouter_client = OpenRouterClient(token=api_key)
        
        # Create MCP client
        with MCPClient(openrouter_client) as client:
            # Register the local MCP server
            server_url = "http://localhost:8000"
            try:
                client.register_mcp_server("mcp_server", server_url)
            except Exception as e:
                logger.error(f"Failed to register MCP server: {str(e)}")
                logger.error("Make sure the MCP server is running at http://localhost:8000")
                return
            
            # Test chat with tool calls
            messages = [
                {
                    "role": "user",
                    "content": "Scrape this example url: https://www.google.com"
                }
            ]
            
            try:
                # Get the chat response
                response = client.chat(messages=messages)
                
                # Print the final response
                if not response:
                    logger.error("No response received from the model")
                    return
                    
                if not hasattr(response, 'choices'):
                    logger.error(f"Invalid response format - no choices attribute: {response}")
                    return
                
                if response.choices is None:
                    logger.error("Response choices is None")
                    return
                    
                if not response.choices:
                    logger.error("No choices in response")
                    return
                    
                final_message = response.choices[0].message
                if not final_message:
                    logger.error("No message in first choice")
                    return
                    
                logger.info(f"Final response: {final_message.content}")
                    
            except Exception as e:
                logger.error(f"Error during chat: {str(e)}")
                if hasattr(e, 'response'):
                    logger.error(f"Response status: {e.response.status_code if e.response else 'No response'}")
                    logger.error(f"Response content: {e.response.text if e.response else 'No content'}")
                
    except Exception as e:
        logger.error(f"Error initializing clients: {str(e)}")

if __name__ == "__main__":
    main() 