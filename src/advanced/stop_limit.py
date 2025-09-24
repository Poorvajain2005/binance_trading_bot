import logging
from binance.client import Client
from binance.enums import *

class StopLimitOrder:
    def __init__(self, client: Client):
        self.client = client

    def place_order(self, symbol, side, quantity, stop_price, limit_price):
        """Place stop-limit order: triggers limit order when stop price is hit"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_STOP,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                stopPrice=stop_price,
                price=limit_price
            )
            logging.info("Stop-limit order placed: %s", order)
            return order
        except Exception as e:
            logging.error("Error placing stop-limit order: %s", e)
            return None
