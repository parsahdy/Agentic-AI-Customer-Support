import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"
REPORT_JSON_PATH = RESULTS_DIR / "evaluation_report.json"
REPORT_MD_PATH = RESULTS_DIR / "evaluation_report.md"


# Known evaluators are shown in this order; unknown ones come after them.
EVALUATOR_ORDER = ["routing", "tool", "outcome"]

ROUTES = ["direct", "rag", "tool"]


def load_results(results_dir=RESULTS_DIR):
    """Read every *_results.json file written by the evaluators."""

    files = sorted(Path(results_dir).glob("*_results.json"))

    if not files:
        raise FileNotFoundError(
            f"No *_results.json files found in {results_dir}. "
            "Run the evaluators first."
        )

    payloads = []

    for file in files:
        with file.open("r", encoding="utf-8") as handle:
            payloads.append(json.load(handle))

    def order(payload):
        name = payload["evaluator"]

        if name in EVALUATOR_ORDER:
            return EVALUATOR_ORDER.index(name)

        return len(EVALUATOR_ORDER)

    return sorted(payloads, key=order)


def find_warnings(payloads):
    warnings = []

    outcome_paths = {p["outcome_path"] for p in payloads}
    dataset_paths = {p["dataset_path"] for p in payloads}
    totals = {p["evaluator"]: p["summary"]["total"] for p in payloads}

    if len(outcome_paths) > 1:
        warnings.append(
            "Evaluators were run on different outcome files: "
            f"{sorted(outcome_paths)}. Their scores are not comparable."
        )

    if len(dataset_paths) > 1:
        warnings.append(
            "Evaluators were run on different datasets: "
            f"{sorted(dataset_paths)}."
        )

    if len(set(totals.values())) > 1:
        warnings.append(
            f"Evaluators saw a different number of scenarios: {totals}."
        )

    return warnings


def build_report(payloads):
    evaluators = {}
    scenarios = {}
    critical_failures = []

    for payload in payloads:
        name = payload["evaluator"]
        failures = []

        for r in payload["results"]:
            row = scenarios.setdefault(
                r["id"],
                {"id": r["id"], "category": r["category"], "results": {}},
            )
            row["results"][name] = r["passed"]

            if r.get("critical"):
                critical_failures.append(
                    {
                        "evaluator": name,
                        "id": r["id"],
                        "detail": r["critical"],
                    }
                )

            if not r["passed"]:
                failures.append(
                    {
                        "id": r["id"],
                        "category": r["category"],
                        "reason": r["reason"],
                    }
                )

        evaluators[name] = {
            "dataset_path": payload["dataset_path"],
            "outcome_path": payload["outcome_path"],
            "summary": payload["summary"],
            "failures": failures,
        }

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "warnings": find_warnings(payloads),
        "evaluators": evaluators,
        "critical_failures": critical_failures,
        "scenarios": list(scenarios.values()),
    }


def md_table(headers, rows):
    def cell(value):
        return str(value).replace("|", "\\|")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for row in rows:
        lines.append("| " + " | ".join(cell(c) for c in row) + " |")

    return lines


def render_by_category(summary):
    rows = [
        (category, stats["passed"], stats["total"])
        for category, stats in summary["by_category"].items()
    ]

    return ["### By category", ""] + md_table(
        ["category", "passed", "total"], rows
    )


def render_routing_details(summary):
    confusion = summary.get("confusion", {})
    columns = ROUTES + ["none"]

    rows = [
        [expected] + [confusion.get(expected, {}).get(c, 0) for c in columns]
        for expected in ROUTES
    ]

    return (
        ["### Confusion matrix (rows = expected, columns = actual)", ""]
        + md_table(["expected \\ actual"] + columns, rows)
    )


def render_tool_details(summary):
    lines = []

    titles = {
        "tool_calls": "Requested tools (per tool)",
        "executed_tools": "Executed tools (per tool)",
    }

    for key, title in titles.items():
        stats = summary.get("tool_stats", {}).get(key, {})

        rows = [
            (tool, s["expected"], s["missing"], s["extra"])
            for tool, s in sorted(stats.items())
        ]

        lines += [f"### {title}", ""]
        lines += md_table(["tool", "expected", "missing", "extra"], rows)
        lines.append("")

    return lines


def render_outcome_details(summary):
    rows = [
        (name, s["passed"], s["failed"], s["skipped"])
        for name, s in sorted(summary.get("by_check", {}).items())
    ]

    lines = ["### Checks", ""]
    lines += md_table(["check", "passed", "failed", "skipped"], rows)

    incomplete = summary.get("incomplete", [])

    if incomplete:
        lines += [
            "",
            "Incomplete scenarios (some checks were skipped): "
            + ", ".join(incomplete),
        ]

    return lines


DETAIL_RENDERERS = {
    "routing": render_routing_details,
    "tool": render_tool_details,
    "outcome": render_outcome_details,
}


def render_markdown(report):
    evaluators = report["evaluators"]
    critical = report["critical_failures"]

    lines = [
        "# Evaluation report",
        "",
        f"Generated at: {report['generated_at']}",
        "",
    ]

    if report["warnings"]:
        lines += ["## Warnings", ""]
        lines += [f"- {warning}" for warning in report["warnings"]]
        lines.append("")

    # Overview: one line per evaluator, never one merged score.
    overview_rows = []

    for name, data in evaluators.items():
        summary = data["summary"]
        critical_count = sum(1 for c in critical if c["evaluator"] == name)

        overview_rows.append(
            (
                name,
                f"{summary['passed']} / {summary['total']}",
                summary["total"] - summary["passed"],
                critical_count,
            )
        )

    lines += ["## Overview", ""]
    lines += md_table(
        ["evaluator", "passed / total", "failed", "critical"],
        overview_rows,
    )
    lines.append("")

    lines += ["## Critical failures", ""]

    if critical:
        lines += md_table(
            ["evaluator", "scenario", "detail"],
            [(c["evaluator"], c["id"], c["detail"]) for c in critical],
        )
    else:
        lines.append("None.")

    lines.append("")

    # Scenario x evaluator matrix.
    names = list(evaluators)

    def mark(value):
        if value is None:
            return "-"

        return "pass" if value else "FAIL"

    scenario_rows = [
        [s["id"], s["category"]] + [mark(s["results"].get(n)) for n in names]
        for s in report["scenarios"]
    ]

    lines += ["## Scenarios", ""]
    lines += md_table(["scenario", "category"] + names, scenario_rows)
    lines.append("")

    # One section per evaluator.
    for name, data in evaluators.items():
        lines += [f"## {name.capitalize()} evaluator", ""]
        lines += [
            f"Dataset: `{data['dataset_path']}`  ",
            f"Outcomes: `{data['outcome_path']}`",
            "",
        ]

        lines += render_by_category(data["summary"])
        lines.append("")

        renderer = DETAIL_RENDERERS.get(name)

        if renderer is not None:
            lines += renderer(data["summary"])
            lines.append("")

        lines += ["### Failures", ""]

        if data["failures"]:
            lines += md_table(
                ["scenario", "category", "reason"],
                [(f["id"], f["category"], f["reason"]) for f in data["failures"]],
            )
        else:
            lines.append("None.")

        lines.append("")

    return "\n".join(lines)


def save_report(report, markdown):
    REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_JSON_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    with REPORT_MD_PATH.open("w", encoding="utf-8") as file:
        file.write(markdown)


def print_overview(report):
    print("Evaluation report\n")

    for name, data in report["evaluators"].items():
        summary = data["summary"]
        print(f"  {name:12} {summary['passed']} / {summary['total']} passed")

    print(f"\n  critical failures: {len(report['critical_failures'])}")

    for warning in report["warnings"]:
        print(f"  WARNING: {warning}")


def main():
    report = build_report(load_results())
    markdown = render_markdown(report)

    save_report(report, markdown)

    print_overview(report)
    print(f"\nSaved to {REPORT_MD_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Saved to {REPORT_JSON_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
