# market_analysis_app/data/data_fetcher.py

import yfinance as yf
import pandas as pd

def get_data(symbol, interval='15m', period='1d'):
    """Fetches historical data for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        if data.empty:
            print(f"No data fetched for {symbol} with interval {interval} and period {period}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    nifty_data = get_data('^NSEI') # NIFTY
    if nifty_data is not None:
        print(nifty_data.head())

    banknifty_data = get_data('^NSEBANK') # BANKNIFTY
    if banknifty_data is not None:
        print(banknifty_data.head())

    sensex_data = get_data('^BSESN') # SENSEX
    if sensex_data is not None:
        print(sensex_data.head())
