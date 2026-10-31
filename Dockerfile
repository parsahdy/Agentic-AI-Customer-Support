FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/opt/huggingface \
    PYTHONPATH=/app:/app/app

WORKDIR /app

# faiss-cpu needs the OpenMP runtime, which slim images do not ship.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch first, so pip does not download the multi-GB CUDA build.
RUN pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu

# Download the embedding model at build time instead of at every start.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Run as a normal user, not root.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /opt/huggingface

COPY --chown=appuser:appuser . .

EXPOSE 8000

# 0.0.0.0 so the port is reachable from outside the container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]