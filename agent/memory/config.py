import os


MEMORY_BACKEND = os.getenv(
    "MEMORY_BACKEND",
    "memory"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)