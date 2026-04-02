import json
import os


SETTINGS_DIR = "data"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")


DEFAULT_SETTINGS = {
    "email_address": "",
    "email_password": "",
    "to_email": "",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
}


def ensure_settings_dir():
    os.makedirs(SETTINGS_DIR, exist_ok=True)


def load_settings() -> dict:
    ensure_settings_dir()

    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_settings(settings: dict) -> None:
    ensure_settings_dir()

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)