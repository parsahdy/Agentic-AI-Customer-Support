                    Agent Service
                          │
                          ▼
                    Agent Graph
                   /     |      \
                  /      |       \
             Router    Nodes    State
                │        │
                │        ├── LLM
                │        ├── Retriever
                │        └── Tools
                │
                ▼
          Routing Strategy
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
      RAG      Tool    Direct




## Sprint 3.1 — Agent Foundation

    Impletaion
    -AgentState
    -Graph
    -LLM node
    -basic agent service
    -config
    -model abstraction


## Sprint 3.2 — State Design

    AgentState

    ├── messages
    ├── user_id
    ├── session_id
    ├── query
    ├── retrieved_documents
    ├── tool_calls
    ├── tool_results
    ├── final_answer
    ├── error
    └── metadata

    learning
    -TypedDict
    -state schema
    -reducers
    -message state
    -immutable vs mutable state
    -state lifecycle


## Sprint 3.3 — Nodes & Edges
Graph را از یک Node ساده به workflow تبدیل می‌کنیم.

    Learning
    -Node design
    -Single Responsibility برای Nodeها
    -Edge
    -START
    -END
    -graph compilation
    -separation between business logic and orchestration


## Sprint 3.4 — Conditional Routing

    Learning
    -Conditional Edge
    -Router
    -Intent classification
    -routing strategy


## Sprint 3.5 — Tool Calling
Agent را به Tool مجهز می‌کنیم.

    Agent
    │
    ├── search_knowledge_base()
    ├── get_order()
    ├── cancel_order()
    ├── create_ticket()
    └── get_customer_info()

    Learning:
    -Function Tool
    -Tool schema
    -structured arguments
    -tool result
    -tool errors
    -tool selection
    -tool execution


## Sprint 3.6 — Agent Loop

    User
    ↓
    LLM
    ↓
    Tool Call?
    ├── No → Final Answer
    │
    └── Yes
        ↓
        Tool
        ↓
    Tool Result
        ↓
        LLM
        ↓
    Tool Call?
        ↓


## Sprint 3.7 — RAG Tool Integration
Agent به Knowledge Base وصل می‌شود

    Agent
    │
    ├── KnowledgeBaseSearch
    │       ↓
    │    Retriever
    │       ↓
    │    Vector Store
    │
    ├── Order Tool
    │
    └── Ticket Tool


RAG تبدیل می‌شود به Tool برای Agent


## Sprint 3.8 — Memory
اینجا Agent را conversational می‌کنیم.

Short-term memory
Long-term memory


## Sprint 3.9 — Persistence & Checkpointing


## Sprint 3.10 — Retry & Error Handling

    Tool
    ↓
    Error
    ↓
    Retry?
    ├── Yes → Tool
    └── No → Recovery

    -retry policy
    -exponential backoff
    -max retries
    -transient vs permanent errors
    -fallback
    -graceful degradation
    -error state


## Sprint 3.11 — Human-in-the-Loop


## Sprint 3.12 — Guardrails

    Input Guardrail
    قبل از Agent

    Output Guardrail
    بعد از Agent


## Sprint 3.13 — Agent Routing & Specialized Agents

                     Triage Agent
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Support Agent  Order Agent   Billing Agent

    Learning
    -agent routing
    -sub-agents
    -delegation
    -handoff
    -supervisor pattern


## Sprint 3.14 — Agent Observability
ینجا باید بفهمیم Agent دقیقاً چه کاری انجام داده.

Observability را صرفاً با print() انجام نمی‌دهیم. ابزارهای مدرن Agent tracing می‌توانند model generation، tool calls، guardrails و lifecycle را trace کنند


## Sprint 3.15 — Agent Evaluation
هم تست‌های deterministic برای orchestration خواهیم داشت و هم evaluationهای model-based؛ ابزارهای Agent مدرن هم برای workflowهای agentic ابزارهای testing/evaluation ارائه می‌کنند


## Sprint 3.16 — Agent Security

    -Prompt Injection
    -Tool Injection
    -Data Leakage
    -Privilege Escalation
    -Unsafe Tool Calls
    -Sensitive Information


## Sprint 3.17 — Structured Output


## Sprint 3.18 — Streaming
و API بتواند eventهای Agent را stream کند.


## Sprint 3.19 — Production Agent Service

    FastAPI
    │
    ▼
    Agent Service
    │
    ▼
    LangGraph
    │
    ├── State
    ├── Router
    ├── RAG Tool
    ├── Business Tools
    ├── Memory
    ├── Guardrails
    ├── HITL
    ├── Retry
    └── Observability

