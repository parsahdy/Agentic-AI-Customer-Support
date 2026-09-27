
# LLM
LLM_MODEL="openrouter/free"
BASE_URL="https://openrouter.ai/api/v1"
TEMPERATURE=0.3

# Router
ROUTER_TYPE="llm"


# Loop
MAX_ITERATIONS = 5


# Memory
import os
from dotenv import load_dotenv
load_dotenv()

MEMORY_BACKEND = "postgres"

MEMORY_DATABASE_URL = os.getenv("MEMORY_DATABASE_URL")