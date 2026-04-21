---
name: stock-checker-skill
description: Query latest stock prices and market news using a local Python script. Use when the user asks for stock quotes, market trends, or financial news.
---

# Stock Checker Skill

This skill provides a local Python script to query real-time stock data and market news from Yahoo Finance.

## Setup

Before running the script, ensure dependencies are installed. It is recommended to use a virtual environment.

```bash
# From the skill's assets directory or where the script is located
pip install -r requirements.txt
```

## Workflows

### Querying Stock Prices

Use the script to get latest data in JSON format for one or more symbols.

```bash
python3 stock_checker.py AAPL MSFT TSLA
```

### Getting Market News and Summaries

Use the `--news` flag to get headlines in JSON format.

```bash
python3 stock_checker.py --news
```

**Workflow for Summarization:**
1. Run the script with `--news`.
2. Parse the JSON to identify the URL of interest.
3. Call `web_fetch` with the URL and a prompt like "Summarize this market news article in simple words."
4. Present the summary to the user.

## Asset Locations

- Script: `assets/stock_checker.py`
- Dependencies: `assets/requirements.txt`

## Guidance

- **Symbol Normalization**: Always uppercase stock symbols before passing them to the script.
- **Error Handling**: If a symbol is invalid, the script will return "N/A" or an error status in JSON. Inform the user if a symbol could not be found.
- **News Context**: When showing news, the script provides titles and links. You can summarize these for the user.
