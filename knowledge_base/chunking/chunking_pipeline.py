from .chunker_factory import ChunkerFactory


def chunk_pipeline(documents: list[dict], 
                   chunker: str = "recursive") -> list[dict]:

    if not documents:
        return []

    chunker = ChunkerFactory.create(chunker)

    chunked_documents = chunker.chunk(documents)

    return chunked_documents
