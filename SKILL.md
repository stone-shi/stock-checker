---
name: stock_checker
description: Query latest stock prices and market news in JSON format using yfinance.
version: 1.1.0
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    homepage: "https://github.com/stone-shi/stock-checker"
    user-invocable: true
---

# Stock Checker Skill

This skill allows the agent to fetch real-time stock quotes and market news headlines using a local Python script powered by `yfinance`.

## Setup and Environment

This skill relies on a virtual environment (`venv`) to manage its dependencies. If the environment is not set up yet, run the following commands in the skill directory:
```bash
# Create the virtual environment if it does not exist
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

## Instructions

1.  **Environment Check**: Ensure the Python virtual environment is set up and dependencies in `requirements.txt` are installed.
2.  **Inquiry Phase**: When a user asks for stock data or news, use the `exec` tool to run the `stock_checker.py` script.
3.  **Command Execution**:
    -   To get stock prices: `./venv/bin/python stock_checker.py <SYMBOL1> <SYMBOL2> ...`
    -   To get market news: `./venv/bin/python stock_checker.py --news`
4.  **Data Processing**: The script outputs structured JSON. Parse this JSON to provide a concise and clear summary to the user.
5.  **Summarization**: If news headlines are returned, offer to summarize specific articles using the `web_fetch` or `browser` tool on the provided URLs.

## Examples

### User: "What is the price of AAPL?"
**Agent Action**: `exec("./venv/bin/python stock_checker.py AAPL")`
**Output**: 
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "status": "success",
      "price": 266.09,
      "currency": "USD",
      "change": -6.96,
      "change_percent": -2.55,
      "day_high": 272.8,
      "day_low": 265.4
    }
  ]
}
```

### User: "Show me market news"
**Agent Action**: `exec("./venv/bin/python stock_checker.py --news")`
**Output**: JSON containing a list of news items with `title`, `publisher`, and `link`.

## Constraints
- Always uppercase stock symbols.
- Do not make up stock data; only report what the script returns.
- If the script returns an error for a symbol, inform the user clearly.
