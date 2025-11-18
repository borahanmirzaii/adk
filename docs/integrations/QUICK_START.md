# Quick Start: Integrating CopilotKit, LangGraph, and Langfuse with ADK

Quick setup guides for integrating each tool with your ADK project.

## CopilotKit + ADK

### 1. Create Project with CopilotKit CLI

```bash
npx copilotkit@latest create -f adk
cd your-project
```

### 2. Project Structure

```
your-project/
├── frontend/          # Next.js with CopilotKit
├── backend/          # ADK agent
└── package.json
```

### 3. Run

```bash
# Terminal 1: Frontend
cd frontend
npm run dev

# Terminal 2: Backend
cd backend
python main.py
```

### 4. Customize Your Agent

Edit `backend/main.py`:

```python
from google import adk

agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You are a helpful assistant."
)
```

## Langfuse + ADK

### 1. Install Dependencies

```bash
pip install langfuse google-adk openinference-instrumentation-google-adk
```

### 2. Set Environment Variables

```bash
export LANGFUSE_PUBLIC_KEY="pk-..."
export LANGFUSE_SECRET_KEY="sk-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"  # or self-hosted
```

### 3. Instrument Your Code

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

# Add Langfuse
tracer_provider.add_span_processor(
    BatchSpanProcessor(LangfuseSpanProcessor())
)

# Your ADK code
from google import adk

agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You are a helpful assistant."
)

response = agent.run("Hello!")
```

### 4. View Traces

Visit https://cloud.langfuse.com (or your self-hosted instance) to see traces.

## LangGraph + ADK

### 1. Install Dependencies

```bash
pip install langgraph langchain-google-genai google-adk
```

### 2. Create LangGraph Workflow

```python
from langgraph.graph import StateGraph, END
from google import adk

# Define your ADK agents
researcher = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Research topics."
)

writer = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="Write content."
)

# Create LangGraph workflow
def research_node(state):
    result = researcher.run(state["query"])
    return {"research": result}

def write_node(state):
    result = writer.run(f"Write about: {state['research']}")
    return {"content": result}

# Build graph
workflow = StateGraph(dict)
workflow.add_node("research", research_node)
workflow.add_node("write", write_node)
workflow.add_edge("research", "write")
workflow.add_edge("write", END)
app = workflow.compile()

# Run
result = app.invoke({"query": "Quantum computing"})
```

## Full Stack: All Three

### 1. Backend Setup (ADK + Langfuse)

```python
# backend/main.py
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from langfuse.opentelemetry import LangfuseSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from google import adk
from fastapi import FastAPI

# Instrumentation
trace.set_tracer_provider(TracerProvider())
GoogleADKInstrumentor().instrument()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(LangfuseSpanProcessor())
)

# ADK Agent
agent = adk.LlmAgent(
    model=adk.models.Gemini(),
    instructions="You are a helpful assistant."
)

# FastAPI server
app = FastAPI()

@app.post("/chat")
async def chat(message: str):
    response = agent.run(message)
    return {"response": response}
```

### 2. Frontend Setup (CopilotKit)

```typescript
// frontend/app/page.tsx
'use client'
import { CopilotKit } from '@copilotkit/react-core'
import { CopilotSidebar } from '@copilotkit/react-ui'

export default function Page() {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000">
      <CopilotSidebar>
        <div>Your app content</div>
      </CopilotSidebar>
    </CopilotKit>
  )
}
```

### 3. Run

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Next Steps

- Read full integration guide: `COPILOTKIT_LANGGRAPH_LANGFUSE.md`
- Explore CopilotKit examples: https://github.com/CopilotKit/CopilotKit
- Check Langfuse dashboard: https://cloud.langfuse.com
- Study LangGraph docs: https://langchain-ai.github.io/langgraph/

