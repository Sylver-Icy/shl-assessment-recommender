import pandas as pd
import re

df = pd.read_csv("data/raw/assessments_full.csv")

def clean(text):
    if not isinstance(text, str):
        return text
    return re.sub(
        r"\s*Remote Testing:.*$",
        "",
        text,
        flags=re.DOTALL
    ).strip()

df["description"] = df["description"].apply(clean)

df.to_csv("data/processed/assessments_clean.csv", index=False)