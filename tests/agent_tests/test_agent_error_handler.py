from __future__ import annotations

import unittest

from agent.errors import (
    AgentErrorHandler,
    ErrorType, 
    TransientError,
    PermanentError,
)

from agent.state import AgentState



class ErrorHandlerTest(unittest.TestCase):

    def setUp(self):
        self.handler = AgentErrorHandler()
        self.state = AgentState(
            current_node="test_node"
        )

    def test_transient_error_handler(self):
        # Arrange
        error = TransientError("temporary failure")

        # Act
        result = self.handler.handle(error, self.state)

        # Assert
        self.assertEqual(result["type"], ErrorType.TRANSIENT)
        self.assertTrue(result["retryable"])
        self.assertEqual(result["message"], "temporary failure")
        self.assertEqual(result["node"], "test_node")
        self.assertEqual(result["retry_count"], 0)

        print("Transient error: PASSED.")


    def test_permanent_error_handler(self):

        # Arrange
        error = PermanentError("permanent failure")

        # Act
        result = self.handler.handle(error, self.state)

        # Assert
        self.assertEqual(result["type"], ErrorType.PERMANENT)
        self.assertFalse(result["retryable"])
        self.assertEqual(result["message"], "permanent failure")
        self.assertEqual(result["node"], "test_node")
        self.assertEqual(result["retry_count"], 0)

        print("Permanent error: PASSED.")

    
    def test_unknown_error_handler(self):

        # Arrange
        error = Exception("unknown failure")

        # Act
        result = self.handler.handle(error, self.state)

        # Assert
        self.assertEqual(result["type"], ErrorType.UNKNOWN)
        self.assertIsNone(result["retryable"])
        self.assertEqual(result["message"], "unknown failure")
        self.assertEqual(result["node"], "test_node")
        self.assertEqual(result["retry_count"], 0)

        print("Unknown error: PASSED.")



if __name__ == "__main__":

    unittest.main()