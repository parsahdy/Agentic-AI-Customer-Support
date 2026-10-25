"""
Terminal for the human operator.
 
Run it next to the API:
 
    python admin_cli.py
 
It checks the API every few seconds. When a request is waiting for a human,
it prints it and asks for a decision.
"""

import json
import sys
import time
 
import httpx

API_URL = "http://127.0.0.1:8000"
POLL_SECONDS = 3

DECISIONS = {
    "a": "approve",
    "r": "reject",
    "e": "escalate",
}


def show(review: dict) -> None:
    print("\n" + "=" * 60)
    print(f"Review ID : {review["review_id"]}")
    request = review["request"]
    print(f"User said : {request.get("request")}")
    print(f"Reason    : {request.get("reason")}")

    for operation in request.get("sensitive_operations", []):
        print(f"Operation : {operation['name']} {json.dumps(operation['arguments'])}")

        if request.get("generated_answer") is not None:
            print(f"Draft ans.: {request['generated_answer']}")
            print(f"Confidence: {request.get('confidence_score')}")
    
        print("=" * 60)


def ask_decision() -> dict:
    while True:
        choice = input("[a]pprove / [r]eject / [e]scalate : ").strip().lower()

        if choice in DECISIONS:
            comment = input("Comment (optional): ").strip() or None
            return {"decision": DECISIONS[choice], "comment": comment}
 
        print("Please type a, r or e.")


def main() -> None:
    print(f"Watching {API_URL} for reviews. Ctrl+C to stop.")

    with httpx.Client(base_url=API_URL, timeout=120) as client:
        while True:
            try:
                pending = client.get("/agent/reviews/pending").json()
            except httpx.HTTPError as exc:
                print(f"API not reachable: {exc}")
                pending = []

            for review in pending:
                show(review)
                decision = ask_decision()

                response = client.post(
                    f"/agent/reviews/{review['review_id']}/decision",
                    json=decision,
                )
                print("->", response.status_code, response.json().get("final_answer"))

                time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
