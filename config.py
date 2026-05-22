import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
CURRENCY_FILE = Path(os.getenv("CURRENCY_FILE", ROOT_DIR / "currencies.txt"))
RATES_FILE = Path(os.getenv("RATES_FILE", ROOT_DIR / "rates.json"))
EXCHANGE_ID_FILE = Path(os.getenv("EXCHANGE_ID_FILE", ROOT_DIR / "exchange_id.txt"))
OPENEXCHANGE_URL = os.getenv(
    "OPENEXCHANGE_URL",
    "https://openexchangerates.org/api/latest.json",
).strip()
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "USD").strip().upper()
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)


def get_app_id() -> str:
    app_id = os.getenv("OPENEXCHANGE_APP_ID")
    if app_id:
        app_id = app_id.strip()
    elif EXCHANGE_ID_FILE.exists():
        app_id = EXCHANGE_ID_FILE.read_text().strip()
    else:
        raise RuntimeError(
            "OpenExchangeRates app id is not configured. Set OPENEXCHANGE_APP_ID "
            "or create exchange_id.txt in the project root."
        )
    if not app_id:
        raise RuntimeError("OpenExchangeRates app id is empty.")
    return app_id
