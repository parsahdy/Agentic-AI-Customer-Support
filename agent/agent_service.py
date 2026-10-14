import os

from dotenv import load_dotenv
from langgraph.types import Command
from openai import AsyncOpenAI

from . import config
from .graph import build_graph
from .memory.memory_service import MemoryService
from .tools.registry import ToolRegistry
from .errors import RetryPolicy, ErrorPolicy
from .guardrails import (
    InputGuardrail,
    OutputGuardrail,
    RequiredInputRule,
    RequiredOutputRule,
    MaxInputLengthRule,
    MaxOutputLengthRule,
    ControlCharacterRule,
    SensitiveDataRule,
)

from knowledge_base.kb_service import KnowledgeBaseService
from evaluation import (
RetrievalEvaluator,
FaithfulnessEvaluator,
ConfidenceEvaluator,
)


load_dotenv()


class InputGuardrailError(ValueError):
    """
    Raised when a user query fails input validation.
    """

    def __init__(self, result):
        self.result = result
        messages = "; ".join(
            violation.message
            for violation in result.violations
        )
        
        super().__init__(messages or "Input validation failed.")


class OutputGuardrailError(ValueError):
    """
    Raised when the agent output fails validation.
    """

    def __init__(self, result):
        self.result = result
        messages = "; ".join(
            violation.message
            for violation in result.violations
        )

        super().__init__(messages or "Output validation failed.")


class AgentService:

    def __init__(
        self,
        memory: MemoryService | None = None,
        registry: ToolRegistry | None = None,
        kb: KnowledgeBaseService | None = None,
        retrieval_evaluator: RetrievalEvaluator | None = None,
        faithfulness_evaluator: FaithfulnessEvaluator | None = None,
        confidence_evaluator: ConfidenceEvaluator | None = None,
        retry_policy: RetryPolicy | None = None,
        error_policy: ErrorPolicy | None = None,
        input_guardrail: InputGuardrail | None = None,
        output_guardrail: OutputGuardrail | None = None,
    ):

        self.memory = (
            memory
            if memory is not None
            else MemoryService()
        )

        self.registry = (
            registry
            if registry is not None
            else ToolRegistry()
        )

        #self.kb = (
        #    kb
        #    if kb is not None
        #    else KnowledgeBaseService()
        #)

        self.kb = kb

        self.retrieval_evaluator = (
            retrieval_evaluator
            if retrieval_evaluator is not None
            else RetrievalEvaluator()
        )

        self.faithfulness_evaluator = (
            faithfulness_evaluator
            if faithfulness_evaluator is not None
            else FaithfulnessEvaluator(
                client=AsyncOpenAI(
                    api_key=os.getenv("GROQ_API_KEY"),
                    base_url=config.BASE_URL,
                ),
                model=config.LLM_MODEL,
            )
        )

        self.confidence_evaluator = (
            confidence_evaluator
            if confidence_evaluator is not None
            else ConfidenceEvaluator()
        )

        self.retry_policy = (
            retry_policy
            if retry_policy is not None
            else RetryPolicy()
        )

        self.error_policy = (
            error_policy
            if error_policy is not None
            else ErrorPolicy()
        )

        self.input_guardrail = (
            input_guardrail
            if input_guardrail is not None
            else InputGuardrail(
                rules=[
                    RequiredInputRule(),
                    MaxInputLengthRule(),
                    ControlCharacterRule(),
                ]
            )
        )

        self.output_guardrail = (
            output_guardrail
            if output_guardrail is not None
            else OutputGuardrail(
                rules=[
                    RequiredOutputRule(),
                    MaxOutputLengthRule(),
                    SensitiveDataRule(),
                ]
            )
        )

        self.graph = build_graph(
            memory=self.memory,
            registry=self.registry,
            kb=self.kb,
            retrieval_evaluator=self.retrieval_evaluator,
            faithfulness_evaluator=self.faithfulness_evaluator,
            confidence_evaluator=self.confidence_evaluator,
            retry_policy=self.retry_policy,
            error_policy=self.error_policy,
        )


    def run(
        self,
        query: str,
        user_id: str,
        session_id: str,
    ):
        """
        Validate the input, run the agent, and validate its output.
        """

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id is required.")
        
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id is required.")
        
        input_result = self.input_guardrail.validate(query)

        if input_result.decision.value == "error":
            raise RuntimeError(
                "Input validation could not be completed."
            )

        if not input_result.allowed:
            raise InputGuardrailError(input_result)

        initial_state = {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ],
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "current_node": "",
            "retrieved_documents": [],
            "retrieval_score": 0.0,
            "top1_score": 0.0,
            "mean_topk_score": 0.0,
            "faithfulness_score": 0.0,
            "confidence_score": 0.0,
            "tool_calls": [],
            "tool_results": [],
            "iteration": 0,
            "max_iteration": 5,
            "final_answer": "",
            "error": None,
            "error_policy": "",
            "metadata": {},
            "route": None,
            "memory_context": [],
            "human_review_required": False,
            "human_review_request": {},
            "human_decision": {},
        }

        thread_id = f"{user_id}:{session_id}"

        graph_config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        output = self.graph.invoke(
            initial_state,
            config=config,
        )

        if not isinstance(output, dict):
            raise OutputGuardrailError(
                self.output_guardrail.validate(output)
            )

        output_result = self.output_guardrail.validate(
            output.get("final_answer")
        )

        if output_result.decision.value == "error":
            raise RuntimeError(
                "Output validation could not be completed."
            )

        if not output_result.allowed:
            raise OutputGuardrailError(output_result)

        return output


    def resume(
        self,
        decision: dict,
        user_id: str,
        session_id: str,
    ):
        """
        Resume a paused workflow with a human decision.
        """

        if decision is None:
            raise ValueError(
                "Decision is required for resuming agent workflow."
            )

        if not isinstance(user_id, str) or not user_id.strip(): 
            raise ValueError("user_id is required.") 
        
        if not isinstance(session_id, str) or not session_id.strip(): 
            raise ValueError("session_id is required.")

        thread_id = f"{user_id}:{session_id}"

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        output = self.graph.invoke(
            Command(resume=decision),
            config=config,
        )

        if not isinstance(output, dict):
            raise OutputGuardrailError(
                self.output_guardrail.validate(output)
            )

        output_result = self.output_guardrail.validate(
            output.get("final_answer")
        )

        if output_result.decision.value == "error":
            raise RuntimeError(
                "Output validation could not be completed."
            )

        if not output_result.allowed:
            raise OutputGuardrailError(output_result)

        return output


    def close(self) -> None:

        short_term = self.memory.short_term
        long_term = self.memory.long_term

        if hasattr(short_term, "close"):
            short_term.close()

        if hasattr(long_term, "close"):
            long_term.close()