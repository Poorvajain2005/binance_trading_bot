#!/usr/bin/env python3
import websocket
import json
import threading
import time
from binance import Client

class RealTimeBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.prices = {}
        self.ws = None
        
    def on_message(self, ws, message):
        data = json.loads(message)
        symbol = data['s']
        price = float(data['c'])
        self.prices[symbol] = price
        print(f"{symbol}: ${price:,.2f}")
        
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        
    def start_price_stream(self, symbols):
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        stream_url = f"wss://stream.binance.com:9443/ws/{'/'.join(streams)}"
        
        self.ws = websocket.WebSocketApp(
            stream_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Start WebSocket in separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
    def get_current_price(self, symbol):
        return self.prices.get(symbol, 0)
        
    def monitor_prices(self, symbols):
        print("Starting real-time price monitoring...")
        self.start_price_stream(symbols)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping price monitor...")
            if self.ws:
                self.ws.close()

def main():
    # Demo mode - replace with real keys
    API_KEY = "your_api_key"
    API_SECRET = "your_secret"
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
    
    bot = RealTimeBot(API_KEY, API_SECRET)
    bot.monitor_prices(symbols)

if __name__ == "__main__":
    main()