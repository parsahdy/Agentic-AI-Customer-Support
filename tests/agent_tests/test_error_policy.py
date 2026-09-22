from __future__ import annotations

import unittest

from agent.errors import (
    ErrorPolicy,
    RecoveryAction,
    TransientError,
    PermanentError,
)

from agent.state import AgentState


class ErrorPolicyTest(unittest.TestCase):

    def setUp(self):
        self.policy = ErrorPolicy()
        self.state = AgentState(
            current_node="test_node"
        )


    def test_retry_recovery(self):

        error = TransientError("temporary failure")

        result = self.policy.policy(error, self.state)

        self.assertEqual(result, RecoveryAction.RETRY)

        print("Retry recovery test: PASSED.")


    def test_fail_recovery(self):

        error = PermanentError("permanent failure")
        
        result = self.policy.policy(error, self.state)

        self.assertEqual(result, RecoveryAction.FAIL)

        print("Fail recovery test: PASSED.")


    def test_unknown_recovery(self):

        error = Exception("unknown failure")
                
        result = self.policy.policy(error, self.state)

        self.assertEqual(result, RecoveryAction.HUMAN_REVIEW)

        print("Human review recovery test: PASSED.")


if __name__ == "__main__":

    unittest.main()