# market_analysis_app/strategies/strategy1.py

import pandas_ta as ta
import numpy as np

def strategy1(data):
    """Strategy using MA 21, EMA 9, Vortex, MACD, and PSAR."""
    # Calculate indicators
    data.ta.ema(length=9, append=True, col_names=('EMA_9',))
    data.ta.sma(length=21, append=True, col_names=('SMA_21',))
    data.ta.vortex(append=True, col_names=('VORTEX_P', 'VORTEX_N'))
    data.ta.macd(append=True, col_names=('MACD', 'MACD_H', 'MACD_S'))
    psar = data.ta.psar(append=True, col_names=('PSARl', 'PSARs', 'PSARaf', 'PSARr'))
    data.rename(columns={'PSARl': 'PSAR_long', 'PSARs': 'PSAR_short'}, inplace=True)


    # Buy Signal
    buy_signal = (
        (data['EMA_9'] > data['SMA_21']) &
        (data['VORTEX_P'] > data['VORTEX_N']) &
        (data['MACD'] > data['MACD_S'])
    )

    # Sell Signal
    sell_signal = (
        (data['EMA_9'] < data['SMA_21']) &
        (data['VORTEX_N'] > data['VORTEX_P']) &
        (data['MACD'] < data['MACD_S'])
    )

    data['signal'] = 0
    data.loc[buy_signal, 'signal'] = 1
    data.loc[sell_signal, 'signal'] = -1

    # Trailing Stop Loss and Target
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
            stop_loss = row['PSAR_long']
            target_price = entry_price * 1.01 # 1% target
        elif position == 0 and row['signal'] == -1:
            position = -1
            entry_price = row['Close']
            stop_loss = row['PSAR_short']
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
            else:
                # Update stop loss for trailing
                stop_loss = max(stop_loss, row['PSAR_long'])
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
            else:
                # Update stop loss for trailing
                stop_loss = min(stop_loss, row['PSAR_short'])

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
    # This is for testing purposes and will be moved to main.py
    try:
        from market_analysis_app.data.data_fetcher import get_data
        from market_analysis_app.config import SYMBOLS

        # Fetch NIFTY data
        nifty_data = get_data(SYMBOLS['INDICES']['NIFTY'])

        # Apply strategy
        nifty_data_with_indicators = strategy1(nifty_data)

        print(nifty_data_with_indicators.tail(20))

    except ImportError as e:
        print(f"Error: {e}. Please run this from the root directory of the project.")