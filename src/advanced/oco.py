# OCO is not directly available for futures in python-binance. 
# For assignment purpose, we simulate placing two orders: take-profit and stop-loss.

import logging
from binance.client import Client
from binance.enums import *

class OCOOrder:
    def __init__(self, client: Client):
        self.client = client

    def place_order(self, symbol, side, quantity, take_profit_price, stop_loss_price):
        """Place OCO order: take-profit and stop-loss simultaneously"""
        try:
            # Take profit order (opposite side)
            tp_side = SIDE_SELL if side.upper() == "BUY" else SIDE_BUY
            tp = self.client.futures_create_order(
                symbol=symbol,
                side=tp_side,
                type=FUTURE_ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=take_profit_price
            )
            # Stop loss order (opposite side)
            sl = self.client.futures_create_order(
                symbol=symbol,
                side=tp_side,
                type=FUTURE_ORDER_TYPE_STOP_MARKET,
                stopPrice=stop_loss_price,
                quantity=quantity
            )
            logging.info("OCO simulated: TP=%s, SL=%s", tp, sl)
            return tp, sl
        except Exception as e:
            logging.error("Error placing OCO order: %s", e)
            return None
