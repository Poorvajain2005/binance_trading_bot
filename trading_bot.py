#!/usr/bin/env python3
import logging
import sys
import argparse
from binance import Client
from binance.exceptions import BinanceAPIException

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_symbol(self, symbol):
        try:
            info = self.client.futures_exchange_info()
            symbols = [s['symbol'] for s in info['symbols']]
            return symbol.upper() in symbols
        except Exception as e:
            self.logger.error(f"Error validating symbol: {e}")
            return False
            
    def get_balance(self):
        try:
            account = self.client.futures_account()
            self.logger.info("Balance retrieved successfully")
            return float(account['totalWalletBalance'])
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting balance: {e}")
            raise
            
    def market_order(self, symbol, side, quantity):
        try:
            self.logger.info(f"Placing market order: {side} {quantity} {symbol}")
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            self.logger.info(f"Market order executed: {order}")
            return order
        except BinanceAPIException as e:
            self.logger.error(f"Market order failed: {e}")
            raise
            
    def limit_order(self, symbol, side, quantity, price):
        try:
            self.logger.info(f"Placing limit order: {side} {quantity} {symbol} @ {price}")
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce='GTC'
            )
            self.logger.info(f"Limit order placed: {order}")
            return order
        except BinanceAPIException as e:
            self.logger.error(f"Limit order failed: {e}")
            raise
            
    def stop_limit_order(self, symbol, side, quantity, stop_price, limit_price):
        try:
            self.logger.info(f"Placing stop-limit order: {side} {quantity} {symbol} stop@{stop_price} limit@{limit_price}")
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=quantity,
                stopPrice=stop_price,
                price=limit_price,
                timeInForce='GTC'
            )
            self.logger.info(f"Stop-limit order placed: {order}")
            return order
        except BinanceAPIException as e:
            self.logger.error(f"Stop-limit order failed: {e}")
            raise
            
    def twap_order(self, symbol, side, total_quantity, duration_minutes, intervals=10):
        """TWAP - Time Weighted Average Price order"""
        import time
        import threading
        
        try:
            chunk_size = total_quantity / intervals
            interval_seconds = (duration_minutes * 60) / intervals
            
            self.logger.info(f"Starting TWAP order: {side} {total_quantity} {symbol} over {duration_minutes}min in {intervals} chunks")
            
            orders = []
            
            def execute_chunk(chunk_num):
                try:
                    time.sleep(chunk_num * interval_seconds)
                    order = self.market_order(symbol, side, chunk_size)
                    orders.append(order)
                    self.logger.info(f"TWAP chunk {chunk_num + 1}/{intervals} executed: {order['orderId']}")
                except Exception as e:
                    self.logger.error(f"TWAP chunk {chunk_num + 1} failed: {e}")
            
            # Execute chunks in parallel with delays
            threads = []
            for i in range(intervals):
                thread = threading.Thread(target=execute_chunk, args=(i,))
                threads.append(thread)
                thread.start()
            
            return {
                'type': 'TWAP',
                'status': 'EXECUTING',
                'total_quantity': total_quantity,
                'intervals': intervals,
                'duration_minutes': duration_minutes,
                'message': f'TWAP order started: {intervals} chunks over {duration_minutes} minutes'
            }
            
        except Exception as e:
            self.logger.error(f"TWAP order failed: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot')
    parser.add_argument('--api-key', required=True, help='Binance API Key')
    parser.add_argument('--api-secret', required=True, help='Binance API Secret')
    parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    parser.add_argument('--side', choices=['BUY', 'SELL'], required=True, help='Order side')
    parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
    parser.add_argument('--type', choices=['MARKET', 'LIMIT', 'STOP_LIMIT', 'TWAP'], required=True, help='Order type')
    parser.add_argument('--price', type=float, help='Price for limit orders')
    parser.add_argument('--stop-price', type=float, help='Stop price for stop-limit orders')
    parser.add_argument('--duration', type=int, help='Duration in minutes for TWAP orders')
    parser.add_argument('--intervals', type=int, default=10, help='Number of intervals for TWAP orders')
    
    args = parser.parse_args()
    
    try:
        bot = BasicBot(args.api_key, args.api_secret)
        
        # Validate symbol
        if not bot.validate_symbol(args.symbol):
            print(f"Error: Invalid symbol {args.symbol}")
            return
            
        # Show balance
        balance = bot.get_balance()
        print(f"Account Balance: {balance} USDT")
        
        # Place order based on type
        if args.type == 'MARKET':
            order = bot.market_order(args.symbol, args.side, args.quantity)
        elif args.type == 'LIMIT':
            if not args.price:
                print("Error: --price required for limit orders")
                return
            order = bot.limit_order(args.symbol, args.side, args.quantity, args.price)
        elif args.type == 'STOP_LIMIT':
            if not args.stop_price or not args.price:
                print("Error: --stop-price and --price required for stop-limit orders")
                return
            order = bot.stop_limit_order(args.symbol, args.side, args.quantity, args.stop_price, args.price)
        elif args.type == 'TWAP':
            if not args.duration:
                print("Error: --duration required for TWAP orders")
                return
            order = bot.twap_order(args.symbol, args.side, args.quantity, args.duration, args.intervals)
            
        if args.type == 'TWAP':
            print(f"TWAP Status: {order['status']}")
            print(f"Message: {order['message']}")
            print(f"Total Quantity: {order['total_quantity']}")
            print(f"Intervals: {order['intervals']}")
        else:
            print(f"Order Status: {order['status']}")
            print(f"Order ID: {order['orderId']}")
            print(f"Executed Quantity: {order.get('executedQty', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()