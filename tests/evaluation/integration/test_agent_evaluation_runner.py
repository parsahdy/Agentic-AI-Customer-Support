import unittest
from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from agent import AgentService, ToolRegistry, ToolExecutor


class TestAgentEvaluationRunner(unittest.TestCase):

    def setUp(self):
        self.memory_service_mock = Mock()

        self.memory_service_mock.get_checkpointer.return_value = (
            InMemorySaver()
        )
        self.memory_service_mock.get_store.return_value = InMemoryStore()

        self.memory_service_mock.search_memories.return_value = []
        self.memory_service_mock.save_memory.return_value = None


    def test_evaluation_runner_runs_direct_route(self):
        with (
            patch("agent.nodes.router") as mock_router,
            patch("agent.nodes.create_llm") as mock_create_llm,
            patch("agent.nodes.create_tool_llm") as mock_create_tool_llm,
        ):
            # 1. Force the router to select the direct route.
            mock_router.route.return_value = "direct"

            # 2. Return a predictable response from the LLM.
            mock_llm = Mock()
            mock_llm.invoke.return_value = AIMessage(
                content="Test answer"
            )
            mock_create_llm.return_value = mock_llm

            # 3. Prevent real tool-LLM initialization during graph building.
            mock_create_tool_llm.return_value = Mock()

            # 4. Build the service while dependencies are patched.
            agent = AgentService(
                memory=self.memory_service_mock
            )

            # 5. Execute the real graph.
            result = agent.run(
                query="Test input",
                user_id="test_user",
                session_id="test_session",
            )

            # 6. Verify the result and routing behavior.
            self.assertEqual(result["final_answer"], "Test answer")
            self.assertEqual(result["route"], "direct")
            mock_router.route.assert_called_once()
            mock_llm.invoke.assert_called_once()


    def _run_rag_test(self, confidence_score: float):
        confidence_evaluator = Mock()
        confidence_evaluator.calculate.return_value = confidence_score

        faithfulness_evaluator = Mock()
        faithfulness_evaluator.evaluate.return_value = 0.95

        retrieval_evaluator = Mock()
        retrieval_evaluator.evaluate.return_value = 0.9

        kb = Mock()
        kb.search.return_value = {
            "retrieval_documents": [
                {"content": "Test retrieved context"}
            ],
            "top1_score": 0.95,
            "mean_topk_score": 0.9,
        }

        with (
            patch("agent.nodes.router") as mock_router,
            patch("agent.nodes.create_llm") as mock_create_llm,
            patch("agent.nodes.create_tool_llm") as mock_create_tool_llm,
        ):
            # 1. Force the router to select the RAG route.
            mock_router.route.return_value = "rag"

            # 2. Return a predictable response from the LLM.
            mock_llm = Mock()
            mock_llm.invoke.return_value = AIMessage(
                content="RAG answer"
            )
            mock_create_llm.return_value = mock_llm

            # 3. Prevent real tool-LLM initialization during graph building.
            mock_create_tool_llm.return_value = Mock()

            # 4. Build the service while dependencies are patched.
            agent = AgentService(
                memory=self.memory_service_mock,
                kb=kb,
                retrieval_evaluator=retrieval_evaluator,
                faithfulness_evaluator=faithfulness_evaluator,
                confidence_evaluator=confidence_evaluator,
            )

            # 5. Execute the real graph.
            result = agent.run(
                query="Test input",
                user_id="test_user",
                session_id="test_session",
            )

        return result, agent


    def test_evaluation_runner_runs_rag_route_without_hitl(self):
        result, _ = self._run_rag_test(confidence_score=0.9)

        self.assertEqual(result["final_answer"], "RAG answer")
        self.assertEqual(result["route"], "rag")
        self.assertEqual(result["confidence_score"], 0.9)
        self.assertFalse(result["human_review_required"])


    def test_evaluation_runner_runs_rag_route_with_hitl(self):
        result, _ = self._run_rag_test(confidence_score=0.3)

        self.assertEqual(result["route"], "rag")
        self.assertEqual(result["confidence_score"], 0.3)
        self.assertTrue(result["human_review_required"])
        self.assertIsNotNone(result["human_review_request"])


    def _run_tool_test(self, tool_name: str, arguments: dict):
        with (
            patch("agent.nodes.router") as mock_router,
            patch("agent.nodes.create_llm") as mock_create_llm,
            patch("agent.nodes.create_tool_llm") as mock_create_tool_llm,
        ):

            mock_router.route.return_value = "tool"

            mock_llm = Mock()
            mock_llm.invoke.return_value = AIMessage(
                content="Tool execution answer"
            )
            mock_create_llm.return_value = mock_llm

            mock_tool_llm = Mock()
            mock_tool_llm.invoke.return_value = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": tool_name,
                        "args": arguments,
                        "id": "call_id_001",
                        "type": "tool_call",
                    }
                ],
            )
            mock_create_tool_llm.return_value = mock_tool_llm

            agent = AgentService(
                memory=self.memory_service_mock,
            )

            result = agent.run(
                query="Run {tool_name}",
                user_id="test_user",
                session_id="test_session",
            )

            return result, agent


    def test_tool_route_get_order_without_hitl(self):
        result, _ = self._run_tool_test(
            tool_name="get_order",
            arguments={"order_id": "123"},
        )

        self.assertEqual(result["route"], "tool")
        self.assertFalse(result["human_review_required"])

        self.assertTrue(result["tool_results"])
        self.assertTrue(result["tool_results"][0]["success"])
        self.assertEqual(
            result["tool_results"][0]["result"]["status"],
            "processing",
        )


    def test_tool_route_cancel_order_with_hitl(self):
        result, _ = self._run_tool_test(
            tool_name="cancel_order",
            arguments={"order_id": 123},
        )

        self.assertEqual(result["route"], "tool")
        self.assertTrue(result["human_review_required"])
        self.assertIsNotNone(result["human_review_request"])



if __name__ == "__main__":
    unittest.main()