import unittest
from unittest.mock import patch, MagicMock, mock_open
import asyncio


class TestMCPGetStockPrices(unittest.TestCase):

    @patch("mcp_server.fetch_stock_data")
    def test_get_stock_prices(self, mock_fetch):
        from mcp_server import get_stock_prices

        mock_fetch.return_value = [{"symbol": "AAPL", "price": 150.0}]
        result = get_stock_prices(["AAPL"])
        self.assertEqual(result, {"stocks": [{"symbol": "AAPL", "price": 150.0}]})
        mock_fetch.assert_called_once_with(["AAPL"])


class TestMCPGetMarketNews(unittest.TestCase):

    @patch("mcp_server.fetch_market_news")
    def test_get_market_news(self, mock_fetch):
        from mcp_server import get_market_news

        mock_fetch.return_value = [{"title": "News 1"}]
        result = get_market_news(count=3)
        self.assertEqual(result, {"news": [{"title": "News 1"}]})
        mock_fetch.assert_called_once_with(count=3)

    @patch("mcp_server.fetch_market_news")
    def test_get_market_news_default_count(self, mock_fetch):
        from mcp_server import get_market_news

        mock_fetch.return_value = []
        result = get_market_news()
        self.assertEqual(result, {"news": []})
        mock_fetch.assert_called_once_with(count=5)


class TestMCPGetVersion(unittest.TestCase):

    @patch("builtins.open", mock_open(read_data="1.0.0\n"))
    def test_get_version_found(self):
        from mcp_server import get_version

        result = asyncio.run(get_version(None))
        self.assertEqual(result.body.decode(), "1.0.0")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_version_not_found(self, mock_open):
        from mcp_server import get_version

        result = asyncio.run(get_version(None))
        self.assertEqual(result.body.decode(), "unknown")


if __name__ == "__main__":
    unittest.main()
