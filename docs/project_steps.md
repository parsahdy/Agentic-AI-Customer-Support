# Project Roadmap

This file tracks the main implementation areas. It is a high-level guide, not a promise that every planned item is already implemented.

## Implemented Foundations

- LangGraph agent state, nodes, routing, and workflow.
- Direct, RAG, and tool routes.
- Tool registry and execution with retry handling.
- Conversation memory and graph checkpointing.
- Retrieval, faithfulness, and confidence evaluation.
- Human-review policies and interrupt/resume flow.
- Input and output guardrails.
- FastAPI endpoints for agent requests and human decisions.
- PostgreSQL integration and Docker Compose setup.
- Scenario-based evaluation runner and tests.

## Next Development Areas

- Improve automated evaluation metrics and reporting.
- Expand API validation, authentication, and operational safeguards.
- Add a web-based operator interface beyond the current terminal client.
- Improve structured logging, tracing, and monitoring.
- Strengthen automated tests for failure paths and end-to-end API behavior.
- Review deployment configuration, secrets handling, and production readiness.

## Development Principle

Keep components focused and avoid adding abstractions or services until there is a clear requirement. Update this roadmap when implementation status changes.
