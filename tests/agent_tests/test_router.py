import unittest
from unittest.mock import patch

from agent.nodes import router_node


class TestRouterNode(unittest.TestCase):

    @patch("agent.nodes.router")
    def test_router_returns_direct_route(self, mock_router):
        state = {
            "messages": [],
            "user_id": "user_1",
            "session_id": "session_1",
            "query": "Hello",
        }

        mock_router.route.return_value = "direct"

        result = router_node(state)

        self.assertEqual(result["route"], "direct")
        mock_router.route.assert_called_once_with(state)

    @patch("agent.nodes.router")
    def test_router_returns_rag_route(self, mock_router):
        state = {
            "messages": [],
            "user_id": "user_1",
            "session_id": "session_1",
            "query": "What is your return policy?",
        }

        mock_router.route.return_value = "rag"

        result = router_node(state)

        self.assertEqual(result["route"], "rag")
        mock_router.route.assert_called_once_with(state)

    @patch("agent.nodes.router")
    def test_router_returns_tool_route(self, mock_router):
        state = {
            "messages": [],
            "user_id": "user_1",
            "session_id": "session_1",
            "query": "Check my order status",
        }

        mock_router.route.return_value = "tool"

        result = router_node(state)

        self.assertEqual(result["route"], "tool")
        mock_router.route.assert_called_once_with(state)


if __name__ == "__main__":
    unittest.main()