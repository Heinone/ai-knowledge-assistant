import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL",
    "gpt-5-mini"
)

VECTOR_STORE = os.getenv(
    "VECTOR_STORE",
    "local"
)