import statistics
from datetime import datetime, timedelta
from config import Config

class MarketAnalyzer:
    def __init__(self):
        self.buy_threshold = Config.BUY_ALERT_THRESHOLD
        self.sell_threshold = Config.SELL_ALERT_THRESHOLD
    
    def analyze_stock(self, current_data, historical_data=None):
        if not current_data:
            return None
        
        analysis = {
            'symbol': current_data['symbol'],
            'current_price': current_data['current_price'],
            'change_percent': current_data['change_percent'],
            'signal': 'HOLD',
            'confidence': 'LOW',
            'reasons': []
        }
        
        change_percent = current_data['change_percent']
        
        # Primary analysis based on daily change
        if change_percent <= self.buy_threshold:
            analysis['signal'] = 'BUY'
            analysis['reasons'].append(f"Down {abs(change_percent):.2f}% - Good buying opportunity")
            
            if change_percent <= self.buy_threshold * 1.5:
                analysis['confidence'] = 'HIGH'
                analysis['reasons'].append("Significant drop - Strong buy signal")
            else:
                analysis['confidence'] = 'MEDIUM'
        
        elif change_percent >= self.sell_threshold:
            analysis['signal'] = 'SELL'
            analysis['reasons'].append(f"Up {change_percent:.2f}% - Consider taking profits")
            
            if change_percent >= self.sell_threshold * 1.5:
                analysis['confidence'] = 'HIGH'
                analysis['reasons'].append("Major gain - Strong sell signal")
            else:
                analysis['confidence'] = 'MEDIUM'
        
        else:
            # Even for HOLD, provide some insight
            if abs(change_percent) < 0.5:
                analysis['reasons'].append("Market stable - no significant movement")
            elif change_percent > 0:
                analysis['reasons'].append(f"Up {change_percent:.2f}% - moderate gain")
            else:
                analysis['reasons'].append(f"Down {abs(change_percent):.2f}% - moderate decline")
        
        # Add technical analysis if historical data is available
        if historical_data and len(historical_data.get('closes', [])) > 0:
            try:
                technical_info = self._technical_analysis(historical_data)
                analysis.update(technical_info)
            except Exception as e:
                print(f"Technical analysis failed: {e}")
        
        return analysis
    
    def _technical_analysis(self, historical_data):
        if not historical_data or len(historical_data['closes']) < 20:
            return {}
        
        closes = historical_data['closes']
        current_price = closes[-1]
        
        sma_20 = statistics.mean(closes[-20:])
        sma_5 = statistics.mean(closes[-5:])
        
        price_vs_sma20 = ((current_price - sma_20) / sma_20) * 100
        
        technical_signals = []
        
        if current_price < sma_20 * 0.95:
            technical_signals.append("Price significantly below 20-day average - Oversold")
        elif current_price > sma_20 * 1.05:
            technical_signals.append("Price significantly above 20-day average - Overbought")
        
        if sma_5 > sma_20:
            technical_signals.append("Short-term trend is bullish")
        elif sma_5 < sma_20:
            technical_signals.append("Short-term trend is bearish")
        
        volatility = statistics.stdev(closes[-10:]) if len(closes) >= 10 else 0
        avg_price = statistics.mean(closes[-10:])
        volatility_percent = (volatility / avg_price) * 100 if avg_price > 0 else 0
        
        if volatility_percent > 3:
            technical_signals.append(f"High volatility ({volatility_percent:.1f}%) - Increased risk")
        
        return {
            'sma_20': sma_20,
            'sma_5': sma_5,
            'price_vs_sma20': price_vs_sma20,
            'volatility_percent': volatility_percent,
            'technical_signals': technical_signals
        }
    
    def should_send_alert(self, analysis):
        if not analysis:
            return False
        
        return (analysis['signal'] in ['BUY', 'SELL'] and 
                analysis['confidence'] in ['MEDIUM', 'HIGH'])