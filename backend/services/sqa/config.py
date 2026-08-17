from ollama import Client

MODEL_NAME = "gemma3:4b"
# MODEL_NAME = "qwen3:4b-q4_K_M"

# qwen2.5:7b
# llama3.2:3b

PARAMETERS = [
    "evidence",
    "completeness",
    "clarity",
    "profile",
    "transaction",
    "justification",
]

client = Client()