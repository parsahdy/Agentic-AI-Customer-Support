from __future__ import annotations

import unittest
from unittest.mock import Mock

from agent.agent_service import (
    AgentService,
    InputGuardrailError,
)
from agent.memory.memory_service import MemoryService
from agent.tools.registry import ToolRegistry
from agent.errors.retry_policy import RetryPolicy
from agent.errors.error_policy import ErrorPolicy
from knowledge_base.kb_service import KnowledgeBaseService


class TestInputGuardrail(unittest.TestCase):

    def setUp(self):
        self.memory = Mock(spec=MemoryService)
        self.registry = Mock(spec=ToolRegistry)
        self.kb = Mock(spec=KnowledgeBaseService)
        self.retry_policy = Mock(spec=RetryPolicy)
        self.error_policy = Mock(spec=ErrorPolicy)

        self.memory.get_checkpointer.return_value = None
        self.memory.get_store.return_value = None
        self.memory.search_memories.return_value = []

        self.registry.get_tools.return_value = []   

        self.agent = AgentService(
            memory=self.memory,
            registry=self.registry,
            kb=self.kb,
            retry_policy=self.retry_policy,
            error_policy=self.error_policy,
        )

        self.agent.graph = Mock()

        self.user_id = "user_1"
        self.session_id = "session_1"


    def test_allow_valid_input(self):
        query = "I wanted to thank you for your excellent service."

        self.agent.graph.invoke.return_value = {
            "route": "direct",
            "final_answer": "You're welcome!",
            "error": None,
        }

        result = self.agent.run(
            query=query,
            user_id=self.user_id,
            session_id=self.session_id
        )

        self.assertEqual(result["route"], "direct")
        self.assertEqual(result["final_answer"], "You're welcome!")

        self.agent.graph.invoke.assert_called_once()

        initial_state = self.agent.graph.invoke.call_args.args[0]

        self.assertEqual(initial_state["query"], query)
        self.assertEqual(initial_state["user_id"], self.user_id)
        self.assertEqual(initial_state["session_id"], self.session_id)


    def test_block_empty_input(self):
        with self.assertRaises(InputGuardrailError):
            self.agent.run(
                query="",
                user_id=self.user_id,
                session_id=self.session_id,
            )

        self.agent.graph.invoke.assert_not_called()


    def test_block_whitspace_input(self):
        with self.assertRaises(InputGuardrailError):
            self.agent.run(
                query="  \n\t",
                user_id=self.user_id,
                session_id=self.session_id,
            )

        self.agent.graph.invoke.assert_not_called()


    def test_block_input_exceeding_max_length(self):
        query = "a" * 10_001

        with self.assertRaises(InputGuardrailError):
            self.agent.run(
                query=query,
                user_id=self.user_id,
                session_id=self.session_id,
            )

        self.agent.graph.invoke.assert_not_called()


    def test_block_forbidden_control_character(self):
        query = "Hello\x00World"

        with self.assertRaises(InputGuardrailError):
            self.agent.run(
                query=query,
                user_id=self.user_id,
                session_id=self.session_id,
            )

        self.agent.graph.invoke.assert_not_called()


    def test_allow_normal_newline_and_tab(self):
        query = "Hello!\nI need help with my order.\tOrder ID: 123"


        self.agent.graph.invoke.return_value = {
            "route": "direct",
            "final_answer": "How can I help?",
            "error": None,
        }

        result = self.agent.run(
            query=query,
            user_id=self.user_id,
            session_id=self.session_id,
        )

        self.assertTrue(result["final_answer"])
        self.agent.graph.invoke.assert_called_once()


    def test_reject_missing_user_id(self):
        with self.assertRaises(ValueError):
            self.agent.run(
                query="Hello",
                user_id=" ",
                session_id=self.session_id,
            )

        self.agent.graph.invoke.assert_not_called()    


    def test_reject_missing_session_id(self):
        with self.assertRaises(ValueError):
            self.agent.run(
                query="Hello",
                user_id=self.user_id,
                session_id=" ",
            )

        self.agent.graph.invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()