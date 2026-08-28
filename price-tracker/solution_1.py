import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

OUTPUT_FILE = Path("dna_pinkday_sale.json")
SOURCE_URL = "https://kauppa.dna.fi/laitteet/pinkit-paivat/kaikki"

# DNA's public, search-only Algolia credentials used by the storefront.
ALGOLIA_APP_ID = "ZOGF71LKCH"
ALGOLIA_API_KEY = "4f08f6a64f8511d643af41c7061c75d9"
INDEX_NAME = "prodEpcProducts"
ENDPOINT = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/*/queries"
PINKDAY_CATEGORY = "pinkit-paivat/kaikki"


def first_value(obj: dict[str, Any], *paths: str) -> Any:
    """Return the first non-empty value, supporting dotted dictionary paths."""
    for path in paths:
        value: Any = obj
        for part in path.split("."):
            if not isinstance(value, dict) or part not in value:
                value = None
                break
            value = value[part]
        if value not in (None, "", []):
            return value
    return None


def localized_text(value: Any) -> str | None:
    """Read Finnish text from DNA's localized values, or accept plain text."""
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for language in ("fi", "en", "sv"):
            text = value.get(language)
            if isinstance(text, str) and text.strip():
                return text.strip()
    return None


def cents_to_euros(value: Any) -> float | None:
    """Convert the integer cent prices returned by DNA into euro values."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return round(value / 100, 2)
    return None


def normalise_hit(hit: dict[str, Any]) -> dict[str, Any] | None:
    """Add convenient fields while retaining the complete original Algolia hit."""
    title = localized_text(first_value(hit, "name", "listingProductNameBase"))
    if not title:
        return None

    raw_url = first_value(hit, "url", "path", "pdpUrl", "productUrl", "slug")
    if isinstance(raw_url, str) and raw_url:
        product_url = (
            raw_url
            if raw_url.startswith(("http://", "https://"))
            else f"https://kauppa.dna.fi/{raw_url.lstrip('/')}"
        )
    else:
        product_url = None

    # Preserve the complete source record so present and future DNA fields remain
    # available, including variants, images, stock, gifts and campaign details.
    return {
        "title": title,
        "url": product_url,
        "price_eur": cents_to_euros(hit.get("oneTimePrice")),
        "dna_price_eur": cents_to_euros(hit.get("dnaPrice")),
        "customer_price_eur": cents_to_euros(
            first_value(hit, "customerLoyaltyPrices.grossSinglePrice")
        ),
        "lowest_30_day_price_eur": cents_to_euros(hit.get("discount30")),
        "source_data": hit,
    }


def build_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"POST"}),
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update(
        {
            "x-algolia-api-key": ALGOLIA_API_KEY,
            "x-algolia-application-id": ALGOLIA_APP_ID,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; DNA-Pinkday-Scraper/1.0)",
        }
    )
    return session


def fetch_dna_pinkday_sale() -> None:
    products: dict[str, dict[str, Any]] = {}
    page = 0
    hits_per_page = 100
    reported_total: int | None = None

    with build_session() as session:
        while True:
            params = urlencode(
                {
                    "query": "",
                    "hitsPerPage": hits_per_page,
                    "page": page,
                    "facetFilters": json.dumps(
                        [[f"productCategory:{PINKDAY_CATEGORY}"]],
                        separators=(",", ":"),
                    ),
                }
            )
            payload = {"requests": [{"indexName": INDEX_NAME, "params": params}]}

            response = session.post(ENDPOINT, json=payload, timeout=(10, 30))
            response.raise_for_status()
            data = response.json()

            results = data.get("results")
            if not isinstance(results, list) or not results:
                raise RuntimeError("DNA Algolia returned no result set")

            result = results[0]
            if not isinstance(result, dict):
                raise RuntimeError("DNA Algolia returned an invalid result set")

            hits = result.get("hits", [])
            if not isinstance(hits, list):
                raise RuntimeError("DNA Algolia returned an invalid product list")

            nb_pages = result.get("nbPages", 1)
            reported_total = result.get("nbHits", reported_total)
            if not isinstance(nb_pages, int) or nb_pages < 1:
                nb_pages = 1

            print(
                f"Fetched Pinkit P\u00e4iv\u00e4t page {page + 1} of {nb_pages} "
                f"({len(hits)} products)"
            )

            for hit in hits:
                if not isinstance(hit, dict):
                    continue
                item = normalise_hit(hit)
                if item:
                    key = str(hit.get("objectID") or item["url"] or item["title"])
                    products[key] = item

            page += 1
            if page >= nb_pages:
                break

    if not products:
        raise RuntimeError("No Pinkit P\u00e4iv\u00e4t sale products were captured")
    if isinstance(reported_total, int) and len(products) != reported_total:
        raise RuntimeError(
            f"Expected {reported_total} Pinkit P\u00e4iv\u00e4t products, "
            f"but captured {len(products)} unique products"
        )

    output = {
        "campaign": "Pinkit P\u00e4iv\u00e4t",
        "source_url": SOURCE_URL,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "product_count": len(products),
        "products": list(products.values()),
    }

    temporary_file = OUTPUT_FILE.with_suffix(f"{OUTPUT_FILE.suffix}.tmp")
    temporary_file.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary_file.replace(OUTPUT_FILE)
    print(f"Successfully saved {len(products)} sale products to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    fetch_dna_pinkday_sale()
