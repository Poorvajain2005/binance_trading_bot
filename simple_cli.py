#!/usr/bin/env python3
from trading_bot import BasicBot
import sys

def get_testnet_keys():
    print("Enter your Binance Testnet API credentials:")
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    return api_key, api_secret

def main():
    print("=== Binance Futures Trading Bot ===")
    print("Using Testnet: https://testnet.binancefuture.com")
    
    # Get API keys
    api_key, api_secret = get_testnet_keys()
    
    try:
        bot = BasicBot(api_key, api_secret)
        balance = bot.get_balance()
        print(f"\n✅ Connected! Balance: {balance} USDT")
        
        while True:
            print("\n--- Trading Menu ---")
            print("1. Market Order")
            print("2. Limit Order") 
            print("3. Stop-Limit Order")
            print("4. TWAP Order (Bonus)")
            print("5. Check Balance")
            print("6. Exit")
            
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                symbol = input("Symbol (e.g., BTCUSDT): ").upper()
                side = input("Side (BUY/SELL): ").upper()
                quantity = float(input("Quantity: "))
                
                order = bot.market_order(symbol, side, quantity)
                print(f"✅ Market order executed: {order['orderId']}")
                
            elif choice == '2':
                symbol = input("Symbol (e.g., BTCUSDT): ").upper()
                side = input("Side (BUY/SELL): ").upper()
                quantity = float(input("Quantity: "))
                price = float(input("Price: "))
                
                order = bot.limit_order(symbol, side, quantity, price)
                print(f"✅ Limit order placed: {order['orderId']}")
                
            elif choice == '3':
                symbol = input("Symbol (e.g., BTCUSDT): ").upper()
                side = input("Side (BUY/SELL): ").upper()
                quantity = float(input("Quantity: "))
                stop_price = float(input("Stop Price: "))
                limit_price = float(input("Limit Price: "))
                
                order = bot.stop_limit_order(symbol, side, quantity, stop_price, limit_price)
                print(f"✅ Stop-limit order placed: {order['orderId']}")
                
            elif choice == '4':
                symbol = input("Symbol (e.g., BTCUSDT): ").upper()
                side = input("Side (BUY/SELL): ").upper()
                quantity = float(input("Total Quantity: "))
                duration = int(input("Duration (minutes): "))
                intervals = int(input("Number of intervals (default 10): ") or "10")
                
                order = bot.twap_order(symbol, side, quantity, duration, intervals)
                print(f"✅ TWAP order started: {order['message']}")
                
            elif choice == '5':
                balance = bot.get_balance()
                print(f"Balance: {balance} USDT")
                
            elif choice == '6':
                print("Goodbye!")
                break
                
            else:
                print("Invalid option")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()