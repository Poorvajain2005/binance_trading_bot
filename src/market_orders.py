import logging
from binance.client import Client
from binance.enums import *

class MarketOrder:
    def __init__(self, client: Client):
        self.client = client

    def place_order(self, symbol, side, quantity):
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity=quantity
            )
            logging.info("Market order placed: %s", order)
            return order
        except Exception as e:
            logging.error("Error placing market order: %s", e)
            return None
