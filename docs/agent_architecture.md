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


3.11.3
Human Review Node
    ↓
nodes.py / graph integration


3.11.5
State Integration
    ↓
state.py

3.11.6
Graph Routing
    ↓
graph.py

3.11.7
Interrupt / Resume
    ↓
thread_id + persistence


knowledge_base/
│
├── embedding/
├── vector_store/
├── retriever/
│       ↓
│   retrieval_score
│
└── kb_service.py
        ↓
     documents
     + scores


evaluation/
│
├── retrieval/
├── response/
└── confidence/
        ↓
   evaluation results
        ↓
   confidence_score


agent/
│
└── graph/
        ↓
   Retrieval Gate
        ↓
   Human Policy
        ↓
   Human Review


نابراین پیشنهاد من این است که برای Sprint 3.11 همین‌جا HITL infrastructure را ببندیم، ولی اتصال واقعی:

RAG
 ↓
Retrieval Evaluation
 ↓
LLM
 ↓
Faithfulness
 ↓
Confidence
 ↓
Human Policy

را در Sprint مربوط به RAG/Agent integration کامل کنیم


## Sprint 3.12 — Guardrails

    Input Guardrail
    قبل از Agent

    Output Guardrail
    بعد از Agent



of


## Sprint 3.14 — Agent Evaluation
هم تست‌های deterministic برای orchestration خواهیم داشت و هم evaluationهای model-based؛ ابزارهای Agent مدرن هم برای workflowهای agentic ابزارهای testing/evaluation ارائه می‌کنند



## Sprint 3.15 — Production Agent Service

خب تست ها بدون مشکل اجرا شدن. اما اینجا یک چیزی برام سوال شد.
همونطور که میبینی من یه متد resume هم دارم. اما این متد کی اجرا میشه؟
اصلا این وقفه برای human  کجا میره؟
بعد اون انسان چجوری باید سیستم رو به ادامه یعنی اجرای resume برسونه؟

نظر خودم اینکه در مرحله آخر یعنی بعد از همین evaluation که باید این سیستم رو با اون app ساده fastapi که دارم متصل کنم تا ورودی کاربر از اونجا وارد بشه و بعد یه صفحه admin طور داشته باشم که در صورت وقفه یه پیام به اونجا بره و اونجا دوتا تصمیم گرفته بشه یکی اینکه چرخه agent کلا متوقف بشه و ادمین خودش کار رو انجام بده، یا اینکه ادامه و اجرای متد resume.


نکته‌ی مهم اینه که interrupt خودش به ادمین پیام نمی‌فرستد و صفحه‌ی مدیریتی هم ایجاد نمی‌کند. کارش این است که اجرای گراف را متوقف کند و اطلاعات لازم برای تصمیم‌گیری را در وضعیت ذخیره‌شده‌ی اجرای LangGraph نگه دارد. برنامه‌ی بیرونی تو باید این وضعیت را تشخیص دهد، درخواست بازبینی را به ادمین نشان دهد و بعد تصمیم او را به resume() برساند.
جریان کامل کار
۱. کاربر درخواست می‌دهد

مثلاً: «سفارش ۱۲۳ من را لغو کن.»

درخواست از طریق FastAPI وارد AgentService.run() می‌شود.


۲. Agent تشخیص می‌دهد که تأیید انسانی لازم است

مثلاً cancel_order حساس است؛ گراف به human_review می‌رسد و interrupt() اجرا می‌شود.


۳. FastAPI نتیجه‌ی وقفه را دریافت می‌کند

وضعیت اجرا و جزئیات درخواست بازبینی باید برای پیگیری ذخیره شوند؛ مثلاً با شناسه‌ی اجرا و وضعیت pending_review.


۴. ادمین در صفحه‌ی مدیریتی تصمیم می‌گیرد

درخواست حساس و اطلاعات لازم را می‌بیند و یکی از گزینه‌ها را انتخاب می‌کند.


ادامه‌ی Agent

FastAPI تصمیم را به resume() می‌دهد؛ گراف از checkpoint ادامه می‌یابد.


توقف یا واگذاری به انسان

Agent ادامه نمی‌دهد؛ درخواست به‌عنوان ردشده یا واگذارشده ثبت می‌شود و ادمین در صورت نیاز کار را دستی انجام می‌دهد.




پس resume() دقیقاً کِی اجرا می‌شود؟
وقتی ادمین در صفحه‌ی مدیریتی تصمیمی بگیرد و درخواستش را به FastAPI بفرستد. خود LangGraph به‌صورت خودکار resume() را اجرا نمی‌کند.

مثلاً ادمین تأیید می‌کند عملیات لغو سفارش ادامه پیدا کند. FastAPI تصمیم را به متد resume() می‌دهد و این متد باید گراف را با همان thread_id قبلی و Command(resume=decision) ادامه دهد. در نتیجه LangGraph از checkpoint اجرای متوقف‌شده ادامه می‌دهد؛ نه اینکه کل درخواست را از ابتدا اجرا کند.

در طراحی فعلی تو، تصمیم باید با قرارداد HumanDecision سازگار باشد. طبق کدی که قبلاً بررسی کردیم، تصمیم‌ها شامل approve، reject و escalate هستند.
درخواست وقفه به کجا می‌رود؟
فعلاً هیچ صفحه‌ای آن را دریافت نمی‌کند. اطلاعات درخواست بازبینی در خروجی اجرای گراف و checkpoint آن در دسترس است. برای رساندن آن به ادمین، باید یک لایه‌ی بیرونی بسازی:
- FastAPI نتیجه‌ی اجرای run() را می‌گیرد.
- اگر وضعیت human_review بود، درخواست بازبینی را با شناسه‌ی اجرا در یک محل پایدار ثبت می‌کند.
- صفحه‌ی مدیریتی درخواست‌های منتظر بررسی را دریافت و نمایش می‌دهد.
- با انتخاب ادمین، صفحه تصمیم را به یک endpoint در FastAPI می‌فرستد.
- FastAPI تصمیم را اعتبارسنجی می‌کند، resume() را اجرا می‌کند و نتیجه‌ی جدید را برمی‌گرداند.
برای نسخه‌ی اولیه، ذخیره‌ی وضعیت درخواست‌ها در دیتابیس و یک endpoint برای دریافت درخواست‌های منتظر بررسی کافی است. بعداً می‌توانی WebSocket یا اعلان بلادرنگ اضافه کنی.
درباره‌ی دو انتخابی که پیشنهاد دادی
ایده‌ات درست است، اما بهتر است تصمیم‌ها را دقیق‌تر تعریف کنی:
تصمیم ادمین	رفتار سیستم
تأیید	اجرای Agent ادامه پیدا می‌کند و عملیات مجاز اجرا می‌شود.
رد	Agent عملیات را اجرا نمی‌کند و درخواست با وضعیت ردشده خاتمه می‌یابد.
واگذاری به انسان	Agent متوقف می‌ماند و ادمین یا اپراتور کار را دستی انجام می‌دهد.
در کد فعلی، reject و escalate هر دو به مسیر پایان می‌روند؛ پس برای واگذاری دستی، باید وضعیت آن را بیرون از گراف هم ثبت کنی تا سیستم بداند کار هنوز نیاز به رسیدگی انسانی دارد.

یک نکته‌ی امنیتی مهم: برای عملیات حساسی مثل لغو سفارش، صرفاً نمایش درخواست در پنل کافی نیست. باید مطمئن شوی ابزار cancel_order پیش از تأیید اجرا نمی‌شود و درخواست resume هم فقط توسط ادمین مجاز قابل ارسال است.

پیشنهاد من این است که فعلاً سراغ طراحی پنل نرویم. ابتدا قرارداد run() و resume() را روشن کنیم: چه چیزی به API برمی‌گردد، شناسه‌ی اجرای متوقف‌شده کجا نگهداری می‌شود و پاسخ ادمین با چه فرمتی به گراف می‌رسد. بعد اتصال FastAPI به این دو متد بسیار ساده‌تر خواهد بود.


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



## Architecture

router
  │
  ├── direct ──→ LLM ──→ save_memory ──→ END
  │
  ├── rag ──→ RAG ──→ LLM ──→ human_policy
  │                                      │
  │                                      ├── human_review ──→ END
  │                                      │
  │                                      └── save_memory ──→ END
  │
  └── tool ──→ tool_call ──→ tool ──→ LLM ──→ human_policy
  