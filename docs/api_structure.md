# API Structure

The FastAPI application is located in `app/`. It exposes the agent workflow and the human-review endpoints.

## Structure

```text
app/
├── main.py
├── admincli.py
├── database.py
├── models.py
├── schemas.py
└── routes/
    └── agent.py
```

## Responsibilities

- **main.py:** Creates the FastAPI application, initializes one `AgentService` during lifespan, and registers routes.
- **database.py:** Creates the SQLAlchemy engine/session and provides the database dependency.
- **models.py:** Defines database tables, including pending human reviews.
- **schemas.py:** Defines request and response models with Pydantic.
- **routes/agent.py:** Exposes agent requests and human-review operations.
- **admincli.py:** A small terminal-based operator client that polls for pending reviews and submits decisions.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/agent/ask` | Submit a user query to the agent. |
| GET | `/agent/reviews/pending` | List reviews waiting for an operator. |
| POST | `/agent/reviews/{review_id}/decision` | Submit an operator decision and resume the workflow. |

The API keeps the `AgentService` instance in application state so the graph and its persistence resources are shared during the process lifetime.

The paused graph state is stored by the LangGraph checkpointer. The `pending_reviews` table stores the operator-facing request and decision history; it is not a replacement for the graph checkpoint.
