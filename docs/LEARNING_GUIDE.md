# ADK Agent Development Learning Guide

This guide will help you learn, create, and build agents using Google's Agent Development Kit (ADK).

## 📚 Learning Path

### Phase 1: Foundations (Week 1-2)

1. **Understand ADK Core Concepts**
   - Read: `../insp/adk-docs/docs/get-started/about.md`
   - Review: `../insp/adk-docs/docs/agents/index.md`
   - Key concepts:
     - LlmAgent: Basic agent with LLM
     - Tools: Function tools, Agent tools, MCP tools
     - Context: Session state and memory
     - Models: Gemini, Vertex AI, LiteLLM

2. **Installation & Setup**
   - Follow: `../insp/adk-docs/docs/get-started/installation.md`
   - Set up Python ADK with `uv`
   - Configure Google Cloud credentials
   - Test with a simple agent

3. **First Agent**
   - Complete: `../insp/adk-docs/docs/get-started/quickstart.md`
   - Build a simple conversational agent
   - Add a function tool
   - Test locally with `adk run` or `adk web`

### Phase 2: Building Blocks (Week 3-4)

1. **Tools Deep Dive**
   - Study: `../insp/adk-docs/docs/tools-custom/index.md`
   - Types of tools:
     - Function tools
     - Agent tools (multi-agent)
     - MCP tools
     - OpenAPI tools
   - Practice: Build custom tools for your use case

2. **State & Memory**
   - Read: `../insp/insp/blog-state-memory.html`
   - Study: `../insp/adk-docs/docs/sessions/index.md`
   - Implement:
     - Session state management
     - Short-term memory
     - Long-term memory with Memory Bank

3. **Workflow Agents**
   - Learn: `../insp/adk-docs/docs/agents/workflow-agents/index.md`
   - Types:
     - SequentialAgent: Linear workflows
     - ParallelAgent: Concurrent execution
     - LoopAgent: Iterative processes
   - Practice: Build a multi-step workflow

### Phase 3: Advanced Patterns (Week 5-6)

1. **Multi-Agent Systems**
   - Study: `../insp/adk-docs/docs/agents/multi-agents.md`
   - Review sample agents:
     - `../insp/adk-samples/python/agents/llm-auditor/`
     - `../insp/adk-samples/python/agents/customer-service/`
   - Patterns:
     - Agent hierarchy
     - Inter-agent communication
     - Distributed agents (A2A)

2. **Custom Agents**
   - Learn: `../insp/adk-docs/docs/agents/custom-agents.md`
   - Build: `BaseAgent` implementations
   - Advanced: Custom streaming, custom callbacks

3. **Deployment**
   - Study: `../insp/adk-docs/docs/deploy/index.md`
   - Options:
     - Cloud Run (serverless)
     - Vertex AI Agent Engine
     - GKE (Kubernetes)
   - Practice: Deploy a simple agent

### Phase 4: Production (Week 7-8)

1. **Observability**
   - Study: `../insp/adk-docs/docs/observability/index.md`
   - Tools: Cloud Trace, Phoenix, Weave, etc.
   - Implement logging and monitoring

2. **Evaluation**
   - Learn: `../insp/adk-docs/docs/evaluate/index.md`
   - Build test suites
   - Measure agent performance

3. **Safety & Security**
   - Review: `../insp/adk-docs/docs/safety/index.md`
   - Implement guardrails
   - Test safety plugins

## 🎯 Recommended Sample Agents to Study

### Beginner
1. **LLM Auditor** (`../insp/adk-samples/python/agents/llm-auditor/`)
   - Multi-agent pattern
   - Simple workflow
   - Good introduction

2. **Personalized Shopping** (`../insp/adk-samples/python/agents/personalized-shopping/`)
   - Single agent
   - Conversational
   - E-commerce use case

### Intermediate
3. **Customer Service** (`../insp/adk-samples/python/agents/customer-service/`)
   - Advanced multi-agent
   - Real-time streaming
   - External system integration

4. **RAG Agent** (`../insp/adk-samples/python/agents/RAG/`)
   - Retrieval-Augmented Generation
   - Document processing
   - Citation handling

### Advanced
5. **Data Science Agent** (`../insp/adk-samples/python/agents/data-science/`)
   - Complex multi-agent system
   - Database integration
   - NL2SQL capabilities

6. **Travel Concierge** (`../insp/adk-samples/python/agents/travel-concierge/`)
   - Advanced patterns
   - Dynamic instructions
   - Updatable context

## 📖 Key Resources

### Documentation
- **Main Docs**: `../insp/adk-docs/docs/`
- **API Reference**: `../insp/adk-docs/docs/api-reference/`
- **Tutorials**: `../insp/adk-docs/docs/tutorials/`

### Samples
- **All Samples**: `../insp/adk-samples/python/agents/`
- **Sample README**: `../insp/adk-samples/python/agents/README.md`

### Articles
- **Medium Guide**: `../insp/medium-adk-guide.html`
- **State & Memory Blog**: `../insp/blog-state-memory.html`

## 🛠️ Development Workflow

1. **Local Development**
   ```bash
   cd your-agent/
   adk run .  # CLI mode
   # or
   adk web    # Web UI
   ```

2. **Testing**
   ```bash
   pytest tests/
   python eval/test_eval.py
   ```

3. **Deployment**
   ```bash
   python deployment/deploy.py
   ```

## 💡 Tips

- Start simple: Build a single-agent with one tool
- Study existing samples: Don't reinvent the wheel
- Use ADK Dev UI: Great for debugging (`adk web`)
- Test incrementally: Add features one at a time
- Read agent READMEs: Each sample has detailed docs
- Join community: Check `../insp/adk-docs/docs/community.md`

## 🎓 Next Steps

After completing this guide:
1. Build your own agent for a specific use case
2. Contribute to adk-samples
3. Share your learnings with the community
4. Explore advanced topics:
   - A2A protocol
   - Custom streaming
   - Advanced grounding
   - Plugin development

