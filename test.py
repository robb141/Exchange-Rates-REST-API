import json
import os
import tempfile
import unittest
from pathlib import Path

# Configure test files before importing the app so config values are loaded correctly.
TEST_DIR = Path(tempfile.mkdtemp(prefix="exchange_rates_test_"))
os.environ["CURRENCY_FILE"] = str(TEST_DIR / "currencies.txt")
os.environ["RATES_FILE"] = str(TEST_DIR / "rates.json")
os.environ["OPENEXCHANGE_APP_ID"] = "dummy"

from main import app


class CurrencyApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.currency_file = Path(os.environ["CURRENCY_FILE"])
        cls.rate_file = Path(os.environ["RATES_FILE"])
        cls.currency_file.write_text("USD\nEUR\nPLN\nCZK\n")
        cls.rate_file.write_text(
            json.dumps({"USD": 1.0, "EUR": 0.85, "PLN": 4.0, "CZK": 22.0})
        )

    def test_get_currencies(self):
        response = self.client.get("/currencies")
        self.assertEqual(response.status_code, 200)
        self.assertIn("EUR", response.json["currencies"])

    def test_conversion(self):
        response = self.client.get(
            "/currency",
            query_string={"currency_from": "EUR", "currency_target": "PLN", "amount": "10"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json["amount"], 47.05882352941176, places=6)

    def test_add_currency(self):
        response = self.client.post("/currencies", json={"currency": "NOK"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Currency NOK added.")

    def test_update_rate(self):
        response = self.client.put("/currencies/EUR", json={"amount": "0.90"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Rate for EUR saved.", response.json["message"])

    def test_remove_currency(self):
        response = self.client.delete("/currencies/CZK")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Currency CZK removed.", response.json["message"])


if __name__ == "__main__":
    unittest.main()
