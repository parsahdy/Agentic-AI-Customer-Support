from __future__ import annotations

from typing import Any

from ragas.metrics.collections import Faithfulness



class FaithfulnessEvaluator:

    def __init__(self, llm: Any) -> None:

        self.scorer = Faithfulness(llm=llm)


    async def evaluate(self, query: str, answer: str,
                       retrieved_contexts: list[str]) -> float:

        
        result = await self.scorer.ascore(
            user_input=query,
            response=answer,
            retrieved_contexts=retrieved_contexts,
        )

        return float(result.value)