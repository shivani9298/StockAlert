import requests
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries
from config import Config

class StockDataProvider:
    def __init__(self):
        self.use_alpha_vantage = Config.ALPHA_VANTAGE_API_KEY is not None and Config.ALPHA_VANTAGE_API_KEY.strip()
        
        if self.use_alpha_vantage:
            self.av_client = TimeSeries(key=Config.ALPHA_VANTAGE_API_KEY, output_format='pandas')
        else:
            print("Warning: No Alpha Vantage API key configured. Get a free key at https://www.alphavantage.co/")
    
    def get_current_price(self, symbol):
        if not self.use_alpha_vantage:
            print(f"Cannot get data for {symbol}: No Alpha Vantage API key configured")
            return None
            
        try:
            import time
            time.sleep(0.5)  # Alpha Vantage rate limit protection
            
            data, meta_data = self.av_client.get_daily(symbol=symbol, outputsize='compact')
            if not data.empty:
                current_price = data['4. close'].iloc[0]
                previous_close = data['4. close'].iloc[1] if len(data) > 1 else current_price
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                return {
                    'symbol': symbol,
                    'current_price': float(current_price),
                    'previous_close': float(previous_close),
                    'change': float(change),
                    'change_percent': float(change_percent),
                    'timestamp': datetime.now(),
                    'source': 'Alpha Vantage'
                }
        except Exception as e:
            print(f"Alpha Vantage failed for {symbol}: {e}")
        
        print(f"Failed to get data for {symbol}")
        return None
    
    def get_historical_data(self, symbol, days=30):
        if not self.use_alpha_vantage:
            print(f"Cannot get historical data for {symbol}: No Alpha Vantage API key configured")
            return None
            
        try:
            import time
            time.sleep(0.5)  # Alpha Vantage rate limit protection
            
            data, meta_data = self.av_client.get_daily(symbol=symbol, outputsize='full')
            if not data.empty:
                # Get the last 'days' number of entries
                recent_data = data.head(days)
                
                return {
                    'symbol': symbol,
                    'timestamps': [int(ts.timestamp()) for ts in recent_data.index],
                    'closes': recent_data['4. close'].tolist(),
                    'highs': recent_data['2. high'].tolist(),
                    'lows': recent_data['3. low'].tolist(),
                    'opens': recent_data['1. open'].tolist(),
                    'volumes': recent_data['5. volume'].tolist()
                }
        except Exception as e:
            print(f"Alpha Vantage historical data failed for {symbol}: {e}")
        
        return None
    
    def get_multiple_quotes(self, symbols):
        results = {}
        for symbol in symbols:
            data = self.get_current_price(symbol)
            if data:
                results[symbol] = data
        return results