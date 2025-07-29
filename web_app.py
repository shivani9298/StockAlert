#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import os
import threading
import time
from datetime import datetime
from stock_data import StockDataProvider
from market_analyzer import MarketAnalyzer
from email_notifier import EmailNotifier
from config import Config
from main import StockAlertSystem

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
CORS(app)

# Global variables to track monitoring state
monitoring_thread = None
monitoring_active = False
alert_system = None
last_check_time = None
last_analyses = {}

@app.route('/')
def index():
    return render_template('index.html', 
                         monitoring_active=monitoring_active,
                         last_check_time=last_check_time,
                         analyses=last_analyses)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Update .env file with new settings
        env_content = []
        
        # Read current .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
        # Update values
        settings_map = {
            'EMAIL_ADDRESS': request.form.get('email_address', ''),
            'EMAIL_PASSWORD': request.form.get('email_password', ''),
            'RECIPIENT_EMAIL': request.form.get('recipient_email', ''),
            'BUY_ALERT_THRESHOLD': request.form.get('buy_threshold', '-2.0'),
            'SELL_ALERT_THRESHOLD': request.form.get('sell_threshold', '3.0'),
            'CHECK_INTERVAL': request.form.get('check_interval', '60'),
            'SMTP_SERVER': request.form.get('smtp_server', 'smtp.gmail.com'),
            'SMTP_PORT': request.form.get('smtp_port', '587')
        }
        
        # Create new env content
        new_env_content = []
        new_env_content.append("# Email Configuration\n")
        new_env_content.append(f"SMTP_SERVER={settings_map['SMTP_SERVER']}\n")
        new_env_content.append(f"SMTP_PORT={settings_map['SMTP_PORT']}\n")
        new_env_content.append(f"EMAIL_ADDRESS={settings_map['EMAIL_ADDRESS']}\n")
        new_env_content.append(f"EMAIL_PASSWORD={settings_map['EMAIL_PASSWORD']}\n")
        new_env_content.append(f"RECIPIENT_EMAIL={settings_map['RECIPIENT_EMAIL']}\n")
        new_env_content.append("\n# Alert Thresholds (percentages)\n")
        new_env_content.append(f"BUY_ALERT_THRESHOLD={settings_map['BUY_ALERT_THRESHOLD']}\n")
        new_env_content.append(f"SELL_ALERT_THRESHOLD={settings_map['SELL_ALERT_THRESHOLD']}\n")
        new_env_content.append("\n# Check Interval (minutes)\n")
        new_env_content.append(f"CHECK_INTERVAL={settings_map['CHECK_INTERVAL']}\n")
        
        # Write to .env file
        with open(env_path, 'w') as f:
            f.writelines(new_env_content)
        
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings'))
    
    # GET request - show current settings
    current_settings = {
        'email_address': os.getenv('EMAIL_ADDRESS', ''),
        'email_password': os.getenv('EMAIL_PASSWORD', ''),
        'recipient_email': os.getenv('RECIPIENT_EMAIL', ''),
        'buy_threshold': os.getenv('BUY_ALERT_THRESHOLD', '-2.0'),
        'sell_threshold': os.getenv('SELL_ALERT_THRESHOLD', '3.0'),
        'check_interval': os.getenv('CHECK_INTERVAL', '60'),
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': os.getenv('SMTP_PORT', '587')
    }
    
    return render_template('settings.html', settings=current_settings)

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    global monitoring_thread, monitoring_active, alert_system
    
    if monitoring_active:
        return jsonify({'status': 'error', 'message': 'Monitoring is already active'})
    
    try:
        # Reload config after settings change
        os.system('python -c "from dotenv import load_dotenv; load_dotenv(override=True)"')
        
        alert_system = StockAlertSystem()
        monitoring_active = True
        
        def monitor_loop():
            global last_check_time, last_analyses, monitoring_active
            while monitoring_active:
                try:
                    last_analyses = alert_system.run_once()
                    last_check_time = datetime.now()
                    time.sleep(int(os.getenv('CHECK_INTERVAL', 60)) * 60)
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(60)
        
        monitoring_thread = threading.Thread(target=monitor_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    except Exception as e:
        monitoring_active = False
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    global monitoring_active
    
    monitoring_active = False
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})

@app.route('/api/test_alert', methods=['POST'])
def test_alert():
    try:
        alert_system = StockAlertSystem()
        analyses = alert_system.run_once()
        
        return jsonify({
            'status': 'success', 
            'message': f'Test completed. Found {len(analyses)} stocks.',
            'data': analyses
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/send_summary', methods=['POST'])
def send_summary():
    try:
        alert_system = StockAlertSystem()
        alert_system.send_daily_summary()
        return jsonify({'status': 'success', 'message': 'Daily summary sent'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/status')
def get_status():
    return jsonify({
        'monitoring_active': monitoring_active,
        'last_check_time': last_check_time.isoformat() if last_check_time else None,
        'analyses_count': len(last_analyses),
        'symbols': list(Config.SYMBOLS.keys())
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)