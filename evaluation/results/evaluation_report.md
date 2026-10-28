# Evaluation report

Generated at: 2026-10-28T14:25:06

## Overview

| evaluator | passed / total | failed | critical |
| --- | --- | --- | --- |
| routing | 34 / 44 | 10 | 0 |
| tool | 39 / 44 | 5 | 0 |

## Critical failures

None.

## Scenarios

| scenario | category | routing | tool |
| --- | --- | --- | --- |
| direct_001 | direct | pass | pass |
| direct_002 | direct | pass | pass |
| direct_003 | direct | pass | pass |
| direct_004 | direct | pass | pass |
| direct_005 | direct | pass | pass |
| direct_006 | direct | pass | pass |
| direct_007 | direct | FAIL | pass |
| direct_008 | direct | pass | pass |
| direct_009 | direct | pass | pass |
| direct_010 | direct | pass | pass |
| direct_011 | direct | pass | pass |
| rag_001 | rag | pass | pass |
| rag_002 | rag | FAIL | pass |
| rag_003 | rag | pass | pass |
| rag_004 | rag | FAIL | pass |
| rag_005 | rag | pass | pass |
| rag_006 | rag | pass | pass |
| rag_007 | rag | pass | pass |
| rag_008 | rag | FAIL | pass |
| rag_009 | rag | pass | pass |
| rag_010 | rag | FAIL | pass |
| rag_011 | rag | FAIL | pass |
| tool_001 | tool | pass | pass |
| tool_002 | tool | pass | pass |
| tool_003 | tool | pass | pass |
| tool_004 | tool | FAIL | FAIL |
| tool_005 | tool | pass | pass |
| tool_006 | tool | FAIL | FAIL |
| tool_007 | tool | FAIL | FAIL |
| tool_008 | tool | pass | pass |
| tool_009 | tool | FAIL | FAIL |
| tool_010 | tool | pass | pass |
| tool_011 | tool | pass | FAIL |
| human_review_001 | human_review | pass | pass |
| human_review_002 | human_review | pass | pass |
| human_review_003 | human_review | pass | pass |
| human_review_004 | human_review | pass | pass |
| human_review_005 | human_review | pass | pass |
| human_review_006 | human_review | pass | pass |
| human_review_007 | human_review | pass | pass |
| human_review_008 | human_review | pass | pass |
| human_review_009 | human_review | pass | pass |
| human_review_010 | human_review | pass | pass |
| human_review_011 | human_review | pass | pass |

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
