import pandas as pd
from service.recommendation_service import recommend_assessments

FILE_PATH = "data/train/Gen_AI Dataset.xlsx"
TRAIN_SHEET = "Train-Set"
K = 10


def parse_labels(cell):
    if pd.isna(cell):
        return set()

    text = str(cell)

    if "|" in text:
        return {x.strip() for x in text.split("|")}
    if "," in text:
        return {x.strip() for x in text.split(",")}

    return {text.strip()}


def normalize_url(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.lower().rstrip("/")
    if "/view/" in url:
        return url.split("/view/")[-1]
    return url


def recall_at_k(predicted, relevant):
    if not relevant:
        return 0.0
    return len(predicted & relevant) / len(relevant)


def evaluate():
    df = pd.read_excel(FILE_PATH, sheet_name=TRAIN_SHEET)

    recalls = []

    # Group rows by Query so we aggregate all correct answers (≈5) per query
    grouped = df.groupby("Query")

    for query, group in grouped:
        # Collect ALL relevant assessments for this query
        relevant = set()
        for cell in group["Assessment_url"]:
            relevant |= {normalize_url(u) for u in parse_labels(cell)}

        # Run recommender ONCE per query
        results = recommend_assessments(query, top_k=K)
        predicted = {normalize_url(r["url"]) for r in results}

        # Debug logs for first 5 queries
        if len(recalls) < 5:
            print("=" * 80)
            print("QUERY:")
            print(query)

            print("\nRELEVANT (ground truth, normalized):")
            for r in sorted(relevant):
                print("  -", r)

            print("\nPREDICTED (model output, normalized):")
            for p in sorted(predicted):
                print("  -", p)

            print("\nINTERSECTION (correct hits):")
            hits = predicted & relevant
            if hits:
                for h in hits:
                    print("  ✔", h)
            else:
                print("  ❌ none")

        recalls.append(recall_at_k(predicted, relevant))

    mean_recall = sum(recalls) / len(recalls)
    print(f"Mean Recall@{K}: {mean_recall:.4f}")


if __name__ == "__main__":
    evaluate()