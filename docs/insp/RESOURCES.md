# ADK Agent Development Resources

This folder contains inspiration and reference materials for learning and building ADK (Agent Development Kit) agents.

## 📚 Main Resources

### Official Documentation
- **ADK Documentation**: https://google.github.io/adk-docs/
- **ADK Tutorials**: https://google.github.io/adk-docs/tutorials/
- **ADK Samples Repository**: https://github.com/google/adk-samples (cloned in `adk-samples/`)

### Articles & Blog Posts
- **Medium - From Zero to Multi-Agents**: https://medium.com/@sokratis.kartakis/from-zero-to-multi-agents-a-beginners-guide-to-google-agent-development-kit-adk-b56e9b5f7861
  - Saved as: `medium-adk-guide.html`
- **Google Cloud Blog - Agent State and Memory**: https://cloud.google.com/blog/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk
  - Saved as: `blog-state-memory.html`

## 🎯 Key Concepts

### Agent State and Memory
- **Short-term memory**: Session-based state management
- **Long-term memory**: Memory Bank integration with Vertex AI Agent Engine
- State storage options: SQL databases, Vertex AI Agent Engine, Cloud Run

### ADK Components
- **Models**: Gemini 2.5 Flash and other models
- **Function Tools**: Allow agents to perform actions
- **Callbacks**: For memory generation and state management
- **Session Management**: For maintaining context within conversations

## 📁 Repository Structure

```
docs/
├── insp/                    # Inspiration materials
│   ├── adk-samples/         # Cloned ADK samples repository
│   ├── adk-docs/            # Cloned ADK documentation repository
│   ├── medium-adk-guide.html
│   ├── blog-state-memory.html
│   └── RESOURCES.md         # This file
├── tutorials/               # Tutorial materials
├── cookbooks/              # Code recipes and patterns
└── design-patterns/        # Design pattern examples
```

## 🚀 Getting Started

1. Explore the `adk-samples/` directory for working examples
2. Review the ADK documentation in `adk-docs/`
3. Study the articles in this folder
4. Check out tutorials in `../tutorials/`
5. Review design patterns in `../design-patterns/`

## 🔗 Additional Resources

- **ADK Python**: https://github.com/google/adk-python
- **ADK Go**: https://github.com/google/adk-go
- **ADK Java**: https://github.com/google/adk-java
- **Vertex AI Agent Engine**: For production deployment
- **Cloud Run**: For serverless agent deployment

## 📝 Notes

- ADK supports Python, Go, and Java
- Agents can be deployed to Cloud Run or Vertex AI Agent Engine
- Memory Bank can be used independently of Agent Engine Runtime
- Sample agents cover various use cases: customer service, RAG, multi-agent workflows, etc.

