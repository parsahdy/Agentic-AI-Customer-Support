import unittest
from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage

from agent.agent_service import AgentService
from agent.memory.memory_service import MemoryService
from agent.tools.registry import ToolRegistry
from agent.errors.retry_policy import RetryPolicy
from agent.errors.error_policy import ErrorPolicy
from knowledge_base.kb_service import KnowledgeBaseService


class AgentWorkflowMockTest(unittest.TestCase):

    def setUp(self):
        # External dependencies
        self.memory = Mock(spec=MemoryService)
        self.registry = Mock(spec=ToolRegistry)
        self.kb = Mock(spec=KnowledgeBaseService)

        # Policies
        self.retry_policy = Mock(spec=RetryPolicy)
        self.error_policy = Mock(spec=ErrorPolicy)

        # Checkpointer / Store required by LangGraph
        self.memory.get_checkpointer.return_value = None
        self.memory.get_store.return_value = None

        # Memory dependency
        self.memory.search_memories.return_value = []

        # Tool dependency
        self.registry.get_tools.return_value = []

    @patch("agent.nodes.create_llm")
    @patch("agent.nodes.router")
    def test_direct_workflow(
        self,
        mock_router,
        mock_create_llm,
    ):
        """
        Direct request should follow:

        START
        → load_memory
        → router
        → llm
        → save_memory
        → END
        """

        # Arrange
        mock_router.route.return_value = "direct"

        mock_llm = Mock()
        mock_llm.invoke.return_value = AIMessage(
            content="You're very welcome! I'm happy to help."
        )
        mock_create_llm.return_value = mock_llm

        agent = AgentService(
            memory=self.memory,
            registry=self.registry,
            kb=self.kb,
            retry_policy=self.retry_policy,
            error_policy=self.error_policy,
        )

        # Act
        result = agent.run(
            query="I wanted to thank you for your excellent service.",
            user_id="user-1",
            session_id="session-1",
        )

        # Assert
        self.assertEqual(result["route"], "direct")
        self.assertTrue(result["final_answer"])
        self.assertFalse(result["human_review_required"])
        self.assertEqual(result["retrieved_documents"], [])
        self.assertEqual(result["error"], {})

        mock_router.route.assert_called_once()
        mock_create_llm.assert_called_once()
        mock_llm.invoke.assert_called_once()


if __name__ == "__main__":
    unittest.main()