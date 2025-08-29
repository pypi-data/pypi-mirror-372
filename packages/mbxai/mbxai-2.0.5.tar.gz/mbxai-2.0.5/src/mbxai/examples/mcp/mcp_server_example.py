"""Example MCP server implementation."""

import asyncio
from typing import Any
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from mbxai.mcp import MCPServer
from fastapi import Body
import uvicorn

# Create a FastMCP instance for this module
mcp = FastMCP("html-structure-analyser")

class ScraperInput(BaseModel):
    url: str

@mcp.tool()
async def scrape_html(input: ScraperInput) -> str:
    """Scrape HTML content from a URL.
    
    This function fetches the HTML content from a given URL using httpx.
    It handles redirects and raises appropriate exceptions for HTTP errors.
    
    Args:
        input: ScraperInput model containing the URL to scrape
    
    Returns:
        str: The HTML content of the page
    
    Raises:
        httpx.HTTPError: If there's an HTTP error while fetching the page
        Exception: For any other unexpected errors
    """
    # This is a mock implementation that returns sample HTML
    sample_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sample Page</title>
    </head>
    <body>
        <header>
            <h1>Welcome to Sample Page</h1>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>
        <main>
            <section id="content">
                <h2>Main Content</h2>
                <p>This is a sample HTML page that was scraped from {input.url}</p>
                <article>
                    <h3>Article Title</h3>
                    <p>This is a sample article with some content.</p>
                </article>
            </section>
        </main>
        <footer>
            <p>&copy; 2024 Sample Website</p>
        </footer>
    </body>
    </html>
    """
    return sample_html

class CustomMCPServer(MCPServer):
    """Custom MCP server with overridden endpoints."""
    
    def _register_endpoints(self) -> None:
        """Register FastAPI endpoints."""
        @self.app.get("/tools")
        async def get_tools():
            """Return the list of available tools."""
            tools = []
            for tool in self._tools.values():
                tool_dict = tool.model_dump(exclude={'function'})
                tool_dict['internal_url'] = f"http://localhost:8000/tools/{tool.name}/invoke"
                tool_dict['service'] = "html-structure-analyser"
                tools.append(tool_dict)
            return {"tools": tools}

        @self.app.post("/tools/{tool_name}/invoke")
        async def invoke_tool(tool_name: str, arguments: dict[str, Any] = Body(...)):
            """Invoke a specific MCP tool."""
            try:
                result = await self.mcp_server.call_tool(tool_name, arguments=arguments)
                if isinstance(result, list) and len(result) == 1:
                    first_item = result[0]
                    if hasattr(first_item, "type") and first_item.type == "text":
                        return first_item.text
                elif isinstance(result, dict) and result.get("type") == "text":
                    return result["text"]
                return result
            except Exception as e:
                return {"error": f"Error invoking tool {tool_name}: {str(e)}"}

async def start_server():
    # Create and start the MCP server
    server = CustomMCPServer("html-structure-analyser")
    
    # Register the tool with the MCP server
    await server.add_tool(scrape_html)
    
    # Create uvicorn config
    config = uvicorn.Config(server.app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    
    # Start the server
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_server()) 
