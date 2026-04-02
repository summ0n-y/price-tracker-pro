from bs4 import BeautifulSoup
import re


def detect_currency(text: str) -> str:
    if "£" in text:
        return "GBP"
    if "$" in text:
        return "USD"
    if "€" in text:
        return "EUR"
    if "₺" in text or "TL" in text.upper():
        return "TRY"
    return "UNKNOWN"


def clean_price(text: str) -> float | None:
    if not text:
        return None

    text = text.strip()
    text = re.sub(r"[^\d,\.]", "", text)

    if text.count(",") == 1 and text.count(".") >= 1:
        text = text.replace(".", "").replace(",", ".")
    elif text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def parse_product_info(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    name_selectors = [
        "div.product_main h1",
        "h1",
        ".product-title",
        "[data-testid='product-title']",
        "meta[property='og:title']",
    ]

    price_selectors = [
        "p.price_color",
        ".price",
        ".product-price",
        "[data-testid='price-current']",
        ".prc-dsc",
        "meta[property='product:price:amount']",
    ]

    product_name = None
    product_price = None
    currency = "UNKNOWN"

    for selector in name_selectors:
        el = soup.select_one(selector)
        if el:
            if el.name == "meta":
                product_name = el.get("content", "").strip()
            else:
                product_name = el.get_text(strip=True)
            if product_name:
                break

    for selector in price_selectors:
        el = soup.select_one(selector)
        if el:
            if el.name == "meta":
                raw_price = el.get("content", "").strip()
            else:
                raw_price = el.get_text(strip=True)

            currency = detect_currency(raw_price)
            product_price = clean_price(raw_price)
            if product_price is not None:
                break

    return {
        "name": product_name,
        "price": product_price,
        "currency": currency,
    }