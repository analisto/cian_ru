"""
cian.ru scraper -- https://www.cian.ru/cat.php?deal_type=sale&offer_type=flat&region=1
Strategy:
  1. Open a visible Chromium browser once to capture session cookies
     (bypasses the bot-detection captcha).  Cookies are saved to
     data/cookies.json and reused on subsequent runs (valid ~12 hours).
  2. Use curl_cffi (Chrome impersonation) + saved cookies to fetch each
     page of the SSR HTML concurrently.
  3. Parse the JSON offer array embedded in the HTML (<= 28 offers/page).
  4. Flatten and write to data/data.csv.

Requirements:
    pip install playwright curl_cffi
    playwright install chromium
"""

import asyncio
import csv
import json
import re
import sys
import time
from pathlib import Path

from curl_cffi.requests import AsyncSession
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL      = "https://www.cian.ru"
LISTING_URL   = (
    f"{BASE_URL}/cat.php"
    "?deal_type=sale&engine_version=2&offer_type=flat&region=1"
)
OUTPUT_PATH   = Path(__file__).parent.parent / "data" / "data.csv"
COOKIES_PATH  = Path(__file__).parent.parent / "data" / "cookies.json"

MAX_PAGES     = 54          # cian.ru shows ~87k offers; 54 p × 28 = ~1512
CONCURRENCY   = 5           # parallel page fetches
RETRY_LIMIT   = 3
RETRY_DELAY   = 3.0
CAPTCHA_WAIT  = 90          # seconds to wait for the browser to load listings
IMPERSONATE   = "chrome120"

HEADERS = {
    "accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "ru-RU,ru;q=0.9,en;q=0.8",
    "referer":         BASE_URL + "/",
    "dnt":             "1",
}

FIELDNAMES = [
    "id", "url",
    "deal_type", "offer_type", "flat_type",
    "rooms_count", "total_area", "living_area", "kitchen_area",
    "floor_number", "floors_total",
    "price_rub", "price_type", "sale_type", "mortgage_allowed",
    "material_type", "build_year",
    "city", "district", "street", "house",
    "underground", "underground_walk_min",
    "is_apartments", "has_furniture", "is_new",
    "description",
    "photos_count",
    "creation_date", "added",
]


# ---------------------------------------------------------------------------
# Cookie persistence
# ---------------------------------------------------------------------------

def load_cookies() -> dict | None:
    if not COOKIES_PATH.exists():
        return None
    age = time.time() - COOKIES_PATH.stat().st_mtime
    if age > 12 * 3600:
        print("Saved cookies are stale (>12 h), will re-authenticate.", flush=True)
        return None
    with open(COOKIES_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_cookies(cookies: dict):
    COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False)
    print(f"  Cookies saved to {COOKIES_PATH}", flush=True)


# ---------------------------------------------------------------------------
# Step 1: browser session to get valid cookies
# ---------------------------------------------------------------------------

async def get_cookies() -> dict:
    """
    Opens cian.ru in a real browser, waits for the listing page to load
    (solve any captcha that appears), then returns the session cookies.
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=[
                "--lang=ru-RU",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
            ],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            locale="ru-RU",
            no_viewport=True,
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = await context.new_page()

        ready = asyncio.get_event_loop().create_future()

        async def on_response(resp):
            if ready.done():
                return
            url = resp.url
            ct  = resp.headers.get("content-type", "")
            # Consider the session ready when the listing API fires or the
            # main page returns a large HTML with offer data
            if "get-infinite-search-result-desktop" in url:
                ready.set_result(True)

        page.on("response", on_response)

        print("=" * 60, flush=True)
        print("Opening cian.ru in browser ...", flush=True)
        print("If a captcha appears -- solve it.", flush=True)
        print(f"Waiting up to {CAPTCHA_WAIT} s for listings to load ...", flush=True)
        print("=" * 60, flush=True)

        await page.goto(LISTING_URL + "&p=1", wait_until="domcontentloaded", timeout=30000)

        try:
            await asyncio.wait_for(ready, timeout=CAPTCHA_WAIT)
        except asyncio.TimeoutError:
            print("Timeout waiting for listing page. Continuing anyway.", flush=True)

        raw = await context.cookies()
        cookies = {c["name"]: c["value"] for c in raw}
        await browser.close()

    save_cookies(cookies)
    return cookies


# ---------------------------------------------------------------------------
# Step 2: parse offers from page HTML
# ---------------------------------------------------------------------------

def _extract_json_array(html: str, key: str) -> list:
    """Find `"key":[{...}]` (non-empty array of objects) and parse it."""
    needle = f'"{key}":[{{'
    idx = html.find(needle)
    if idx == -1:
        return []
    arr_start = idx + len(f'"{key}":')
    if arr_start >= len(html):
        return []

    depth, pos = 0, arr_start
    for i, c in enumerate(html[arr_start:arr_start + 10_000_000]):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[arr_start : arr_start + i + 1])
                except json.JSONDecodeError:
                    return []
    return []


def _address_parts(address: list) -> dict:
    """Extract city, district, street, house from the address array."""
    parts = {"city": "", "district": "", "street": "", "house": ""}
    for item in address:
        geo_type = item.get("geoType", "")
        title    = item.get("title", "")
        if geo_type == "location" and not parts["city"]:
            parts["city"] = title
        elif geo_type == "district" and not parts["district"]:
            parts["district"] = title
        elif geo_type == "street" and not parts["street"]:
            parts["street"] = title
        elif geo_type == "house" and not parts["house"]:
            parts["house"] = title
    return parts


def _underground(geo: dict) -> tuple[str, str]:
    undergrounds = geo.get("undergrounds", []) or []
    if not undergrounds:
        return "", ""
    ug = undergrounds[0]
    name     = ug.get("name", "")
    walk_min = ug.get("travelTime", "")
    return name, str(walk_min) if walk_min else ""


def flatten_offer(offer: dict) -> dict:
    row = {f: "" for f in FIELDNAMES}

    row["id"]          = str(offer.get("id", "") or offer.get("cianId", ""))
    raw_url            = offer.get("fullUrl", "")
    # Strip tracking params from URL
    row["url"]         = raw_url.split("?")[0] if raw_url else ""

    row["deal_type"]   = offer.get("dealType", "")
    row["offer_type"]  = offer.get("offerType", "")
    row["flat_type"]   = offer.get("flatType", "")
    row["rooms_count"] = str(offer.get("roomsCount", "") or "")
    row["total_area"]  = str(offer.get("totalArea", "") or "")
    row["living_area"] = str(offer.get("livingArea", "") or "")
    row["kitchen_area"]= str(offer.get("kitchenArea", "") or "")
    row["floor_number"]= str(offer.get("floorNumber", "") or "")

    building           = offer.get("building", {}) or {}
    row["floors_total"]= str(building.get("floorsCount", "") or "")
    row["material_type"]= building.get("materialType", "") or ""
    row["build_year"]  = str(building.get("buildYear", "") or "")

    bt = offer.get("bargainTerms", {}) or {}
    row["price_rub"]        = str(bt.get("priceRur", "") or bt.get("price", "") or "")
    row["price_type"]       = bt.get("priceType", "") or ""
    row["sale_type"]        = bt.get("saleType", "") or ""
    row["mortgage_allowed"] = str(bt.get("mortgageAllowed", "") or "")

    geo                    = offer.get("geo", {}) or {}
    address                = geo.get("address", []) or []
    addr_parts             = _address_parts(address)
    row["city"]            = addr_parts["city"]
    row["district"]        = addr_parts["district"]
    row["street"]          = addr_parts["street"]
    row["house"]           = addr_parts["house"]
    ug_name, ug_walk       = _underground(geo)
    row["underground"]     = ug_name
    row["underground_walk_min"] = ug_walk

    row["is_apartments"]   = str(offer.get("isApartments", "") or "")
    row["has_furniture"]   = str(offer.get("hasFurniture", "") or "")
    row["is_new"]          = str(offer.get("isNew", "") or "")
    row["description"]     = (offer.get("description", "") or "").replace("\n", " ")

    photos                 = offer.get("photos", []) or []
    row["photos_count"]    = str(len(photos))

    row["creation_date"]   = offer.get("creationDate", "") or ""
    row["added"]           = offer.get("added", "") or ""

    return row


def parse_page(html: str) -> list[dict]:
    offers = _extract_json_array(html, "offers")
    return [flatten_offer(o) for o in offers if isinstance(o, dict)]


# ---------------------------------------------------------------------------
# Step 3: async page fetcher
# ---------------------------------------------------------------------------

async def fetch_page(
    session: AsyncSession,
    page_num: int,
    cookies: dict,
    sem: asyncio.Semaphore,
) -> tuple[int, list[dict]]:
    url = f"{LISTING_URL}&p={page_num}"
    async with sem:
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                r = await session.get(
                    url, headers=HEADERS, cookies=cookies, timeout=30
                )
                if r.status_code == 200 and '"offers":[' in r.text:
                    rows = parse_page(r.text)
                    return page_num, rows
                if r.status_code == 200 and ("Captcha" in r.text[:1000] or "captcha" in r.text[:1000]):
                    print(f"  [p{page_num}] captcha — session expired", flush=True)
                    return page_num, []
                print(f"  [p{page_num}] HTTP {r.status_code} (attempt {attempt})", flush=True)
            except Exception as e:
                print(f"  [p{page_num}] {e} (attempt {attempt})", flush=True)
            if attempt < RETRY_LIMIT:
                await asyncio.sleep(RETRY_DELAY)
    return page_num, []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ── Step 1: get cookies ───────────────────────────────────────────────
    cookies = load_cookies()
    if cookies:
        print(f"Using saved cookies ({len(cookies)} entries).", flush=True)
    else:
        print("Step 1 -- Open browser to capture cookies ...", flush=True)
        cookies = await get_cookies()
        print(f"  {len(cookies)} cookies captured.", flush=True)

    # Quick check that cookies work
    print("Checking cookies on page 1 ...", flush=True)
    async with AsyncSession(impersonate=IMPERSONATE) as s:
        r = await s.get(LISTING_URL + "&p=1", headers=HEADERS, cookies=cookies, timeout=30)
        if '"offers":[' not in r.text:
            print("Cookies don't seem to work (no offers in page 1). Re-run to refresh.", flush=True)
            sys.exit(1)
        # Detect total offer count
        m = re.search(r'"offersQty"\s*:\s*(\d+)', r.text)
        total_offers = int(m.group(1)) if m else 0
        # Parse page 1 already fetched
        rows_p1 = parse_page(r.text)

    offers_per_page = len(rows_p1) or 28
    total_pages     = min(MAX_PAGES, -(-total_offers // offers_per_page))  # ceiling div
    print(f"Total offers: {total_offers:,} | pages to scrape: {total_pages} "
          f"(capped at MAX_PAGES={MAX_PAGES})", flush=True)
    print(f"Page 1: {len(rows_p1)} offers", flush=True)

    # ── Step 2: scrape remaining pages ────────────────────────────────────
    all_rows: list[dict] = list(rows_p1)
    sem = asyncio.Semaphore(CONCURRENCY)

    async with AsyncSession(impersonate=IMPERSONATE) as session:
        tasks = [
            fetch_page(session, p, cookies, sem)
            for p in range(2, total_pages + 1)
        ]
        for coro in asyncio.as_completed(tasks):
            p, rows = await coro
            all_rows.extend(rows)
            print(
                f"  page {p}/{total_pages} | {len(rows)} offers"
                f" | total: {len(all_rows)}",
                flush=True,
            )

    # ── Step 3: write CSV ─────────────────────────────────────────────────
    print(f"\nWriting {len(all_rows)} rows to {OUTPUT_PATH}", flush=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Done. {len(all_rows)} records saved.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
