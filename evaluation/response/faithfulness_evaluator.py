from __future__ import annotations

import asyncio
from typing import Any

from ragas.metrics.collections import Faithfulness
from ragas.llms import llm_factory



class FaithfulnessEvaluator:

    def __init__(self, client: Any, model: str) -> None:
        llm = llm_factory(
            model=model,
            provider="openai",
            client=client,
        )

        self.scorer = Faithfulness(llm=llm)


    def evaluate(
        self, 
        query: str, 
        answer: str,
        retrieved_contexts: list[str]
    ) -> float:

        
        result = asyncio.run(
            self.scorer.ascore(
                user_input=query,
                response=answer,
                retrieved_contexts=retrieved_contexts,
            )
        )

        return float(result.value)