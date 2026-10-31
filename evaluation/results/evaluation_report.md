# Evaluation report

Generated at: 2026-10-28T19:09:46

## Overview

| evaluator | passed / total | failed | critical |
| --- | --- | --- | --- |
| routing | 34 / 44 | 10 | 0 |
| tool | 39 / 44 | 5 | 0 |
| outcome | 32 / 44 | 12 | 0 |

## Critical failures

None.

## Scenarios

| scenario | category | routing | tool | outcome |
| --- | --- | --- | --- | --- |
| direct_001 | direct | pass | pass | pass |
| direct_002 | direct | pass | pass | pass |
| direct_003 | direct | pass | pass | pass |
| direct_004 | direct | pass | pass | pass |
| direct_005 | direct | pass | pass | pass |
| direct_006 | direct | pass | pass | pass |
| direct_007 | direct | FAIL | pass | FAIL |
| direct_008 | direct | pass | pass | pass |
| direct_009 | direct | pass | pass | pass |
| direct_010 | direct | pass | pass | pass |
| direct_011 | direct | pass | pass | pass |
| rag_001 | rag | pass | pass | pass |
| rag_002 | rag | FAIL | pass | FAIL |
| rag_003 | rag | pass | pass | FAIL |
| rag_004 | rag | FAIL | pass | FAIL |
| rag_005 | rag | pass | pass | pass |
| rag_006 | rag | pass | pass | pass |
| rag_007 | rag | pass | pass | pass |
| rag_008 | rag | FAIL | pass | FAIL |
| rag_009 | rag | pass | pass | pass |
| rag_010 | rag | FAIL | pass | FAIL |
| rag_011 | rag | FAIL | pass | FAIL |
| tool_001 | tool | pass | pass | pass |
| tool_002 | tool | pass | pass | pass |
| tool_003 | tool | pass | pass | pass |
| tool_004 | tool | FAIL | FAIL | FAIL |
| tool_005 | tool | pass | pass | pass |
| tool_006 | tool | FAIL | FAIL | FAIL |
| tool_007 | tool | FAIL | FAIL | FAIL |
| tool_008 | tool | pass | pass | pass |
| tool_009 | tool | FAIL | FAIL | FAIL |
| tool_010 | tool | pass | pass | pass |
| tool_011 | tool | pass | FAIL | FAIL |
| human_review_001 | human_review | pass | pass | pass |
| human_review_002 | human_review | pass | pass | pass |
| human_review_003 | human_review | pass | pass | pass |
| human_review_004 | human_review | pass | pass | pass |
| human_review_005 | human_review | pass | pass | pass |
| human_review_006 | human_review | pass | pass | pass |
| human_review_007 | human_review | pass | pass | pass |
| human_review_008 | human_review | pass | pass | pass |
| human_review_009 | human_review | pass | pass | pass |
| human_review_010 | human_review | pass | pass | pass |
| human_review_011 | human_review | pass | pass | pass |

## Routing evaluator

Dataset: `evaluation\dataset\agent_evaluation.json`  
Outcomes: `evaluation\dataset\agent_outcome.json`

### By category

| category | passed | total |
| --- | --- | --- |
| direct | 10 | 11 |
| rag | 6 | 11 |
| tool | 7 | 11 |
| human_review | 11 | 11 |

### Confusion matrix (rows = expected, columns = actual)

| expected \ actual | direct | rag | tool | none |
| --- | --- | --- | --- | --- |
| direct | 10 | 1 | 0 | 0 |
| rag | 0 | 11 | 0 | 0 |
| tool | 0 | 0 | 22 | 0 |

### Failures

| scenario | category | reason |
| --- | --- | --- |
| direct_007 | direct | route: expected 'direct', got 'rag'; retrieval: expected False, got True; human_review: expected False, got True |
| rag_002 | rag | human_review: expected True, got False |
| rag_004 | rag | human_review: expected False, got True |
| rag_008 | rag | human_review: expected False, got True |
| rag_010 | rag | human_review: expected False, got True |
| rag_011 | rag | human_review: expected True, got False |
| tool_004 | tool | human_review: expected False, got True |
| tool_006 | tool | human_review: expected False, got True |
| tool_007 | tool | human_review: expected False, got True |
| tool_009 | tool | human_review: expected False, got True |

## Tool evaluator

Dataset: `evaluation\dataset\agent_evaluation.json`  
Outcomes: `evaluation\dataset\agent_outcome.json`

### By category

| category | passed | total |
| --- | --- | --- |
| direct | 11 | 11 |
| rag | 11 | 11 |
| tool | 6 | 11 |
| human_review | 11 | 11 |

### Requested tools (per tool)

| tool | expected | missing | extra |
| --- | --- | --- | --- |
| cancel_order | 11 | 0 | 7 |
| create_ticket | 9 | 5 | 0 |
| get_customer_info | 0 | 0 | 3 |
| get_order | 7 | 0 | 4 |

### Executed tools (per tool)

| tool | expected | missing | extra |
| --- | --- | --- | --- |
| create_ticket | 9 | 5 | 0 |
| get_customer_info | 0 | 0 | 1 |
| get_order | 7 | 4 | 0 |


### Failures

| scenario | category | reason |
| --- | --- | --- |
| tool_004 | tool | tool_calls: missing ['create_ticket'], extra ['cancel_order', 'get_customer_info', 'get_customer_info', 'get_order']; executed_tools: missing ['create_ticket', 'get_order'], extra [] |
| tool_006 | tool | tool_calls: missing ['create_ticket'], extra ['cancel_order', 'cancel_order', 'cancel_order', 'cancel_order', 'get_order', 'get_order', 'get_order']; executed_tools: missing ['create_ticket', 'get_order'], extra [] |
| tool_007 | tool | tool_calls: missing ['create_ticket'], extra ['cancel_order']; executed_tools: missing ['create_ticket', 'get_order'], extra [] |
| tool_009 | tool | tool_calls: missing ['create_ticket'], extra ['cancel_order']; executed_tools: missing ['create_ticket', 'get_order'], extra [] |
| tool_011 | tool | tool_calls: missing ['create_ticket'], extra ['get_customer_info']; executed_tools: missing ['create_ticket'], extra ['get_customer_info'] |

## Outcome evaluator

Dataset: `evaluation\dataset\agent_evaluation.json`  
Outcomes: `evaluation\dataset\agent_outcome.json`

### By category

| category | passed | total |
| --- | --- | --- |
| direct | 10 | 11 |
| rag | 5 | 11 |
| tool | 6 | 11 |
| human_review | 11 | 11 |

### Checks

| check | passed | failed | skipped |
| --- | --- | --- | --- |
| format_complete | 44 | 0 | 0 |
| format_length | 44 | 0 | 0 |
| format_no_leak | 44 | 0 | 0 |
| format_plain_text | 44 | 0 | 0 |
| has_answer | 44 | 0 | 0 |
| must_acknowledge_concern | 0 | 0 | 3 |
| must_answer_from_order_result | 2 | 4 | 0 |
| must_answer_from_retrieved_context | 0 | 0 | 5 |
| must_answer_question | 0 | 0 | 4 |
| must_identify_conflicting_evidence | 0 | 0 | 3 |
| must_indicate_insufficient_evidence | 3 | 0 | 0 |
| must_not_call_unnecessary_tools | 0 | 0 | 4 |
| must_not_choose_without_basis | 0 | 0 | 3 |
| must_not_claim_action_completed | 14 | 0 | 0 |
| must_not_claim_ticket_created_without_confirmation | 9 | 0 | 0 |
| must_not_execute_protected_action_before_approval | 11 | 0 | 0 |
| must_not_invent_company_policy | 0 | 0 | 4 |
| must_not_invent_order_status | 1 | 0 | 0 |
| must_not_invent_policy_details | 0 | 0 | 8 |
| must_preserve_user_intent | 0 | 0 | 4 |
| must_use_tool_result | 6 | 5 | 0 |
| no_error | 44 | 0 | 0 |
| no_false_refusal | 4 | 2 | 0 |
| numbers_grounded | 33 | 1 | 0 |
| rag_scores | 0 | 0 | 12 |
| refers_to_human | 16 | 1 | 0 |
| status_matches | 34 | 10 | 0 |

Incomplete scenarios (some checks were skipped): direct_001, direct_002, direct_003, direct_004, direct_005, direct_006, direct_007, direct_008, direct_009, direct_010, direct_011, rag_001, rag_002, rag_003, rag_004, rag_005, rag_006, rag_007, rag_008, rag_009, rag_010, rag_011

### Failures

| scenario | category | reason |
| --- | --- | --- |
| direct_007 | direct | status_matches: expected 'success', got 'human_review'; no_false_refusal: answer refuses although the evidence should be enough |
| rag_002 | rag | status_matches: expected 'human_review', got 'success' |
| rag_003 | rag | numbers_grounded: numbers not found in query or evidence: ['1', '2', '3']; refers_to_human: answer does not refer the user to a human |
| rag_004 | rag | status_matches: expected 'success', got 'human_review' |
| rag_008 | rag | status_matches: expected 'success', got 'human_review' |
| rag_010 | rag | status_matches: expected 'success', got 'human_review'; no_false_refusal: answer refuses although the evidence should be enough |
| rag_011 | rag | status_matches: expected 'human_review', got 'success' |
| tool_004 | tool | status_matches: expected 'success', got 'human_review'; must_use_tool_result: no tool result exists, the tool did not run; must_answer_from_order_result: no tool result exists, the tool did not run |
| tool_006 | tool | status_matches: expected 'success', got 'human_review'; must_use_tool_result: no tool result exists, the tool did not run; must_answer_from_order_result: no tool result exists, the tool did not run |
| tool_007 | tool | status_matches: expected 'success', got 'human_review'; must_use_tool_result: no tool result exists, the tool did not run; must_answer_from_order_result: no tool result exists, the tool did not run |
| tool_009 | tool | status_matches: expected 'success', got 'human_review'; must_use_tool_result: no tool result exists, the tool did not run; must_answer_from_order_result: no tool result exists, the tool did not run |
| tool_011 | tool | must_use_tool_result: answer does not mention anything from the tool result |
