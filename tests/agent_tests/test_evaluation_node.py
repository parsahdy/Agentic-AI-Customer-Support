from __future__ import annotations

import unittest
from unittest.mock import Mock, AsyncMock

from agent.nodes import create_evaluation_node



class AgentWorkflowTest(unittest.IsolatedAsyncioTestCase):

    async def test_evaluation_node_calculates_scores(self):
        # Arrange
        faithfulness_evaluator = Mock()
        confidence_evaluator = Mock()

        faithfulness_evaluator.evaluate = AsyncMock(return_value=0.8)
        confidence_evaluator.calculate.return_value = 0.72

        evaluation_node = create_evaluation_node(
            faithfulness_evaluator=faithfulness_evaluator,
            confidence_evaluator=confidence_evaluator,
        )

        state = {
            "query": "How can I create an account?",
            "final_answer": "You can create an account from the signup page.",
            "retrieved_documents": [
                {"content": "To create an account, visit the signup page."}
            ],
            "top1_score": 0.77,
            "mean_topk_score": 0.36,
        }

        # Act
        result = await evaluation_node(state)

        # Assert
        self.assertEqual(result["faithfulness_score"], 0.8)
        self.assertEqual(result["confidence_score"], 0.72)

        faithfulness_evaluator.evaluate.assert_awaited_once_with(
            query=state["query"],
            final_answer=state["final_answer"],
            retrieved_contexts=state["retrieved_documents"],
        )

        confidence_evaluator.calculate.assert_called_once_with(
            top1_score=state["top1_score"],
            mean_topk_score=state["mean_topk_score"],
            faithfulness_score=0.8,
        )
