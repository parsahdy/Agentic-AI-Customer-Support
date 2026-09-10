from __future__ import annotations

from unittest.mock import patch

from agent.human_loop import (
    CompositeHumanPolicy,
    HumanDecision,
    HumanLoopHandler,
    HumanReviewRequest,
    LowConfidencePolicy,
    SensitiveOperationPolicy,
)


class HumanLoopTest:

    @staticmethod
    def test_low_confidence_requires_human():

        policy = LowConfidencePolicy(
            review_threshold=0.6
        )

        request = HumanReviewRequest(
            request="Why has my efund not arrived?",
            reason="Low retrievel confidence.",
            confidence_score=0.4,
        )

        assert policy.should_intervene(request) is True

        print("Low confdence -> human review: PASSED")


    @staticmethod
    def test_high_confidence_does_not_require_human():

        policy = LowConfidencePolicy(
            review_threshold=0.6
        )

        request = HumanReviewRequest(
            request="Where is my order?",
            reason="Normal request.",
            confidence_score=0.9,
        )

        assert policy.should_intervene(request) is False

        print(
            "High confidence -> no human: PASSED"
        )


    @staticmethod
    def test_missing_confidence_requires_human():

        policy = LowConfidencePolicy(
            review_threshold=0.6
        )

        request = HumanReviewRequest(
            request="Where is my order?",
            reason="Normal request.",
            confidence_score=0.9,
        )

        assert policy.should_intervene(request) is False

        print(
            "High confidence -> no human: PASSED"
        )


    @staticmethod
    def test_sensitive_operation_requires_human():

        policy = SensitiveOperationPolicy()

        request = HumanReviewRequest(
            request="Please Cancel my order.",
            reason="Sensitive operation.",
        )

        assert policy.should_intervene(request) is True

        print("Sensitive operation -> human review: PASSED")


    @staticmethod
    def test_normal_operation_does_not_require_human():

        policy = SensitiveOperationPolicy()

        request = HumanReviewRequest(
            request="Where is my order?",
            reason="Normal operation.",
        )

        assert policy.should_intervene(request) is False

        print(
            "Normal operation -> no human: PASSED"
        )


    @staticmethod
    def test_composite_policy_requires_human():

        policy = CompositeHumanPolicy(
            policies=[
                LowConfidencePolicy(
                    review_threshold=0.6
                ),
                SensitiveOperationPolicy(),
            ]
        )

        request = HumanReviewRequest(
            request="Please cancel my order.",
            reason="Sensitive operation.",
            confidence_score=0.95,
        )

        assert policy.should_intervene(request) is True

        print("Composite policy -> human review: PASSED")


    @staticmethod
    def test_composite_policy_allows_normal_request():

        policy = CompositeHumanPolicy(
            policies=[
                LowConfidencePolicy(review_threshold=0.6),
                SensitiveOperationPolicy(),
            ]
        )

        request = HumanReviewRequest(
            request="Where is my order?",
            reason="Normal request.",
            confidence_score=0.95,
        )

        assert policy.should_intervene(request) is False

        print("Composite policy -> no human: PASSED")


    @staticmethod
    def test_handler_returns_human_decision():

        policy = SensitiveOperationPolicy()

        handler = HumanLoopHandler(policy=policy)

        request = HumanReviewRequest(
            request="Please cancel my order.",
            reason="Sensitive operation.",
        )

        human_response = {
            "decision": "approve",
            "comment": "Approved by support operator.",
        }

        with patch(
            "agent.human_loop.handler.interrupt",
            return_value=human_response,
        ) as mock_interrupt:

            result = handler.request_human_decision(request)

        assert isinstance(result, HumanDecision)
        assert result.decision == "approve"
        assert (result.comment == "Approved by support operator.")

        mock_interrupt.assert_called_once()

        payload = mock_interrupt.call_args.args[0]

        assert payload["type"] == "human_review"
        assert payload["request"]["request"] == "Please cancel my order."

        print("Human decision -> handler: PASSED")


    @staticmethod
    def test_handler_rejects_invalid_decision():

        policy = SensitiveOperationPolicy()

        handler = HumanLoopHandler(policy=policy)

        request = HumanReviewRequest(
            request="Please cancel my order.",
            reason="Sensitive operation.",
        )

        with patch(
            "agent.human_loop.handler.interrupt",
            return_value={"decision": "invalid_decision"}):

            try:
                handler.request_human_decision(request)

                assert False

            except ValueError:
                pass

        print("Invalid human decision -> rejected: PASSED")


    @staticmethod
    def test_handler_does_not_interrupt_when_not_required():

        policy = SensitiveOperationPolicy()

        handler = HumanLoopHandler(policy=policy)

        request = HumanReviewRequest(
            request="Where is my order?",
            reason="Normal request.",
        )

        with patch(
            "agent.human_loop.handler.interrupt"
            ) as mock_interrupt:

            try:
                handler.request_human_decision(request)

                assert False

            except ValueError:
                pass

        mock_interrupt.assert_not_called()

        print("No intervention -> no interrupt: PASSED")



if __name__ == "__main__":

    HumanLoopTest.test_low_confidence_requires_human()
    HumanLoopTest.test_high_confidence_does_not_require_human()
    HumanLoopTest.test_missing_confidence_requires_human()
    HumanLoopTest.test_sensitive_operation_requires_human()
    HumanLoopTest.test_normal_operation_does_not_require_human()
    HumanLoopTest.test_composite_policy_requires_human()
    HumanLoopTest.test_composite_policy_allows_normal_request()
    HumanLoopTest.test_handler_returns_human_decision()
    HumanLoopTest.test_handler_rejects_invalid_decision()
    HumanLoopTest.test_handler_does_not_interrupt_when_not_required()

    print("\nAll human-loop tests passed.")
