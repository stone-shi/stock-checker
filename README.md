# Stock Price Checker CLI

A simple Python CLI tool to query the latest stock prices using `yfinance` and `rich`.

## Features
- Query multiple stock symbols at once.
- Displays price, change, percentage change, day high, and day low.
- Color-coded output for gains and losses.
- **Top Market News:** Get the latest headlines from the financial markets.
- **JSON Output:** Structured data for programmatic use (e.g., by LLMs).

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

Run the script with one or more stock symbols:

```bash
python stock_checker.py AAPL MSFT TSLA
```

Get top market news:

```bash
python stock_checker.py --news
```

Output JSON for LLM consumption:

```bash
python stock_checker.py AAPL MSFT --json
```

## Recommended Libraries for Stock Data

- **yfinance** (Used here): Best for hobbyists. Free, no API key required, easy to use.
- **Polygon.io**: Best for professional/real-time data. High accuracy, low latency, requires API key.
- **Alpaca-py**: Best for algorithmic trading.
- **Alpha Vantage**: Best for technical indicators.
