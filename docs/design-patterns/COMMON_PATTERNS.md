# ADK Design Patterns

Common design patterns for building robust ADK agents, extracted from sample agents and best practices.

## Table of Contents
1. [Multi-Agent Orchestration](#multi-agent-orchestration)
2. [Router Pattern](#router-pattern)
3. [Critic-Revise Pattern](#critic-revise-pattern)
4. [Pipeline Pattern](#pipeline-pattern)
5. [Hierarchical Agent Pattern](#hierarchical-agent-pattern)
6. [State Machine Pattern](#state-machine-pattern)
7. [RAG Pattern](#rag-pattern)
8. [Human-in-the-Loop Pattern](#human-in-the-loop-pattern)

## Multi-Agent Orchestration

**Use Case**: Coordinate multiple specialized agents to accomplish a complex task.

**Pattern**: A main orchestrator agent uses `AgentTool` to delegate to specialized sub-agents.

**Example**: Blog Writer Agent
- **Researcher Agent**: Gathers information
- **Writer Agent**: Creates content
- **Editor Agent**: Reviews and improves

**Reference**: `../insp/adk-samples/python/agents/blog-writer/`

```python
researcher = adk.LlmAgent(
    model=model,
    instructions="Research topics thoroughly."
)

writer = adk.LlmAgent(
    model=model,
    instructions="Write engaging blog posts."
)

orchestrator = adk.LlmAgent(
    model=model,
    instructions="Coordinate research and writing.",
    tools=[
        adk.AgentTool(researcher, name="researcher"),
        adk.AgentTool(writer, name="writer")
    ]
)
```

## Router Pattern

**Use Case**: Route requests to different agents based on intent or content.

**Pattern**: A router agent analyzes input and delegates to appropriate specialized agents.

**Example**: Customer Service Agent
- Routes technical issues to tech support agent
- Routes billing questions to billing agent
- Routes general questions to FAQ agent

**Reference**: `../insp/adk-samples/python/agents/customer-service/`

```python
router = adk.LlmAgent(
    model=model,
    instructions="Route customer inquiries to the right specialist.",
    tools=[
        adk.AgentTool(tech_support, name="tech_support"),
        adk.AgentTool(billing, name="billing"),
        adk.AgentTool(faq, name="faq")
    ]
)
```

## Critic-Revise Pattern

**Use Case**: Improve quality through iterative review and revision.

**Pattern**: Two agents - one generates, another critiques and revises.

**Example**: LLM Auditor Agent
- **Generator**: Creates initial response
- **Critic**: Reviews for accuracy, safety, quality
- **Reviser**: Improves based on critique

**Reference**: `../insp/adk-samples/python/agents/llm-auditor/`

```python
generator = adk.LlmAgent(
    model=model,
    instructions="Generate responses."
)

critic = adk.LlmAgent(
    model=model,
    instructions="Critique responses for accuracy and safety."
)

reviser = adk.LlmAgent(
    model=model,
    instructions="Revise responses based on critique.",
    tools=[adk.AgentTool(critic, name="critic")]
)

main = adk.SequentialAgent(
    agents=[generator, reviser],
    instructions="Generate then improve."
)
```

## Pipeline Pattern

**Use Case**: Process data through multiple stages.

**Pattern**: Sequential agents, each handling one stage of processing.

**Example**: Data Engineering Agent
- **Ingest**: Load data
- **Transform**: Clean and process
- **Load**: Store results

**Reference**: `../insp/adk-samples/python/agents/data-engineering/`

```python
pipeline = adk.SequentialAgent(
    agents=[
        ingest_agent,
        transform_agent,
        load_agent
    ],
    instructions="Process data through pipeline stages."
)
```

## Hierarchical Agent Pattern

**Use Case**: Complex systems with multiple levels of abstraction.

**Pattern**: Agents organized in a tree structure, with parent agents coordinating children.

**Example**: Marketing Agency Agent
- **Strategy Agent**: High-level planning
  - **Research Agent**: Market research
  - **Content Agent**: Content creation
    - **Writer Agent**: Writing
    - **Designer Agent**: Design

**Reference**: `../insp/adk-samples/python/agents/marketing-agency/`

```python
# Leaf agents
writer = adk.LlmAgent(...)
designer = adk.LlmAgent(...)

# Mid-level agent
content = adk.LlmAgent(
    tools=[
        adk.AgentTool(writer),
        adk.AgentTool(designer)
    ]
)

# Top-level agent
strategy = adk.LlmAgent(
    tools=[
        adk.AgentTool(research),
        adk.AgentTool(content)
    ]
)
```

## State Machine Pattern

**Use Case**: Agents that progress through defined states.

**Pattern**: Use `tool_context.state` to track current state and transition between states.

**Example**: Order Processing Agent
- States: `pending`, `processing`, `shipped`, `delivered`
- State transitions triggered by tools

**Reference**: `../insp/adk-samples/python/agents/order-processing/`

```python
def process_order(tool_context: adk.ToolContext, order_id: str):
    state = tool_context.state
    state["current_state"] = "processing"
    # Process order...
    state["current_state"] = "shipped"
    return {"status": "shipped"}

agent = adk.LlmAgent(
    tools=[adk.FunctionTool(process_order)]
)
```

## RAG Pattern

**Use Case**: Answer questions using external knowledge base.

**Pattern**: Retrieve relevant documents, then generate answer with context.

**Example**: RAG Agent
- Uses Vertex AI Search for retrieval
- Grounds responses with citations

**Reference**: `../insp/adk-samples/python/agents/RAG/`

```python
from google import adk

agent = adk.LlmAgent(
    model=model,
    instructions="Answer questions using provided context.",
    grounding=adk.grounding.VertexAISearch(
        data_store="projects/.../locations/.../dataStores/..."
    )
)
```

## Human-in-the-Loop Pattern

**Use Case**: Require human approval for critical decisions.

**Pattern**: Agent pauses and requests human input before proceeding.

**Example**: Medical Pre-Authorization Agent
- Analyzes request
- Pauses for doctor review
- Proceeds based on approval

**Reference**: `../insp/adk-samples/python/agents/medical-pre-authorization/`

```python
def request_approval(tool_context: adk.ToolContext, decision: str):
    # Send to human reviewer
    # Wait for response
    approval = wait_for_human_input()
    return {"approved": approval}

agent = adk.LlmAgent(
    tools=[adk.FunctionTool(request_approval)]
)
```

## Additional Patterns

### Streaming Pattern
For real-time conversational agents with audio/video streaming.

**Reference**: `../insp/adk-samples/python/agents/realtime-conversational-agent/`

### Evaluation Pattern
Build evaluation suites to test agent performance.

**Reference**: `../insp/adk-samples/python/agents/*/eval/`

### Deployment Pattern
Standardize deployment to Cloud Run or Agent Engine.

**Reference**: `../insp/adk-samples/python/agents/*/deployment/`

## Pattern Selection Guide

| Pattern | Complexity | Use Case |
|---------|-----------|----------|
| Multi-Agent Orchestration | Medium | Complex tasks requiring multiple skills |
| Router Pattern | Easy | Multiple specialized handlers |
| Critic-Revise | Medium | Quality-critical outputs |
| Pipeline | Easy | Sequential data processing |
| Hierarchical | Advanced | Complex multi-level systems |
| State Machine | Medium | Workflow with defined states |
| RAG | Medium | Knowledge-based Q&A |
| Human-in-the-Loop | Medium | Critical decisions requiring approval |

## Best Practices

1. **Start Simple**: Begin with single agent, add complexity gradually
2. **Clear Responsibilities**: Each agent should have a single, clear purpose
3. **State Management**: Use `tool_context.state` for session data
4. **Error Handling**: Always handle errors in tools gracefully
5. **Testing**: Build evaluation suites for each agent
6. **Documentation**: Document agent purpose and patterns used

## References

- **All Samples**: `../insp/adk-samples/python/agents/`
- **Documentation**: `../insp/adk-docs/docs/agents/`
- **Tutorials**: `../insp/adk-docs/docs/tutorials/`

