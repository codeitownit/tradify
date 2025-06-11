# api_server.py
from flask import Flask, jsonify, request
from trading_bot import ForexTradingBot
import threading
import MetaTrader5 as mt5

app = Flask(__name__)
bot = ForexTradingBot()

# Run bot in separate thread
bot_thread = threading.Thread(target=bot.run)
bot_thread.daemon = True
bot_thread.start()
@app.route('/api/trades', methods=['GET'])
def get_active_trades():
    positions = mt5.positions_get()
    print(positions)

    if positions is None:
        print("positions_get() failed, error code:", mt5.last_error())
        return jsonify({
            'statusCode': 500,
            'error': 'Failed to retrieve positions',
            'code': mt5.last_error()
        }), 500

    trades = []
    for pos in positions:
        trades.append({
            'symbol': pos.symbol,
            'direction': 'long' if pos.type == mt5.ORDER_TYPE_BUY else 'short',
            'entryPrice': pos.price_open,
            'currentPrice': mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
            'lotSize': pos.volume,
            'profitLoss': pos.profit
        })

    return jsonify({
        'message': 'Trades fetched successfully',
        'statusCode': 200,
        'data': trades
    }), 200


@app.route('/api/account', methods=['GET'])
def account_info():
    info = mt5.account_info()
    if info is None:
        return jsonify({'error': 'Not connected to MT5', 'code': mt5.last_error()})
    return jsonify(info._asdict())

@app.route('/api/stats', methods=['GET'])
def get_trade_stats():
    # This would query historical trades and calculate stats
    stats = {
        'Win Rate': '65%',
        'Avg Win': '$120',
        'Avg Loss': '$80',
        'Profit Factor': 1.8
    }
    return jsonify(stats)

@app.route('/api/config', methods=['POST'])
def update_config():
    data = request.json
    if 'lot_size' in data:
        bot.lot_size = float(data['lot_size'])
    if 'ml_threshold' in data:
        bot.ml_threshold = float(data['ml_threshold'])
    
    return jsonify({'status': 'success'})

# @app.route('/api/chart/<symbol>', methods=['GET'])
# def get_chart_data(symbol):
    # df = bot.get_price_data(symbol)
    # chart_data = []
    
    # for _, row in df.iterrows():
    #     chart_data.append({
    #         'time': row['time'].isoformat(),
    #         'open': row['open'],
    #         'high': row['high'],
    #         'low': row['low'],
    #         'close': row['close']
    #     })
    
    # return jsonify(chart_data)

@app.route('/api/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    info = mt5.symbol_info("GBPUSD")
    if info is None:
        print("GBPUSD is not a valid symbol on this account.")
    else:
        print(info)

    df = bot.get_price_data(symbol)

    if df.empty:
        return jsonify({
            'error': f"No chart data available for symbol '{symbol}'",
            'statusCode': 404
        }), 404

    chart_data = []
    for _, row in df.iterrows():
        chart_data.append({
            'time': row['time'].isoformat(),
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close']
        })

    return jsonify(chart_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)