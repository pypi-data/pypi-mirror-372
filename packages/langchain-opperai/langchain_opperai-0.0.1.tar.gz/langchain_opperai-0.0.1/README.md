# LangChain Opper

A LangChain integration package for [Opper AI](https://opper.ai) that provides chat models and provider utilities with seamless LangGraph compatibility.

## Features

- **🔗 LangChain Integration**: Drop-in replacement for other LangChain chat models
- **📊 Built-in Tracing**: Automatic span creation and management using Opper's tracing
- **📈 Metrics Support**: Easy metric collection for evaluation and monitoring
- **🏗️ Structured Outputs**: Native support for Pydantic models with `with_structured_output()`
- **🔧 Flexible Configuration**: Customizable instructions, models, and task names
- **🚀 Easy Setup**: Simple installation and configuration

## Installation

```bash
pip install langchain-opperai
```

## Setup

Set your Opper API key as an environment variable:

```bash
export OPPER_API_KEY="your_opper_api_key_here"
```

## Quick Start

### Basic Chat Model

```python
from langchain_opperai import ChatOpperAI
from langchain_core.messages import HumanMessage

# Initialize the chat model
llm = ChatOpperAI(
    task_name="chat",
    model_name="anthropic/claude-3.5-sonnet",
    instructions="You are a helpful AI assistant.",
)

# Use it like any LangChain chat model
messages = [HumanMessage(content="What is the capital of France?")]
result = llm.invoke(messages)
print(result.content)  # "The capital of France is Paris."
```

### Structured Output

```python
from langchain_opperai import ChatOpperAI
from pydantic import BaseModel, Field

class Joke(BaseModel):
    setup: str = Field(description="The joke setup")
    punchline: str = Field(description="The joke punchline")

# Create a structured model
llm = ChatOpperAI()
structured_llm = llm.with_structured_output(Joke)

# Get structured output
joke = structured_llm.invoke("Tell me a joke about cats")
print(f"Setup: {joke.setup}")
print(f"Punchline: {joke.punchline}")
```

### Using the Provider

```python
from langchain_opperai import OpperProvider
from pydantic import BaseModel, Field

class Response(BaseModel):
    answer: str = Field(description="The answer")
    confidence: float = Field(description="Confidence score 0-1")

# Initialize provider
provider = OpperProvider()

# Create models
chat_model = provider.create_chat_model(
    task_name="chat",
    instructions="You are a helpful assistant.",
)

structured_model = provider.create_structured_model(
    task_name="structured_chat",
    instructions="Provide structured responses.",
    output_schema=Response,
)

# With tracing
trace_id = provider.start_trace("conversation", "User asks about Python")
result = chat_model.invoke("What is Python?")
provider.end_trace("Provided Python explanation")
```

### LangGraph Integration

```python
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_opperai import OpperProvider
from typing import TypedDict, Annotated

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chat_node(state: State):
    provider = OpperProvider()
    llm = provider.create_chat_model(
        task_name="langgraph_chat",
        instructions="You are a helpful assistant in a graph workflow.",
    )
    
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
workflow = StateGraph(State)
workflow.add_node("chat", chat_node)
workflow.set_entry_point("chat")
workflow.add_edge("chat", END)

app = workflow.compile()

# Run
result = app.invoke({
    "messages": [HumanMessage(content="Hello!")]
})
```

## API Reference

### ChatOpperAI

A LangChain chat model that integrates with Opper AI.

**Parameters:**
- `task_name` (str): Name for the Opper task (default: "chat")
- `model_name` (str): Model to use (default: "anthropic/claude-3.5-sonnet")
- `instructions` (str): Instructions for the model
- `opper_client` (Optional[Opper]): Opper client instance
- `parent_span_id` (Optional[str]): Parent span ID for tracing

**Methods:**
- `with_structured_output(schema)`: Create a model that returns structured output
- `invoke(messages)`: Generate a response to the given messages
- `ainvoke(messages)`: Async version of invoke

### OpperProvider

A provider class for creating Opper chat models and managing traces.

**Methods:**
- `create_chat_model(**kwargs)`: Create a new ChatOpperAI
- `create_structured_model(task_name, instructions, output_schema, **kwargs)`: Create a structured model
- `start_trace(name, input_data)`: Start a new trace
- `end_trace(output_data)`: End the current trace
- `add_metric(span_id, dimension, value, comment)`: Add a metric to a span

## Environment Variables

- `OPPER_API_KEY`: Your Opper API key (required)

## Requirements

- Python ≥ 3.9.2
- langchain-core ≥ 0.3.0
- opperai ≥ 1.0.0
- pydantic ≥ 2.0.0

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [Opper AI](https://opper.ai)
- [LangChain](https://langchain.com)
- [LangGraph](https://langchain-ai.github.io/langgraph/)