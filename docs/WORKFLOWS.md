# Workflows Documentation

LangGraph workflows for multi-step agent processes.

## Overview

Workflows orchestrate complex multi-step processes using LangGraph.

## Code Review Workflow

### Purpose

Multi-step code review process with state persistence.

### Steps

1. **Static Analysis** - Analyze code structure
2. **Security Scan** - Check for vulnerabilities
3. **Best Practices** - Check coding standards
4. **Generate Report** - Create review report

### State

```python
class ReviewState(TypedDict):
    code: str
    static_analysis_result: list
    security_scan_result: list
    best_practices_result: list
    final_report: str
    errors: list
```

### Usage

```python
from app.workflows.review_workflow import review_workflow

result = review_workflow.invoke({
    "code": "...",
    "static_analysis_result": [],
    "security_scan_result": [],
    "best_practices_result": [],
    "final_report": "",
    "errors": []
})
```

## Deployment Workflow

### Purpose

Orchestrate deployment processes across multiple services.

### Steps

1. **Pre-flight Checks** - Run tests and checks
2. **Build** - Build services
3. **Deploy** - Deploy to environment
4. **Verify** - Verify deployment
5. **Monitor** - Monitor for issues

### State

```python
class DeploymentState(TypedDict):
    deployment_id: str
    service_name: str
    version: str
    status: str
    workflow_state: dict
    errors: list
```

## Creating New Workflows

Use the template:

```bash
just new-workflow my_workflow_name
```

This creates:
- `backend/app/workflows/my_workflow_name.py`

### Example

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class MyWorkflowState(TypedDict):
    input: str
    step1_result: str
    step2_result: str
    final_result: str

def step1_node(state: MyWorkflowState):
    # Process step 1
    return {"step1_result": "..."}

def step2_node(state: MyWorkflowState):
    # Process step 2
    return {"step2_result": "..."}

workflow = StateGraph(MyWorkflowState)
workflow.add_node("step1", step1_node)
workflow.add_node("step2", step2_node)
workflow.set_entry_point("step1")
workflow.add_edge("step1", "step2")
workflow.add_edge("step2", END)

my_workflow = workflow.compile()
```

## State Persistence

Workflow state is persisted in Supabase:

- `code_reviews` table - Code review workflow state
- `deployments` table - Deployment workflow state

## Visualization

Workflows can be visualized using LangGraph's visualization tools.

## Best Practices

1. **Define clear state** - Use TypedDict for type safety
2. **Handle errors** - Add error handling in each node
3. **Persist state** - Save state to Supabase
4. **Test workflows** - Write integration tests
5. **Document steps** - Document each workflow step

