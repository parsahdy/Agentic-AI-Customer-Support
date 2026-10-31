import os

# Retrieval Evaluator
THRESHOLD = 0.70

MAX_WORDS = 80               
FAITHFULNESS_MIN = 0.70      
CONFIDENCE_MIN = 0.60        

SENSITIVE_TOOLS = {"cancel_order"}

# Use a judge model that is different from the agent's model if you can:
# a model grading its own answers is biased towards them.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-oss-120b")
JUDGE_BASE_URL = os.getenv("JUDGE_BASE_URL", "https://api.groq.com/openai/v1")
