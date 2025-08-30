# MBX AI

A Python library for building AI applications with LLMs.

## Features

- **OpenRouter Integration**: Connect to various LLM providers through OpenRouter
- **Intelligent Agent System**: AgentClient with dialog-based thinking, question generation, and quality iteration
- **Tool Integration**: Easily integrate tools with LLMs using the Model Context Protocol (MCP)
- **Structured Output**: Get structured, typed responses from LLMs
- **Chat Interface**: Simple chat interface for interacting with LLMs
- **FastAPI Server**: Built-in FastAPI server for tool integration

## Installation

```bash
pip install mbxai
```

## Quick Start

### Basic Usage

```python
from mbxai import OpenRouterClient

# Initialize the client
client = OpenRouterClient(api_key="your-api-key")

# Chat with an LLM
response = await client.chat([
    {"role": "user", "content": "Hello, how are you?"}
])
print(response.choices[0].message.content)
```

### Quick Agent Example

```python
from mbxai import AgentClient, OpenRouterClient
from pydantic import BaseModel, Field

class TravelPlan(BaseModel):
    destination: str = Field(description="Travel destination")
    activities: list[str] = Field(description="Recommended activities")
    budget: str = Field(description="Estimated budget")

# Initialize agent
client = OpenRouterClient(token="your-api-key")
agent = AgentClient(client)

# Get intelligent response with automatic quality improvement
response = agent.agent(
    prompt="Plan a weekend trip to a mountain destination",
    final_response_structure=TravelPlan,
    ask_questions=False
)

plan = response.final_response
print(f"Destination: {plan.destination}")
print(f"Activities: {', '.join(plan.activities)}")
```

### Using Tools

```python
from mbxai import OpenRouterClient, ToolClient
from pydantic import BaseModel

# Define your tool's input and output models
class CalculatorInput(BaseModel):
    a: float
    b: float

class CalculatorOutput(BaseModel):
    result: float

# Create a calculator tool
async def calculator(input: CalculatorInput) -> CalculatorOutput:
    return CalculatorOutput(result=input.a + input.b)

# Initialize the client with tools
client = ToolClient(OpenRouterClient(api_key="your-api-key"))
client.add_tool(calculator)

# Use the tool in a chat
response = await client.chat([
    {"role": "user", "content": "What is 2 + 3?"}
])
print(response.choices[0].message.content)
```

### Using MCP (Model Context Protocol)

```python
from mbxai import OpenRouterClient, MCPClient
from mbxai.mcp import MCPServer
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# Define your tool's input and output models
class CalculatorInput(BaseModel):
    a: float
    b: float

class CalculatorOutput(BaseModel):
    result: float

# Create a FastMCP instance
mcp = FastMCP("calculator-service")

# Create a calculator tool
@mcp.tool()
async def calculator(argument: CalculatorInput) -> CalculatorOutput:
    return CalculatorOutput(result=argument.a + argument.b)

# Start the MCP server
server = MCPServer("calculator-service")
await server.add_tool(calculator)
await server.start()

# Initialize the MCP client
client = MCPClient(OpenRouterClient(api_key="your-api-key"))
await client.register_mcp_server("calculator-service", "http://localhost:8000")

# Use the tool in a chat
response = await client.chat([
    {"role": "user", "content": "What is 2 + 3?"}
])
print(response.choices[0].message.content)
```

### Using AgentClient (Intelligent Dialog System)

The `AgentClient` provides an intelligent dialog-based thinking process that can ask clarifying questions, iterate on responses, and provide structured outputs.

#### Basic Agent Usage

```python
from mbxai import AgentClient, OpenRouterClient
from pydantic import BaseModel, Field

# Define your response structure
class BookRecommendation(BaseModel):
    title: str = Field(description="The title of the recommended book")
    author: str = Field(description="The author of the book")
    genre: str = Field(description="The genre of the book")
    reason: str = Field(description="Why this book is recommended")

# Initialize the agent
client = OpenRouterClient(token="your-api-key")
agent = AgentClient(client)

# Get a recommendation with questions
response = agent.agent(
    prompt="I want a book recommendation",
    final_response_structure=BookRecommendation,
    ask_questions=True  # Agent will ask clarifying questions
)

if response.has_questions():
    # Display questions to user
    for question in response.questions:
        print(f"Q: {question.question}")
    
    # Collect answers and continue
    from mbxai import AnswerList, Answer
    answers = AnswerList(answers=[
        Answer(key="genre", answer="I love science fiction"),
        Answer(key="complexity", answer="I prefer complex narratives")
    ])
    
    # Continue the conversation
    final_response = agent.answer_to_agent(response.agent_id, answers)
    book_rec = final_response.final_response
    print(f"Recommended: {book_rec.title} by {book_rec.author}")
else:
    # Direct response without questions
    book_rec = response.final_response
    print(f"Recommended: {book_rec.title} by {book_rec.author}")
```

#### Agent with Tool Integration

```python
from mbxai import AgentClient, ToolClient, OpenRouterClient

# Initialize with tool support
openrouter_client = OpenRouterClient(token="your-api-key")
tool_client = ToolClient(openrouter_client)
agent = AgentClient(tool_client)

# Register tools via the agent (schema auto-generated!)
def get_weather(location: str, unit: str = "fahrenheit") -> dict:
    """Get weather information for a location.
    
    Args:
        location: The city or location name
        unit: Temperature unit (fahrenheit or celsius)
    """
    return {"location": location, "temperature": "72°F", "conditions": "Sunny"}

agent.register_tool(
    name="get_weather",
    description="Get current weather for a location",
    function=get_weather
    # Schema automatically generated from function signature!
)

# Use agent with tools
class WeatherResponse(BaseModel):
    location: str = Field(description="The location")
    weather: str = Field(description="Weather description")
    recommendations: list[str] = Field(description="Clothing recommendations")

response = agent.agent(
    prompt="What's the weather in San Francisco and what should I wear?",
    final_response_structure=WeatherResponse,
    ask_questions=False
)

weather_info = response.final_response
print(f"Weather: {weather_info.weather}")
```

#### Agent Configuration

```python
# Configure quality iterations (default: 2)
agent = AgentClient(
    ai_client=openrouter_client,
    max_iterations=3  # More iterations = higher quality, slower response
)

# Different configurations for different use cases:
# max_iterations=0: Fastest, basic quality (chatbots)
# max_iterations=1: Fast, good quality (content generation)
# max_iterations=2: Balanced (default, recommended)
# max_iterations=3+: Highest quality (analysis, reports)
```

#### Agent with MCP Client

```python
from mbxai import AgentClient, MCPClient

# Initialize with MCP support
mcp_client = MCPClient(OpenRouterClient(token="your-api-key"))
agent = AgentClient(mcp_client)

# Register MCP servers
agent.register_mcp_server("data-analysis", "http://localhost:8000")

# Register individual tools
agent.register_tool("analyze_data", "Analyze dataset", analyze_function, schema)

# Use agent with full MCP capabilities
response = agent.agent(
    prompt="Analyze the sales data and provide insights",
    final_response_structure=AnalysisReport,
    ask_questions=True
)
```

#### Agent Features

- **Intelligent Questions**: Automatically generates clarifying questions when needed
- **Quality Iteration**: Improves responses through multiple AI review cycles  
- **Tool Integration**: Seamlessly works with ToolClient and MCPClient
- **Structured Output**: Always returns properly typed Pydantic models
- **Session Management**: Handles multi-turn conversations with question/answer flow
- **Configurable**: Adjust quality vs speed with max_iterations parameter

#### Supported AI Clients

| Client | Structured Responses | Tool Registration | MCP Server Registration |
|--------|---------------------|-------------------|------------------------|
| OpenRouterClient | ✅ | ❌ | ❌ |
| ToolClient | ✅ | ✅ | ❌ |
| MCPClient | ✅ | ✅ | ✅ |

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mbxai.git
cd mbxai
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

## License

MIT License