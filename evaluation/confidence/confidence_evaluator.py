from __future__ import annotations

from evaluation.retrieval.retrieval_evaluator import RetrievalEvaluator

from ..config import THRESHOLD


class ConfidenceEvaluator:
    """
    Combines retrieval quality and answer faithfulness into a
    confidence score for the Human-in-the-Loop decision process.

    Faithfulness acts as a minimum-quality gate because an answer
    that is not sufficiently grounded in the retrieved context
    should not receive a high confidence score merely because
    retrieval quality was high.
    """

    def __init__(self, faithfulness_threshold: float = THRESHOLD) -> None:

        if not 0.0 <= faithfulness_threshold <= 1.0:
            raise ValueError(
                "faithfulness_threshold must be between 0 and 1."
            )

        self.faithfulness_threshold = faithfulness_threshold
        self.retrieval_evaluator = RetrievalEvaluator()


    def calculate(
        self,
        top1_score: float,
        mean_topk_score: float,
        faithfulness_score: float,
    ) -> float:

        """
        Calculate the final confidence score.

        Retrieval quality is calculated from top-1 and mean top-k
        similarity using the harmonic mean.

        Faithfulness acts as a gate. If the generated answer is
        below the configured faithfulness threshold, confidence
        becomes zero.

        Otherwise, confidence is the harmonic mean of retrieval
        quality and faithfulness.
        """ 
       
        if not 0.0 <= faithfulness_score <= 1.0:
            raise ValueError(
                "faithfulness_score must be between 0 and 1."
            )

        retrieval_quality = self.retrieval_evaluator.evaluate(
            top1_score=top1_score,
            mean_topk_score=mean_topk_score,
        )

        if faithfulness_score < self.faithfulness_threshold:
            return 0.0

        if retrieval_quality + faithfulness_score == 0.0:
            return 0.0

        confidence = (
            (2 * retrieval_quality * faithfulness_score)
            / (retrieval_quality + faithfulness_score) 
        )

        return float(confidence)