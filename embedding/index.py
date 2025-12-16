import pickle
import numpy as np
from embedding.openai_client import embed_text

EMBEDDINGS_FILE = "data/processed/embeddings.pkl"


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search(query: str, top_k: int = 25):
    # Load stored embeddings
    with open(EMBEDDINGS_FILE, "rb") as f:
        records = pickle.load(f)

    # Embed the query
    query_vec = embed_text(query)

    # Score each record
    scored = []
    for r in records:
        score = cosine_similarity(query_vec, r["embedding"])
        scored.append((score, r))

    # Sort by similarity (highest first)
    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[:top_k]


if __name__ == "__main__":
    while True:
        query = input("\nAsk something (or 'exit'): ")
        if query.lower() == "exit":
            break

        results = search(query)

        print("\nTop matches:")
        for score, r in results:
            print(f"- {r['name']} ({score:.3f})")
            print(f"  {r['url']}")