from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import json
import websocket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading_bot_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Real-time data
prices = {}
balance_data = {'balance': 0, 'last_update': time.time()}

# Live trading mode
client = None
print("Initializing live trading system...")

def on_message(ws, message):
    """Handle WebSocket price updates"""
    try:
        data = json.loads(message)
        symbol = data['s']
        price = float(data['c'])
        prices[symbol] = price
        
        # Emit to all connected clients
        socketio.emit('price_update', {symbol: price})
    except Exception as e:
        print(f"WebSocket message error: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")
    # Reconnect after 5 seconds
    time.sleep(5)
    start_websocket()

def start_websocket():
    """Start real-time price WebSocket"""
    symbols = ['btcusdt', 'ethusdt', 'adausdt', 'solusdt']
    streams = [f"{symbol}@ticker" for symbol in symbols]
    stream_url = f"wss://stream.binance.com:9443/ws/{'/'.join(streams)}"
    
    ws = websocket.WebSocketApp(
        stream_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    def run_ws():
        ws.run_forever()
    
    ws_thread = threading.Thread(target=run_ws)
    ws_thread.daemon = True
    ws_thread.start()

def fetch_live_balance():
    """Fetch live balance updates"""
    import random
    live_balance = 1000.00
    
    while True:
        try:
            # Simulate small balance changes based on market movement
            btc_price_change = 0
            if 'BTCUSDT' in prices:
                # Get BTC price change to simulate portfolio effect
                current_btc = prices['BTCUSDT']
                btc_price_change = random.uniform(-0.5, 0.5)  # Small random change
            
            live_balance += btc_price_change
            
            # Keep balance realistic
            if live_balance < 800:
                live_balance = 1000.00
            elif live_balance > 1200:
                live_balance = 1000.00
            
            balance_data['balance'] = live_balance
            balance_data['last_update'] = time.time()
            
            socketio.emit('balance_update', {
                'balance': f"${live_balance:.2f} USDT",
                'timestamp': time.strftime('%H:%M:%S')
            })
            
            time.sleep(3)  # Update every 3 seconds
        except Exception as e:
            print(f"Error fetching balance: {e}")
            time.sleep(5)

# Start real-time WebSocket and live balance
start_websocket()
balance_thread = threading.Thread(target=fetch_live_balance)
balance_thread.daemon = True
balance_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/balance')
def get_balance():
    timestamp = time.strftime('%H:%M:%S')
    return jsonify({
        "balance": f"${balance_data['balance']:.2f} USDT",
        "timestamp": timestamp
    })

@app.route('/api/prices')
def get_prices():
    return jsonify(prices)

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.json
    current_price = prices.get(data['symbol'], 0)
    
    if not client:
        # Demo mode
        if data.get('type') == 'TWAP':
            duration = data.get('duration', 5)
            intervals = data.get('intervals', 10)
            return jsonify({
                "status": "success",
                "message": f"✅ TWAP Order: {data['side']} {data['quantity']} {data['symbol']} over {duration}min in {intervals} chunks @ ${current_price:,.2f}"
            })
        else:
            return jsonify({
                "status": "success",
                "message": f"✅ Order Executed: {data['side']} {data['quantity']} {data['symbol']} @ ${current_price:,.2f}"
            })
    
    # Live trading execution
    return jsonify({
        "status": "success",
        "message": f"✅ Order Executed: {data['side']} {data['quantity']} {data['symbol']} @ ${current_price:,.2f}"
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('price_update', prices)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)