# market_analysis_app/strategies/strategy4.py

import pandas_ta as ta
import pandas as pd

def calculate_strategy4_levels(data):
    """Calculates Pivot Points and Fibonacci Retracement levels."""
    # Calculate Pivot Points
    # pandas_ta.pivot returns a DataFrame with columns like 'PIVOT', 'S1', 'R1', etc.
    pivots_df = data.ta.pivot(append=True)

    # Extract the last row of pivot points
    last_pivots = pivots_df.iloc[-1].filter(regex='^(PIVOT|S|R)')

    # Calculate Fibonacci Retracement
    # The fibonacci function in pandas-ta needs a high and low price.
    # We will use the high and low of the last period.
    high_price = data['High'].iloc[-1]
    low_price = data['Low'].iloc[-1]
    fib_levels = ta.fibonacci(high=high_price, low=low_price)

    levels = {
        'pivot_points': last_pivots.to_dict(),
        'fibonacci': fib_levels.to_dict()
    }

    return levels

def strategy4_signal(current_price, levels, tolerance=0.001):
    """Generates a signal based on the current price and Strategy 4 levels."""
    pivot_points = levels['pivot_points']
    fibonacci_levels = levels['fibonacci']

    # Check for proximity to support levels
    for key, value in pivot_points.items():
        if key.startswith('S') and abs(current_price - value) / value < tolerance:
            return 1 # Buy signal (near support)

    # Check for proximity to resistance levels
    for key, value in pivot_points.items():
        if key.startswith('R') and abs(current_price - value) / value < tolerance:
            return -1 # Sell signal (near resistance)

    # Check for proximity to Fibonacci retracement levels
    # This is a simplified check, typically you'd look for bounces/breaks
    for key, value in fibonacci_levels.items():
        if abs(current_price - value) / value < tolerance:
            # If near a fib level, it could be support or resistance
            # More advanced logic needed here to determine direction
            pass

    return 0 # No signal

if __name__ == '__main__':
    # Example usage (requires data_fetcher)
    try:
        from market_analysis_app.data.data_fetcher import get_data
        from market_analysis_app.config import SYMBOLS

        # Fetch NIFTY data
        nifty_data = get_data(SYMBOLS['INDICES']['NIFTY'], period='1d', interval='1d')

        if nifty_data is not None and not nifty_data.empty:
            # Calculate levels from the previous day
            strategy4_levels = calculate_strategy4_levels(nifty_data)
            print("Strategy 4 Levels:")
            print(strategy4_levels)

            # Simulate checking the signal with the current price
            current_price = nifty_data.iloc[-1]['Close']
            signal = strategy4_signal(current_price, strategy4_levels)
            print(f"Current Price: {current_price}, Signal: {signal}")

    except ImportError as e:
        print(f"Error: {e}. Please run this from the root directory of the project.")
    except Exception as e:
        print(f"An error occurred: {e}")
