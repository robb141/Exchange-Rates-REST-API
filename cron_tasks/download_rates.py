import json

import requests

from cron_tasks.celer import app


@app.task
def download_rates():
    """
    Download rates from openexchangerates.org using id hidden in exchange_id.txt.

    """
    # Exchange_id to openexchangerates.org kept in txt file
    with open("exchange_id.txt", "r") as f:
        exchange_rates_id = f.read()

    # Currencies to scrape
    with open(r"currencies.txt", "r") as f:
        my_currencies = f.read().splitlines()

    my_currs = dict.fromkeys(my_currencies, 0)
    response = requests.get(
        f"https://openexchangerates.org/api/latest.json?app_id={exchange_rates_id}"
    )
    all_currencies = response.json()["rates"]
    base = response.json()["base"]
    if base not in my_currs:
        my_currs[base] = 0
    for key in my_currs:
        my_currs[key] = all_currencies[key]
    with open(r"rates.json", "w") as f:
        json.dump(my_currs, f)
    return my_currs


if __name__ == "__main__":
    download_rates()
