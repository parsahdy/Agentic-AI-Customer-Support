from __future__ import annotations

from unittest.mock import patch

from agent.errors import (
ErrorClassifier,
ErrorType,
PermanentToolError,
RetryPolicy,
TransientToolError,
)
from agent.tools import ToolExecutor


class FakeTool:

    def __init__(self, failures_before_success: int = 0):
        self.failures_before_success = failures_before_success
        self.attempts = 0


    def invoke(self, arguments):
        self.attempts += 1

        if self.attempts <= self.failures_before_success:
            raise TransientToolError(
                "Temporary tool failure."
            )

        return {
            "message": "Tool succeeded."
        }


class AlwaysFailingTool:

    def __init__(self):
        self.attempts = 0


    def invoke(self, arguments):
        self.attempts += 1

        raise TransientToolError(
            "Temporary tool failure."
        )


class PermanentFailingTool:

    def __init__(self):
        self.attempts = 0


    def invoke(self, arguments):
        self.attempts += 1

        raise PermanentToolError(
            "Permanent tool failure."
        )


class FakeRegistry:

    def __init__(self, tool):
        self.tool = tool


    def get_tool(self, tool_name):
        return self.tool


class ErrorHandlingTest:

    @staticmethod
    def test_transient_error_classification():

        error = TransientToolError(
            "Temporary failure."
        )

        result = ErrorClassifier.classify(error)

        assert result == ErrorType.TRANSIENT

        print("Transient classification: PASSED")


    @staticmethod
    def test_permanent_error_classification():

        error = PermanentToolError(
            "Permanent failure."
        )

        result = ErrorClassifier.classify(error)

        assert result == ErrorType.PERMANENT

        print("Permanent classification: PASSED")


    @staticmethod
    def test_retry_then_success():

        tool = FakeTool(
            failures_before_success=2
        )

        registry = FakeRegistry(tool)

        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0,
            max_delay=0,
        )

        executor = ToolExecutor(
            registry=registry,
            retry_policy=policy,
        )

        with patch("agent.tools.executor.time.sleep"):
            result = executor.execute(
                tool_name="fake_tool",
                arguments={},
            )

        assert result.success is True
        assert result.retry_count == 2
        assert tool.attempts == 3

        print("Transient retry -> success: PASSED")


    @staticmethod
    def test_max_retries():

        tool = AlwaysFailingTool()

        registry = FakeRegistry(tool)

        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0,
            max_delay=0,
        )

        executor = ToolExecutor(
            registry=registry,
            retry_policy=policy,
        )

        with patch("agent.tools.executor.time.sleep"):
            result = executor.execute(
                tool_name="fake_tool",
                arguments={},
            )

        assert result.success is False
        assert result.retry_count == 3
        assert tool.attempts == 4

        print("Max retries: PASSED")

    @staticmethod
    def test_permanent_error_no_retry():

        tool = PermanentFailingTool()

        registry = FakeRegistry(tool)

        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0,
            max_delay=0,
        )

        executor = ToolExecutor(
            registry=registry,
            retry_policy=policy,
        )

        with patch("agent.tools.executor.time.sleep"):
            result = executor.execute(
                tool_name="fake_tool",
                arguments={},
            )

        assert result.success is False
        assert result.retry_count == 0
        assert tool.attempts == 1

        print("Permanent error -> no retry: PASSED")


    @staticmethod
    def test_exponential_backoff():

        policy = RetryPolicy(
            initial_delay=1,
            max_delay=30,
            backoff_factor=2,
            jitter=0,
        )

        assert policy.get_delay(1) == 1
        assert policy.get_delay(2) == 2
        assert policy.get_delay(3) == 4
        assert policy.get_delay(4) == 8

        print("Exponential backoff: PASSED")



if __name__ == "__main__":

    ErrorHandlingTest.test_transient_error_classification()
    ErrorHandlingTest.test_permanent_error_classification()
    ErrorHandlingTest.test_retry_then_success()
    ErrorHandlingTest.test_max_retries()
    ErrorHandlingTest.test_permanent_error_no_retry()
    ErrorHandlingTest.test_exponential_backoff()

    print("\nAll error-handling tests passed.")
