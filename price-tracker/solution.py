import asyncio
import json
from pathlib import Path
from typing import Any

from playwright.async_api import Response, TimeoutError as PlaywrightTimeoutError, async_playwright

CATEGORY_URL = "https://kauppa.dna.fi/puhelimet"
OUTPUT_FILE = Path("dna_smartphones.json")
PHONE_WORDS = (
    "puhelin", "smartphone", "iphone", "galaxy", "pixel", "oneplus",
    "xiaomi", "motorola", "honor", "nothing", "nokia", "doro", "fold", "flip",
)


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


def normalise_hit(hit: dict[str, Any]) -> dict[str, Any] | None:
    title = first_value(hit, "name", "title", "productName", "displayName")
    if not isinstance(title, str) or not title.strip():
        return None

    searchable = " ".join(
        str(first_value(hit, key) or "")
        for key in ("name", "title", "productName", "categoryName", "categoryPath", "url", "path", "productCategory")
    ).lower()

    if not any(word in searchable for word in PHONE_WORDS):
        return None

    # Handle numeric prices, price objects, or array formats returned by Algolia
    price = first_value(
        hit,
        "oneTimePrice",
        "price.value",
        "price.amount",
        "salesPrice.value",
        "salesPrice",
        "price",
        "currentPrice",
    )
    if isinstance(price, dict):
        price = first_value(price, "value", "amount", "formattedValue")
    elif isinstance(price, list) and price:
        price = price[0]

    if price is None:
        price = "N/A"

    raw_url = first_value(hit, "url", "path", "pdpUrl", "productUrl", "slug")
    if isinstance(raw_url, str) and raw_url:
        url = raw_url if raw_url.startswith("http") else f"https://kauppa.dna.fi/{raw_url.lstrip('/')}"
    else:
        url = "N/A"

    return {"title": title.strip(), "price": price, "url": url}


async def fetch_dna_smartphones() -> None:
    products: dict[str, dict[str, Any]] = {}
    response_tasks: set[asyncio.Task] = set()
    algolia_seen = asyncio.Event()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox"],
        )
        context = await browser.new_context(
            locale="fi-FI",
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        page.set_default_timeout(15_000)

        async def parse_response(response: Response) -> None:
            if "algolia" not in response.url.lower() or response.status != 200:
                return
            try:
                payload = await response.json()
                results = payload.get("results", []) if isinstance(payload, dict) else []
                hit_count = 0
                for result in results:
                    for hit in result.get("hits", []) if isinstance(result, dict) else []:
                        if not isinstance(hit, dict):
                            continue
                        item = normalise_hit(hit)
                        if item:
                            key = str(hit.get("objectID") or item["url"] or item["title"])
                            products[key] = item
                            hit_count += 1
                print(f"Algolia response intercepted: {len(results)} result set(s), {hit_count} phone(s)")
                algolia_seen.set()
            except Exception as exc:
                print(f"Could not parse Algolia response: {exc}")

        def on_response(response: Response) -> None:
            if "algolia" in response.url.lower():
                task = asyncio.create_task(parse_response(response))
                response_tasks.add(task)
                task.add_done_callback(response_tasks.discard)

        page.on("response", on_response)
        print(f"Navigating to {CATEGORY_URL}")
        try:
            await page.goto(CATEGORY_URL, wait_until="domcontentloaded", timeout=60_000)
        except PlaywrightTimeoutError:
            print("Page load timed out; continuing to wait for the Algolia response")

        # Scroll to trigger pagination / dynamic queries
        for _ in range(5):
            try:
                await page.wait_for_timeout(1_000)
                await page.evaluate("window.scrollBy(0, Math.max(window.innerHeight, 900))")
            except Exception as exc:
                print(f"Transient navigation while scrolling: {exc}")

        try:
            await asyncio.wait_for(algolia_seen.wait(), timeout=25)
            await page.wait_for_timeout(2_000)
        except asyncio.TimeoutError:
            print("Timed out waiting for an Algolia response")

        if response_tasks:
            await asyncio.gather(*response_tasks, return_exceptions=True)
        await browser.close()

    data = list(products.values())
    OUTPUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if not data:
        raise RuntimeError("No smartphones were captured from Algolia")
    print(f"Successfully saved {len(data)} smartphones to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    asyncio.run(fetch_dna_smartphones())