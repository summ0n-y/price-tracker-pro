from config import (
    TARGET_URLS,
    HEADERS,
    CSV_FILE,
    EXCEL_FILE,
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    SMTP_SERVER,
    SMTP_PORT,
    TO_EMAIL,
)
from tracker_core import run_tracker


def main():
    email_config = {
        "EMAIL_ADDRESS": EMAIL_ADDRESS,
        "EMAIL_PASSWORD": EMAIL_PASSWORD,
        "SMTP_SERVER": SMTP_SERVER,
        "SMTP_PORT": SMTP_PORT,
        "TO_EMAIL": TO_EMAIL,
    }

    run_tracker(
        target_urls=TARGET_URLS,
        headers=HEADERS,
        csv_file=CSV_FILE,
        excel_file=EXCEL_FILE,
        email_config=email_config,
    )


if __name__ == "__main__":
    main()