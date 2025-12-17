import pandas as pd
import csv
from service.recommendation_service import recommend_assessments
from logger.logging_config import get_logger, log_json

FILE_PATH = "data/train/Gen_AI Dataset.xlsx"
TRAIN_SHEET = "Train-Set"
K = 10

gt_logger = get_logger(
    name="ground_truth_eval",
    logfile="logs/ground_truth_eval.jsonl"
)


# Catalog CSV loading and lookup
CATALOG_PATH = "data/processed/assessments_structured.csv"

def normalize_url(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.lower().rstrip("/")
    if "/view/" in url:
        return url.split("/view/")[-1]
    return url

def load_catalog(path):
    catalog = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = normalize_url(row.get("url", ""))
            if url:
                catalog[url] = row
    return catalog

catalog_lookup = load_catalog(CATALOG_PATH)


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

def trim_query(query: str, head_words: int = 10, tail_words: int = 10):
    if not isinstance(query, str):
        return {"preview": "", "word_count": 0}
    words = query.split()
    word_count = len(words)
    if word_count <= head_words + tail_words:
        preview = query
    else:
        preview = " ".join(words[:head_words]) + " ... " + " ".join(words[-tail_words:])
    return {
        "preview": preview,
        "word_count": word_count
    }

def evaluate():
    df = pd.read_excel(FILE_PATH, sheet_name=TRAIN_SHEET)

    recalls = []
    adjusted_recalls = []

    # Group rows by Query so we aggregate all correct answers per query
    grouped = df.groupby("Query")

    for query, group in grouped:
        # Collect ALL relevant assessments for this query
        relevant = set()
        for cell in group["Assessment_url"]:
            relevant |= {normalize_url(u) for u in parse_labels(cell)}

        enriched_ground_truth = []
        for url in relevant:
            meta = catalog_lookup.get(url)
            if meta:
                enriched_ground_truth.append({
                    "url": url,
                    "name": meta.get("name"),
                    "test_type": meta.get("test_type"),
                    "expanded_test_type": meta.get("expanded_test_type"),
                    "duration_minutes": meta.get("duration_minutes"),
                    "job_levels": meta.get("job_levels"),
                    "remote_support": meta.get("remote_support"),
                    "adaptive_support": meta.get("adaptive_support"),
                    "found_in_catalog": True
                })
            else:
                enriched_ground_truth.append({
                    "url": url,
                    "found_in_catalog": False
                })

        query_trimmed = trim_query(query)

        log_json(gt_logger, {
            "query_preview": query_trimmed["preview"],
            "query_word_count": query_trimmed["word_count"],
            "ground_truth": enriched_ground_truth,
            "query_raw": query
        })

        # Run recommender ONCE per query
        results = recommend_assessments(query, top_k=K)
        predicted = {normalize_url(r["url"]) for r in results}

        reachable = {
            item["url"]
            for item in enriched_ground_truth
            if item.get("found_in_catalog") is True
        }

        if reachable:
            adjusted_recalls.append(len(predicted & reachable) / len(reachable))

        recalls.append(recall_at_k(predicted, relevant))

    mean_recall = sum(recalls) / len(recalls)
    print(f"Mean Recall@{K}: {mean_recall:.4f}")

    if adjusted_recalls:
        mean_adjusted_recall = sum(adjusted_recalls) / len(adjusted_recalls)
        print(f"Adjusted Mean Recall@{K} (catalog-only): {mean_adjusted_recall:.4f}")


if __name__ == "__main__":
    evaluate()