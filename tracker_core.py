import requests
from parser import parse_product_info
from utils import (
    save_price_record,
    get_previous_price,
    generate_summary,
    export_excel_report,
    send_email,
)


def fetch_page(url: str, headers: dict) -> str | None:
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"ERROR: {e}"


def process_product(
    url: str,
    headers: dict,
    csv_file: str,
    email_config: dict | None = None,
    logger=print,
) -> None:
    logger("=" * 60)
    logger(f"İşleniyor: {url}")

    html = fetch_page(url, headers)
    if html is None:
        logger("Sayfa alınamadı.\n")
        return

    if isinstance(html, str) and html.startswith("ERROR:"):
        logger(f"İstek hatası: {html.replace('ERROR:', '').strip()}\n")
        return

    result = parse_product_info(html)

    name = result.get("name")
    price = result.get("price")
    currency = result.get("currency", "UNKNOWN")

    if not name:
        logger("Ürün adı bulunamadı.\n")
        return

    if price is None:
        logger("Fiyat bulunamadı.\n")
        return

    previous_price = get_previous_price(csv_file, url)

    logger(f"Ürün: {name}")
    logger(f"Güncel fiyat: {price:.2f} {currency}")

    if previous_price is not None:
        logger(f"Önceki fiyat: {previous_price:.2f} {currency}")

        if price < previous_price:
            logger("Durum: Fiyat düşmüş 🚨")

            if email_config:
                send_email(
                    subject="Fiyat Düştü!",
                    body=(
                        f"{name} ürünü {price:.2f} {currency} oldu!\n\n"
                        f"Önceki fiyat: {previous_price:.2f} {currency}\n"
                        f"Link: {url}"
                    ),
                    config=email_config,
                )

        elif price > previous_price:
            logger("Durum: Fiyat artmış.")
        else:
            logger("Durum: Fiyat aynı kalmış.")
    else:
        logger("Durum: Bu ürün için ilk kayıt alınıyor.")

    save_price_record(csv_file, name, price, currency, url)
    logger("Kayıt tamam.\n")


def run_tracker(
    target_urls: list[str],
    headers: dict,
    csv_file: str,
    excel_file: str,
    email_config: dict | None = None,
    logger=print,
):
    logger("Çoklu ürün fiyat takibi başlatıldı...\n")

    for url in target_urls:
        process_product(
            url=url,
            headers=headers,
            csv_file=csv_file,
            email_config=email_config,
            logger=logger,
        )

    logger("=" * 60)
    logger(f"Tüm işlemler bitti. CSV dosyası: {csv_file}")

    summary = generate_summary(csv_file)

    if summary:
        logger("\n" + "=" * 80)
        logger("ÖZET RAPOR")
        logger("=" * 80)
        logger(f"{'Ürün':30} {'Fiyat':>10} {'Önceki':>10} {'Para':>8} {'Durum':>12} {'Kayıt':>8}")
        logger("-" * 80)

        for item in summary:
            previous = (
                f"{item['previous_price']:.2f}"
                if item["previous_price"] is not None
                else "-"
            )

            logger(
                f"{item['product_name'][:30]:30} "
                f"{item['current_price']:>10.2f} "
                f"{previous:>10} "
                f"{item['currency']:>8} "
                f"{item['status']:>12} "
                f"{item['record_count']:>8}"
            )

        logger("=" * 80)
    else:
        logger("Özet veri bulunamadı.")

    if export_excel_report(csv_file, excel_file):
        logger(f"Excel raporu oluşturuldu: {excel_file}")
    else:
        logger("Excel raporu oluşturulamadı.")