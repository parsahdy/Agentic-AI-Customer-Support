from knowledge_base.chunking.chunker import (
    ChunkerBase,
    RecursiveCunker,
    SentenceChunker,
)


class ChunkerFactory:

    _chunkers: dict[str, type[ChunkerBase]] = {
        "recursive": RecursiveCunker,
        "sentence": SentenceChunker,
    }

    @classmethod
    def create(cls, chunker: str) -> ChunkerBase:

        chunker = chunker.lower().strip()

        if not chunker in cls._chunkers:
            raise ValueError(
                f"Unkown chunker type: {chunker}"
                f"Available chunkers: {list(cls._chunkers.keys())}"    
            )

        chunker_class = cls._chunkers[chunker]
        return chunker_class()