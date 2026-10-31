# Agent Architecture

The agent is implemented with **LangGraph**. `AgentService` prepares dependencies, validates input and output, and exposes `run()` and `resume()`.

## Workflow

```text
START
  |
Load Memory
  |
Router
  |---- direct --------------------> LLM
  |                                  |
  |                                Save Memory
  |
  |---- rag ----> Retrieve ----> LLM ----> Evaluation
  |                                          |
  |                                      Human Policy
  |                                          |
  |                                      Human Review?
  |                                          |
  |                                      Save Memory
  |
  |---- tool ---> Tool Call ---> Human Policy
                                  |
                         +--------+--------+
                         |                 |
                    Human Review?       Tool
                         |                 |
                      Approve             LLM
                         |                 |
                        Tool          Save Memory
                         |
                        LLM
                         |
                    Save Memory
                         |
                        END
```

## Main Components

- **AgentState:** Shared state passed between graph nodes.
- **Router:** Selects the `direct`, `rag`, or `tool` route.
- **Nodes:** Handle LLM calls, retrieval, tool calls, evaluation, memory, and human review.
- **ToolRegistry:** Provides the tools available to the agent.
- **ToolExecutor:** Executes selected tools and applies retry handling.
- **MemoryService:** Manages conversation memory and the graph checkpointer/store.
- **Policies:** Decide whether low-confidence answers or sensitive operations need human review.
- **Guardrails:** Validate user input and the final response.
- **Error handling:** Classifies failures and applies retry, human-review, or fail actions.

## Human Review

Sensitive tool operations and low-confidence RAG responses can pause the graph with LangGraph `interrupt()`. The graph checkpoint preserves the paused execution.

The API stores a pending-review record for operators. After an operator submits `approve`, `reject`, or `escalate`, the API calls `AgentService.resume()` with the same user/session thread.

An approval allows the graph to continue to the relevant next node. A rejection or escalation ends the automated path without executing the pending tool.

## Important Boundaries

- The router chooses a route; it does not execute business operations.
- Tool selection and tool execution are separate graph steps.
- Human review is an orchestration pause, not a notification or admin interface by itself.
- The API and operator interface are external to the LangGraph workflow.
