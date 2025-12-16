import pandas as pd
from embedding.index import search

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


def recall_at_k(predicted, relevant):
    if not relevant:
        return 0.0
    return len(predicted & relevant) / len(relevant)


def evaluate():
    df = pd.read_excel(FILE_PATH, sheet_name=TRAIN_SHEET)

    recalls = []

    for _, row in df.iterrows():
        query = row["Query"]
        relevant = parse_labels(row["Assessment_url"])

        results = search(query, top_k=K)
        predicted = {r["url"] for _, r in results}

        recalls.append(recall_at_k(predicted, relevant))

    mean_recall = sum(recalls) / len(recalls)
    print(f"Mean Recall@{K}: {mean_recall:.4f}")


if __name__ == "__main__":
    evaluate()