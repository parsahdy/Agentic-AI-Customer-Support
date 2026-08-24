from datetime import datetime
from typing import Any

from knowledge_base.config import VERSION_PATH

from .version import KnowledgeBaseVersion


def versioning_pipeline(
    version: str,
    embedding_model: str,
    chunker_type: str,
    chunk_size: int,
    chunk_overlap: int,
    vector_store_type: str,
    document_count: int,
    chunk_count: int,
    embedding_dimension: int,
    created_at: str | None = None,
) -> dict[str, Any]:

    if created_at is None:
        created_at = datetime.now().isoformat(timespec="seconds")

    versioning = KnowledgeBaseVersion(version_path=VERSION_PATH)

    version_data = versioning.create(
                version=version,
                created_at=created_at,
                embedding_model=embedding_model,
                chunker_type=chunker_type,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                vector_store_type=vector_store_type,
                document_count=document_count,
                chunk_count=chunk_count,
                embedding_dimension=embedding_dimension
    )
    versioning.save(version_data)

    return version_data
