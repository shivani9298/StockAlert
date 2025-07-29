#!/usr/bin/env python3

import schedule
import time
import sys
from datetime import datetime
from stock_data import StockDataProvider
from market_analyzer import MarketAnalyzer
from email_notifier import EmailNotifier
from config import Config

class StockAlertSystem:
    def __init__(self):
        self.data_provider = StockDataProvider()
        self.analyzer = MarketAnalyzer()
        self.notifier = EmailNotifier()
        self.last_alerts = {}
    
    def check_markets(self):
        print(f"\n{'='*50}")
        print(f"Market Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        all_analyses = {}
        alerts_sent = 0
        
        for symbol, name in Config.SYMBOLS.items():
            print(f"\nChecking {symbol} ({name})...")
            
            current_data = self.data_provider.get_current_price(symbol)
            if not current_data:
                print(f"Failed to get data for {symbol}")
                continue
            
            try:
                historical_data = self.data_provider.get_historical_data(symbol, days=30)
            except Exception as e:
                print(f"Historical data failed for {symbol}, continuing with current data only: {e}")
                historical_data = None
            
            analysis = self.analyzer.analyze_stock(current_data, historical_data)
            
            if analysis:
                all_analyses[symbol] = analysis
                print(f"Price: ${analysis['current_price']:.2f} ({analysis['change_percent']:+.2f}%)")
                print(f"Signal: {analysis['signal']} ({analysis['confidence']} confidence)")
                
                if self.analyzer.should_send_alert(analysis):
                    alert_key = f"{symbol}_{analysis['signal']}"
                    
                    if (alert_key not in self.last_alerts or 
                        (datetime.now() - self.last_alerts[alert_key]).seconds > 3600):  # 1 hour cooldown
                        
                        if self.notifier.send_alert(analysis):
                            self.last_alerts[alert_key] = datetime.now()
                            alerts_sent += 1
                        else:
                            print(f"Failed to send alert for {symbol}")
        
        print(f"\nMarket check complete. Sent {alerts_sent} alerts.")
        return all_analyses
    
    def send_daily_summary(self):
        print("Sending daily market summary...")
        all_analyses = {}
        
        for symbol in Config.SYMBOLS.keys():
            current_data = self.data_provider.get_current_price(symbol)
            if current_data:
                historical_data = self.data_provider.get_historical_data(symbol, days=30)
                analysis = self.analyzer.analyze_stock(current_data, historical_data)
                if analysis:
                    all_analyses[symbol] = analysis
        
        if all_analyses:
            self.notifier.send_daily_summary(all_analyses)
    
    def run_once(self):
        try:
            return self.check_markets()
        except Exception as e:
            print(f"Error during market check: {e}")
            return {}
    
    def start_monitoring(self):
        print("Starting Stock Alert System...")
        print(f"Monitoring symbols: {list(Config.SYMBOLS.keys())}")
        print(f"Check interval: {Config.CHECK_INTERVAL} minutes")
        print(f"Buy threshold: {Config.BUY_ALERT_THRESHOLD}%")
        print(f"Sell threshold: {Config.SELL_ALERT_THRESHOLD}%")
        
        schedule.every(Config.CHECK_INTERVAL).minutes.do(self.check_markets)
        schedule.every().day.at("09:00").do(self.send_daily_summary)
        
        print("Performing initial market check...")
        self.check_markets()
        
        print(f"\nSystem running. Next check in {Config.CHECK_INTERVAL} minutes.")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nShutting down Stock Alert System...")
            sys.exit(0)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            system = StockAlertSystem()
            analyses = system.run_once()
            print(f"\nTest completed. Found {len(analyses)} valid analyses.")
            return
        elif sys.argv[1] == "--summary":
            system = StockAlertSystem()
            system.send_daily_summary()
            return
        elif sys.argv[1] == "--help":
            print("Stock Alert System")
            print("Usage:")
            print("  python main.py          # Start continuous monitoring")
            print("  python main.py --test   # Run one-time check")
            print("  python main.py --summary # Send daily summary")
            print("  python main.py --help   # Show this help")
            return
    
    system = StockAlertSystem()
    system.start_monitoring()

if __name__ == "__main__":
    main()