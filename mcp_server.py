"""MCP SSE server wrapping stock_checker functions as exposed tools."""

import os

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from stock_checker import fetch_stock_data, fetch_market_news

mcp = FastMCP(
    "Stock Checker",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
    streamable_http_path="/mcp",
)


@mcp.tool()
def get_stock_prices(symbols: list[str]) -> dict:
    """Fetch latest stock prices for one or more ticker symbols (e.g. AAPL, MSFT).

    Returns price, change, change percent, day high, day low, and currency
    for each symbol.
    """
    results = fetch_stock_data(symbols)
    return {"stocks": results}


@mcp.custom_route("/version", methods=["GET"])
async def get_version(request: Request) -> PlainTextResponse:
    """Return the contents of version.txt (generated at build time)."""
    try:
        with open("version.txt") as f:
            content = f.read().strip()
    except FileNotFoundError:
        content = "unknown"
    return PlainTextResponse(content)


@mcp.tool()
def get_market_news(count: int = 5) -> dict:
    """Fetch top market news headlines.

    Args:
        count: Number of news articles to return (default 5).
    """
    results = fetch_market_news(count=count)
    return {"news": results}


def main():
    transport = os.getenv("MCP_TRANSPORT", "all")
    if transport == "all":
        import uvicorn
        from starlette.applications import Starlette

        sse_app = mcp.sse_app()
        streamable_app = mcp.streamable_http_app()

        # Combine routes from both SSE app (/sse, /messages) and Streamable HTTP app (/mcp, custom routes)
        # Deduplicate routes if custom routes appear in both
        seen_paths = set()
        combined_routes = []
        for r in sse_app.routes + streamable_app.routes:
            path = getattr(r, "path", getattr(r, "path_format", str(r)))
            if path not in seen_paths:
                seen_paths.add(path)
                combined_routes.append(r)

        combined_app = Starlette(
            debug=mcp.settings.debug,
            routes=combined_routes,
            lifespan=lambda app: mcp.session_manager.run(),
        )

        uvicorn.run(
            combined_app,
            host=mcp.settings.host,
            port=mcp.settings.port,
            log_level=mcp.settings.log_level.lower(),
        )
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
