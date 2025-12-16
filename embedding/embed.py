import pandas as pd
import pickle
from embedding.openai_client import embed_text

INPUT_CSV = "data/processed/assessments_structured.csv"
OUTPUT_FILE = "data/processed/embeddings.pkl"


def build_embeddings():
    df = pd.read_csv(INPUT_CSV)

    records = []

    for _, row in df.iterrows():
        desc = row.get("description")

        if isinstance(desc, str) and desc.strip():
            text = desc
        else:
            text = row["name"]

        vector = embed_text(text)

        records.append({
            "name": row["name"],
            "url": row["url"],
            "remote_support": row.get("remote_support"),
            "adaptive_support": row.get("adaptive_support"),
            "description": desc,
            "job_levels": row.get("job_levels"),
            "languages": row.get("languages"),
            "duration_minutes": row.get("duration_minutes"),
            "test_type": row.get("test_type"),
            "embedding": vector
        })

    # Save everything
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(records, f)

    print(f"Saved {len(records)} embeddings to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_embeddings()