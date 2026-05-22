# Exchange Rates REST API

A small Flask REST API for currency conversion using OpenExchangeRates data.

## Setup

1. Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure your OpenExchangeRates app id.

Preferred option:

```bash
export OPENEXCHANGE_APP_ID=your_app_id_here
```

Fallback option: create `exchange_id.txt` in the project root and place the app id on the first line.

## Run the API

```bash
python main.py
```

The API will be available at `http://127.0.0.1:5000`.

## Endpoints

- `GET /currency?currency_from=USD&currency_target=EUR&amount=100`
  - Convert an amount between two currencies
- `GET /currencies`
  - List tracked currency codes
- `POST /currencies` with body `currency=EUR`
  - Add a currency to the tracked list
- `PUT /currencies/<code>` with body `amount=1.234`
  - Update the stored exchange rate for a currency
- `DELETE /currencies/<code>`
  - Remove a currency from the tracked list

## Scheduling

This project includes a Celery beat schedule to refresh rates daily.

Celery requires a message broker. By default, the project uses Redis:

```bash
export CELERY_BROKER_URL=redis://localhost:6379/0
```

Start the Celery beat scheduler with:

```bash
python -m celery -A cron_tasks.celer.app beat
```

If you want to execute the task manually:

```bash
python -m cron_tasks.download_rates
```

## Makefile

You can use the provided `Makefile` to simplify commands:

```bash
make venv          # create the Python virtual environment
make install       # install dependencies
make setup         # create venv and install dependencies
make run           # run the Flask API
make celery-beat   # start Celery beat with CELERY_BROKER_URL
make download      # fetch rates manually
make test          # run tests
```

## Notes

- `rates.json` and `exchange_id.txt` are ignored by Git.
- Environment variables also support:
  - `CURRENCY_FILE`
  - `RATES_FILE`
  - `OPENEXCHANGE_URL`
  - `BASE_CURRENCY`
  - `CELERY_BROKER_URL`
  - `CELERY_RESULT_BACKEND`

## Testing

Run `python test.py` to execute a small local API verification script.
