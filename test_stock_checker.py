import unittest
from unittest.mock import patch, MagicMock
from stock_checker import (
    fetch_stock_data,
    fetch_market_news,
    _round_value,
    _get_fast_info_attr,
    main,
)


class TestRoundValue(unittest.TestCase):

    def test_standard_stock(self):
        self.assertEqual(_round_value(123.456, "AAPL"), 123.46)
        self.assertEqual(_round_value(0.123, "AAPL"), 0.12)

    def test_forex_stock(self):
        self.assertEqual(_round_value(1.16877, "EURUSD=X"), 1.1688)

    def test_penny_stock(self):
        self.assertEqual(_round_value(0.00456, "XYZ"), 0.0046)

    def test_none_value(self):
        self.assertIsNone(_round_value(None, "AAPL"))

    def test_invalid_value(self):
        self.assertIsNone(_round_value("invalid", "AAPL"))


class TestGetFastInfoAttr(unittest.TestCase):

    def test_get_existing_attr(self):
        ticker = MagicMock()
        ticker.fast_info.last_price = 150.0
        result = _get_fast_info_attr(ticker, "last_price")
        self.assertEqual(result, 150.0)

    def test_get_nonexistent_attr(self):
        ticker = MagicMock()
        ticker.fast_info = MagicMock(spec=object())
        result = _get_fast_info_attr(ticker, "nonexistent", "default")
        self.assertEqual(result, "default")

    def test_exception_on_access(self):
        ticker = MagicMock()
        ticker.fast_info = MagicMock(spec=object())
        ticker.fast_info.last_price = 42
        del ticker.fast_info.last_price
        result = _get_fast_info_attr(ticker, "last_price", "fallback")
        self.assertEqual(result, "fallback")


class TestFetchStockData(unittest.TestCase):

    @patch("stock_checker.yf.Ticker")
    def test_success_fast_info(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.info = {}

        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 150.256
        mock_fast_info.previous_close = 149.0
        mock_fast_info.currency = "USD"
        mock_fast_info.day_high = 152.0
        mock_fast_info.day_low = 148.5
        mock_ticker.fast_info = mock_fast_info

        results = fetch_stock_data(["AAPL"])

        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res["symbol"], "AAPL")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["price"], 150.26)
        self.assertEqual(res["change"], 1.26)
        self.assertEqual(res["change_percent"], 0.84)
        self.assertEqual(res["day_high"], 152.0)
        self.assertEqual(res["day_low"], 148.5)
        self.assertEqual(res["currency"], "USD")

    @patch("stock_checker.yf.Ticker")
    def test_fallback_to_info(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = None
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {
            "currentPrice": 200.5,
            "previousClose": 200.0,
            "currency": "EUR",
            "dayHigh": 205.0,
            "dayLow": 199.0,
        }

        results = fetch_stock_data(["MSFT"])

        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res["symbol"], "MSFT")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["price"], 200.5)
        self.assertEqual(res["change"], 0.5)
        self.assertEqual(res["change_percent"], 0.25)
        self.assertEqual(res["day_high"], 205.0)
        self.assertEqual(res["day_low"], 199.0)
        self.assertEqual(res["currency"], "EUR")

    @patch("stock_checker.yf.Ticker")
    def test_fallback_to_info_with_regular_market_price(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = None
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {
            "regularMarketPrice": 50.0,
            "previousClose": 49.0,
        }

        results = fetch_stock_data(["TEST"])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["price"], 50.0)

    @patch("stock_checker.yf.Ticker")
    def test_not_found(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = None
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {}

        results = fetch_stock_data(["INVALID"])

        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res["symbol"], "INVALID")
        self.assertEqual(res["status"], "not_found")
        self.assertIsNone(res["price"])

    @patch("stock_checker.yf.Ticker")
    def test_single_string(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 100.0
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {}

        results = fetch_stock_data("TSLA")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["symbol"], "TSLA")

    @patch("stock_checker.yf.Ticker")
    def test_multiple_symbols(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 100.0
        mock_fast_info.previous_close = 99.0
        mock_fast_info.currency = "USD"
        mock_fast_info.day_high = 101.0
        mock_fast_info.day_low = 98.0
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {}

        results = fetch_stock_data(["AAPL", "MSFT"])

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["symbol"], "AAPL")
        self.assertEqual(results[1]["symbol"], "MSFT")

    @patch("stock_checker.yf.Ticker")
    def test_prev_close_zero(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 150.0
        mock_fast_info.previous_close = 0.0
        mock_fast_info.currency = "USD"
        mock_fast_info.day_high = 152.0
        mock_fast_info.day_low = 148.0
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {}

        results = fetch_stock_data(["AAPL"])

        self.assertEqual(results[0]["change_percent"], None)

    @patch("stock_checker.yf.Ticker")
    def test_exception_handling(self, mock_ticker_class):
        mock_ticker_class.side_effect = Exception("API error")
        results = fetch_stock_data(["AAPL"])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["symbol"], "AAPL")
        self.assertEqual(results[0]["status"], "error")
        self.assertIn("error_message", results[0])

    @patch("stock_checker.yf.Ticker")
    def test_uppercase_symbol(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 50.0
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {}

        results = fetch_stock_data(["aapl"])
        self.assertEqual(results[0]["symbol"], "AAPL")


class TestFetchMarketNews(unittest.TestCase):

    @patch("stock_checker.yf.Search")
    def test_fetch_news(self, mock_search_class):
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search
        mock_search.news = [
            {
                "title": "News 1",
                "publisher": "Pub 1",
                "link": "http://link1",
                "providerPublishTime": 1780147800,
            }
        ]

        news = fetch_market_news(count=1)

        self.assertEqual(len(news), 1)
        item = news[0]
        self.assertEqual(item["title"], "News 1")
        self.assertEqual(item["publisher"], "Pub 1")
        self.assertEqual(item["link"], "http://link1")
        self.assertEqual(item["time"], 1780147800)
        self.assertIsNotNone(item["time_formatted"])

    @patch("stock_checker.yf.Search")
    def test_fetch_news_no_articles(self, mock_search_class):
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search
        mock_search.news = []

        news = fetch_market_news(count=5)
        self.assertEqual(len(news), 0)

    @patch("stock_checker.yf.Search")
    def test_fetch_news_exception(self, mock_search_class):
        mock_search_class.side_effect = Exception("Search error")
        news = fetch_market_news(count=1)
        self.assertEqual(len(news), 1)
        self.assertIn("error", news[0])

    @patch("stock_checker.yf.Search")
    def test_news_missing_fields(self, mock_search_class):
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search
        mock_search.news = [{"title": "Missing fields"}]

        news = fetch_market_news(count=1)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]["title"], "Missing fields")
        self.assertIsNone(news[0]["publisher"])
        self.assertIsNone(news[0]["link"])
        self.assertIsNone(news[0]["time"])
        self.assertIsNone(news[0]["time_formatted"])


class TestMainCLI(unittest.TestCase):

    @patch("stock_checker.fetch_stock_data")
    @patch("stock_checker.json.dumps")
    @patch("stock_checker.print")
    @patch("sys.argv", ["stock_checker.py", "AAPL", "MSFT"])
    def test_main_with_symbols(self, mock_print, mock_json_dumps, mock_fetch):
        mock_fetch.return_value = ["mock_result"]
        mock_json_dumps.return_value = "{}"
        main()
        mock_fetch.assert_called_once_with(["AAPL", "MSFT"])

    @patch("stock_checker.fetch_market_news")
    @patch("stock_checker.json.dumps")
    @patch("stock_checker.print")
    @patch("sys.argv", ["stock_checker.py", "--news"])
    def test_main_with_news(self, mock_print, mock_json_dumps, mock_fetch_news):
        mock_fetch_news.return_value = ["mock_news"]
        mock_json_dumps.return_value = "{}"
        main()
        mock_fetch_news.assert_called_once_with(count=5)

    @patch("stock_checker.fetch_market_news")
    @patch("stock_checker.fetch_stock_data")
    @patch("stock_checker.json.dumps")
    @patch("stock_checker.print")
    @patch("sys.argv", ["stock_checker.py", "AAPL", "--news", "--news-count", "3"])
    def test_main_with_symbols_and_news(self, mock_print, mock_json_dumps, mock_fetch_stock, mock_fetch_news):
        mock_fetch_stock.return_value = ["mock_result"]
        mock_fetch_news.return_value = ["mock_news"]
        mock_json_dumps.return_value = "{}"
        main()
        mock_fetch_stock.assert_called_once_with(["AAPL"])
        mock_fetch_news.assert_called_once_with(count=3)

    @patch("sys.argv", ["stock_checker.py"])
    def test_main_no_args_exits(self):
        with self.assertRaises(SystemExit):
            main()


if __name__ == "__main__":
    unittest.main()
