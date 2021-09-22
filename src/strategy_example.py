# example to buy 50 EURs of BTC and 10 EURs of ETH
strategy = [
    {"market": "BTC-EUR", "side": "buy", "orderType": "market", "body": {"amountQuote": 50}},
    {"market": "ETH-EUR", "side": "buy", "orderType": "market", "body": {"amountQuote": 10}}
]

# specify markets here in which you made trades (which are not in your strategy anymore, but you want to include in the
# reporting; e.g. BTC-EUR)
additional_markets_in_report = []