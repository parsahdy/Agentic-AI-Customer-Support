from __future__ import annotations

import unittest

from agent import AgentService
from agent.errors import ErrorPolicy, RetryPolicy
from agent.memory import MemoryService
from agent.tools import ToolRegistry

from knowledge_base.kb_service import KnowledgeBaseService
from evaluation import RetrievalEvaluator, ConfidenceEvaluator


class AgentWorkflowTest(unittest.TestCase):

    def setUp(self):
        # Core dependencies
        self.memory = MemoryService()
        self.registry = ToolRegistry()
        self.error_policy = ErrorPolicy()
        self.retry_policy = RetryPolicy()


    def test_direct_workflow(self):

        # Arrange
        agent = AgentService(
            memory=self.memory,
            registry=self.registry,
            retry_policy=self.retry_policy,
        )

        # Act
        result = agent.run(
            query= "I wanted to thank you for your excellent service.",
            user_id="user-3",
            session_id="session-3"
        )

        # Assert
        self.assertEqual(result["route"], "direct")
        self.assertIsNotNone(result["final_answer"])
        self.assertFalse(result["human_review_required"])


    def test_rag_workflow(self):

        # Arrange
        self.kb = KnowledgeBaseService()
        self.retrieval_evaluator = RetrievalEvaluator()
        self.confidence_evaluator = ConfidenceEvaluator()

        agent = AgentService(
            memory=self.memory,
            registry=self.registry,
            kb=self.kb,
            retrieval_evaluator=self.retrieval_evaluator, 
            confidence_evaluator=self.confidence_evaluator,
            retry_policy=self.retry_policy,
        )

        # Act
        result = agent.run(
            query= "How can i create an account?",
            user_id="user-5",
            session_id="session-5"
        )

        # Assert
        self.assertEqual(result["route"], "rag")
        self.assertTrue(result["retrieved_documents"])
        self.assertIsNotNone(result["retrieval_score"])
        self.assertIsNotNone(result["top1_score"])
        self.assertIsNotNone(result["mean_topk_score"])
        self.assertTrue(result["final_answer"])


    def test_tool_workflow(self):
        
        # Arrange 
        agent = AgentService(
            memory=self.memory,
            registry=self.registry,
            error_policy=self.error_policy,
            retry_policy=self.retry_policy,
        )

        # Act
        result = agent.run(
            query="What is the status of my order 1234?",
            user_id="user-6",
            session_id="session-6",
        )   

        # Assert
        self.assertEqual(result["route"], "tool")
        self.assertTrue(result["tool_calls"])
        self.assertEqual(
            result["tool_calls"][0]["name"],
            "get_order"
        )
        self.assertTrue(result["tool_results"])

        tool_result = result["tool_results"][0]

        self.assertTrue(tool_result["success"])
        self.assertEqual(
            tool_result["result"]["order_id"],
            1234,
        )
        self.assertEqual(
            tool_result["result"]["status"],
            "processing",
        )
        self.assertTrue(result["final_answer"])
        


    def test_human_review_workflow(self):

        # Arrange
        agent = AgentService(
            memory=self.memory,
            error_policy=self.error_policy,
            retry_policy=self.retry_policy,
        )

        # Act
        result = agent.run(
            query="I want my order with id 1234 to be canceled.",
            user_id="user-6",
            session_id="session-6",
        )

        # Assert
        self.assertEqual(result["route"], "tool")
        self.assertTrue(result["human_review_required"])
        self.assertIsNotNone(result["human_review_request"])
        self.assertIsNotNone(result["human_decision"])
        self.assertEqual(
            result["human_review_request"]["operation"],
            "cancel_order",
        )


if __name__ == "__main__":
    unittest.main()