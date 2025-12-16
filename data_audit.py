import pandas as pd
import re

CSV_PATH = "data/raw/assessments_full.csv"


def audit_dataset(path: str):
    print("🔍 Loading dataset...")
    df = pd.read_csv(path)

    print("\n================ BASIC INFO ================")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    expected_cols = {"name", "url", "description"}
    missing_cols = expected_cols - set(df.columns)

    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
    else:
        print("✅ All expected columns present")

    print("\n================ NULL / EMPTY CHECK ================")
    for col in expected_cols:
        nulls = df[col].isna().sum()
        empties = (df[col].astype(str).str.strip() == "").sum()
        print(f"{col}: {nulls} nulls | {empties} empty strings")

    print("\n================ DUPLICATE CHECK ================")
    dup_urls = df.duplicated(subset=["url"]).sum()
    dup_names = df.duplicated(subset=["name"]).sum()
    print(f"Duplicate URLs: {dup_urls}")
    print(f"Duplicate names: {dup_names}")

    print("\n================ URL VALIDATION ================")
    invalid_urls = df[~df["url"].astype(str).str.startswith("https://www.shl.com/")]
    print(f"Invalid SHL URLs: {len(invalid_urls)}")

    print("\n================ DESCRIPTION SANITY ================")
    short_desc = df[df["description"].astype(str).str.len() < 50]
    print(f"Descriptions < 50 chars: {len(short_desc)}")

    no_remote_testing = df[~df["description"].astype(str).str.contains("Remote Testing", na=False)]
    print(f"Descriptions missing 'Remote Testing': {len(no_remote_testing)}")

    print("\n================ NAME INSIDE DESCRIPTION ================")
    mismatched = df[
        ~df.apply(
            lambda r: str(r["description"]).lower().startswith(str(r["name"]).lower()),
            axis=1
        )
    ]
    print(f"Descriptions NOT starting with name: {len(mismatched)}")

    print("\n================ STRUCTURE SMELL TEST ================")
    weird_quotes = df[df["description"].astype(str).str.count('"') % 2 != 0]
    print(f"Descriptions with unbalanced quotes: {len(weird_quotes)}")

    newline_heavy = df[df["description"].astype(str).str.count("\n") > 5]
    print(f"Descriptions with excessive newlines (>5): {len(newline_heavy)}")

    print("\n================ FINAL VERDICT ================")
    if (
        not missing_cols
        and df.isna().sum().sum() == 0
        and dup_urls == 0
        and len(invalid_urls) == 0
    ):
        print("🔥 DATASET PASSED CORE QUALITY CHECKS")
    else:
        print("⚠️ Dataset has issues")

    print("\nAudit complete.")


if __name__ == "__main__":
    audit_dataset(CSV_PATH)