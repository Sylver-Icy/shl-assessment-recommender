from scraper.catalog_scraper import scrape_catalog
from scraper.detail_scraper import enrich_with_description
import os

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    df = scrape_catalog()
    df.to_csv(f"{DATA_DIR}/assessments_basic.csv", index=False)

    df = enrich_with_description(df)
    df.to_csv(f"{DATA_DIR}/assessments_full.csv", index=False)

    print(f"Scraped {len(df)} assessments")

if __name__ == "__main__":
    main()