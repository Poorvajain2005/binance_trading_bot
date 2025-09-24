#!/usr/bin/env python3
import os
import sys
import logging
from binance.client import Client

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from market_orders import MarketOrder
from limit_orders import LimitOrder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

def main():
    print("Binance Futures Trading Bot")
    print("=" * 40)
    
    # Check for API credentials
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("WARNING: API credentials not found!")
        print("Please set environment variables:")
        print("   BINANCE_API_KEY=your_key")
        print("   BINANCE_API_SECRET=your_secret")
        print("\nFor demo purposes, showing available features:")
        print("\nAvailable Order Types:")
        print("   - Market Orders")
        print("   - Limit Orders") 
        print("   - Stop-Limit Orders")
        print("   - OCO Orders (simulated)")
        print("   - TWAP Orders")
        return
    
    try:
        # Initialize Binance client (testnet)
        client = Client(api_key, api_secret, testnet=True)
        
        # Test connection
        account = client.futures_account()
        print(f"SUCCESS: Connected to Binance Testnet")
        print(f"Account Balance: {account['totalWalletBalance']} USDT")
        
        # Initialize order handlers
        market_order = MarketOrder(client)
        limit_order = LimitOrder(client)
        
        print("\nBot is ready for trading!")
        print("Use the following commands:")
        print("   python src/market_orders.py BTCUSDT BUY 0.01")
        print("   python src/limit_orders.py BTCUSDT BUY 0.01 50000")
        
    except Exception as e:
        logging.error(f"Failed to connect: {e}")
        print(f"ERROR: Connection failed: {e}")

if __name__ == "__main__":
    main()