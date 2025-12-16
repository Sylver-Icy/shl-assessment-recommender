import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SHL-Scraper/1.0)"
}

def enrich_with_description(df):
    descriptions = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Scraping detail pages"):
        try:
            resp = requests.get(row["url"], headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception:
            descriptions.append("")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        description = ""
        main = soup.find("main")
        if main:
            # Grab the first meaningful paragraph after the Description label
            for tag in main.find_all(["p", "div"], recursive=True):
                text = tag.get_text(" ", strip=True)
                if text and len(text) > 50:
                    description = text
                    break

        descriptions.append(description)

    df["description"] = descriptions
    return df