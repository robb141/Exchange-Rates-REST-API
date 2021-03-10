import json
from os import path

from flask import Flask
from flask_restful import Api, Resource, reqparse

from cron_tasks.download_rates import download_rates

app = Flask(__name__)
api = Api(app)


currency_get_args = reqparse.RequestParser()
currency_get_args.add_argument(
    "currency_from", type=str, help="Currency is required.", required=True
)
currency_get_args.add_argument(
    "currency_target", type=str, help="Currency is required.", required=True
)
currency_get_args.add_argument(
    "amount", type=str, help="Amount is required.", required=True
)

currency_put_args = reqparse.RequestParser()
currency_put_args.add_argument(
    "curr", type=str, help="Currency is required.", required=True
)
currency_put_args.add_argument(
    "amount", type=str, help="Amount is required.", required=True
)

currency_post_and_delete_args = reqparse.RequestParser()
currency_post_and_delete_args.add_argument(
    "currency", type=str, help="Currency is required.", required=True
)


class Currency(Resource):
    def _get_currencies(self):
        """Returns list of searched currencies"""
        with open("currencies.txt", "r") as f:
            return f.read().splitlines()

    def _get_rates(self):
        """
        Example how currencies can look like: {'CZK': 22.232, 'EUR': 0.841939, 'PLN': 3.868147, 'USD': 1}
        """
        if not path.exists("rates.json"):
            download_rates()
        with open("rates.json", "r") as f:
            return json.load(f)

    def _put_rates(self, curs):
        with open("rates.json", "w") as f:
            return json.dump(curs, f)

    def get(self):
        args = currency_get_args.parse_args()
        currency_from = args["currency_from"]
        currency_target = args["currency_target"]
        amount = args["amount"]
        currencies = self._get_rates()
        print(currency_target + " " + currency_from + " " + amount)

        # Currencies to scrape. My_currencies can look like: ['CZK', 'EUR', 'USD']
        my_currencies = self._get_currencies()
        if any(cur not in currencies for cur in my_currencies):
            currencies = download_rates()

        if currency_from not in currencies:
            return {"message": f"Currency {currency_from} is not valid."}, 404
        if currency_target not in currencies:
            return {"message": f"Currency {currency_target} is not valid."}, 404
        try:
            float(amount)
        except ValueError:
            return {"message": "Amount could not be converted to number."}, 404

        return {
            currency_target: float(amount)
            / currencies[currency_from]
            * currencies[currency_target]
        }

    def post(self):
        args = currency_post_and_delete_args.parse_args()
        currency = args["currency"]

        my_currencies = self._get_currencies()
        with open("currencies.txt", "a") as f:
            if currency in my_currencies:
                return {"message": "Currency already in currencies."}, 409
            else:
                f.write("\n" + currency)
        return {"message": f"Currency {currency} added."}, 200

    def put(self):
        args = currency_put_args.parse_args()
        currency = args["curr"]
        amount = args["amount"]
        currencies = self._get_rates()

        try:
            float(amount)
        except ValueError:
            return {"message": "Amount could not be converted to number."}, 404

        currencies[currency] = float(amount)
        return self._put_rates(currencies)

    def delete(self):
        args = currency_post_and_delete_args.parse_args()
        currency = args["currency"]

        my_currencies = self._get_currencies()
        if currency not in my_currencies:
            return {
                "message": f"Currency {currency} not in file, nothing to delete."
            }, 404
        with open("currencies.txt", "w") as f:
            my_currencies.remove(currency)
            f.write("\n".join(my_currencies))
        return {"message": f"Currency {currency} was deleted."}, 200


api.add_resource(Currency, "/currency/")


if __name__ == "__main__":
    app.run(debug=True)
