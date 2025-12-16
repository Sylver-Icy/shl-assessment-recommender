import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
from requests.exceptions import HTTPError, ReadTimeout

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SHL-Scraper/1.0)"
}

def scrape_catalog(pages=32):
    records = []

    PAGE_SIZE = 12
    REQUEST_DELAY = 1.0  # seconds
    MAX_RETRIES = 3

    for page in range(pages):
        start = page * PAGE_SIZE
        params = {
            "start": start,
            "type": 1
        }
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.get(
                    CATALOG_URL,
                    headers=HEADERS,
                    params=params,
                    timeout=30
                )
                resp.raise_for_status()
                break
            except (HTTPError, ReadTimeout):
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(REQUEST_DELAY * (attempt + 1))

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.find_all("tr", attrs={"data-entity-id": True})
        print(f"Page {page}: {len(rows)} rows")
        rows = soup.select("tr[data-entity-id]")
        for row in rows:
            title_cell = row.select_one("td.custom__table-heading__title a")
            if not title_cell:
                continue

            name = title_cell.text.strip()
            url = BASE_URL + title_cell["href"]

            # Remote Testing: 2nd column
            remote_support = (
                "Yes"
                if row.select_one("td:nth-of-type(2) .catalogue__circle.-yes")
                else "No"
            )

            # Adaptive / IRT: 3rd column
            adaptive_support = (
                "Yes"
                if row.select_one("td:nth-of-type(3) .catalogue__circle.-yes")
                else "No"
            )

            records.append({
                "name": name,
                "url": url,
                "remote_support": remote_support,
                "adaptive_support": adaptive_support
            })

        time.sleep(REQUEST_DELAY)

    return pd.DataFrame(records)