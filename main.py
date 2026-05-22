from decimal import InvalidOperation

from flask import Flask
from flask_restful import Api, Resource, reqparse

from config import BASE_CURRENCY
from cron_tasks.download_rates import download_rates
from storage import (
    append_currency_code,
    convert_amount,
    load_currency_codes,
    load_rates,
    normalize_currency_code,
    parse_amount,
    remove_currency_code,
    save_rates,
)

app = Flask(__name__)
api = Api(app)


@app.route("/")
def index():
    return {
        "service": "Exchange Rates REST API",
        "endpoints": ["/currency", "/currencies", "/currencies/<code>"],
    }


currency_get_args = reqparse.RequestParser()
currency_get_args.add_argument(
    "currency_from",
    type=str,
    required=True,
    location=["args"],
    help="currency_from is required.",
)
currency_get_args.add_argument(
    "currency_target",
    type=str,
    required=True,
    location=["args"],
    help="currency_target is required.",
)
currency_get_args.add_argument(
    "amount",
    type=str,
    required=True,
    location=["args"],
    help="amount is required.",
)

currency_post_args = reqparse.RequestParser()
currency_post_args.add_argument(
    "currency",
    type=str,
    required=True,
    location=["form", "json"],
    help="currency is required.",
)

currency_put_args = reqparse.RequestParser()
currency_put_args.add_argument(
    "amount",
    type=str,
    required=True,
    location=["form", "json"],
    help="amount is required.",
)


class CurrencyConversion(Resource):
    def get(self):
        args = currency_get_args.parse_args()
        currency_from = normalize_currency_code(args["currency_from"])
        currency_target = normalize_currency_code(args["currency_target"])
        amount = args["amount"]

        rates = load_rates()
        if not rates:
            rates = download_rates()

        if currency_from not in rates or currency_target not in rates:
            rates = download_rates()

        if currency_from not in rates:
            return {"message": f"Currency {currency_from} is not valid."}, 404
        if currency_target not in rates:
            return {"message": f"Currency {currency_target} is not valid."}, 404

        try:
            converted = convert_amount(amount, currency_from, currency_target, rates)
        except ValueError:
            return {"message": "Amount must be a valid number."}, 400
        except InvalidOperation:
            return {"message": "Amount must be a valid number."}, 400

        return {
            "currency_from": currency_from,
            "currency_target": currency_target,
            "amount": float(converted),
        }


class CurrencyList(Resource):
    def get(self):
        return {"currencies": load_currency_codes()}

    def post(self):
        args = currency_post_args.parse_args()
        currency = normalize_currency_code(args["currency"])

        if not append_currency_code(currency):
            return {"message": f"Currency {currency} is already tracked."}, 409

        return {"message": f"Currency {currency} added."}, 201


class CurrencyRate(Resource):
    def put(self, currency_code):
        currency_code = normalize_currency_code(currency_code)
        args = currency_put_args.parse_args()
        amount = args["amount"]

        tracked = load_currency_codes()
        if currency_code not in tracked:
            return {"message": f"Currency {currency_code} is not tracked."}, 404

        try:
            value = parse_amount(amount)
        except ValueError:
            return {"message": "amount must be a valid number."}, 400

        rates = load_rates()
        rates[currency_code] = value
        save_rates(rates)
        return {"message": f"Rate for {currency_code} saved."}, 200

    def delete(self, currency_code):
        currency_code = normalize_currency_code(currency_code)
        if currency_code == BASE_CURRENCY:
            return {"message": f"Cannot remove base currency {BASE_CURRENCY}."}, 400

        if not remove_currency_code(currency_code):
            return {"message": f"Currency {currency_code} is not tracked."}, 404

        rates = load_rates()
        rates.pop(currency_code, None)
        save_rates(rates)
        return {"message": f"Currency {currency_code} removed."}, 200


api.add_resource(CurrencyConversion, "/currency")
api.add_resource(CurrencyList, "/currencies")
api.add_resource(CurrencyRate, "/currencies/<string:currency_code>")


if __name__ == "__main__":
    app.run(debug=True)
