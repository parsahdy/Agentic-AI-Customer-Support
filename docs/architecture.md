# System Architecture

The project is organized into a small set of cooperating components.

| Component | Responsibility |
|---|---|
| `agent/` | LangGraph workflow, routing, tools, memory, guardrails, and error handling. |
| `knowledge_base/` | Document preparation, chunking, embeddings, vector storage, retrieval, and metadata. |
| `evaluation/` | Retrieval/response evaluation and scenario-based agent evaluation. |
| `app/` | FastAPI endpoints, SQLAlchemy persistence, and operator CLI. |
| `data/` | Knowledge-base source and generated data. |
| `tests/` | Unit and integration tests for project components. |
| `docs/` | Architecture and development documentation. |

## Main Request Flow

1. FastAPI receives a query and passes it to `AgentService`.
2. Input guardrails validate the query.
3. LangGraph loads memory and routes the request.
4. The selected path uses the LLM directly, retrieves knowledge, or selects business tools.
5. Evaluation and human-review policies are applied where required.
6. The workflow saves memory and returns a structured result.
7. Output guardrails validate the final answer.

PostgreSQL is used by the application and can also be used for agent memory/checkpoint persistence. Docker Compose defines the application and database services.
