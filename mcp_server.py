"""MCP SSE server wrapping stock_checker functions as exposed tools."""

import os

from mcp.server.fastmcp import FastMCP
from stock_checker import fetch_stock_data, fetch_market_news

mcp = FastMCP(
    "Stock Checker",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


@mcp.tool()
def get_stock_prices(symbols: list[str]) -> dict:
    """Fetch latest stock prices for one or more ticker symbols (e.g. AAPL, MSFT).

    Returns price, change, change percent, day high, day low, and currency
    for each symbol.
    """
    results = fetch_stock_data(symbols)
    return {"stocks": results}


@mcp.tool()
def get_market_news(count: int = 5) -> dict:
    """Fetch top market news headlines.

    Args:
        count: Number of news articles to return (default 5).
    """
    results = fetch_market_news(count=count)
    return {"news": results}


def main():
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
