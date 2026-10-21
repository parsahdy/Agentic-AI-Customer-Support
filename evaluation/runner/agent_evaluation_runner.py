import json
import uuid
from pathlib import Path

from agent import AgentService


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_evaluation.json"
)

OUTCOME_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_outcome.json"
)


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
    }


def runner():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        evaluation_data = json.load(file)

    if not isinstance(evaluation_data, list):
        raise ValueError(
            "The evaluation dataset must be a JSON array."
        )

    agent = AgentService()
    outcomes = []

    run_id = uuid.uuid4().hex

    for scenario in evaluation_data:
        try:
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

        # Persist progress so completed scenarios aren't lost
        # if a later scenario fails unexpectedly.
        with OUTCOME_PATH.open("w", encoding="utf-8") as file:
            json.dump(
                outcomes,
                file,
                indent=4,
                ensure_ascii=False,
            )

    return outcomes


if __name__ == "__main__":
    runner()