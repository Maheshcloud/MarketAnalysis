# tests/test_data_fetcher.py

import unittest
from unittest.mock import patch
import pandas as pd
from market_analysis_app.data.data_fetcher import get_data

class TestDataFetcher(unittest.TestCase):

    @patch('yfinance.Ticker')
    def test_get_data_success(self, mock_ticker):
        # Mock the yfinance Ticker and history method
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame({
            'Open': [100, 101],
            'High': [102, 103],
            'Low': [99, 100],
            'Close': [101, 102],
            'Volume': [1000, 1200]
        })

        data = get_data("TEST")
        self.assertIsNotNone(data)
        self.assertFalse(data.empty)
        self.assertEqual(len(data), 2)
        mock_ticker.assert_called_with("TEST")
        mock_instance.history.assert_called_with(period='1d', interval='15m')

    @patch('yfinance.Ticker')
    def test_get_data_empty(self, mock_ticker):
        # Mock yfinance to return empty DataFrame
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame()

        data = get_data("TEST")
        self.assertIsNone(data)

    @patch('yfinance.Ticker')
    def test_get_data_exception(self, mock_ticker):
        # Mock yfinance to raise an exception
        mock_instance = mock_ticker.return_value
        mock_instance.history.side_effect = Exception("Network Error")

        data = get_data("TEST")
        self.assertIsNone(data)

if __name__ == '__main__':
    unittest.main()
