# market_analysis_app/strategies/strategy3.py

import pandas_ta as ta
import numpy as np
import pandas as pd

def strategy3(data):
    """Strategy using Ichimoku Cloud and candlestick patterns."""
    # Calculate Ichimoku Cloud
    ichimoku_df, span_df = data.ta.ichimoku()
    data = pd.concat([data, ichimoku_df, span_df], axis=1)

    # Identify candlestick patterns
    data.ta.cdl_pattern(name=['doji', 'engulfing', 'hammer'], append=True)

    # Ichimoku Buy Signal
    ichimoku_buy = (
        (data['Close'] > data['ISA_9']) &
        (data['Close'] > data['ISB_26']) &
        (data['ISA_9'] > data['ISB_26']) &
        (data['ICS_26'] > data['Close'].shift(26))
    )

    # Ichimoku Sell Signal
    ichimoku_sell = (
        (data['Close'] < data['ISA_9']) &
        (data['Close'] < data['ISB_26']) &
        (data['ISA_9'] < data['ISB_26']) &
        (data['ICS_26'] < data['Close'].shift(26))
    )

    # Candlestick signals (simplified)
    bullish_candle = (data['CDL_HAMMER'] > 0) | (data['CDL_ENGULFING'] > 0) # Simplified
    bearish_candle = (data['CDL_ENGULFING'] < 0) # Simplified

    # Combined Signal
    buy_signal = ichimoku_buy & bullish_candle
    sell_signal = ichimoku_sell & bearish_candle

    data['signal'] = 0
    data.loc[buy_signal, 'signal'] = 1
    data.loc[sell_signal, 'signal'] = -1

    # Target and Stop Loss
    position = 0
    entry_price = np.nan
    stop_loss = np.nan
    target_price = np.nan

    positions = []
    entry_prices = []
    stop_losses = []
    target_prices = []

    for i, row in data.iterrows():
        if position == 0 and row['signal'] == 1:
            position = 1
            entry_price = row['Close']
            stop_loss = entry_price * 0.995 # 0.5% stop loss
            target_price = entry_price * 1.01 # 1% target
        elif position == 0 and row['signal'] == -1:
            position = -1
            entry_price = row['Close']
            stop_loss = entry_price * 1.005 # 0.5% stop loss
            target_price = entry_price * 0.99 # 1% target
        elif position == 1:
            # Check for stop loss hit
            if row['Low'] < stop_loss:
                position = 0
                entry_price = np.nan
                stop_loss = np.nan
                target_price = np.nan
            # Check for target hit
            elif row['High'] > target_price:
                position = 0
                entry_price = np.nan
                stop_loss = np.nan
                target_price = np.nan
        elif position == -1:
            # Check for stop loss hit
            if row['High'] > stop_loss:
                position = 0
                entry_price = np.nan
                stop_loss = np.nan
                target_price = np.nan
            # Check for target hit
            elif row['Low'] < target_price:
                position = 0
                entry_price = np.nan
                stop_loss = np.nan
                target_price = np.nan

        positions.append(position)
        entry_prices.append(entry_price)
        stop_losses.append(stop_loss)
        target_prices.append(target_price)

    data['position'] = positions
    data['entry_price'] = entry_prices
    data['stop_loss'] = stop_losses
    data['target_price'] = target_prices

    return data

if __name__ == '__main__':
    # Example usage (requires data_fetcher)
    try:
        from market_analysis_app.data.data_fetcher import get_data
        from market_analysis_app.config import SYMBOLS

        # Fetch NIFTY data
        nifty_data = get_data(SYMBOLS['INDICES']['NIFTY'])

        # Apply strategy
        nifty_data_with_indicators = strategy3(nifty_data)

        print(nifty_data_with_indicators.tail(10))

    except ImportError as e:
        print(f"Error: {e}. Please run this from the root directory of the project.")
    except Exception as e:
        print(f"An error occurred: {e}")
