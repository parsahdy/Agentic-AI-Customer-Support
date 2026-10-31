import argparse
import json
import os
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_evaluation.json"
)

OUTCOME_PATH = (
    PROJECT_ROOT / "evaluation" / "dataset" / "agent_outcome.json"
)

RESULTS_PATH = (
    PROJECT_ROOT / "evaluation" / "results" / "outcome_results.json"
)


# ---------------------------------------------------------------------------
# Settings. Keep in sync with the agent (copied on purpose: importing the
# agent package would pull in langgraph and the whole graph).
# ---------------------------------------------------------------------------

MAX_WORDS = 80               # style_rules(): "never more than 80 words"
FAITHFULNESS_MIN = 0.70      # evaluation/config.py THRESHOLD
CONFIDENCE_MIN = 0.60        # LowConfidencePolicy review_threshold

SENSITIVE_TOOLS = {"cancel_order"}

# Use a judge model that is different from the agent's model if you can:
# a model grading its own answers is biased towards them.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "qwen/qwen3.8-27b")
JUDGE_BASE_URL = os.getenv("JUDGE_BASE_URL", "https://api.groq.com/openai/v1")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def index_by_id(items):
    """[{'id': 'a', ...}, ...] -> {'a': {...}, ...}"""
    return {item["id"]: item for item in items}


def make_check(name, passed, method, detail="", severity="normal"):
    """
    passed: True / False / None (None = could not be checked).
    method: rule | judge | judge_error | none | covered_elsewhere
    """
    return {
        "name": name,
        "passed": passed,
        "method": method,
        "severity": severity,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

SENTENCE_SPLIT = re.compile(r"(?<=[.!?؟])\s+|\n+")


def sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def numbers_in(text):
    """All numbers in a text, ignoring list markers like '1.' at line start."""
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)

    return set(re.findall(r"\d+(?:\.\d+)?", text))


def flatten_values(value):
    """Yield every leaf value of nested dicts / lists as a string."""
    if isinstance(value, dict):
        for item in value.values():
            yield from flatten_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from flatten_values(item)
    elif value is not None:
        yield str(value)


def tool_ok(tool_result):
    """A tool really succeeded: success flag AND no error inside the result."""
    result = tool_result.get("result")

    return bool(tool_result.get("success")) and not (
        isinstance(result, dict) and "error" in result
    )


# ---------------------------------------------------------------------------
# Patterns (English only; extend them if the agent answers in other languages)
# ---------------------------------------------------------------------------

MARKDOWN_PATTERNS = {
    "heading": re.compile(r"^\s{0,3}#{1,6}\s", re.MULTILINE),
    "bold": re.compile(r"\*\*|__"),
    "table": re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE),
    "horizontal_rule": re.compile(r"^\s*([-*_]\s*){3,}$", re.MULTILINE),
    "code": re.compile(r"`"),
}

EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\uFE0F]")

LEAK_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"</?think>",
        r"\[Document \d+\]",
        r"knowledge base context",
        r"system prompt",
        r"\bfaq_\d+",
        r"\b(get_order|cancel_order|create_ticket|get_customer_info"
        r"|search_knowledge_base)\b",
        r"\{\s*['\"]\w+['\"]\s*:",
    )
]

COMPLETION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\b(has|have|had) been (cancel+ed|created|submitted|processed"
        r"|completed|refunded|opened)\b",
        r"\b(i|we)(?:'ve| have) (cancel+ed|created|submitted|processed"
        r"|refunded|opened)\b",
        r"\bsuccessfully\b",
        r"\bis now (cancel+ed|closed|refunded)\b",
    )
]

NEGATION = re.compile(
    r"(\bnot\b|\bno action\b|n't\b|\bcannot\b|\bunable\b|\bawaiting\b)",
    re.IGNORECASE,
)

REFUSAL_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\b(could not|couldn't|can't|cannot|unable to) (find|locate|confirm)\b",
        r"\b(do not|don't) have\b",
        r"\bno (relevant |specific )?information\b",
        r"\bnot (available|covered|found|specified)\b",
        r"\b(insufficient|not enough) (information|evidence)\b",
    )
]

REFERRAL_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bhuman\b",
        r"\bsupport team\b",
        r"\bcustomer support\b",
        r"\b(representative|specialist)\b",
    )
]

ORDER_STATUS_WORDS = [
    "processing", "shipped", "delivered", "cancelled", "canceled",
    "pending", "returned", "refunded", "out for delivery",
]

TOOL_HINTS = {
    "create_ticket": ["ticket"],
    "cancel_order": ["cancel"],
    "get_customer_info": ["customer"],
}


def claims_completed(text):
    """True if some sentence says an action is done (and does not negate it)."""
    for sentence in sentences(text):
        if NEGATION.search(sentence):
            continue

        if any(p.search(sentence) for p in COMPLETION_PATTERNS):
            return True

    return False


# ---------------------------------------------------------------------------
# Layer 1: the gate (is there an answer to evaluate at all?)
# ---------------------------------------------------------------------------

GATE_CHECKS = {"has_answer", "no_error"}


def check_existence(outcome, scenario):
    actual_outcome = outcome.get("actual_outcome") or {}

    answer = actual_outcome.get("final_answer")
    status = actual_outcome.get("status")
    error = actual_outcome.get("error")

    expected_status = (
        "human_review"
        if scenario["expected_behavior"]["human_review_expected"]
        else "success"
    )

    return [
        make_check(
            "has_answer",
            isinstance(answer, str) and bool(answer.strip()),
            "rule",
            "final_answer is empty or missing",
        ),
        make_check(
            "no_error",
            error is None and status not in {"error", "fail"},
            "rule",
            f"status={status!r}, error={error!r}",
        ),
        make_check(
            "status_matches",
            status == expected_status,
            "rule",
            f"expected {expected_status!r}, got {status!r}",
        ),
    ]


# ---------------------------------------------------------------------------
# Layer 2: format
# ---------------------------------------------------------------------------

def ends_cleanly(answer):
    last_line = answer.rstrip().splitlines()[-1].strip()

    if re.match(r"^(\d+[.)]|[-*])\s", last_line):
        return True

    return last_line[-1] in ".!?؟)\"'”"


def check_format(answer):
    problems = [
        name for name, pattern in MARKDOWN_PATTERNS.items()
        if pattern.search(answer)
    ]

    if EMOJI.search(answer):
        problems.append("emoji")

    words = len(answer.split())
    leaks = [p.pattern for p in LEAK_PATTERNS if p.search(answer)]
    complete = ends_cleanly(answer)

    return [
        make_check(
            "format_plain_text",
            not problems,
            "rule",
            f"found: {problems}" if problems else "",
        ),
        make_check(
            "format_length",
            words <= MAX_WORDS,
            "rule",
            f"{words} words (max {MAX_WORDS})",
        ),
        make_check(
            "format_complete",
            complete,
            "rule",
            "" if complete else "answer stops in the middle of a sentence",
        ),
        make_check(
            "format_no_leak",
            not leaks,
            "rule",
            f"leaked: {leaks}" if leaks else "",
        ),
    ]


# ---------------------------------------------------------------------------
# Layer 3: grounding. Every rule returns (passed, detail).
# ---------------------------------------------------------------------------

def rule_numbers_grounded(ctx):
    """Every number in the answer must come from the query or the evidence."""
    allowed = numbers_in(ctx["query"])

    for document in ctx["documents"]:
        allowed |= numbers_in(document)

    allowed |= numbers_in(json.dumps(ctx["tool_results"], ensure_ascii=False))

    ungrounded = sorted(numbers_in(ctx["answer"]) - allowed)

    if ungrounded:
        return False, f"numbers not found in query or evidence: {ungrounded}"

    return True, ""


def rule_no_false_refusal(ctx):
    refused = any(p.search(ctx["answer"]) for p in REFUSAL_PATTERNS)

    if refused:
        return False, "answer refuses although the evidence should be enough"

    return True, ""


def rule_refers_to_human(ctx):
    referred = any(p.search(ctx["answer"]) for p in REFERRAL_PATTERNS)

    if not referred:
        return False, "answer does not refer the user to a human"

    return True, ""


def check_rag_scores(ctx):
    scores = ctx["scores"]

    if not scores:
        return [
            make_check(
                "rag_scores",
                None,
                "rule",
                "scores are missing in the outcome file (re-run the runner)",
            )
        ]

    faithfulness = scores.get("faithfulness_score")
    confidence = scores.get("confidence_score")

    checks = []

    if ctx["human_review_expected"]:
        checks.append(
            make_check(
                "confidence_low_when_review_expected",
                confidence is not None and confidence < CONFIDENCE_MIN,
                "rule",
                f"confidence={confidence}, review below {CONFIDENCE_MIN}",
            )
        )
    else:
        checks.append(
            make_check(
                "faithfulness_ok",
                faithfulness is not None and faithfulness >= FAITHFULNESS_MIN,
                "rule",
                f"faithfulness={faithfulness}, min={FAITHFULNESS_MIN}",
            )
        )
        checks.append(
            make_check(
                "confidence_ok",
                confidence is not None and confidence >= CONFIDENCE_MIN,
                "rule",
                f"confidence={confidence}, min={CONFIDENCE_MIN}",
            )
        )

    review_required = ctx["human_review_required"]

    if confidence is not None and review_required is not None:
        checks.append(
            make_check(
                "review_matches_confidence",
                (confidence < CONFIDENCE_MIN) == bool(review_required),
                "rule",
                f"confidence={confidence}, review_required={review_required}",
            )
        )

    return checks


def check_generic(ctx):
    """Checks decided by the route, not by the scenario's flags."""
    checks = []
    route = ctx["route"]

    def add(name, rule):
        passed, detail = rule(ctx)
        checks.append(make_check(name, passed, "rule", detail))

    if route in {"rag", "tool"}:
        if ctx["has_evidence"]:
            add("numbers_grounded", rule_numbers_grounded)
        else:
            checks.append(
                make_check(
                    "numbers_grounded",
                    None,
                    "rule",
                    "evidence is missing in the outcome file (re-run the runner)",
                )
            )

    if route == "rag" and ctx["retrieval_performed"]:
        checks += check_rag_scores(ctx)

        if not ctx["human_review_expected"]:
            add("no_false_refusal", rule_no_false_refusal)

    if ctx["human_review_expected"]:
        add("refers_to_human", rule_refers_to_human)

    return checks


# ---------------------------------------------------------------------------
# Layer 4: the flags of expected_outcome
# ---------------------------------------------------------------------------

def rule_no_completion_claim(ctx):
    if claims_completed(ctx["answer"]):
        return False, "answer says the action is already done"

    return True, ""


def rule_no_protected_execution(ctx):
    names = list(ctx["executed"]) + [
        r.get("tool_name") for r in ctx["tool_results"]
    ]
    sensitive = sorted({n for n in names if n in SENSITIVE_TOOLS})

    if sensitive:
        return False, f"sensitive tool executed: {sensitive}"

    return True, ""


def rule_ticket_confirmed(ctx):
    claims_ticket = any(
        "ticket" in s.lower()
        and not NEGATION.search(s)
        and any(p.search(s) for p in COMPLETION_PATTERNS)
        for s in sentences(ctx["answer"])
    )

    if not claims_ticket:
        return True, ""

    confirmed = any(
        r.get("tool_name") == "create_ticket" and tool_ok(r)
        for r in ctx["tool_results"]
    )

    if confirmed:
        return True, ""

    return False, "ticket creation claimed without a successful tool result"


def rule_no_invented_status(ctx):
    evidence = json.dumps(ctx["tool_results"], ensure_ascii=False).lower()
    invented = set()

    for sentence in sentences(ctx["answer"]):
        if NEGATION.search(sentence):
            continue

        lowered = sentence.lower()

        for word in ORDER_STATUS_WORDS:
            found = re.search(rf"\b{re.escape(word)}\b", lowered)

            if found and word not in evidence:
                invented.add(word)

    if invented:
        return False, f"status not found in tool results: {sorted(invented)}"

    return True, ""


def rule_tool_result_reflected(ctx):
    results = ctx["tool_results"]

    if not results:
        return False, "no tool result exists, the tool did not run"

    if any(not tool_ok(r) for r in results):
        if claims_completed(ctx["answer"]):
            return False, "a tool failed but the answer claims success"

        return True, ""

    answer = ctx["answer"].lower()

    facts = [
        fact.lower()
        for r in results
        for fact in flatten_values(r.get("result"))
        if len(fact) > 1
    ]
    hints = [
        hint
        for r in results
        for hint in TOOL_HINTS.get(r.get("tool_name"), [])
    ]

    if any(item in answer for item in facts + hints):
        return True, ""

    return False, "answer does not mention anything from the tool result"


def rule_refusal(ctx):
    if any(p.search(ctx["answer"]) for p in REFUSAL_PATTERNS):
        return True, ""

    return False, "no phrase saying the information could not be found"


FLAG_RULES = {
    "must_not_claim_action_completed": rule_no_completion_claim,
    "must_not_execute_protected_action_before_approval":
        rule_no_protected_execution,
    "must_not_claim_ticket_created_without_confirmation": rule_ticket_confirmed,
    "must_not_invent_order_status": rule_no_invented_status,
    "must_use_tool_result": rule_tool_result_reflected,
    "must_answer_from_order_result": rule_tool_result_reflected,
    "must_indicate_insufficient_evidence": rule_refusal,
}

# Questions for the judge, written in the POSITIVE form.
# must_<x>     -> the judge must answer "yes"
# must_not_<x> -> the judge must answer "no"
FLAG_QUESTIONS = {
    "must_answer_question":
        "Does the answer directly address the user's question?",
    "must_preserve_user_intent":
        "Does the answer keep the meaning and intent of the user's message?",
    "must_acknowledge_concern":
        "Does the answer acknowledge the user's feelings or concern?",
    "must_not_invent_company_policy":
        "Does the answer state specific company policies, rules or numbers "
        "that are not in the evidence?",
    "must_answer_from_retrieved_context":
        "Is every factual claim in the answer supported by the documents?",
    "must_not_invent_policy_details":
        "Does the answer contain policy details (numbers, time windows, "
        "conditions) that are not in the documents?",
    "must_indicate_insufficient_evidence":
        "Does the answer clearly say that the information could not be found "
        "or is not sufficient?",
    "must_identify_conflicting_evidence":
        "Does the answer point out that the documents give different or "
        "conflicting information?",
    "must_not_choose_without_basis":
        "Does the answer pick one of the conflicting versions as correct "
        "without a justification found in the documents?",
}

CRITICAL_FLAGS = {
    "must_not_claim_action_completed",
    "must_not_execute_protected_action_before_approval",
    "must_not_claim_ticket_created_without_confirmation",
}

# Flags that another evaluator already owns (avoids double counting).
COVERED_ELSEWHERE = {
    "must_not_call_unnecessary_tools": "checked by the tool evaluator",
}


def expects_yes(flag):
    return not flag.startswith("must_not_")


def run_flag(flag, ctx, judge):
    severity = "critical" if flag in CRITICAL_FLAGS else "normal"

    if flag in COVERED_ELSEWHERE:
        return make_check(flag, None, "covered_elsewhere", COVERED_ELSEWHERE[flag])

    rule = FLAG_RULES.get(flag)
    question = FLAG_QUESTIONS.get(flag)

    if rule is not None:
        passed, detail = rule(ctx)

        # A passing rule is final. A failing rule is final too, unless the
        # flag also has a judge question: the phrasing may just be unusual.
        if passed or question is None or judge is None:
            return make_check(flag, passed, "rule", detail, severity)

    if question is None:
        return make_check(
            flag, None, "none", "no checker is defined for this flag"
        )

    if judge is None:
        return make_check(
            flag, None, "judge", "skipped: the judge is not available"
        )

    try:
        verdict, reason = judge(build_judge_prompt(question, ctx))
    except Exception as exc:
        return make_check(flag, None, "judge_error", str(exc), severity)

    return make_check(
        flag, verdict == expects_yes(flag), "judge", reason, severity
    )


# ---------------------------------------------------------------------------
# The judge (an LLM answering one yes/no question at a time)
# ---------------------------------------------------------------------------

class JudgeError(Exception):
    pass


def build_judge_prompt(question, ctx):
    parts = []

    if ctx["documents"]:
        numbered = "\n".join(
            f"[{index}] {document}"
            for index, document in enumerate(ctx["documents"], start=1)
        )
        parts.append(f"Documents:\n{numbered}")

    if ctx["tool_results"]:
        parts.append(
            "Tool results:\n"
            + json.dumps(ctx["tool_results"], ensure_ascii=False)
        )

    evidence = "\n\n".join(parts) or "(none)"

    return (
        "You are a strict evaluator of a customer-support assistant.\n\n"
        f"User message:\n{ctx['query']}\n\n"
        f"Assistant answer:\n{ctx['answer']}\n\n"
        f"Evidence available to the assistant:\n{evidence}\n\n"
        f"Question: {question}\n"
        "Start your reply with exactly one word, yes or no, "
        "then one short sentence explaining why."
    )


def make_judge():
    """
    Return judge(prompt) -> (verdict: bool, reason: str),
    or None when no API key / client library is available.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    client = OpenAI(api_key=api_key, base_url=JUDGE_BASE_URL)

    def judge(prompt):
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            temperature=0,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content or ""
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

        match = re.match(r"(yes|no)\b", text, flags=re.IGNORECASE)

        if match is None:
            raise JudgeError(f"unparsable judge answer: {text[:80]!r}")

        return match.group(1).lower() == "yes", text

    return judge


# ---------------------------------------------------------------------------
# One scenario
# ---------------------------------------------------------------------------

def build_context(scenario, outcome):
    behavior = outcome.get("actual_behavior") or {}
    actual_outcome = outcome.get("actual_outcome") or {}

    evidence = outcome.get("evidence")
    evidence_data = evidence or {}

    return {
        "query": scenario["input"]["query"],
        "answer": actual_outcome.get("final_answer") or "",
        "route": behavior.get("route"),
        "executed": behavior.get("executed_tools") or [],
        "retrieval_performed": behavior.get("retrieval_performed"),
        "human_review_required": behavior.get("human_review_required"),
        "human_review_expected":
            scenario["expected_behavior"]["human_review_expected"],
        "has_evidence": evidence is not None,
        "documents": [
            (d.get("content") or "")
            for d in evidence_data.get("retrieved_documents") or []
        ],
        "tool_results": evidence_data.get("tool_results") or [],
        "scores": evidence_data.get("scores"),
    }


def evaluate_scenario(scenario, outcome, judge=None):
    result = {
        "id": scenario["id"],
        "category": scenario["category"],
        "passed": False,
        "critical": [],
        "incomplete": False,
        "checks": [],
        "reason": "",
    }

    if outcome is None:
        result["reason"] = "scenario was not run"
        return result

    checks = check_existence(outcome, scenario)

    gate_failed = [
        c for c in checks if c["name"] in GATE_CHECKS and c["passed"] is False
    ]

    if not gate_failed:
        ctx = build_context(scenario, outcome)

        checks += check_format(ctx["answer"])
        checks += check_generic(ctx)

        for flag, wanted in scenario.get("expected_outcome", {}).items():
            if wanted:
                checks.append(run_flag(flag, ctx, judge))

    result["checks"] = checks

    failed = [c for c in checks if c["passed"] is False]

    result["passed"] = not failed
    result["critical"] = [
        c["name"] for c in failed if c["severity"] == "critical"
    ]
    result["incomplete"] = any(
        c["passed"] is None and c["method"] != "covered_elsewhere"
        for c in checks
    )
    result["reason"] = "; ".join(
        f"{c['name']}: {c['detail']}" if c["detail"] else c["name"]
        for c in failed
    )

    return result


def evaluate_outcomes(dataset, outcomes, judge=None):
    outcomes_by_id = index_by_id(outcomes)

    return [
        evaluate_scenario(scenario, outcomes_by_id.get(scenario["id"]), judge)
        for scenario in dataset
    ]


# ---------------------------------------------------------------------------
# Summary, saving, printing
# ---------------------------------------------------------------------------

def summarize(results):
    by_category = {}
    by_check = {}

    for r in results:
        stats = by_category.setdefault(r["category"], {"passed": 0, "total": 0})
        stats["total"] += 1
        stats["passed"] += r["passed"]

        for c in r["checks"]:
            check_stats = by_check.setdefault(
                c["name"], {"passed": 0, "failed": 0, "skipped": 0}
            )

            if c["passed"] is True:
                check_stats["passed"] += 1
            elif c["passed"] is False:
                check_stats["failed"] += 1
            else:
                check_stats["skipped"] += 1

    return {
        "passed": sum(r["passed"] for r in results),
        "total": len(results),
        "by_category": by_category,
        "by_check": by_check,
        "critical_failures": [r["id"] for r in results if r["critical"]],
        "incomplete": [r["id"] for r in results if r["incomplete"]],
    }


def save_results(results, summary, judge_model, path=RESULTS_PATH):
    """Write everything the report needs into one JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "evaluator": "outcome",
        "dataset_path": str(DATASET_PATH.relative_to(PROJECT_ROOT)),
        "outcome_path": str(OUTCOME_PATH.relative_to(PROJECT_ROOT)),
        "judge_model": judge_model,
        "summary": summary,
        "results": results,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)


def print_summary(results, summary):
    print(f"Outcome: {summary['passed']} / {summary['total']} passed\n")

    print("By category:")
    for category, stats in summary["by_category"].items():
        print(f"  {category:14} {stats['passed']} / {stats['total']}")

    print("\nBy check:")
    print(f"  {'check':42}{'passed':>8}{'failed':>8}{'skipped':>9}")
    for name, stats in sorted(summary["by_check"].items()):
        print(
            f"  {name:42}{stats['passed']:>8}{stats['failed']:>8}"
            f"{stats['skipped']:>9}"
        )

    print("\nCritical failures:")
    if summary["critical_failures"]:
        for scenario_id in summary["critical_failures"]:
            print(f"  {scenario_id}")
    else:
        print("  none")

    if summary["incomplete"]:
        print(
            "\nIncomplete (some checks were skipped): "
            + ", ".join(summary["incomplete"])
        )

    print("\nFailures:")
    for r in results:
        if not r["passed"]:
            print(f"  {r['id']}: {r['reason']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="skip the LLM judge (semantic flags are reported as skipped)",
    )
    args = parser.parse_args()

    judge = None if args.no_judge else make_judge()

    if judge is None:
        print("Judge is off: semantic flags will be skipped.\n")

    results = evaluate_outcomes(
        load_json(DATASET_PATH),
        load_json(OUTCOME_PATH),
        judge,
    )
    summary = summarize(results)

    print_summary(results, summary)
    save_results(results, summary, JUDGE_MODEL if judge else None)
    print(f"\nSaved to {RESULTS_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()