from python_bitvavo_api.bitvavo import Bitvavo


class Client(object):
    def __init__(self, key, secret):
        self.bitvavo = Bitvavo({'APIKEY': key, 'APISECRET': secret})

    def get_balance(self, only_euro=False):
        response = self.bitvavo.balance({})
        if only_euro:
            response = list(filter(lambda x: x['symbol'] == 'EUR', response))

        return response

    def place_order(self, order):
        response = self.bitvavo.placeOrder(market=order['market'], side=order['side'], orderType=order['orderType'],
                                           body=order['body'])
        print(f"Handled {response['side']} order {response['market']}: {response['filledAmount']} for "
              f"{response['filledAmountQuote']+response['feePaid']} {response['feeCurrency']}")

    def get_orders(self, market):
        response = self.bitvavo.getOrders(market, {'limit': 1000})

        return response

    def get_ticker_price(self, market):
        response = self.bitvavo.tickerPrice({'market': market})

        return response

