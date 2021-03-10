import requests

BASE = "http://127.0.0.1:5000"


# # GET
# d = {"currency_from": "EUR", "currency_target": "PLN", "amount": 20}
# response = requests.get(BASE + "/currency/", data=d)
# print(response.json())

# # POST
# response = requests.post(BASE + '/currency/', {'currency': 'NOK'})
# print(response.json())

# # PUT
# response = requests.put(BASE + '/currency/', {'curr': 'CZK', 'amount': 2000})
# print(response.json())

# # DELETE
# response = requests.delete(BASE + '/currency/', data={'currency': 'LBP'})
# print(response.json())
