import unittest
from unittest.mock import patch, MagicMock
from stock_checker import fetch_stock_data, fetch_market_news, _round_value


class TestStockChecker(unittest.TestCase):

    def test_round_value(self):
        # Standard stock rounding (2 decimals)
        self.assertEqual(_round_value(123.456, "AAPL"), 123.46)
        self.assertEqual(_round_value(0.123, "AAPL"), 0.12)

        # Forex stock rounding (4 decimals)
        self.assertEqual(_round_value(1.16877, "EURUSD=X"), 1.1688)

        # Penny stock/very small magnitude rounding (4 decimals)
        self.assertEqual(_round_value(0.00456, "XYZ"), 0.0046)

        # None handling
        self.assertIsNone(_round_value(None, "AAPL"))

        # Invalid float value
        self.assertIsNone(_round_value("invalid", "AAPL"))

    @patch("stock_checker.yf.Ticker")
    def test_fetch_stock_data_success_fast_info(self, mock_ticker_class):
        # Setup mock ticker with fast_info
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # mock fast_info attribute access
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 150.256
        mock_fast_info.previous_close = 149.0
        mock_fast_info.currency = "USD"
        mock_fast_info.day_high = 152.0
        mock_fast_info.day_low = 148.5
        mock_ticker.fast_info = mock_fast_info

        # Mock ticker.info to return None or raise an exception to ensure fast_info is used
        mock_ticker.info = {}

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
    def test_fetch_stock_data_fallback_to_info(self, mock_ticker_class):
        # Setup mock ticker where fast_info fails or returns None, but info works
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        # fast_info attributes return None or raise exception
        mock_fast_info = MagicMock()
        mock_fast_info.last_price = None
        mock_ticker.fast_info = mock_fast_info

        # info works
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
    def test_fetch_stock_data_not_found(self, mock_ticker_class):
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
    def test_fetch_stock_data_single_string(self, mock_ticker_class):
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker

        mock_fast_info = MagicMock()
        mock_fast_info.last_price = 100.0
        mock_ticker.fast_info = mock_fast_info
        mock_ticker.info = {}

        results = fetch_stock_data("TSLA")  # string instead of list

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["symbol"], "TSLA")

    @patch("stock_checker.yf.Search")
    def test_fetch_market_news(self, mock_search_class):
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search

        # Mock news articles
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


if __name__ == "__main__":
    unittest.main()
