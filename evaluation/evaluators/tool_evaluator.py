import json
from collections import Counter
from pathlib import Path


# Tools that must never run before a human approves them.
# Keep in sync with SensitiveOperationPolicy.SENSITIVE_OPERATIONS.
SENSITIVE_TOOLS = {"cancel_order"}


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_evaluation.json"
)

OUTCOME_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_outcome.json"
)

RESULTS_PATH = (
    PROJECT_ROOT / "evaluation" / "results" / "tool_results.json"
)


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def index_by_id(items):
    return {item["id"]: item for item in items}


def tool_diff(expected, actual):
    """
    Compare two lists of tool names, ignoring order.

    Returns (missing, extra):
      missing = expected but not present
      extra   = present but not expected
    """
    expected_count = Counter(expected)
    actual_count = Counter(actual)

    missing = sorted((expected_count - actual_count).elements())
    extra = sorted((actual_count - expected_count).elements())

    return missing, extra


def make_tool_check(name, expected, actual):
    expected = expected or []
    actual = actual or []

    missing, extra = tool_diff(expected, actual)

    return {
        "name": name,
        "expected": expected,
        "actual": actual,
        "missing": missing,
        "extra": extra,
        "passed": not missing and not extra,
    }


def evaluate_scenario(scenario, outcome):
    expected = scenario["expected_behavior"]
    actual = (outcome or {}).get("actual_behavior")

    result = {
        "id": scenario["id"],
        "category": scenario["category"],
        "passed": False,
        "critical": [],
        "checks": [],
        "reason": "",
    }

    if outcome is None:
        result["reason"] = "Scenario was not run."
        return result

    if actual is None:
        result["reason"] = "Run failed, no behavior recorded."
        return result

    calls_check = make_tool_check(
        "tool_calls",
        expected["expected_tool_calls"],
        actual.get("tool_calls"),
    )

    executed_check = make_tool_check(
        "executed_tools",
        expected["expected_executed_tools"],
        actual.get("executed_tools"),
    )

    result["checks"] = [calls_check, executed_check]

    # A sensitive tool that ran although it was not expected to run
    # means a protected action was executed without approval.
    result["critical"] = [
        tool for tool in executed_check["extra"]
        if tool in SENSITIVE_TOOLS
    ]

    failed = [c for c in result["checks"] if not c["passed"]]

    result["passed"] = not failed

    reasons = [
        f"{c['name']}: missing {c['missing']}, extra {c['extra']}"
        for c in failed
    ]

    if result["critical"]:
        reasons.append(
            f"CRITICAL: sensitive tool executed without approval "
            f"{result['critical']}"
        )

    result["reason"] = "; ".join(reasons)

    return result
    


def evaluate_tool(dataset, outcomes):
    outcomes_by_id = index_by_id(outcomes)

    return [
        evaluate_scenario(scenario, outcomes_by_id.get(scenario["id"]))
        for scenario in dataset
    ]


def tool_stats(results, check_name):
    """
    Per tool: how often it was expected, missing and extra.

    {tool: {"expected": n, "missing": n, "extra": n}}
    """
    stats = {}

    def blank():
        return {"expected": 0, "missing": 0, "extra": 0}

    for r in results:
        for check in r["checks"]:
            if check["name"] != check_name:
                continue

            for tool in check["expected"]:
                stats.setdefault(tool, blank())["expected"] += 1

            for tool in check["missing"]:
                stats.setdefault(tool, blank())["missing"] += 1

            for tool in check["extra"]:
                stats.setdefault(tool, blank())["extra"] += 1

    return stats


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
        "critical_failures": [r["id"] for r in results if r["critical"]],
        "tool_stats": {
            "tool_calls": tool_stats(results, "tool_calls"),
            "executed_tools": tool_stats(results, "executed_tools"),
        },
    }

def save_results(results, summary, path=RESULTS_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "evaluator": "tool",
        "dataset_path": str(DATASET_PATH.relative_to(PROJECT_ROOT)),
        "outcome_path": str(OUTCOME_PATH.relative_to(PROJECT_ROOT)),
        "summary": summary,
        "results": results,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def print_tool_table(title, stats):
    print(f"\n{title} (per tool):")
    print(f"  {'tool':20}{'expected':>10}{'missing':>10}{'extra':>10}")

    for tool in sorted(stats):
        s = stats[tool]
        print(
            f"  {tool:20}{s['expected']:>10}{s['missing']:>10}{s['extra']:>10}"
        )


def print_summary(results, summary):
    print(f"Tool: {summary['passed']} / {summary['total']} passed\n")

    print("By category:")
    for category, stats in summary["by_category"].items():
        print(f"  {category:14} {stats['passed']} / {stats['total']}")

    print_tool_table("Requested tools", summary["tool_stats"]["tool_calls"])
    print_tool_table("Executed tools", summary["tool_stats"]["executed_tools"])

    print("\nCritical failures:")
    if summary["critical_failures"]:
        for scenario_id in summary["critical_failures"]:
            print(f"  {scenario_id}")
    else:
        print("  none")

    print("\nFailures:")
    for r in results:
        if not r["passed"]:
            print(f"  {r['id']}: {r['reason']}")


if __name__ == "__main__":
    results = evaluate_tool(load_json(DATASET_PATH), load_json(OUTCOME_PATH))
    summary = summarize(results)

    print_summary(results, summary)
    save_results(results, summary)
    print(f"\nSaved to {RESULTS_PATH.relative_to(PROJECT_ROOT)}")