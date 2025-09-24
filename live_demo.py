#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading_bot_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Live trading simulation
trading_data = {
    'balance': 10000.00,
    'initial_balance': 10000.00,
    'positions': {},
    'orders': [],
    'prices': {},
    'last_update': time.time()
}

def fetch_real_prices():
    """Fetch actual prices from Binance and simulate trading"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
    
    while True:
        try:
            # Get real prices from Binance public API
            response = requests.get('https://api.binance.com/api/v3/ticker/24hr', timeout=10)
            data = response.json()
            
            price_updates = {}
            
            for item in data:
                if item['symbol'] in symbols:
                    symbol = item['symbol']
                    current_price = float(item['lastPrice'])
                    change_24h = float(item['priceChangePercent'])
                    volume = float(item['volume'])
                    
                    # Store previous price for comparison
                    prev_price = trading_data['prices'].get(symbol, {}).get('price', current_price)
                    
                    price_updates[symbol] = {
                        'price': current_price,
                        'change_24h': change_24h,
                        'volume': volume,
                        'trend': 'up' if current_price > prev_price else 'down' if current_price < prev_price else 'neutral',
                        'timestamp': time.time()
                    }
            
            # Update stored prices
            trading_data['prices'].update(price_updates)
            
            # Calculate portfolio value based on positions
            portfolio_value = trading_data['balance']
            for symbol, position in trading_data['positions'].items():
                if symbol in price_updates:
                    current_price = price_updates[symbol]['price']
                    position_value = position['quantity'] * current_price
                    portfolio_value += position_value - position['cost']
            
            # Calculate P&L
            total_pnl = portfolio_value - trading_data['initial_balance']
            pnl_percent = (total_pnl / trading_data['initial_balance']) * 100
            
            # Emit live updates
            socketio.emit('market_update', {
                'prices': price_updates,
                'balance': trading_data['balance'],
                'portfolio_value': portfolio_value,
                'pnl': total_pnl,
                'pnl_percent': pnl_percent,
                'positions': trading_data['positions'],
                'timestamp': time.strftime('%H:%M:%S'),
                'status': 'LIVE'
            })
            
            print(f"Updated {len(price_updates)} symbols - Portfolio: ${portfolio_value:.2f}")
            time.sleep(3)  # Update every 3 seconds
            
        except Exception as e:
            print(f"Error fetching prices: {e}")
            # Emit error status
            socketio.emit('market_update', {
                'prices': trading_data['prices'],
                'balance': trading_data['balance'],
                'portfolio_value': trading_data['balance'],
                'pnl': 0,
                'pnl_percent': 0,
                'positions': trading_data['positions'],
                'timestamp': time.strftime('%H:%M:%S'),
                'status': 'ERROR',
                'error': str(e)
            })
            time.sleep(10)

# Start price fetching
price_thread = threading.Thread(target=fetch_real_prices)
price_thread.daemon = True
price_thread.start()

@app.route('/')
def index():
    return render_template('live_demo.html')

@app.route('/api/order', methods=['POST'])
def execute_order():
    try:
        data = request.json
        symbol = data['symbol']
        side = data['side']
        quantity = float(data['quantity'])
        
        # Get current price
        if symbol not in trading_data['prices']:
            return jsonify({'status': 'error', 'message': 'Symbol price not available'})
        
        current_price = trading_data['prices'][symbol]['price']
        order_value = quantity * current_price
        
        # Check if we have enough balance for buy orders
        if side == 'BUY' and order_value > trading_data['balance']:
            return jsonify({'status': 'error', 'message': 'Insufficient balance'})
        
        # Execute the order
        order_id = f"ORD_{int(time.time() * 1000)}"
        
        if side == 'BUY':
            # Buy order - reduce balance, increase position
            trading_data['balance'] -= order_value
            
            if symbol in trading_data['positions']:
                # Add to existing position
                old_qty = trading_data['positions'][symbol]['quantity']
                old_cost = trading_data['positions'][symbol]['cost']
                new_qty = old_qty + quantity
                new_cost = old_cost + order_value
                
                trading_data['positions'][symbol] = {
                    'quantity': new_qty,
                    'avg_price': new_cost / new_qty,
                    'cost': new_cost
                }
            else:
                # New position
                trading_data['positions'][symbol] = {
                    'quantity': quantity,
                    'avg_price': current_price,
                    'cost': order_value
                }
        
        else:  # SELL
            # Check if we have enough position to sell
            if symbol not in trading_data['positions'] or trading_data['positions'][symbol]['quantity'] < quantity:
                return jsonify({'status': 'error', 'message': 'Insufficient position'})
            
            # Sell order - increase balance, reduce position
            trading_data['balance'] += order_value
            
            position = trading_data['positions'][symbol]
            position['quantity'] -= quantity
            position['cost'] -= (position['cost'] / (position['quantity'] + quantity)) * quantity
            
            if position['quantity'] <= 0:
                del trading_data['positions'][symbol]
        
        # Record the order
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': current_price,
            'value': order_value,
            'timestamp': time.strftime('%H:%M:%S'),
            'status': 'FILLED'
        }
        
        trading_data['orders'].append(order)
        
        # Keep only last 50 orders
        if len(trading_data['orders']) > 50:
            trading_data['orders'] = trading_data['orders'][-50:]
        
        # Emit balance update
        portfolio_value = trading_data['balance']
        for pos_symbol, position in trading_data['positions'].items():
            if pos_symbol in trading_data['prices']:
                pos_price = trading_data['prices'][pos_symbol]['price']
                portfolio_value += position['quantity'] * pos_price
        
        total_pnl = portfolio_value - trading_data['initial_balance']
        
        socketio.emit('order_executed', {
            'order': order,
            'balance': trading_data['balance'],
            'portfolio_value': portfolio_value,
            'pnl': total_pnl,
            'positions': trading_data['positions']
        })
        
        return jsonify({
            'status': 'success',
            'message': f'✅ EXECUTED: {side} {quantity} {symbol} @ ${current_price:,.4f}',
            'order_id': order_id,
            'execution_price': current_price,
            'new_balance': trading_data['balance']
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'❌ Error: {str(e)}'})

@app.route('/api/orders')
def get_orders():
    return jsonify(trading_data['orders'][-20:])  # Last 20 orders

@app.route('/api/positions')
def get_positions():
    return jsonify(trading_data['positions'])

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current data immediately
    portfolio_value = trading_data['balance']
    for symbol, position in trading_data['positions'].items():
        if symbol in trading_data['prices']:
            current_price = trading_data['prices'][symbol]['price']
            portfolio_value += position['quantity'] * current_price
    
    total_pnl = portfolio_value - trading_data['initial_balance']
    pnl_percent = (total_pnl / trading_data['initial_balance']) * 100
    
    emit('market_update', {
        'prices': trading_data['prices'],
        'balance': trading_data['balance'],
        'portfolio_value': portfolio_value,
        'pnl': total_pnl,
        'pnl_percent': pnl_percent,
        'positions': trading_data['positions'],
        'timestamp': time.strftime('%H:%M:%S'),
        'status': 'CONNECTED'
    })

if __name__ == '__main__':
    print("Starting Live Trading Demo...")
    print("Fetching real market data from Binance...")
    print("Starting with $10,000 demo balance")
    print("Open http://localhost:5000")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)