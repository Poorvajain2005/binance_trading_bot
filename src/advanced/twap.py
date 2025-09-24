import logging
import time
from binance.client import Client
from binance.enums import *

class TWAPOrder:
    def __init__(self, client: Client):
        self.client = client

    def place_order(self, symbol, side, total_quantity, slices, interval_sec):
        """Place TWAP order: split large orders into smaller chunks over time"""
        try:
            qty_per_order = total_quantity / slices
            orders = []
            for i in range(slices):
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                    type=FUTURE_ORDER_TYPE_MARKET,
                    quantity=qty_per_order
                )
                logging.info("TWAP slice %d/%d placed: %s", i+1, slices, order)
                orders.append(order)
                if i < slices - 1:  # Don't sleep after last order
                    time.sleep(interval_sec)
            return orders
        except Exception as e:
            logging.error("Error placing TWAP orders: %s", e)
            return None
