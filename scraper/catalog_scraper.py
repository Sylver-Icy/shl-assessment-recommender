import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SHL-Scraper/1.0)"
}

def scrape_catalog(pages=32):
    records = []

    PAGE_SIZE = 12

    for page in range(pages):
        start = page * PAGE_SIZE
        params = {
            "start": start,
            "type": 1
        }
        resp = requests.get(CATALOG_URL, headers=HEADERS, params=params)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.find_all("tr", attrs={"data-entity-id": True})
        print(f"Page {page}: {len(rows)} rows")
        rows = soup.select("tr[data-entity-id]")
        for row in rows:
            link = row.find("a", href=True)
            if not link:
                continue

            name = link.text.strip()
            url = BASE_URL + link["href"]

            records.append({
                "name": name,
                "url": url
            })

    return pd.DataFrame(records)