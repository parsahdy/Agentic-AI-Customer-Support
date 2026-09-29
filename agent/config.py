
# LLM
#LLM_MODEL="openrouter/free"
#BASE_URL="https://openrouter.ai/api/v1"
#TEMPERATURE=0.3

# Groq Console
LLM_MODEL="qwen/qwen3.8-27b"
BASE_URL="https://api.groq.com/openai/v1"
TEMPERATURE=0.3
MAX_TOKENS=512

# JEV
JEV_MODEL="typesafe/jev-router"

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