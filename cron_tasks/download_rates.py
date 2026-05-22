import json
import sys
from decimal import Decimal
from pathlib import Path

import requests

try:
    from cron_tasks.celer import app
except ImportError:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from cron_tasks.celer import app

from config import BASE_CURRENCY, OPENEXCHANGE_URL, get_app_id
from storage import load_currency_codes, save_rates


@app.task(name="cron_tasks.download_rates.download_rates")
def download_rates():
    app_id = get_app_id()
    tracked_currencies = load_currency_codes()

    response = requests.get(f"{OPENEXCHANGE_URL}?app_id={app_id}", timeout=10)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to download exchange rates: {response.status_code} {response.text}"
        )

    payload = response.json()
    rates = payload.get("rates")
    api_base = payload.get("base", BASE_CURRENCY).strip().upper()

    if not isinstance(rates, dict):
        raise RuntimeError("Unexpected response from exchange rates provider.")

    if api_base not in tracked_currencies:
        tracked_currencies.append(api_base)

    missing = [code for code in tracked_currencies if code != api_base and code not in rates]
    if missing:
        raise RuntimeError(
            f"Exchange rates response does not include: {', '.join(missing)}"
        )

    downloaded = {api_base: Decimal("1")}
    for code in tracked_currencies:
        if code == api_base:
            continue
        downloaded[code] = Decimal(str(rates[code]))

    save_rates(downloaded)
    return downloaded


if __name__ == "__main__":
    print(download_rates())
