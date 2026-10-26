import json
import uuid
from pathlib import Path

from agent import AgentService
from evaluation import ConfidenceEvaluator


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_evaluation.json"
)

OUTCOME_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_simulated_outcome.json"
)


# ---------------------------------------------------------------------------
# Simulation support
#
# Scenarios with an `input.simulation` block describe the retrieval result
# (fixture + scores) and the faithfulness / confidence the agent should see.
# These fakes feed that block to the real graph, so the routing, the human
# policy and the interrupt logic are exercised exactly as in production.
# ---------------------------------------------------------------------------

SIMULATION_FIXTURES = {
    "sufficient_return_policy": [
        {
            "document_id": "sim_return_policy",
            "chunk_id": 0,
            "content": (
                "Return policy: items can be returned within 30 days of "
                "delivery if they are unused and in the original packaging. "
                "Refunds are issued to the original payment method within "
                "5-7 business days after the returned item is received."
            ),
            "metadata": {},
        },
    ],
    "no_relevant_document": [
        {
            "document_id": "sim_unrelated",
            "chunk_id": 0,
            "content": (
                "Our support team is available Monday to Friday, "
                "from 9:00 to 17:00."
            ),
            "metadata": {},
        },
    ],
    "conflicting_policy_documents": [
        {
            "document_id": "sim_policy_old",
            "chunk_id": 0,
            "content": (
                "Return policy (2023 handbook): items can be returned "
                "within 14 days of delivery."
            ),
            "metadata": {},
        },
        {
            "document_id": "sim_policy_new",
            "chunk_id": 0,
            "content": (
                "Return policy (2024 handbook): items can be returned "
                "within 30 days of delivery."
            ),
            "metadata": {},
        },
    ],
}


class SimulationContext:
    """Holds the simulation block of the scenario that is running."""

    def __init__(self):
        self.current: dict = {}

    def set(self, simulation: dict | None) -> None:
        self.current = simulation or {}


class SimulatedKnowledgeBase:
    """Returns the fixture documents and scores of the current scenario."""

    def __init__(self, context: SimulationContext):
        self.context = context

    def search(self, query: str) -> dict:
        simulation = self.context.current

        documents = SIMULATION_FIXTURES.get(
            simulation.get("retrieval_fixture"),
            [],
        )
        scores = simulation.get("retrieval_scores", {})

        return {
            "retrieval_documents": [dict(item) for item in documents],
            "top1_score": scores.get("top1_score", 0.0),
            "mean_topk_score": scores.get("mean_topk_score", 0.0),
        }


class SimulatedFaithfulnessEvaluator:
    """Returns the faithfulness score defined by the scenario."""

    def __init__(self, context: SimulationContext):
        self.context = context

    def evaluate(self, query, answer, retrieved_contexts) -> float:
        return float(self.context.current.get("faithfulness_score", 0.0))


class SimulatedConfidenceEvaluator:
    """
    Returns the confidence score defined by the scenario. Without a
    simulated value it falls back to the real ConfidenceEvaluator.
    """

    def __init__(self, context: SimulationContext):
        self.context = context
        self.real = ConfidenceEvaluator()

    def calculate(
        self,
        top1_score,
        mean_topk_score,
        faithfulness_score,
    ) -> float:

        if "confidence_score" in self.context.current:
            return float(self.context.current["confidence_score"])

        return self.real.calculate(
            top1_score=top1_score,
            mean_topk_score=mean_topk_score,
            faithfulness_score=faithfulness_score,
        )


def build_agent(context: SimulationContext) -> AgentService:
    return AgentService(
        kb=SimulatedKnowledgeBase(context),
        faithfulness_evaluator=SimulatedFaithfulnessEvaluator(context),
        confidence_evaluator=SimulatedConfidenceEvaluator(context),
    )


# ---------------------------------------------------------------------------
# Outcome recording
# ---------------------------------------------------------------------------

def _to_jsonable(value):
    """Convert common Python objects to JSON-serializable values."""
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return {
            key: _to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]

    return value


def _extract_tool_names(items):
    """Extract tool names from recorded tool calls or results."""
    names = []

    for item in items or []:
        if not isinstance(item, dict):
            continue

        name = item.get("name") or item.get("tool_name")

        if name:
            names.append(name)

    return names


def _build_outcome(scenario, result):
    """Build an actual outcome record from the agent result."""
    result = _to_jsonable(result)

    if not isinstance(result, dict):
        raise TypeError(
            "AgentService.run() must return a dictionary-like result."
        )

    route = result.get("route")
    status = result.get("status")

    tool_calls = result.get("tool_calls", [])
    tool_results = result.get("tool_results", [])

    human_review_required = result.get("human_review_required")

    if human_review_required is None:
        human_review_required = status == "human_review"

    retrieved_documents = [
        {
            "document_id": document.get("document_id"),
            "content": document.get("content"),
            "score": document.get("score"),
        }
        for document in result.get("retrieved_documents", [])
    ]

    return {
        "id": scenario["id"],
        "category": scenario["category"],
        "input": scenario["input"],
        "actual_behavior": {
            "route": route,
            "tool_calls": _extract_tool_names(tool_calls),
            "executed_tools": _extract_tool_names(tool_results),
            "retrieval_performed": bool(result.get("retrieval_performed")),
            "human_review_required": human_review_required,
        },
        "actual_outcome": {
            "final_answer": result.get("final_answer"),
            "status": status,
            "error": result.get("error"),
        },
        "evidence": {
            "retrieved_documents": retrieved_documents,
            "tool_calls": tool_calls,
            "tool_results": tool_results,
        },
    }


def runner():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        evaluation_data = json.load(file)

    if not isinstance(evaluation_data, list):
        raise ValueError(
            "The evaluation dataset must be a JSON array."
        )

    context = SimulationContext()
    agent = build_agent(context)
    outcomes = []

    run_id = uuid.uuid4().hex

    try:
        for scenario in evaluation_data:
            try:
                context.set(scenario["input"].get("simulation"))

                result = agent.run(
                    query=scenario["input"]["query"],
                    user_id=scenario["id"],
                    session_id=f"{scenario['id']}:{run_id}",
                )

                outcome = _build_outcome(scenario, result)

            except Exception as exc:
                outcome = {
                    "id": scenario.get("id"),
                    "category": scenario.get("category"),
                    "input": scenario.get("input"),
                    "actual_behavior": None,
                    "actual_outcome": {
                        "status": "error",
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        },
                    },
                }

            outcomes.append(outcome)

            with OUTCOME_PATH.open("w", encoding="utf-8") as file:
                json.dump(
                    outcomes,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

    finally:
        agent.close()

    return outcomes


if __name__ == "__main__":
    runner()