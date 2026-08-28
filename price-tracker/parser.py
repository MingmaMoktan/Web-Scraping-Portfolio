import json
import csv
from pathlib import Path

# Update filenames as needed
RAW_FILE = Path("dna_pinkday_sale.json")
OUTPUT_JSON = Path("cleaned_products.json")
OUTPUT_CSV = Path("cleaned_products.csv")


def parse_price(val) -> float:
    """Converts price from cents or standard float/int to EUR float."""
    if val is None:
        return 0.0
    try:
        val = float(val)
        # If price is in cents (e.g. 19900), convert to EUR (199.0)
        if val > 1000:
            return round(val / 100.0, 2)
        return round(val, 2)
    except (ValueError, TypeError):
        return 0.0


def parse_dna_item(item: dict) -> dict:
    """Extracts required fields from a single product dictionary."""
    source = item.get("source_data", {})

    # 1. Title
    title = item.get("title") or source.get("name", {}).get("fi") or "N/A"

    # 2. URL
    raw_url = item.get("url") or source.get("url") or ""
    if raw_url.startswith("http"):
        full_url = raw_url
    elif raw_url:
        full_url = f"https://kauppa.dna.fi{raw_url}"
    else:
        full_url = "N/A"

    # 3. Prices
    price_eur = parse_price(item.get("price_eur") or source.get("oneTimePrice"))
    dna_price_eur = parse_price(item.get("dna_price_eur") or source.get("dnaPrice"))
    cust_price_eur = parse_price(item.get("customer_price_eur"))

    # 4. In Stock Status
    in_stock = source.get("inStock", False)

    # 5. Manufacturer / Brand
    manufacturer = source.get("manufacturer") or "N/A"

    # 6. Gift Information
    gifts_list = source.get("gifts", [])
    if gifts_list and isinstance(gifts_list, list):
        gift_text = gifts_list[0].get("listingText", "")
        # Clean inline HTML tags if present
        gift_text = (
            gift_text.replace('<span style="color:#DA0070;">', "")
            .replace("</span>", "")
            .strip()
        )
    else:
        gift_text = "No gift"

    return {
        "title": str(title).strip(),
        "url": full_url,
        "price_eur": price_eur,
        "dna_price_eur": dna_price_eur,
        "customer_price_eur": cust_price_eur,
        "in_stock": in_stock,
        "manufacturer": manufacturer,
        "gift": gift_text,
    }


def main():
    if not RAW_FILE.exists():
        print(f"Error: File '{RAW_FILE}' not found.")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Core Fix: Locate the product list across various dictionary wrappers
    if isinstance(data, dict):
        if "products" in data:
            raw_items = data["products"]
        elif "results" in data:
            raw_items = data["results"][0].get("hits", [])
        elif "hits" in data:
            raw_items = data["hits"]
        else:
            raw_items = [data]
    elif isinstance(data, list):
        raw_items = data
    else:
        raw_items = []

    parsed_products = [parse_dna_item(item) for item in raw_items]

    # Save to Clean JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(parsed_products, f, ensure_ascii=False, indent=2)

    # Save to CSV
    if parsed_products:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=parsed_products[0].keys())
            writer.writeheader()
            writer.writerows(parsed_products)

    print(f"Successfully parsed {len(parsed_products)} products.")
    print(f"Exported to '{OUTPUT_JSON}' and '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()