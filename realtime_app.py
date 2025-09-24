#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading_bot_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data storage
live_data = {
    'prices': {},
    'balance': 1000.00,
    'orders': [],
    'pnl': 0.00
}

def fetch_live_prices():
    """Fetch real-time prices from Binance API"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
    
    while True:
        try:
            # Get real prices from Binance
            url = 'https://api.binance.com/api/v3/ticker/price'
            response = requests.get(url, timeout=5)
            data = response.json()
            
            # Filter and update prices
            for item in data:
                if item['symbol'] in symbols:
                    old_price = live_data['prices'].get(item['symbol'], 0)
                    new_price = float(item['price'])
                    
                    # Calculate change
                    change = 0
                    if old_price > 0:
                        change = ((new_price - old_price) / old_price) * 100
                    
                    live_data['prices'][item['symbol']] = {
                        'price': new_price,
                        'change': change,
                        'timestamp': time.time()
                    }
            
            # Simulate realistic balance changes based on market movement
            btc_change = live_data['prices'].get('BTCUSDT', {}).get('change', 0)
            eth_change = live_data['prices'].get('ETHUSDT', {}).get('change', 0)
            
            # Simulate portfolio changes
            portfolio_change = (btc_change * 0.5 + eth_change * 0.3) * 0.01
            live_data['balance'] += portfolio_change
            live_data['pnl'] += portfolio_change
            
            # Keep balance realistic
            if live_data['balance'] < 500:
                live_data['balance'] = 1000.00
                live_data['pnl'] = 0.00
            
            # Emit updates to all clients
            pnl_color = 'green' if live_data['pnl'] >= 0 else 'red'
            pnl_sign = '+' if live_data['pnl'] >= 0 else ''
            
            socketio.emit('live_update', {
                'prices': live_data['prices'],
                'balance': live_data['balance'],
                'pnl': f"{pnl_sign}{live_data['pnl']:.2f}",
                'pnl_color': pnl_color,
                'timestamp': time.strftime('%H:%M:%S')
            })
            
            print(f"Updated prices: {len(live_data['prices'])} symbols")
            time.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            print(f"Error fetching prices: {e}")
            time.sleep(5)

# Start background price fetching
price_thread = threading.Thread(target=fetch_live_prices)
price_thread.daemon = True
price_thread.start()

@app.route('/')
def index():
    return render_template('realtime.html')

@app.route('/api/prices')
def get_prices():
    return jsonify(live_data['prices'])

@app.route('/api/balance')
def get_balance():
    pnl_color = 'green' if live_data['pnl'] >= 0 else 'red'
    pnl_sign = '+' if live_data['pnl'] >= 0 else ''
    
    return jsonify({
        'balance': f"${live_data['balance']:.2f} USDT",
        'pnl': f"{pnl_sign}{live_data['pnl']:.2f}",
        'pnl_color': pnl_color,
        'timestamp': time.strftime('%H:%M:%S')
    })

@app.route('/api/order', methods=['POST'])
def place_order():
    try:
        data = request.json
        symbol = data['symbol']
        side = data['side']
        quantity = float(data['quantity'])
        order_type = data.get('type', 'MARKET')
        
        # Get current price
        current_price = live_data['prices'].get(symbol, {}).get('price', 0)
        
        # Simulate order execution
        order_id = f"ORDER_{int(time.time())}"
        
        # Calculate order value
        order_value = quantity * current_price
        
        # Update balance (simulate execution)
        if side == 'BUY':
            live_data['balance'] -= order_value
        else:
            live_data['balance'] += order_value
        
        # Store order
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': current_price,
            'type': order_type,
            'status': 'FILLED',
            'timestamp': time.strftime('%H:%M:%S')
        }
        
        live_data['orders'].append(order)
        
        # Emit balance update
        pnl_color = 'green' if live_data['pnl'] >= 0 else 'red'
        pnl_sign = '+' if live_data['pnl'] >= 0 else ''
        
        socketio.emit('balance_update', {
            'balance': live_data['balance'],
            'pnl': f"{pnl_sign}{live_data['pnl']:.2f}",
            'pnl_color': pnl_color,
            'timestamp': time.strftime('%H:%M:%S')
        })
        
        return jsonify({
            'status': 'success',
            'message': f'✅ EXECUTED: {side} {quantity} {symbol} @ ${current_price:,.2f}',
            'order_id': order_id,
            'execution_price': current_price
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Error: {str(e)}'
        })

@app.route('/api/orders')
def get_orders():
    return jsonify(live_data['orders'][-10:])  # Last 10 orders

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    pnl_color = 'green' if live_data['pnl'] >= 0 else 'red'
    pnl_sign = '+' if live_data['pnl'] >= 0 else ''
    
    emit('live_update', {
        'prices': live_data['prices'],
        'balance': live_data['balance'],
        'pnl': f"{pnl_sign}{live_data['pnl']:.2f}",
        'pnl_color': pnl_color,
        'timestamp': time.strftime('%H:%M:%S')
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("Starting Real-Time Trading Bot...")
    print("Fetching live prices from Binance...")
    print("Open http://localhost:5000 to view")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)