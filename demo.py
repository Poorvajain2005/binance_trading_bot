#!/usr/bin/env python3
"""
Demo script showing how to use the BasicBot class
Run this to test the bot functionality
"""
from trading_bot import BasicBot

# Demo with placeholder keys - replace with real testnet keys
API_KEY = "your_testnet_api_key"
API_SECRET = "your_testnet_secret"

def demo():
    print("=== Trading Bot Demo ===")
    print("Replace API_KEY and API_SECRET with real testnet credentials")
    
    if API_KEY == "your_testnet_api_key":
        print("\nPlease update API keys in demo.py")
        print("1. Go to https://testnet.binancefuture.com/")
        print("2. Generate API keys")
        print("3. Replace API_KEY and API_SECRET in this file")
        return
    
    try:
        # Initialize bot
        bot = BasicBot(API_KEY, API_SECRET)
        
        # Check balance
        balance = bot.get_balance()
        print(f"Balance: {balance} USDT")
        
        # Example market order (commented for safety)
        # order = bot.market_order("BTCUSDT", "BUY", 0.001)
        # print(f"Order placed: {order}")
        
        print("✅ Bot is working! Uncomment order lines to place real trades.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo()