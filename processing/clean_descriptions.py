import pandas as pd
import re

df = pd.read_csv("data/raw/assessments_full.csv")

def clean(text):
    if not isinstance(text, str):
        return text
    # Remove everything after "Remote Testing:"
    text = re.sub(
        r"\s*Remote Testing:.*$",
        "",
        text,
        flags=re.DOTALL
    )

    # Nuke newlines and excessive whitespace
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()

df["description"] = df["description"].apply(clean)

df.to_csv("data/processed/assessments_clean.csv", index=False)