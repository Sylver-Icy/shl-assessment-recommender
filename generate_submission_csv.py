import pandas as pd
import csv
from service.recommendation_service import recommend_assessments

FILE_PATH = "data/train/Gen_AI Dataset.xlsx"
TEST_SHEET = "Test-Set"
K = 10

OUTPUT_FILE = "submission.csv"

df = pd.read_excel(FILE_PATH, sheet_name=TEST_SHEET)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Query", "Assessment_url"])

    for query in df["Query"]:
        if not isinstance(query, str) or not query.strip():
            continue

        results = recommend_assessments(query, top_k=K)

        for r in results:
            writer.writerow([query, r["url"]])

print("submission.csv generated successfully")