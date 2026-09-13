from __future__ import annotations


class RetrievalEvaluator:
    """
    Evaluates retrieval quality from the top-ranked similarity
    and the average similarity of the retrieved top-k documents.

    Both scores are expected to be cosine-similarity scores in the
    [0, 1] range because the project's embeddings are normalized.
    """

    def evaluate(
        self,
        top1_score: float,
        mean_topk_score: float,
    ) -> float:

        if not 0.0 <= top1_score <= 1.0:
            raise ValueError(
                "top1_score must be between 0 and 1."
            )

        if not 0.0 <= mean_topk_score <= 1.0:
            raise ValueError(
                "mean_topk_score must be between 0 and 1."
            )

        if top1_score + mean_topk_score == 0:
            return 0.0

        retrieval_quality = (
            (2 * top1_score * mean_topk_score) / (top1_score + mean_topk_score)
        )

        return float(retrieval_quality)