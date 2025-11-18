# ADK Cookbook: Basic Patterns

Common patterns and recipes for building ADK agents.

## Table of Contents
1. [Simple Conversational Agent](#simple-conversational-agent)
2. [Agent with Function Tools](#agent-with-function-tools)
3. [Multi-Agent Workflow](#multi-agent-workflow)
4. [State Management](#state-management)
5. [Session & Memory](#session--memory)
6. [Error Handling](#error-handling)

## Simple Conversational Agent

The most basic agent - just an LLM with instructions.

```python
from google import adk

agent = adk.LlmAgent(
    model=adk.models.Gemini(model_name="gemini-2.0-flash-exp"),
    instructions="You are a helpful assistant."
)

# Run
response = agent.run("Hello!")
```

**Reference**: See `../insp/adk-samples/python/agents/personalized-shopping/`

## Agent with Function Tools

Add capabilities to your agent with function tools.

```python
from google import adk
from typing import Dict, Any

def get_weather(tool_context: adk.ToolContext, location: str) -> Dict[str, Any]:
    """Get weather for a location."""
    # Your weather API call here
    return {"location": location, "temperature": "72°F"}

agent = adk.LlmAgent(
    model=adk.models.Gemini(model_name="gemini-2.0-flash-exp"),
    instructions="You are a weather assistant.",
    tools=[adk.FunctionTool(get_weather)]
)

response = agent.run("What's the weather in San Francisco?")
```

**Reference**: See `../insp/adk-samples/python/agents/llm-auditor/llm_auditor/tools/`

## Multi-Agent Workflow

Create a team of agents working together.

```python
from google import adk

# Sub-agents
researcher = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You research topics thoroughly."
)

writer = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You write clear, engaging content."
)

# Main agent orchestrates sub-agents
main_agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You coordinate research and writing.",
    tools=[
        adk.AgentTool(researcher, name="researcher"),
        adk.AgentTool(writer, name="writer")
    ]
)
```

**Reference**: See `../insp/adk-samples/python/agents/blog-writer/`

## State Management

Maintain state across agent interactions.

```python
from google import adk

def start_quiz(tool_context: adk.ToolContext) -> Dict[str, Any]:
    state = tool_context.state
    state["quiz_started"] = True
    state["score"] = 0
    state["current_question"] = 1
    return {"status": "Quiz started"}

def answer_question(tool_context: adk.ToolContext, answer: str) -> Dict[str, Any]:
    state = tool_context.state
    # Check answer and update score
    if answer == "correct":
        state["score"] += 1
    state["current_question"] += 1
    return {"score": state["score"]}

agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You are a quiz master.",
    tools=[
        adk.FunctionTool(start_quiz),
        adk.FunctionTool(answer_question)
    ]
)

# State persists across runs in a session
session = adk.Session()
response1 = agent.run("Start a quiz", session=session)
response2 = agent.run("My answer is Python", session=session)
```

**Reference**: See `../insp/blog-state-memory.html` and `../insp/adk-docs/docs/sessions/state.md`

## Session & Memory

Use sessions for conversation context and memory for long-term storage.

```python
from google import adk

# Create a session for conversation context
session = adk.Session()

agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You remember past conversations.",
)

# First interaction
response1 = agent.run("My name is Alice", session=session)

# Later - agent remembers
response2 = agent.run("What's my name?", session=session)

# For long-term memory, use Memory Bank (Vertex AI)
# See: ../insp/adk-docs/docs/sessions/memory.md
```

**Reference**: 
- `../insp/blog-state-memory.html`
- `../insp/adk-docs/docs/sessions/memory.md`
- `../insp/adk-docs/docs/sessions/session.md`

## Error Handling

Handle errors gracefully in tools and agents.

```python
from google import adk
from typing import Dict, Any
import logging

def risky_operation(tool_context: adk.ToolContext, input: str) -> Dict[str, Any]:
    """A tool that might fail."""
    try:
        # Your operation here
        result = perform_operation(input)
        return {"success": True, "result": result}
    except Exception as e:
        logging.error(f"Operation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Please try again with different input."
        }

# Agent with error handling
agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Handle errors gracefully and inform the user.",
    tools=[adk.FunctionTool(risky_operation)]
)
```

**Reference**: See `../insp/adk-samples/python/agents/customer-service/` for production error handling

## Sequential Workflow

Chain multiple steps in order.

```python
from google import adk

step1 = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Research the topic."
)

step2 = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Write a summary."
)

workflow = adk.SequentialAgent(
    agents=[step1, step2],
    instructions="Research then summarize."
)

response = workflow.run("Tell me about quantum computing")
```

**Reference**: See `../insp/adk-docs/docs/agents/workflow-agents/sequential-agents.md`

## Parallel Execution

Run multiple agents concurrently.

```python
from google import adk

agent1 = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Analyze from technical perspective."
)

agent2 = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Analyze from business perspective."
)

parallel = adk.ParallelAgent(
    agents=[agent1, agent2],
    instructions="Get both perspectives."
)

response = parallel.run("Analyze this product idea")
```

**Reference**: See `../insp/adk-docs/docs/agents/workflow-agents/parallel-agents.md`

## Loop Pattern

Iterate until a condition is met.

```python
from google import adk

def check_quality(tool_context: adk.ToolContext, content: str) -> Dict[str, Any]:
    """Check if content meets quality standards."""
    quality_score = evaluate_content(content)
    return {
        "quality_score": quality_score,
        "meets_standard": quality_score >= 0.8
    }

improver = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Improve the content.",
    tools=[adk.FunctionTool(check_quality)]
)

loop_agent = adk.LoopAgent(
    agent=improver,
    max_iterations=5,
    instructions="Keep improving until quality is high enough."
)

response = loop_agent.run("Improve this draft")
```

**Reference**: See `../insp/adk-docs/docs/agents/workflow-agents/loop-agents.md`

## More Patterns

For more advanced patterns, see:
- `../insp/adk-samples/python/agents/` - Real-world examples
- `../insp/adk-docs/docs/agents/` - Official documentation
- `../design-patterns/` - Design pattern examples

