from pathlib import Path

CHUNKER = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
}

K = 5

SENTENCE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BGE_MODEL = "BAAI/bge-m3"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = PROJECT_ROOT / "data" / "knowledge_base" 
INDEX_PATH = KB_DIR / "vector_index.faiss"
METADATA_PATH = KB_DIR / "vector_metadata.json"