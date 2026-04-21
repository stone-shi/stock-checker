# Stock Price Checker CLI

A simple Python CLI tool to query the latest stock prices using `yfinance` and `rich`.

## Features
- Query multiple stock symbols at once.
- Returns structured JSON data containing price, change, percentage change, day high, and day low.
- **Top Market News:** Get the latest headlines from the financial markets in JSON.
- **LLM Optimized:** Default JSON output makes it easy for AI agents to consume and process data.

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
