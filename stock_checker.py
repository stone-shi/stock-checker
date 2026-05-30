import yfinance as yf
import argparse
import sys
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Union

# Suppress yfinance logger spam to stderr
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def _get_fast_info_attr(ticker, attr: str, default=None):
    """Safely read an attribute from ticker.fast_info (a proxy object, not a dict)."""
    try:
        return getattr(ticker.fast_info, attr, default)
    except Exception:
        return default


def _round_value(val: Optional[float], symbol: str) -> Optional[float]:
    """Round the value based on the symbol type and magnitude."""
    if val is None:
        return None
    try:
        val_float = float(val)
        if "=X" in symbol.upper() or abs(val_float) < 0.1:
            return round(val_float, 4)
        return round(val_float, 2)
    except (ValueError, TypeError):
        return None


def fetch_stock_data(symbols: Union[list[str], str]) -> list[dict]:
    if isinstance(symbols, str):
        symbols = [symbols]

    results = []
    for symbol in symbols:
        symbol_upper = symbol.upper()
        data = {
            "symbol": symbol_upper,
            "status": "success",
            "price": None,
            "currency": "USD",
            "change": None,
            "change_percent": None,
            "day_high": None,
            "day_low": None,
        }
        try:
            ticker = yf.Ticker(symbol)

            price = None
            prev_close = None
            currency = None
            day_high = None
            day_low = None

            # 1. Try fast_info first (safer and faster)
            try:
                price = _get_fast_info_attr(ticker, "last_price")
                prev_close = _get_fast_info_attr(ticker, "previous_close")
                currency = _get_fast_info_attr(ticker, "currency")
                day_high = _get_fast_info_attr(ticker, "day_high")
                day_low = _get_fast_info_attr(ticker, "day_low")
            except Exception:
                pass

            # 2. If price is still None, fallback to scraping ticker.info
            if price is None:
                try:
                    info = ticker.info
                    price = info.get("currentPrice") or info.get("regularMarketPrice")
                    prev_close = info.get("previousClose")
                    currency = info.get("currency")
                    day_high = info.get("dayHigh")
                    day_low = info.get("dayLow")
                except Exception:
                    pass

            if price is not None:
                data["price"] = _round_value(price, symbol_upper)
                if currency:
                    data["currency"] = currency

                data["day_high"] = _round_value(day_high, symbol_upper)
                data["day_low"] = _round_value(day_low, symbol_upper)

                if prev_close is not None:
                    change = float(price) - float(prev_close)
                    data["change"] = _round_value(change, symbol_upper)
                    if float(prev_close) != 0:
                        data["change_percent"] = round(
                            (change / float(prev_close)) * 100, 2
                        )
            else:
                data["status"] = "not_found"

        except Exception as e:
            data["status"] = "error"
            data["error_message"] = str(e)

        results.append(data)
    return results


def fetch_market_news(count: int = 5) -> list[dict]:
    try:
        search = yf.Search("market", news_count=count)
        news_items = []
        for article in search.news:
            pub_time = article.get("providerPublishTime")
            time_formatted = None
            if pub_time is not None:
                try:
                    time_formatted = datetime.fromtimestamp(
                        int(pub_time), tz=timezone.utc
                    ).isoformat()
                except Exception:
                    pass
            news_items.append(
                {
                    "title": article.get("title"),
                    "publisher": article.get("publisher"),
                    "link": article.get("link"),
                    "time": pub_time,
                    "time_formatted": time_formatted,
                }
            )
        return news_items
    except Exception as e:
        return [{"error": str(e)}]


def main():
    parser = argparse.ArgumentParser(
        description="Query latest stock prices and market news in JSON format."
    )
    parser.add_argument(
        "symbols",
        nargs="*",
        help="One or more stock symbols (e.g., AAPL MSFT TSLA)",
    )
    parser.add_argument(
        "--news", action="store_true", help="Show top market news"
    )
    parser.add_argument(
        "--news-count",
        type=int,
        default=5,
        help="Number of news articles to fetch (default: 5)",
    )

    args = parser.parse_args()

    if not args.symbols and not args.news:
        parser.print_help()
        sys.exit(1)

    output_data = {}

    if args.symbols:
        output_data["stocks"] = fetch_stock_data(args.symbols)

    if args.news:
        output_data["news"] = fetch_market_news(count=args.news_count)

    print(json.dumps(output_data, indent=2))


if __name__ == "__main__":
    main()
