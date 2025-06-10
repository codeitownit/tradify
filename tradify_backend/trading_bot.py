# trading_bot.py
import os
import json
import time
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import MetaTrader5 as mt5
import ta
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class ForexTradingBot:
    def __init__(self):
        # Initialize configuration
        self.symbols = ['EURUSD', 'GBPUSD', 'DXY']
        self.trading_hours = self.get_current_session_hours()
        self.timeframe = mt5.TIMEFRAME_M15
        self.lot_size = 0.1  # Default, can be changed via frontend
        self.model = None
        self.ml_threshold = 0.7  # Confidence threshold for ML predictions
        
        # Initialize MT5 connection
        if not mt5.initialize():
            print("MT5 initialization failed")
            mt5.shutdown()
            raise ConnectionError("Failed to connect to MT5")
        else:
            print("MT5 successfully connected to account")
            account_info = mt5.account_info()
            print(account_info)
        
        # Load ML model or train if not exists
        self.load_or_train_model()
        
        # Initialize news cache
        self.news_cache = {'last_updated': None, 'events': []}
        
    def get_current_session_hours(self):
        """Get trading hours based on current month"""
        now = datetime.now()
        month = now.month
        
        if month in [1, 2, 11, 12] or (month == 3 and now.day <= 9):
            return {
                'overlap_start': self.create_utc3_time(16, 0),
                'overlap_end': self.create_utc3_time(20, 0),
                'newyork_start': self.create_utc3_time(20, 0),
                'newyork_end': self.create_utc3_time(1, 0),
                'look_start': self.create_utc3_time(15, 15)
            }
        else:
            return {
                'overlap_start': self.create_utc3_time(15, 0),
                'overlap_end': self.create_utc3_time(19, 0),
                'newyork_start': self.create_utc3_time(19, 0),
                'newyork_end': self.create_utc3_time(0, 0),
                'look_start': self.create_utc3_time(14, 15)
            }
    
    def create_utc3_time(self, hour, minute):
        """Create datetime object with UTC+3 timezone"""
        now = datetime.utcnow() + timedelta(hours=3)
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def load_or_train_model(self):
        """Load trained XGBoost model or train new one"""
        model_path = 'xgboost_model.model'
        
        if os.path.exists(model_path):
            self.model = xgb.Booster()
            self.model.load_model(model_path)
            print("Loaded trained XGBoost model")
        else:
            print("Training new XGBoost model...")
            self.train_model()
    
    def train_model(self):
        """Train XGBoost model from historical data"""
        # This would be replaced with actual training data from the text files
        # For now we'll create dummy data
        X = np.random.rand(1000, 10)  # 10 features
        y = np.random.randint(0, 2, 1000)  # Binary classification
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        
        params = {
            'objective': 'binary:logistic',
            'max_depth': 5,
            'eta': 0.1,
            'eval_metric': 'logloss'
        }
        
        self.model = xgb.train(params, dtrain, num_boost_round=100,
                             evals=[(dtest, 'test')])
        
        # Save model
        self.model.save_model('xgboost_model.model')
        print("Model trained and saved")
    
    def fetch_forex_factory_news(self):
        """Fetch high-impact news events from Forex Factory"""
        url = "https://www.forexfactory.com/calendar"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_events = []
        for event in soup.select('.calendar__row.calendar__row--high'):
            time = event.select_one('.calendar__time').text.strip()
            currency = event.select_one('.calendar__currency').text.strip()
            title = event.select_one('.calendar__event-title').text.strip()
            
            if currency == 'USD':
                news_events.append({
                    'time': time,
                    'title': title,
                    'currency': currency
                })
        
        self.news_cache = {
            'last_updated': datetime.now(),
            'events': news_events
        }
        return news_events
    
    def is_news_time(self):
        """Check if current time is within 15 minutes of high-impact news"""
        if not self.news_cache['events'] or \
           (datetime.now() - self.news_cache['last_updated']) > timedelta(hours=1):
            self.fetch_forex_factory_news()
        
        for event in self.news_cache['events']:
            # Parse event time and compare with current time
            # This is simplified - would need proper time parsing
            event_time = datetime.strptime(event['time'], "%H:%M").time()
            current_time = datetime.now().time()
            
            if abs((datetime.combine(datetime.today(), event_time) - 
                   datetime.combine(datetime.today(), current_time)).total_seconds()) <= 900:
                return True
        return False
    
    # def get_price_data(self, symbol, count=100):
    #     """Get historical price data for a symbol"""
    #     rates = mt5.copy_rates_from_pos(symbol, self.timeframe, 0, count)
    #     df = pd.DataFrame(rates)
    #     df['time'] = pd.to_datetime(df['time'], unit='s')
    #     return df
    def get_price_data(self, symbol):
        # Ensure symbol is available
        if not mt5.symbol_select(symbol, True):
            print(f"Symbol '{symbol}' not found or could not be selected")
            return pd.DataFrame()

        # Try fetching 100 M1 bars
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)

        if rates is None or len(rates) == 0:
            print(f"No rates data returned for symbol '{symbol}'")
            return pd.DataFrame()

        df = pd.DataFrame(rates)

        if 'time' not in df.columns:
            print(f"'time' column missing in data for symbol '{symbol}'")
            return pd.DataFrame()

        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def identify_support_resistance(self, df):
        """Identify support and resistance levels"""
        # This is a simplified version - would need more sophisticated logic
        levels = []
        
        # Identify local minima (support) and maxima (resistance)
        for i in range(2, len(df)-2):
            if df['low'][i] < df['low'][i-1] and df['low'][i] < df['low'][i+1]:
                # Support level
                level = {
                    'price': df['low'][i],
                    'type': 'support',
                    'time': df['time'][i]
                }
                # Round to appropriate decimal places
                if 'DXY' in df['symbol'].iloc[0]:
                    level['price'] = round(level['price'], 3)
                    if level['price'] * 1000 % 10 == 0:  # Third decimal is 0
                        levels.append(level)
                else:  # EURUSD
                    level['price'] = round(level['price'], 5)
                    if level['price'] * 100000 % 10 == 0:  # Fifth decimal is 0
                        levels.append(level)
            
            if df['high'][i] > df['high'][i-1] and df['high'][i] > df['high'][i+1]:
                # Resistance level
                level = {
                    'price': df['high'][i],
                    'type': 'resistance',
                    'time': df['time'][i]
                }
                # Round to appropriate decimal places
                if 'DXY' in df['symbol'].iloc[0]:
                    level['price'] = round(level['price'], 3)
                    if level['price'] * 1000 % 10 == 0:  # Third decimal is 0
                        levels.append(level)
                else:  # EURUSD
                    level['price'] = round(level['price'], 5)
                    if level['price'] * 100000 % 10 == 0:  # Fifth decimal is 0
                        levels.append(level)
        
        return levels
    
    def check_engulfing_pattern(self, df, index):
        """Check for bullish/bearish engulfing pattern"""
        if index < 1:
            return False
        
        prev_candle = df.iloc[index-1]
        current_candle = df.iloc[index]
        
        # Bullish engulfing
        if (current_candle['close'] > current_candle['open'] and
            prev_candle['close'] < prev_candle['open'] and
            current_candle['open'] < prev_candle['close'] and
            current_candle['close'] > prev_candle['open']):
            return 'bullish'
        
        # Bearish engulfing
        if (current_candle['close'] < current_candle['open'] and
            prev_candle['close'] > prev_candle['open'] and
            current_candle['open'] > prev_candle['close'] and
            current_candle['close'] < prev_candle['open']):
            return 'bearish'
        
        return False
    
    def check_consecutive_candles(self, df, index, direction):
        """Check for 2 consecutive candles in same direction"""
        if index < 1:
            return False
        
        if direction == 'bullish':
            return (df.iloc[index]['close'] > df.iloc[index]['open'] and
                    df.iloc[index-1]['close'] > df.iloc[index-1]['open'])
        else:
            return (df.iloc[index]['close'] < df.iloc[index]['open'] and
                    df.iloc[index-1]['close'] < df.iloc[index-1]['open'])
    
    def generate_features(self, df, levels):
        """Generate features for ML model"""
        features = []
        
        # Technical indicators
        df['rsi'] = ta.RSI(df['close'], timeperiod=14)
        df['macd'], df['macd_signal'], _ = ta.MACD(df['close'])
        df['sma_50'] = ta.SMA(df['close'], timeperiod=50)
        df['sma_200'] = ta.SMA(df['close'], timeperiod=200)
        
        # Support/resistance features
        for level in levels:
            # Distance to nearest support/resistance
            # Price action at levels
            # Add more relevant features
            pass
        
        # Convert to numpy array
        return np.array(features)
    
    def get_trading_signal(self):
        """Generate trading signal based on strategy rules and ML model"""
        now = datetime.now()
        
        # Check if we're in trading hours
        if not (self.trading_hours['look_start'] <= now <= self.trading_hours['newyork_end']):
            return None
        
        # Check for news events
        if self.is_news_time():
            return {'action': 'close_all', 'reason': 'news_event'}
        
        # Get price data for all symbols
        signals = []
        for symbol in self.symbols:
            df = self.get_price_data(symbol)
            df['symbol'] = symbol
            
            # Identify support/resistance levels
            levels = self.identify_support_resistance(df)
            
            # Check for trading opportunities at each level
            for level in levels:
                # Check price is near level (within 5 pips)
                current_price = df.iloc[-1]['close']
                pip_size = 0.0001 if 'DXY' not in symbol else 0.001
                
                if abs(current_price - level['price']) <= 5 * pip_size:
                    # Check for engulfing pattern or consecutive candles
                    engulfing = self.check_engulfing_pattern(df, -1)
                    consecutive_bullish = self.check_consecutive_candles(df, -1, 'bullish')
                    consecutive_bearish = self.check_consecutive_candles(df, -1, 'bearish')
                    
                    if engulfing or consecutive_bullish or consecutive_bearish:
                        # Generate features for ML model
                        features = self.generate_features(df, levels)
                        
                        # Get ML prediction
                        dmatrix = xgb.DMatrix(features.reshape(1, -1))
                        prediction = self.model.predict(dmatrix)[0]
                        
                        if prediction >= self.ml_threshold:
                            if level['type'] == 'support':
                                signals.append({
                                    'symbol': symbol,
                                    'direction': 'bullish' if symbol == 'DXY' else 'bearish',
                                    'level': level,
                                    'confidence': prediction
                                })
                            else:  # resistance
                                signals.append({
                                    'symbol': symbol,
                                    'direction': 'bearish' if symbol == 'DXY' else 'bullish',
                                    'level': level,
                                    'confidence': prediction
                                })
        
        # Process signals according to strategy rules
        if signals:
            # For now, just take the first signal
            signal = signals[0]
            
            # Determine trade direction based on DXY or EURUSD signal
            if signal['symbol'] == 'DXY':
                return {
                    'action': 'open',
                    'symbols': ['EURUSD', 'GBPUSD'],
                    'direction': 'sell' if signal['direction'] == 'bullish' else 'buy',
                    'reason': 'DXY_signal'
                }
            else:  # EURUSD
                return {
                    'action': 'open',
                    'symbols': ['EURUSD', 'GBPUSD'],
                    'direction': signal['direction'],
                    'reason': 'EURUSD_signal'
                }
        
        return None
    
    def execute_trade(self, signal):
        """Execute trade based on signal"""
        if signal['action'] == 'open':
            for symbol in signal['symbols']:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": self.lot_size,
                    "type": mt5.ORDER_TYPE_BUY if signal['direction'] == 'buy' else mt5.ORDER_TYPE_SELL,
                    "price": mt5.symbol_info_tick(symbol).ask if signal['direction'] == 'buy' else mt5.symbol_info_tick(symbol).bid,
                    "deviation": 10,
                    "magic": 123456,
                    "comment": signal['reason'],
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Failed to open {symbol} trade: {result.comment}")
                else:
                    print(f"Opened {symbol} {signal['direction']} trade at {result.price}")
        
        elif signal['action'] == 'close_all':
            positions = mt5.positions_get()
            for pos in positions:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": pos.ticket,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": mt5.ORDER_TYPE_BUY if pos.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL,
                    "price": mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
                    "deviation": 10,
                    "magic": 123456,
                    "comment": "Closing before news",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Failed to close {pos.symbol} trade: {result.comment}")
                else:
                    print(f"Closed {pos.symbol} trade at {result.price}")
    
    def run(self):
        """Main trading loop"""
        print("Starting trading bot...")
        
        try:
            while True:
                signal = self.get_trading_signal()
                
                if signal:
                    self.execute_trade(signal)
                
                # Sleep for 15 minutes (aligned with candle close)
                time.sleep(60 * 15 - (time.time() % (60 * 15)))
                
        except KeyboardInterrupt:
            print("Stopping trading bot...")
        finally:
            mt5.shutdown()


if __name__ == "__main__":
    bot = ForexTradingBot()
    bot.run()