import yfinance as yf
import argparse
import sys
import json
from datetime import datetime

def fetch_stock_data(symbols):
    results = []
    for symbol in symbols:
        data = {
            "symbol": symbol.upper(),
            "status": "success",
            "price": None,
            "currency": "USD",
            "change": None,
            "change_percent": None,
            "day_high": None,
            "day_low": None
        }
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
            data["currency"] = info.get('currency', 'USD')
            data["day_high"] = info.get('dayHigh')
            data["day_low"] = info.get('dayLow')

            if price is None:
                fast = ticker.fast_info
                price = fast.get('last_price')
                prev_close = fast.get('previous_close')
                data["currency"] = fast.get('currency', 'USD')
                data["day_high"] = fast.get('day_high')
                data["day_low"] = fast.get('day_low')

            if price is not None:
                data["price"] = round(price, 2)
                if prev_close is not None:
                    change = price - prev_close
                    data["change"] = round(change, 2)
                    data["change_percent"] = round((change / prev_close) * 100, 2)
            else:
                data["status"] = "not_found"
                
        except Exception as e:
            data["status"] = "error"
            data["error_message"] = str(e)
        
        results.append(data)
    return results

def fetch_market_news(count=5):
    try:
        search = yf.Search("market", news_count=count)
        news_items = []
        for article in search.news:
            news_items.append({
                "title": article.get("title"),
                "publisher": article.get("publisher"),
                "link": article.get("link"),
                "time": article.get("providerPublishTime")
            })
        return news_items
    except Exception as e:
        return [{"error": str(e)}]

def main():
    parser = argparse.ArgumentParser(description="Query latest stock prices and market news in JSON format.")
    parser.add_argument("symbols", nargs="*", help="One or more stock symbols (e.g., AAPL MSFT TSLA)")
    parser.add_argument("--news", action="store_true", help="Show top market news")
    
    args = parser.parse_args()
    
    if not args.symbols and not args.news:
        parser.print_help()
        sys.exit(1)
    
    output_data = {}
    
    if args.symbols:
        output_data["stocks"] = fetch_stock_data(args.symbols)
    
    if args.news:
        output_data["news"] = fetch_market_news()
    
    print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    main()
