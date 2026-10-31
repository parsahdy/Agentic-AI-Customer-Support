# Evaluation Strategy

The project evaluates both the quality of retrieved/generated answers and the agent's behavior across complete scenarios.

## Runtime Evaluation

The RAG path uses:

- **RetrievalEvaluator:** Checks retrieval relevance and produces retrieval scores.
- **FaithfulnessEvaluator:** Estimates whether the generated answer is supported by retrieved context.
- **ConfidenceEvaluator:** Combines evaluation signals into a confidence score.

Low-confidence results can be sent to the human-review path.

## Scenario-Based Evaluation

The evaluation dataset is stored at:

```text
evaluation/dataset/agent_evaluation.json
```

Each scenario defines an input, expected behavior, and expected outcome. Scenarios cover direct answers, RAG requests, and tool-related requests.

Run the evaluation runner with:

```bash
python -m evaluation.runner.agent_evaluation_runner
```

The runner invokes `AgentService` for each scenario and writes observed outcomes to `evaluation/dataset/agent_outcome.json`.

## What to Check

| Area | Evaluation question |
|---|---|
| Routing | Was the correct route selected? |
| Retrieval | Was retrieval performed when needed? |
| Tool selection | Were the appropriate tools selected? |
| Tool execution | Were tools executed with the expected arguments and result handling? |
| Human review | Were sensitive or low-confidence cases paused? |
| Final answer | Was the answer consistent with available evidence and tool results? |
| Error handling | Did the workflow recover or fail according to policy? |

The scenario runner records observed behavior; expected-versus-actual scoring and consolidated reporting can be expanded separately. Model-based scores should be interpreted as evaluation signals, not guarantees of correctness.
