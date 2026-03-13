"""
Scraper capitalmotorswa.com.au — Inventaire complet.
Inventaire ~55 voitures, scraping simple requests + BeautifulSoup.
"""

import csv
import json
import re
import time
import random
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = DATA_DIR / "capital_motors_listings.csv"

BASE_URL = "https://www.capitalmotorswa.com.au"
INVENTORY_URL = f"{BASE_URL}/used-cars"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-AU,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": BASE_URL,
}

CSV_FIELDS = [
    "make", "model", "year", "km", "price",
    "seller_type", "dealer_name", "location",
    "listing_url", "date_scraped", "source",
    "badge", "transmission", "is_estimated",
]


def parse_price(text: str) -> float | None:
    if not text:
        return None
    nums = re.sub(r"[^\d]", "", str(text))
    return float(nums) if nums else None


def parse_km(text: str) -> int | None:
    if not text:
        return None
    nums = re.sub(r"[^\d]", "", str(text))
    val = int(nums) if nums else None
    # Valeur aberrante > 500k probablement en miles
    if val and val > 500000:
        val = int(val * 1.60934)
    return val


def parse_year(text: str) -> int | None:
    if not text:
        return None
    match = re.search(r"\b(19|20)\d{2}\b", str(text))
    return int(match.group()) if match else None


def parse_make_model(title: str) -> tuple[str, str]:
    """Extrait make et model depuis le titre d'une annonce."""
    title = title.strip()
    known_makes = [
        "Toyota", "Mazda", "Honda", "Hyundai", "Kia", "Suzuki",
        "Ford", "Holden", "Nissan", "Mitsubishi", "Volkswagen", "Subaru",
        "Mercedes-Benz", "BMW", "Audi", "Jeep", "Renault", "Peugeot",
    ]
    for make in known_makes:
        if make.lower() in title.lower():
            # Enlever l'année et le make pour obtenir le modèle
            remainder = re.sub(r"\b(19|20)\d{2}\b", "", title).strip()
            remainder = re.sub(make, "", remainder, flags=re.IGNORECASE).strip()
            model = remainder.split()[0] if remainder.split() else ""
            return make, model
    # Fallback : premier mot = make, deuxième = model
    parts = title.split()
    make = parts[0] if len(parts) > 0 else ""
    model = parts[1] if len(parts) > 1 else ""
    return make, model


def scrape_inventory_page(url: str) -> list[dict]:
    """Scrape une page d'inventaire Capital Motors."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Erreur : {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    listings = []
    today = date.today().isoformat()

    # Sélecteurs génériques pour les dealers australiens
    selectors = [
        ".vehicle-item",
        ".car-item",
        ".listing-card",
        ".inventory-item",
        '[class*="vehicle"]',
        '[class*="car-card"]',
        "article",
    ]

    cards = []
    for sel in selectors:
        cards = soup.select(sel)
        if len(cards) >= 3:
            break

    if not cards:
        # Chercher via JSON-LD
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") in ("Car", "Vehicle"):
                        make = item.get("brand", {}).get("name", "")
                        model = item.get("model", "")
                        price = item.get("offers", {}).get("price")
                        if make and price:
                            listings.append({
                                "make": make,
                                "model": model,
                                "year": item.get("vehicleModelDate", ""),
                                "km": item.get("mileageFromOdometer", {}).get("value", ""),
                                "price": price,
                                "seller_type": "dealer",
                                "dealer_name": "Capital Motors WA",
                                "location": "Perth WA",
                                "listing_url": item.get("url", url),
                                "date_scraped": today,
                                "source": "capital_motors",
                                "badge": "",
                                "transmission": "",
                            })
            except (json.JSONDecodeError, AttributeError):
                continue

    for card in cards:
        try:
            # Titre
            title_elem = (
                card.select_one("h2") or
                card.select_one("h3") or
                card.select_one('[class*="title"]') or
                card.select_one('[class*="name"]')
            )
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Prix
            price_elem = card.select_one('[class*="price"]') or card.select_one('[class*="Price"]')
            price_text = price_elem.get_text(strip=True) if price_elem else ""
            price = parse_price(price_text)

            # Kilométrage
            km_elem = (
                card.select_one('[class*="km"]') or
                card.select_one('[class*="odometer"]') or
                card.select_one('[class*="mileage"]')
            )
            km_text = km_elem.get_text(strip=True) if km_elem else ""
            km = parse_km(km_text)

            # Lien
            link = card.find("a", href=True)
            listing_url = ""
            if link:
                href = link["href"]
                listing_url = href if href.startswith("http") else f"{BASE_URL}{href}"

            year = parse_year(title)
            make, model = parse_make_model(title)

            if not price:
                continue

            listings.append({
                "make": make,
                "model": model,
                "year": year or "",
                "km": km or "",
                "price": price,
                "seller_type": "dealer",
                "dealer_name": "Capital Motors WA",
                "location": "Perth WA",
                "listing_url": listing_url,
                "date_scraped": today,
                "source": "capital_motors",
                "badge": "",
                "transmission": "",
            })
        except Exception:
            continue

    return listings


def scrape_with_playwright_capital() -> list[dict]:
    """Fallback Playwright pour Capital Motors."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []

    listings = []
    today = date.today().isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=HEADERS["User-Agent"],
            locale="en-AU",
        )
        try:
            page.goto(INVENTORY_URL, wait_until="networkidle", timeout=30000)
            time.sleep(2)

            items = page.evaluate("""
                () => {
                    const selectors = ['.vehicle-item', '.car-item', 'article', '[class*="vehicle"]'];
                    let cards = [];
                    for (const sel of selectors) {
                        const found = document.querySelectorAll(sel);
                        if (found.length > 2) { cards = found; break; }
                    }
                    return Array.from(cards).map(card => {
                        const title = card.querySelector('h2, h3, [class*="title"]');
                        const price = card.querySelector('[class*="price"], [class*="Price"]');
                        const km = card.querySelector('[class*="km"], [class*="odometer"]');
                        const link = card.querySelector('a[href]');
                        return {
                            title: title ? title.textContent.trim() : '',
                            price: price ? price.textContent.trim() : '',
                            km: km ? km.textContent.trim() : '',
                            url: link ? link.href : '',
                        };
                    });
                }
            """)

            for item in items:
                price = parse_price(item.get("price", ""))
                km_val = parse_km(item.get("km", ""))
                title = item.get("title", "")
                year = parse_year(title)
                make, model = parse_make_model(title)
                if price:
                    listings.append({
                        "make": make,
                        "model": model,
                        "year": year or "",
                        "km": km_val or "",
                        "price": price,
                        "seller_type": "dealer",
                        "dealer_name": "Capital Motors WA",
                        "location": "Perth WA",
                        "listing_url": item.get("url", INVENTORY_URL),
                        "date_scraped": today,
                        "source": "capital_motors",
                        "badge": "",
                        "transmission": "",
                    })
        except Exception as e:
            print(f"  Erreur Playwright : {e}")
        finally:
            browser.close()

    return listings


def generate_sample_data_capital() -> list[dict]:
    """Données d'exemple Capital Motors WA (inventaire typique)."""
    today = date.today().isoformat()
    base = {
        "seller_type": "dealer",
        "dealer_name": "Capital Motors WA",
        "location": "Perth WA",
        "date_scraped": today,
        "source": "capital_motors",
        "badge": "",
        "transmission": "Automatic",
        "is_estimated": True,
    }

    samples = [
        {**base, "make": "Toyota", "model": "Corolla", "year": 2016, "km": 95000,
         "price": 13900, "listing_url": f"{BASE_URL}/used-cars/toyota-corolla-2016"},
        {**base, "make": "Toyota", "model": "Yaris", "year": 2015, "km": 78000,
         "price": 10990, "listing_url": f"{BASE_URL}/used-cars/toyota-yaris-2015"},
        {**base, "make": "Mazda", "model": "3", "year": 2015, "km": 102000,
         "price": 12500, "listing_url": f"{BASE_URL}/used-cars/mazda-3-2015"},
        {**base, "make": "Mazda", "model": "2", "year": 2016, "km": 68000,
         "price": 11200, "listing_url": f"{BASE_URL}/used-cars/mazda-2-2016"},
        {**base, "make": "Honda", "model": "Jazz", "year": 2014, "km": 88000,
         "price": 10500, "listing_url": f"{BASE_URL}/used-cars/honda-jazz-2014"},
        {**base, "make": "Honda", "model": "Civic", "year": 2013, "km": 115000,
         "price": 9900, "listing_url": f"{BASE_URL}/used-cars/honda-civic-2013"},
        {**base, "make": "Hyundai", "model": "i30", "year": 2015, "km": 89000,
         "price": 11500, "listing_url": f"{BASE_URL}/used-cars/hyundai-i30-2015"},
        {**base, "make": "Hyundai", "model": "Accent", "year": 2014, "km": 97000,
         "price": 8990, "listing_url": f"{BASE_URL}/used-cars/hyundai-accent-2014"},
        {**base, "make": "Kia", "model": "Rio", "year": 2015, "km": 72000,
         "price": 9500, "listing_url": f"{BASE_URL}/used-cars/kia-rio-2015"},
        {**base, "make": "Suzuki", "model": "Swift", "year": 2015, "km": 65000,
         "price": 10200, "listing_url": f"{BASE_URL}/used-cars/suzuki-swift-2015"},
        {**base, "make": "Nissan", "model": "Tiida", "year": 2013, "km": 128000,
         "price": 8500, "listing_url": f"{BASE_URL}/used-cars/nissan-tiida-2013"},
        {**base, "make": "Ford", "model": "Focus", "year": 2014, "km": 108000,
         "price": 9800, "listing_url": f"{BASE_URL}/used-cars/ford-focus-2014"},
        {**base, "make": "Toyota", "model": "Corolla", "year": 2017, "km": 74000,
         "price": 14500, "listing_url": f"{BASE_URL}/used-cars/toyota-corolla-2017"},
        {**base, "make": "Mazda", "model": "3", "year": 2017, "km": 81000,
         "price": 13800, "listing_url": f"{BASE_URL}/used-cars/mazda-3-2017"},
        {**base, "make": "Volkswagen", "model": "Polo", "year": 2015, "km": 92000,
         "price": 11900, "listing_url": f"{BASE_URL}/used-cars/volkswagen-polo-2015"},
    ]
    return samples


def save_to_csv(listings: list[dict], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for listing in listings:
            row = {field: listing.get(field, "") for field in CSV_FIELDS}
            writer.writerow(row)
    print(f"  ✅ {len(listings)} annonces sauvegardées dans {filepath}")


def scrape_capital_motors(force_sample: bool = False) -> list[dict]:
    """Fonction principale scraping Capital Motors WA."""
    print("\n🔍 Scraping Capital Motors WA...")

    if force_sample:
        print("  Mode données d'exemple activé.")
        listings = generate_sample_data_capital()
        save_to_csv(listings, OUTPUT_FILE)
        return listings

    all_listings = []

    # Pages à scraper
    urls = [
        INVENTORY_URL,
        f"{INVENTORY_URL}?page=2",
        f"{INVENTORY_URL}/under-15000",
    ]

    for url in urls:
        print(f"  URL : {url}")
        page_listings = scrape_inventory_page(url)
        all_listings.extend(page_listings)
        print(f"  → {len(page_listings)} annonces")

        if page_listings:
            time.sleep(random.uniform(1.0, 2.0))

    if not all_listings:
        print("  Essai avec Playwright...")
        all_listings = scrape_with_playwright_capital()

    if not all_listings:
        print("  ⚠️  Aucune annonce. Utilisation des données d'exemple.")
        all_listings = generate_sample_data_capital()

    # Dédoublonnage par URL
    seen_urls = set()
    unique_listings = []
    for lst in all_listings:
        url = lst.get("listing_url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_listings.append(lst)

    save_to_csv(unique_listings, OUTPUT_FILE)
    print(f"\n✅ Total Capital Motors : {len(unique_listings)} annonces")
    return unique_listings


if __name__ == "__main__":
    import sys
    force_sample = "--sample" in sys.argv
    listings = scrape_capital_motors(force_sample=force_sample)
    print("\nExemple d'annonces :")
    for lst in listings[:5]:
        km_str = f"{lst['km']:,}" if isinstance(lst['km'], (int, float)) and lst['km'] else "N/A"
        print(f"  {lst['year']} {lst['make']} {lst['model']} — {km_str} km — ${lst['price']:,.0f}")
