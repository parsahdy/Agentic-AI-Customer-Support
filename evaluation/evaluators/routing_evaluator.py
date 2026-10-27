import json
from pathlib import Path


ROUTES = ["direct", "rag", "tool"]


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_evaluation.json"
)

OUTCOME_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_outcome.json"
)

RESULTS_PATH = (
    PROJECT_ROOT / "evaluation" / "results" / "routing_results.json"
)


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def index_by_id(items):
    """[{'id': 'a', ...}, ...] -> {'a': {...}, ...}"""
    return {item["id"]: item for item in items}


def make_check(name, expected, actual):
    return {
        "name": name,
        "expected": expected,
        "actual": actual,
        "passed": expected == actual,
    }


def evaluate_scenario(scenario, outcome):
    expected = scenario["expected_behavior"]
    actual = (outcome or {}).get("actual_behavior")

    result = {
        "id": scenario["id"],
        "category": scenario["category"],
        "expected_route": expected["route"],
        "actual_route": None,
        "passed": False,
        "checks": [],
        "reason": "",
    }

    if outcome is None:
        result["reason"] = "scenario was not run"
        return result

    if actual is None:
        result["reason"] = "run failed, no behavior recorded"
        return result

    result["actual_route"] = actual.get("route")

    result["checks"] = [
        make_check("route", expected["route"], actual.get("route")),
        make_check("retrieval", expected["retrieval_expected"],
                   actual.get("retrieval_performed")),
        make_check("human_review", expected["human_review_expected"],
                   actual.get("human_review_required")),
    ]

    failed = [c for c in result["checks"] if not c["passed"]]

    result["passed"] = not failed
    result["reason"] = "; ".join(
        f"{c['name']}: expected {c['expected']!r}, got {c['actual']!r}"
        for c in failed
    )

    return result


def evaluate_routing(dataset, outcomes):
    outcomes_by_id = index_by_id(outcomes)

    return [
        evaluate_scenario(scenario, outcomes_by_id.get(scenario["id"]))
        for scenario in dataset
    ]


def confusion_matrix(results):
    """
    {expected_route: {actual_route: count}}

    Nested dicts (not tuple keys) so the matrix can be saved as JSON.
    A run without a route is counted under "none".
    """
    matrix = {}

    for r in results:
        row = matrix.setdefault(r["expected_route"], {})
        column = r["actual_route"] or "none"
        row[column] = row.get(column, 0) + 1

    return matrix


def summarize(results):
    by_category = {}

    for r in results:
        stats = by_category.setdefault(r["category"], {"passed": 0, "total": 0})
        stats["total"] += 1
        stats["passed"] += r["passed"]

    return {
        "passed": sum(r["passed"] for r in results),
        "total": len(results),
        "by_category": by_category,
        "confusion": confusion_matrix(results),
    }


def save_results(results, summary, path=RESULTS_PATH):
    """Write everything the report needs into one JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "evaluator": "routing",
        "dataset_path": str(DATASET_PATH.relative_to(PROJECT_ROOT)),
        "outcome_path": str(OUTCOME_PATH.relative_to(PROJECT_ROOT)),
        "summary": summary,
        "results": results,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def print_summary(results, summary):
    print(f"Routing: {summary['passed']} / {summary['total']} passed\n")

    print("By category:")
    for category, stats in summary["by_category"].items():
        print(f"  {category:14} {stats['passed']} / {stats['total']}")

    print("\nConfusion matrix (rows = expected, columns = actual):")
    columns = ROUTES + ["none"]
    print(f"  {'':10}" + "".join(f"{c:>9}" for c in columns))
    for expected in ROUTES:
        row = "".join(
            f"{summary['confusion'].get(expected, {}).get(c, 0):>9}"
            for c in columns
        )
        print(f"  {expected:10}{row}")

    print("\nFailures:")
    for r in results:
        if not r["passed"]:
            print(f"  {r['id']}: {r['reason']}")


if __name__ == "__main__":
    results = evaluate_routing(load_json(DATASET_PATH), load_json(OUTCOME_PATH))
    summary = summarize(results)

    print_summary(results, summary)
    save_results(results, summary)
    print(f"\nSaved to {RESULTS_PATH.relative_to(PROJECT_ROOT)}")