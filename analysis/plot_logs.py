import json
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide")

# -------------------------
# Utils
# -------------------------
def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def normalize_url(url: str):
    if not url:
        return ""
    return url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]

# -------------------------
# Load data
# -------------------------
EVAL_PATH = Path("logs/eval.jsonl")
GT_PATH = Path("logs/ground_truth_eval.jsonl")

eval_data = load_jsonl(EVAL_PATH)[0]
gt_data = load_jsonl(GT_PATH)[0]

# -------------------------
# Header
# -------------------------
query_text = eval_data["query"]
query_trimmed = query_text[:200] + "..."
query_word_count = gt_data.get("query_word_count", len(query_text.split()))

st.title("📊 Recommendation Evaluation Dashboard")
st.markdown(f"**Query (trimmed):** {query_trimmed}")
st.markdown(f"**Word count:** {query_word_count}")

st.divider()

# -------------------------
# Ground Truth Table
# -------------------------
gt_rows = []
for item in gt_data["ground_truth"]:
    gt_rows.append({
        "name": item.get("name"),
        "test_type": ", ".join(item.get("test_type", [])),
        "duration": item.get("duration_minutes", ""),
        "remote": item.get("remote_support"),
        "adaptive": item.get("adaptive_support"),
        "found_in_catalog": item.get("found_in_catalog"),
        "url_norm": normalize_url(item.get("url"))
    })

gt_df = pd.DataFrame(gt_rows)

# -------------------------
# Top-10 Table
# -------------------------
top10_rows = []
for item in eval_data["top10"]:
    top10_rows.append({
        "name": item["name"],
        "test_type": ", ".join(item.get("test_type", [])),
        "duration": item.get("duration_minutes"),
        "final_score": round(item.get("final_score", 0), 4),
        "remote": item.get("remote_support"),
        "adaptive": item.get("adaptive_support"),
        "url_norm": normalize_url(item.get("url"))
    })

top10_df = pd.DataFrame(top10_rows).drop_duplicates(subset=["name"])

# -------------------------
# Side-by-side tables
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Ground Truth")
    st.dataframe(
        gt_df.drop(columns=["url_norm"]),
        width="stretch"
    )

with col2:
    st.subheader("🤖 Top-10 Recommendations")
    st.dataframe(
        top10_df.drop(columns=["url_norm"]),
        width="stretch"
    )

st.divider()

# -------------------------
# Pie chart – GT Coverage
# -------------------------
gt_urls = set(gt_df["url_norm"])
top10_urls = set(top10_df["url_norm"])
top25_urls = {normalize_url(i["url"]) for i in eval_data["top25"]}

gt_in_top10 = len(gt_urls & top10_urls)
gt_in_top25_only = len((gt_urls & top25_urls) - top10_urls)
gt_missed = len(gt_urls - top25_urls)

labels = []
values = []

if gt_in_top10 > 0:
    labels.append("GT in Top-10")
    values.append(gt_in_top10)

if gt_in_top25_only > 0:
    labels.append("GT in Top-25 only")
    values.append(gt_in_top25_only)

if gt_missed > 0:
    labels.append("GT missed")
    values.append(gt_missed)

st.subheader("🎯 Ground Truth Coverage")

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(
    values,
    labels=labels,
    autopct="%1.0f%%",
    startangle=90
)
ax.axis("equal")
ax.set_ylabel("")

st.pyplot(fig)

st.divider()

# -------------------------
# Top-25 Reference Table
# -------------------------
top25_rows = []
for item in eval_data["top25"]:
    top25_rows.append({
        "name": item["name"],
        "semantic_score": round(item.get("semantic_score", 0), 4),
        "final_score": round(item.get("final_score", 0), 4),
        "test_type": ", ".join(item.get("test_type", [])),
        "duration": item.get("duration_minutes"),
        "remote": item.get("remote_support"),
        "adaptive": item.get("adaptive_support")
    })

top25_df = pd.DataFrame(top25_rows)

st.subheader("📚 Top-25 Reference")

st.dataframe(
    top25_df,
    width="stretch",
    height=1200
)

st.write("Top-25 actual count:", len(top25_df))