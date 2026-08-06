## Project Steps

- Agent 
- Tool Calling
- Evaluation Pipeline
- Retrieval Evaluation
- LLM-as-a-Judge
- Separate KB Builder Service
- API Service
- Docker Compose 
- Streaming Responses
- Conversation Memory
- Human-in-the-loop
- Logging
- Monitoring
- Config Management
- Unit Test
- Integration Test


## Software Architecture

- Factory Pattern 
- Builder Pattern
- Strategy Pattern
- Repository Pattern
- Service Layer Pattern
- Dependency Injection
- Singleton (for Knowledge Base)
- State Machine (Agent)
- Observer Pattern (for Logging and Events)


## Steps

# Phase 0 — Architecture


# Phase 1 — Knowledge Base Service

    - knowledge_base_service/

        - obligation:

        - Embedding
        - Vector Store
        - Update KB
        - Rebuild KB
        - Versioning

    independent service

# Phase 2 — API Service

    - api_service/

        - FastAPI

        - API only


# Phase 3 — Agent Service 


    - agent/

        - graph.py

        - nodes.py

        - state.py

        - tools.py

        - prompts.py

        - evaluator.py


# Phase 4 — LangGraph

    - StateGraph

    - Conditional Edge

    - Loop

    - Retry

    - Human Approval

    - Memory

    - Checkpoint

    - Interrupt


# Phase 5 — Tool Calling

    - Agent will have various tools.

        - Search FAQ
        - Check Order
        - Create Ticket
        - CRM Lookup
        - Escalate
        - Calculator
        - Weather (Demo)
        - Email Sender


# Phase 6 — Evaluation 

    - evaluation/

        - faithfulness.py

        - answer_relevancy.py

        - retrieval_precision.py

        - retrieval_recall.py

        - latency.py

        - cost.py


# Phase 7 — Observability

    - Logging
    - Tracing
    - Metrics


# Phase 8 — Deployment

    - Docker
    - Docker Compose
    - Nginx
    - Redis
    - Postgres


# Phase 9 — CI/CD

    - GitHub Actions
    - pytest
    - lint
    - format


## FarmeWorks

- Agent Framework: LangGraph
- LLM Abstraction: LangChain
- Evaluation: LangSmith 
- Embedding: Sentence Transformers
- Vector DB: first FAISS then Qdrant
- Backend: FastAPI
- Database: PostgreSQL
- Containerization: Docker + Docker Compose
- Testing: pytest
- Formatting: Ruff + Black
- Type Checking: mypy