import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
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

def print_table(results, news=None):
    console = Console()
    
    if results:
        table = Table(title="Latest Stock Prices")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Price", style="green")
        table.add_column("Currency", style="magenta")
        table.add_column("Change", style="bold")
        table.add_column("Change %", style="bold")
        table.add_column("Day High", style="yellow")
        table.add_column("Day Low", style="yellow")

        for res in results:
            if res["status"] == "success" and res["price"] is not None:
                color = "green" if (res["change"] or 0) >= 0 else "red"
                change_val = res['change'] if res['change'] is not None else 0.0
                change_pct_val = res['change_percent'] if res['change_percent'] is not None else 0.0
                
                change_str = f"[{color}]{change_val:+.2f}[/]"
                change_pct_str = f"[{color}]{change_pct_val:+.2f}%[/]"
                
                table.add_row(
                    res["symbol"],
                    f"{res['price']:.2f}",
                    res["currency"],
                    change_str,
                    change_pct_str,
                    f"{res['day_high']:.2f}" if res['day_high'] else "N/A",
                    f"{res['day_low']:.2f}" if res['day_low'] else "N/A"
                )
            elif res["status"] == "error":
                table.add_row(res["symbol"], "ERROR", "-", "-", "-", "-", "-")
            else:
                table.add_row(res["symbol"], "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

        console.print(table)

    if news:
        console.print("\n[bold]Top Market News[/bold]")
        for item in news:
            if "error" in item:
                console.print(f"[red]Error fetching news: {item['error']}[/]")
                continue
            
            title = item.get('title', 'No Title')
            publisher = item.get('publisher', 'Unknown')
            link = item.get('link', '')
            
            content = f"[bold]{title}[/bold]\n[dim]Source: {publisher}[/dim]\n[blue]{link}[/blue]"
            console.print(Panel(content, expand=False))

def main():
    parser = argparse.ArgumentParser(description="Query latest stock prices and market news.")
    parser.add_argument("symbols", nargs="*", help="One or more stock symbols (e.g., AAPL MSFT TSLA)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
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
    
    if args.json:
        print(json.dumps(output_data, indent=2))
    else:
        print_table(output_data.get("stocks", []), output_data.get("news"))

if __name__ == "__main__":
    main()
