# Stock Price Checker - OpenClaw Skill

A Python-based OpenClaw skill to query the latest stock prices and market news using `yfinance`.

## Features
- Optimized for **OpenClaw** agents.
- Returns structured JSON data for easy agent consumption.
- Supports multiple stock symbols and market news.
- Seamlessly integrates with OpenClaw's `exec` and `web_fetch` capabilities.

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with one or more stock symbols to get JSON data:

```bash
python stock_checker.py AAPL MSFT TSLA
```

Get top market news in JSON:

```bash
python stock_checker.py --news
```

## Recommended Libraries for Stock Data

- **yfinance** (Used here): Best for hobbyists. Free, no API key required, easy to use.
- **Polygon.io**: Best for professional/real-time data. High accuracy, low latency, requires API key.
- **Alpaca-py**: Best for algorithmic trading.
- **Alpha Vantage**: Best for technical indicators.
