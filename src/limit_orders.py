import logging
from binance.client import Client
from binance.enums import *

class LimitOrder:
    def __init__(self, client: Client):
        self.client = client

    def place_order(self, symbol, side, quantity, price):
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=price
            )
            logging.info("Limit order placed: %s", order)
            return order
        except Exception as e:
            logging.error("Error placing limit order: %s", e)
            return None
