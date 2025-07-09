# market_analysis_app/strategies/strategy2.py

import pandas as pd

def calculate_strategy2_levels(previous_day_data):
    """Calculates the breakout and breakdown levels for Strategy 2."""
    H = previous_day_data['High']
    L = previous_day_data['Low']
    C = previous_day_data['Close']

    buy_breakout = (H - L) * 1.1 / 2 + C
    stoploss_buy = C - (H - L) * 1.1 / 4
    sell_breakdown = C - (H - L) * 1.1 / 2
    stoploss_sell = (H - L) * 1.1 / 4 + C

    return {
        'buy_breakout': buy_breakout,
        'stoploss_buy': stoploss_buy,
        'sell_breakdown': sell_breakdown,
        'stoploss_sell': stoploss_sell
    }

def strategy2_signal(current_price, levels):
    """Generates a signal based on the current price and Strategy 2 levels."""
    if current_price > levels['buy_breakout']:
        return 1  # Buy signal
    elif current_price < levels['sell_breakdown']:
        return -1  # Sell signal
    else:
        return 0  # No signal

if __name__ == '__main__':
    # Example usage (requires data_fetcher)
    try:
        from market_analysis_app.data.data_fetcher import get_data
        from market_analysis_app.config import SYMBOLS

        # Fetch NIFTY data for 2 days to get previous day's data
        nifty_data = get_data(SYMBOLS['INDICES']['NIFTY'], period='2d', interval='1d')

        if nifty_data is not None and len(nifty_data) >= 2:
            # Calculate levels from the previous day
            strategy2_levels = calculate_strategy2_levels(nifty_data.iloc[-2])
            print(f"Strategy 2 Levels: {strategy2_levels}")

            # Simulate checking the signal with the current price
            # In a real scenario, this would be a real-time price
            current_price = nifty_data.iloc[-1]['Close'] 
            signal = strategy2_signal(current_price, strategy2_levels)
            print(f"Current Price: {current_price}, Signal: {signal}")

    except ImportError as e:
        print(f"Error: {e}. Please run this from the root directory of the project.")
