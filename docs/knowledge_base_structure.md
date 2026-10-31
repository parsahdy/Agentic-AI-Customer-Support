# Knowledge Base

The `knowledge_base/` package prepares source documents and makes them searchable by the agent.

## Pipeline

```text
Source Documents
      |
Document Loading / Transformation
      |
Document Processing
      |
Chunking
      |
Embedding
      |
Vector Store
      |
Document Mapping / Versioning / Statistics
      |
Retriever
      |
Retrieved Documents + Scores
```

## Main Responsibilities

- **Document loader:** Loads source content and applies the configured transformation.
- **Document processor:** Cleans and normalizes documents.
- **Chunking:** Splits documents into smaller overlapping passages.
- **Embedding:** Converts chunks into vectors using the configured sentence-transformer model.
- **Vector store:** Builds and searches the FAISS index.
- **Document mapping:** Keeps metadata associated with indexed chunks.
- **Versioning and statistics:** Records information about the built knowledge base.
- **Retriever:** Finds relevant chunks for a user query.
- **KnowledgeBaseService:** Coordinates the build and retrieval components.

The current configuration uses the `all-MiniLM-L6-v2` sentence-transformer model, recursive chunking, and FAISS. These settings are configurable in `knowledge_base/config.py`.

The agent accesses the knowledge base through `KnowledgeBaseService`; it does not need to manage the lower-level pipeline directly.
