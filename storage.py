import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List

from config import BASE_CURRENCY, CURRENCY_FILE, RATES_FILE


def normalize_currency_code(value: str) -> str:
    if value is None:
        raise ValueError("Currency code is required.")
    code = value.strip().upper()
    if not code.isalpha() or len(code) != 3:
        raise ValueError("Currency code must be a three-letter alphabetic code.")
    return code


def ensure_file_exists(path: Path, default_content: str = "") -> None:
    if not path.exists():
        path.write_text(default_content)


def load_currency_codes() -> List[str]:
    ensure_file_exists(CURRENCY_FILE)
    currencies: List[str] = []
    for line in CURRENCY_FILE.read_text().splitlines():
        code = line.strip().upper()
        if code and code not in currencies:
            currencies.append(code)
    if BASE_CURRENCY not in currencies:
        currencies.append(BASE_CURRENCY)
        save_currency_codes(currencies)
    return currencies


def save_currency_codes(currencies: List[str]) -> None:
    normalized = [normalize_currency_code(code) for code in currencies]
    unique_codes: List[str] = []
    for code in normalized:
        if code not in unique_codes:
            unique_codes.append(code)
    CURRENCY_FILE.write_text("\n".join(unique_codes) + ("\n" if unique_codes else ""))


def append_currency_code(code: str) -> bool:
    code = normalize_currency_code(code)
    currencies = load_currency_codes()
    if code in currencies:
        return False
    currencies.append(code)
    save_currency_codes(currencies)
    return True


def remove_currency_code(code: str) -> bool:
    code = normalize_currency_code(code)
    if code == BASE_CURRENCY:
        return False
    currencies = load_currency_codes()
    if code not in currencies:
        return False
    currencies = [c for c in currencies if c != code]
    save_currency_codes(currencies)
    return True


def load_rates() -> Dict[str, Decimal]:
    if not RATES_FILE.exists():
        return {}
    raw = json.loads(RATES_FILE.read_text())
    rates: Dict[str, Decimal] = {}
    for key, value in raw.items():
        rates[normalize_currency_code(key)] = Decimal(str(value))
    return rates


def save_rates(rates: Dict[str, Decimal]) -> None:
    data = {normalize_currency_code(key): float(value) for key, value in rates.items()}
    RATES_FILE.write_text(json.dumps(data, indent=2))


def parse_amount(value: str) -> Decimal:
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValueError("Amount must be a valid number.")


def convert_amount(amount: str, currency_from: str, currency_target: str, rates: Dict[str, Decimal]) -> Decimal:
    currency_from = normalize_currency_code(currency_from)
    currency_target = normalize_currency_code(currency_target)
    amount_value = parse_amount(amount)
    if currency_from not in rates:
        raise KeyError(currency_from)
    if currency_target not in rates:
        raise KeyError(currency_target)
    return (amount_value / rates[currency_from]) * rates[currency_target]
