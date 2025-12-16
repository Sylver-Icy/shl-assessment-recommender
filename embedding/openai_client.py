from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"


def embed_text(text: str) -> list[float]:
    """
    Convert input text into an embedding vector using OpenAI.
    This function is intentionally small and deterministic.
    """

    #guard embeddings expect strings
    if not isinstance(text, str):
        raise ValueError("Input to embed_text must be a string")


    response = _client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding