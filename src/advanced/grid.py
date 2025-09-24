import logging
import time
from binance.client import Client
from binance.enums import *

class GridOrder:
    def __init__(self, client: Client):
        self.client = client

    def place_order(self, symbol, quantity_per_grid, price_low, price_high, grid_count):
        try:
            price_step = (price_high - price_low) / (grid_count - 1)
            orders = []
            
            for i in range(grid_count):
                price = price_low + (i * price_step)
                
                # Place buy orders below current price, sell orders above
                side = SIDE_BUY if i < grid_count // 2 else SIDE_SELL
                
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity_per_grid,
                    price=price
                )
                logging.info("Grid order %d placed: %s", i+1, order)
                orders.append(order)
                
            return orders
        except Exception as e:
            logging.error("Error placing grid orders: %s", e)
            return None