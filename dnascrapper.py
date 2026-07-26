import os
import pandas as pd
import requests
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

APP_ID = os.getenv("ALGOLIA_APP_ID")
API_KEY = os.getenv("ALGOLIA_API_KEY")

if not APP_ID or not API_KEY:
    raise ValueError(
        "Missing credentials. Ensure ALGOLIA_APP_ID and ALGOLIA_API_KEY exist in .env"
    )

URL = f"https://{APP_ID.lower()}-dsn.algolia.net/1/indexes/*/queries"

HEADERS = {
    "x-algolia-application-id": APP_ID,
    "x-algolia-api-key": API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
}

PAYLOAD = {
    "requests": [
        {
            "indexName": "prodEpcProducts_discount30_desc",
            "facetFilters": [
                ["productCategory:puhelimet-ja-lisalaitteet/puhelimet"]
            ],
            "hitsPerPage": 500,
            "page": 0,
            "query": "",
        }
    ]
}


def main():
    print("Connecting to Algolia endpoint...")
    response = requests.post(URL, headers=HEADERS, json=PAYLOAD)

    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}:")
        print(response.text)
        return

    data = response.json()
    hits = data["results"][0].get("hits", [])
    print(f"Retrieved {len(hits)} raw items.")

    products = []
    for item in hits:
        # Extract localized name
        raw_name = item.get("name") or item.get("title")
        if isinstance(raw_name, dict):
            name = raw_name.get("fi") or next(iter(raw_name.values()), "")
        else:
            name = raw_name

        # Extract price and convert cents to Euros
        price_info = item.get("oneTimePrice") or item.get("price") or 0
        if isinstance(price_info, dict):
            raw_price = price_info.get("value", 0)
        else:
            raw_price = price_info

        price_eur = round(raw_price / 100.0, 2) if raw_price else 0.0

        # Extract single values from list fields
        raw_os = item.get("operatingSystem")
        os_val = raw_os[0] if isinstance(raw_os, list) and raw_os else raw_os

        raw_screen = item.get("screenSize")
        screen_val = (
            raw_screen[0]
            if isinstance(raw_screen, list) and raw_screen
            else raw_screen
        )

        products.append(
            {
                "ID": item.get("objectID") or item.get("id"),
                "Name": name,
                "Brand": item.get("manufacturer") or item.get("brand"),
                "Price_EUR": price_eur,
                "OS": os_val,
                "Screen_Size": screen_val,
                "5G_Capable": item.get("fiveGCapable", False),
                "In_Stock": item.get("inStock", False),
                "URL_Key": item.get("urlKey") or item.get("url"),
            }
        )

    df = pd.DataFrame(products)
    output_filename = "dna_phones_catalog_clean.csv"
    df.to_csv(output_filename, index=False, encoding="utf-8")
    print(f"Successfully processed and saved dataset to {output_filename}")


if __name__ == "__main__":
    main()