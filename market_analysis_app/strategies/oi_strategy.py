# market_analysis_app/strategies/oi_strategy.py

import pandas as pd
from nsepython import nse_optionchain_scrapper
import datetime

def get_oi_data(symbol):
    """Fetches OI data for a given symbol using nsepython."""
    try:
        # nse_optionchain_scrapper expects symbol like 'NIFTY' or 'BANKNIFTY'
        # It fetches data for the current expiry by default.
        # For Sensex, nsepython might not work as it's NSE specific.
        if symbol == "SENSEX":
            print("NSEPython does not support Sensex OI data directly. Skipping.")
            return None

        data = nse_optionchain_scrapper(symbol)
        
        # Extract relevant data and convert to DataFrame
        records = []
        for item in data['records']['data']:
            record = {
                'strike': item['strikePrice'],
                'ce_oi': item['CE']['openInterest'] if 'CE' in item else 0,
                'pe_oi': item['PE']['openInterest'] if 'PE' in item else 0,
                'ce_change_oi': item['CE']['changeinOpenInterest'] if 'CE' in item else 0,
                'pe_change_oi': item['PE']['changeinOpenInterest'] if 'PE' in item else 0,
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        print(f"Error fetching OI data for {symbol}: {e}")
        return None

def calculate_pcr(oi_data):
    """Calculates the PCR (Put-Call Ratio)."""
    if oi_data is None or oi_data.empty:
        return 0
    total_pe_oi = oi_data['pe_oi'].sum()
    total_ce_oi = oi_data['ce_oi'].sum()
    if total_ce_oi == 0:
        return 0 # Avoid division by zero
    pcr = total_pe_oi / total_ce_oi
    return pcr

def oi_trend_analysis(pcr):
    """Analyzes the trend based on PCR."""
    if pcr > 1.2:
        return "Strong Bullish"
    elif pcr > 0.8:
        return "Bullish"
    elif pcr < 0.5:
        return "Strong Bearish"
    elif pcr < 0.8:
        return "Bearish"
    else:
        return "Neutral"

def hero_zero_call(oi_data, current_price):
    """Generates a hero-zero call based on OI data and current price."""
    if oi_data is None or oi_data.empty:
        return "No OI data for Hero-Zero call."

    # Find the ATM strike price
    atm_strike = oi_data.iloc[(oi_data['strike'] - current_price).abs().argsort()[:1]]['strike'].iloc[0]

    # Filter data around ATM
    filtered_oi = oi_data[(oi_data['strike'] >= atm_strike - 500) & (oi_data['strike'] <= atm_strike + 500)]

    if filtered_oi.empty:
        return "No relevant OI data around ATM for Hero-Zero call."

    # Identify strikes with significant OI build-up/unwinding
    # Max CE OI (Resistance)
    max_ce_oi_strike = filtered_oi.loc[filtered_oi['ce_oi'].idxmax()]
    # Max PE OI (Support)
    max_pe_oi_strike = filtered_oi.loc[filtered_oi['pe_oi'].idxmax()]

    call_message = f"Hero-Zero Call for current price {current_price:.2f}:\n"
    call_message += f"  Max CE OI (Resistance): Strike {max_ce_oi_strike['strike']} (OI: {max_ce_oi_strike['ce_oi']})\n"
    call_message += f"  Max PE OI (Support): Strike {max_pe_oi_strike['strike']} (OI: {max_pe_oi_strike['pe_oi']})\n"

    # Simple Hero-Zero logic: Look for strikes where OI is changing significantly
    # This is a very basic example and needs refinement for actual trading.
    significant_change_ce = filtered_oi[filtered_oi['ce_change_oi'].abs() > 10000]
    significant_change_pe = filtered_oi[filtered_oi['pe_change_oi'].abs() > 10000]

    if not significant_change_ce.empty:
        call_message += "  Significant CE OI change at strikes: " + ", ".join(significant_change_ce['strike'].astype(str).tolist()) + "\n"
    if not significant_change_pe.empty:
        call_message += "  Significant PE OI change at strikes: " + ", ".join(significant_change_pe['strike'].astype(str).tolist()) + "\n"

    return call_message

if __name__ == '__main__':
    # Example usage
    # Note: nsepython might have rate limits or require specific headers.
    # This example assumes it works out of the box.
    nifty_oi_data = get_oi_data("NIFTY")
    if nifty_oi_data is not None:
        pcr = calculate_pcr(nifty_oi_data)
        trend = oi_trend_analysis(pcr)
        # For hero-zero call, we need a current price. Using a dummy for example.
        dummy_current_price = 22500
        hero_zero = hero_zero_call(nifty_oi_data, dummy_current_price)

        print(f"PCR: {pcr:.2f}")
        print(f"Trend: {trend}")
        print(hero_zero)
    else:
        print("Could not fetch NIFTY OI data.")
