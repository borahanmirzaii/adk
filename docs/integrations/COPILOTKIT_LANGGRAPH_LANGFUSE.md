# ADK Integrations: CopilotKit, LangGraph, and Langfuse

This document explains how CopilotKit, LangGraph, and Langfuse integrate with Google's Agent Development Kit (ADK) to enhance your agent development workflow.

## Table of Contents
1. [Overview](#overview)
2. [CopilotKit - Agent UI](#copilotkit---agent-ui)
3. [LangGraph - Agent Orchestration](#langgraph---agent-orchestration)
4. [Langfuse - Observability](#langfuse---observability)
5. [Integration Architecture](#integration-architecture)
6. [Getting Started](#getting-started)
7. [Use Cases](#use-cases)

## Overview

These three tools complement ADK by providing:
- **CopilotKit**: Modern React-based UI components for agent interfaces
- **LangGraph**: Advanced workflow orchestration for complex agent behaviors
- **Langfuse**: Comprehensive observability and tracing for agent debugging

Together, they create a complete stack: **Frontend (CopilotKit) → Orchestration (LangGraph) → Core (ADK) → Observability (Langfuse)**

## CopilotKit - Agent UI

### What is CopilotKit?

CopilotKit is an open-source framework for building AI agent user interfaces. It provides React components and infrastructure to embed AI copilots, chatbots, and in-app agents into your applications.

### Key Features

- **AG-UI Protocol Support**: Standardizes communication between frontends and AI agents
- **Pre-built React Components**: Chat interfaces, agentic UI, and more
- **Real-time Interactions**: Bidirectional state synchronization
- **Human-in-the-Loop**: Built-in support for approval workflows
- **Agentic Generative UI**: Dynamic UI generation based on agent actions

### How It Fits with ADK

CopilotKit serves as the **frontend layer** for your ADK agents:

```
┌─────────────────┐
│  CopilotKit UI  │  ← React frontend with chat, state management
└────────┬────────┘
         │ AG-UI Protocol
         ▼
┌─────────────────┐
│   ADK Backend   │  ← Your ADK agents (LlmAgent, workflows, etc.)
└─────────────────┘
```

### Integration Steps

1. **Quick Start with CopilotKit CLI**:
   ```bash
   npx copilotkit@latest create -f adk
   ```
   This creates a full-stack project with ADK backend and Next.js frontend.

2. **Manual Integration**:
   - Install CopilotKit: `npm install @copilotkit/react-core @copilotkit/react-ui`
   - Connect to ADK backend via AG-UI protocol
   - Use CopilotKit components in your React app

### Resources

- **Official Integration Guide**: https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui
- **GitHub**: https://github.com/CopilotKit/CopilotKit
- **AG-UI Protocol**: https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/

### Use Cases

- Building chat interfaces for ADK agents
- Creating in-app AI copilots
- Implementing agentic generative UI
- Adding human-in-the-loop workflows

## LangGraph - Agent Orchestration

### What is LangGraph?

LangGraph is a framework for building stateful, multi-actor applications with LLMs. It's designed for creating complex agent workflows and orchestrating multi-agent systems.

### Key Features

- **State Machines**: Define agent workflows as state graphs
- **Multi-Agent Coordination**: Orchestrate multiple agents working together
- **Conditional Logic**: Complex decision-making in agent workflows
- **Persistence**: Save and resume agent execution
- **Human-in-the-Loop**: Built-in support for human approval steps

### How It Fits with ADK

LangGraph can **complement or enhance** ADK's workflow capabilities:

```
┌─────────────────┐
│   LangGraph     │  ← Complex workflow orchestration
│  (Orchestration)│     State machines, multi-agent coordination
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ADK Agents    │  ← Individual agents (LlmAgent, tools, etc.)
└─────────────────┘
```

**Comparison with ADK Workflows**:

| Feature | ADK | LangGraph |
|---------|-----|-----------|
| Sequential workflows | ✅ SequentialAgent | ✅ State graphs |
| Parallel execution | ✅ ParallelAgent | ✅ Parallel nodes |
| Loops | ✅ LoopAgent | ✅ Cycles in graphs |
| State management | ✅ Session.state | ✅ Graph state |
| Multi-agent | ✅ AgentTool | ✅ Multiple actors |
| Persistence | ✅ Session resume | ✅ Checkpoints |

**When to Use LangGraph with ADK**:
- Complex state machines with many conditional branches
- Need for graph-based visualization of workflows
- Integration with LangChain ecosystem
- Advanced checkpointing and persistence requirements

### Integration Approaches

1. **LangGraph as Orchestrator**:
   - Use LangGraph to orchestrate multiple ADK agents
   - LangGraph handles workflow logic
   - ADK agents handle individual tasks

2. **Hybrid Approach**:
   - Use ADK for agent definitions and tools
   - Use LangGraph for complex workflow orchestration
   - Combine both in a single application

3. **CopilotKit + LangGraph + ADK**:
   - CopilotKit provides UI
   - LangGraph orchestrates workflows
   - ADK provides agent capabilities

### Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **CopilotKit + LangGraph**: https://www.copilotkit.ai/blog/easily-build-a-ui-for-your-ai-agent-in-minutes-langgraph-copilotkit
- **Starter Templates**:
  - https://github.com/CopilotKit/with-langgraph-fastapi
  - https://github.com/CopilotKit/with-langgraph-python

### Use Cases

- Complex multi-step workflows with conditional logic
- State machine-based agent behaviors
- Integration with LangChain ecosystem
- Workflows requiring graph visualization

## Langfuse - Observability

### What is Langfuse?

Langfuse is an open-source LLM observability platform. It provides tracing, analytics, and monitoring for AI applications, helping you debug and optimize your agents.

### Key Features

- **Tracing**: Detailed traces of agent execution
- **Analytics**: Performance metrics and insights
- **Evaluation**: Test and evaluate agent performance
- **Prompt Management**: Version and manage prompts
- **Cost Tracking**: Monitor API costs
- **OpenTelemetry Integration**: Standard observability protocol

### How It Fits with ADK

Langfuse provides **observability layer** for ADK agents:

```
┌─────────────────┐
│   ADK Agents    │  ← Your agents executing
└────────┬────────┘
         │ OpenTelemetry
         ▼
┌─────────────────┐
│   Langfuse      │  ← Traces, metrics, analytics
│  (Observability)│
└─────────────────┘
```

### Integration Steps

1. **Install Dependencies**:
   ```bash
   pip install langfuse google-adk openinference-instrumentation-google-adk
   ```

2. **Set Environment Variables**:
   ```bash
   export LANGFUSE_PUBLIC_KEY="your-public-key"
   export LANGFUSE_SECRET_KEY="your-secret-key"
   export LANGFUSE_HOST="https://cloud.langfuse.com"  # or self-hosted
   ```

3. **Instrument Your ADK Application**:
   ```python
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   from langfuse.opentelemetry import LangfuseSpanProcessor
   from opentelemetry import trace
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor

   # Set up OpenTelemetry
   trace.set_tracer_provider(TracerProvider())
   tracer_provider = trace.get_tracer_provider()

   # Instrument ADK
   GoogleADKInstrumentor().instrument()

   # Add Langfuse span processor
   tracer_provider.add_span_processor(
       BatchSpanProcessor(LangfuseSpanProcessor())
   )

   # Your ADK code
   from google import adk
   agent = adk.LlmAgent(...)
   ```

### What You Get

- **Detailed Traces**: See every agent call, tool invocation, and response
- **Performance Metrics**: Latency, token usage, costs
- **Error Tracking**: Identify and debug failures
- **Prompt Analytics**: Compare prompt versions
- **User Analytics**: Track user interactions

### Resources

- **Official Integration Guide**: https://langfuse.com/integrations/frameworks/google-adk
- **Langfuse Documentation**: https://langfuse.com/docs
- **OpenTelemetry**: https://opentelemetry.io/

### Use Cases

- Debugging agent behavior
- Monitoring production agents
- Optimizing agent performance
- Tracking costs and usage
- Evaluating agent quality

## Integration Architecture

### Complete Stack

```
┌─────────────────────────────────────────┐
│         CopilotKit (Frontend)           │
│  - React UI components                  │
│  - Chat interface                       │
│  - State management                     │
└──────────────┬──────────────────────────┘
               │ AG-UI Protocol
               ▼
┌─────────────────────────────────────────┐
│      LangGraph (Orchestration)          │
│  - Workflow orchestration               │
│  - State machines                       │
│  - Multi-agent coordination             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         ADK (Core Framework)            │
│  - LlmAgent, SequentialAgent, etc.       │
│  - Tools (FunctionTool, AgentTool)      │
│  - Sessions, State, Memory              │
└──────────────┬──────────────────────────┘
               │ OpenTelemetry
               ▼
┌─────────────────────────────────────────┐
│      Langfuse (Observability)           │
│  - Traces and analytics                 │
│  - Performance monitoring               │
│  - Cost tracking                        │
└─────────────────────────────────────────┘
```

### When to Use Each Component

| Component | Use When |
|-----------|----------|
| **CopilotKit** | Building React-based UIs, need standardized agent UI protocol |
| **LangGraph** | Complex workflows, state machines, LangChain ecosystem integration |
| **Langfuse** | Need observability, debugging, production monitoring |
| **ADK Only** | Simple agents, Google Cloud integration, Vertex AI deployment |

## Getting Started

### Option 1: CopilotKit + ADK (Recommended for UI)

```bash
# Create full-stack ADK project with CopilotKit
npx copilotkit@latest create -f adk

# Navigate to project
cd your-project

# Install dependencies
npm install
pip install -r requirements.txt

# Run
npm run dev  # Frontend
python main.py  # ADK backend
```

### Option 2: Langfuse + ADK (Recommended for Observability)

```bash
# Install dependencies
pip install langfuse google-adk openinference-instrumentation-google-adk

# Set up environment
export LANGFUSE_PUBLIC_KEY="..."
export LANGFUSE_SECRET_KEY="..."

# Instrument your ADK code (see Langfuse section above)
```

### Option 3: Full Stack (All Three)

1. Set up ADK backend
2. Add Langfuse instrumentation
3. Create CopilotKit frontend
4. Optionally add LangGraph for complex workflows

## Use Cases

### 1. Customer Service Agent

- **CopilotKit**: Chat interface for customers
- **ADK**: Core agent with customer service tools
- **Langfuse**: Monitor interactions and performance

### 2. Research Assistant

- **CopilotKit**: UI for research queries
- **LangGraph**: Orchestrate research workflow (search → analyze → summarize)
- **ADK**: Individual research agents
- **Langfuse**: Track research quality and sources

### 3. Data Analysis Agent

- **CopilotKit**: Interactive dashboard
- **ADK**: Data processing agents with BigQuery tools
- **Langfuse**: Monitor query performance and costs

### 4. Content Generation

- **CopilotKit**: Content editor with AI assistance
- **LangGraph**: Multi-step content workflow
- **ADK**: Writing and editing agents
- **Langfuse**: Track content quality metrics

## Comparison with ADK Native Features

### ADK Native Observability

ADK has built-in observability options:
- Cloud Trace integration
- Phoenix, Weave, Monocle support
- Custom callbacks

**When to use Langfuse vs ADK native**:
- **Langfuse**: Open-source, self-hostable, comprehensive analytics
- **ADK native**: Google Cloud integration, Vertex AI Agent Engine

### ADK Native Workflows

ADK has workflow agents:
- SequentialAgent
- ParallelAgent
- LoopAgent

**When to use LangGraph vs ADK workflows**:
- **LangGraph**: Complex state machines, graph visualization, LangChain ecosystem
- **ADK workflows**: Simpler workflows, Google Cloud deployment, native ADK integration

## Best Practices

1. **Start Simple**: Begin with ADK only, add other tools as needed
2. **Choose Wisely**: Not every project needs all three tools
3. **UI First**: If building a UI, start with CopilotKit
4. **Monitor Early**: Add Langfuse from the beginning for production
5. **Workflow Complexity**: Use LangGraph only for complex state machines

## Resources

### Official Documentation
- **CopilotKit**: https://docs.copilotkit.ai/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Langfuse**: https://langfuse.com/docs

### Integration Guides
- **CopilotKit + ADK**: https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui
- **Langfuse + ADK**: https://langfuse.com/integrations/frameworks/google-adk
- **CopilotKit + LangGraph**: https://www.copilotkit.ai/blog/easily-build-a-ui-for-your-ai-agent-in-minutes-langgraph-copilotkit

### GitHub Repositories
- **CopilotKit**: https://github.com/CopilotKit/CopilotKit
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **Langfuse**: https://github.com/langfuse/langfuse

## Next Steps

1. **Explore Samples**: Check out CopilotKit starter templates
2. **Try Integration**: Start with one tool (recommend CopilotKit for UI)
3. **Add Observability**: Integrate Langfuse for production monitoring
4. **Complex Workflows**: Consider LangGraph for advanced orchestration

---

**Note**: These tools are complementary to ADK, not replacements. ADK remains the core framework for building agents, while these tools enhance specific aspects of your agent application.

