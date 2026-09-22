from __future__ import annotations

import unittest
from unittest.mock import patch

from agent.errors import (
    RetryPolicy,
    TransientError,
    PermanentError,
)

class RetryPolicyTest(unittest.TestCase):

    def setUp(self):
        self.retry_policy = RetryPolicy(
            max_retries = 3,
            initial_delay = 1.0,
            max_delay = 30.0, 
            backoff_factor = 2.0, 
            jitter = 0.2,
    )


    def test_shoud_retry(self):

        error = TransientError("temporary failure.")

        result = self.retry_policy.should_retry(error, retry_count=2)

        self.assertTrue(result)

        print("transient error -> retry: PASSED")


    def test_should_not_retry(self):

        error = PermanentError("permanent failure.")
        
        result = self.retry_policy.should_retry(error, retry_count=2)

        self.assertFalse(result)

        print("permanent error -> no retry: PASSED")


    def test_should_not_retry_limit(self):

        error = TransientError("temporary failure.")
        
        result = self.retry_policy.should_retry(error, retry_count=6)

        self.assertFalse(result)

        print("retry count limit -> no retry: PASSED")


    def test_get_delay(self):

        with patch(
            "agent.errors.retry_policy.random.uniform",
            return_value=1.0,
        ):
            
            delay = self.retry_policy.get_delay(
                retry_count=4
            )

            self.assertEqual(delay, 9.0)

            print("get delay correctness: PASSED")


if __name__ == "__main__":

    unittest.main()