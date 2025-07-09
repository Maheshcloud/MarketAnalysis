# tests/test_strategy1.py

import unittest
import pandas as pd
import numpy as np
from market_analysis_app.strategies.strategy1 import strategy1

class TestStrategy1(unittest.TestCase):

    def setUp(self):
        # Create a dummy DataFrame for testing
        self.data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'High': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'Low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'Close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        })

    def test_strategy1_buy_signal(self):
        # Manipulate data to create a buy signal scenario
        # EMA_9 > SMA_21, VORTEX_P > VORTEX_N, MACD > MACD_S
        self.data['EMA_9'] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109.5]
        self.data['SMA_21'] = [99, 100, 101, 102, 103, 104, 105, 106, 107, 108.5]
        self.data['VORTEX_P'] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
        self.data['VORTEX_N'] = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
        self.data['MACD'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.data['MACD_S'] = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.data['PSAR_long'] = [98, 99, 100, 101, 102, 103, 104, 105, 106, 107]
        self.data['PSAR_short'] = [103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

        result = strategy1(self.data.copy())
        self.assertEqual(result['signal'].iloc[-1], 1)
        self.assertAlmostEqual(result['entry_price'].iloc[-1], self.data['Close'].iloc[-1])
        self.assertAlmostEqual(result['target_price'].iloc[-1], self.data['Close'].iloc[-1] * 1.01)
        self.assertAlmostEqual(result['stop_loss'].iloc[-1], self.data['PSAR_long'].iloc[-1])

    def test_strategy1_sell_signal(self):
        # Manipulate data to create a sell signal scenario
        # EMA_9 < SMA_21, VORTEX_N > VORTEX_P, MACD < MACD_S
        self.data['EMA_9'] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 107.5]
        self.data['SMA_21'] = [101, 102, 103, 104, 105, 106, 107, 108, 109, 108.5]
        self.data['VORTEX_P'] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.3]
        self.data['VORTEX_N'] = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.4]
        self.data['MACD'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.8]
        self.data['MACD_S'] = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9]
        self.data['PSAR_long'] = [98, 99, 100, 101, 102, 103, 104, 105, 106, 107]
        self.data['PSAR_short'] = [103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

        result = strategy1(self.data.copy())
        self.assertEqual(result['signal'].iloc[-1], -1)
        self.assertAlmostEqual(result['entry_price'].iloc[-1], self.data['Close'].iloc[-1])
        self.assertAlmostEqual(result['target_price'].iloc[-1], self.data['Close'].iloc[-1] * 0.99)
        self.assertAlmostEqual(result['stop_loss'].iloc[-1], self.data['PSAR_short'].iloc[-1])

    def test_strategy1_no_signal(self):
        # Data with no clear signal
        self.data['EMA_9'] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 108]
        self.data['SMA_21'] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 108]
        self.data['VORTEX_P'] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.3]
        self.data['VORTEX_N'] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.3]
        self.data['MACD'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.9]
        self.data['MACD_S'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.9]
        self.data['PSAR_long'] = [98, 99, 100, 101, 102, 103, 104, 105, 106, 107]
        self.data['PSAR_short'] = [103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

        result = strategy1(self.data.copy())
        self.assertEqual(result['signal'].iloc[-1], 0)

if __name__ == '__main__':
    unittest.main()