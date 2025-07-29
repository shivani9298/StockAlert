# Stock Market Alert System

A Python application that monitors index funds (S&P 500, Vanguard Growth, etc.) and sends email alerts when there are good buying or selling opportunities.

## Features

- **Data Source**: Uses Alpha Vantage API for reliable stock data
- **Smart Analysis**: Technical indicators with buy/sell signals
- **Email Alerts**: HTML formatted alerts with market analysis
- **Index Fund Focus**: Pre-configured for popular index funds:
  - SPY (SPDR S&P 500 ETF)
  - VOO (Vanguard S&P 500 ETF)
  - VTI (Vanguard Total Stock Market ETF)
  - VUG (Vanguard Growth ETF)
  - VOOG (Vanguard S&P 500 Growth ETF)
  - VGT (Vanguard Information Technology ETF)

## Tech Stack 
Python Flask 
Pandas 
SMTP 
HTML/CSS
Bootstrap

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Configuration** (required):
   - Get a free Alpha Vantage API key at https://www.alphavantage.co/
   - Add your API key to the .env file

3. **Email Configuration** (required):
   - Use Gmail with App Password (recommended)
   - Set SMTP settings for your email provider
   - Configure recipient email address

## Usage

### Run continuous monitoring:
```bash
python3 main.py
```

### Test the system (one-time check):
```bash
python3 main.py --test
```

### Send daily summary:
```bash
python3 main.py --summary
```

## Run the web-app 
```bash
python3 web_app.py
```

## Configuration

Edit `.env` file:

- **ALPHA_VANTAGE_API_KEY**: Your Alpha Vantage API key (required)
- **BUY_ALERT_THRESHOLD**: Trigger buy alerts when stock drops (default: -2.0%)
- **SELL_ALERT_THRESHOLD**: Trigger sell alerts when stock rises (default: +3.0%)
- **CHECK_INTERVAL**: How often to check markets in minutes (default: 60)

## Alert Logic

### Buy Signals:
- Stock drops below threshold (e.g., -2%)
- Price significantly below 20-day average
- Bearish trend reversal indicators

### Sell Signals:
- Stock rises above threshold (e.g., +3%)
- Price significantly above 20-day average
- Overbought conditions

## Email Setup for Gmail

1. Enable 2-Factor Authentication
2. Generate App Password: Google Account > Security > App passwords
3. Use App Password in EMAIL_PASSWORD field


I made this tool to help me decide when to buy index funds, use with your own judgement.
