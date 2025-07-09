# main.py

import time
import datetime
from dotenv import load_dotenv
import os
import json
import logging
import asyncio

from market_analysis_app.config import SYMBOLS
from market_analysis_app.data.data_fetcher import get_data
from market_analysis_app.strategies import strategy1, strategy2, strategy3, strategy4, oi_strategy
from market_analysis_app.notifiers.telegram_notifier import TelegramNotifier
from market_analysis_app.zerodha.zerodha_client import ZerodhaClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

# Initialize notifier
notifier = None
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    notifier = TelegramNotifier(token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
else:
    logging.warning("Telegram notifier not initialized. Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file.")

# Initialize Zerodha client
zerodha_client = None
if ZERODHA_API_KEY and ZERODHA_API_SECRET:
    zerodha_client = ZerodhaClient(api_key=ZERODHA_API_KEY, api_secret=ZERODHA_API_SECRET, access_token=ZERODHA_ACCESS_TOKEN)
    if not ZERODHA_ACCESS_TOKEN:
        logging.info("Zerodha access token not found. Attempting to generate a new one.")
        login_url = zerodha_client.get_login_url()
        print(f"Please login to Zerodha using this URL: {login_url}")
        request_token = input("Enter the request token from the redirect URL: ")
        if request_token:
            new_access_token = zerodha_client.set_access_token_from_request_token(request_token)
            if new_access_token:
                logging.info(f"New access token: {new_access_token}")
                logging.info("Please update your .env file with this new access token and restart the application.")
                exit()
            else:
                logging.error("Failed to generate new access token. Exiting.")
                exit()
        else:
            logging.error("No request token provided. Exiting.")
            exit()
else:
    logging.warning("Zerodha client not initialized. Please set ZERODHA_API_KEY and ZERODHA_API_SECRET in your .env file.")

async def send_notification(message):
    """Sends a notification."""
    logging.info(f"NOTIFICATION: {message}")
    if notifier:
        await notifier.send_message(message)

def update_dashboard(data):
    """Updates the dashboard data by writing to a JSON file."""
    logging.info("Updating dashboard...")
    try:
        with open("dashboard_data.json", "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Error updating dashboard data: {e}")

def place_order(client, symbol, transaction_type, quantity, price, order_type, product_type, validity, trigger_price=None, squareoff=None):
    """Places an order on Zerodha."""
    order_details = {
        "symbol": symbol,
        "transaction_type": transaction_type,
        "quantity": quantity,
        "price": price,
        "order_type": order_type,
        "product_type": product_type,
        "validity": validity,
        "trigger_price": trigger_price,
        "squareoff": squareoff
    }
    logging.info(f"Attempting to place order: {order_details}")
    if client:
        try:
            order_id = client.kite.place_order(
                variety="regular",
                exchange="NFO", # For options
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                price=price,
                order_type=order_type,
                product=product_type,
                validity=validity,
                trigger_price=trigger_price,
                squareoff=squareoff
            )
            logging.info(f"Order placed successfully. Order ID: {order_id}")
            send_notification(f"Order placed: {symbol} {transaction_type} {quantity}. Order ID: {order_id}")
        except Exception as e:
            logging.error(f"Error placing order: {e}")
            send_notification(f"Error placing order for {symbol}: {e}")
    else:
        logging.warning("Zerodha client not initialized. Cannot place order.")
        send_notification("Zerodha client not initialized. Cannot place order.")

def is_expiry_day(date):
    """Checks if the given date is an expiry day (Thursday for Nifty/BankNifty)."""
    # This is a simplified check. Real expiry dates can vary due to holidays.
    return date.weekday() == 3 # Thursday

async def main():
    """Main function to run the market analysis app."""
    await send_notification("Market Analysis App started.")
    analysis_data = {}

    while True:
        try:
            # Check if within market hours (9:00 AM to 3:30 PM IST)
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))) # IST
            market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

            if market_open <= now <= market_close:
                logging.info(f"----- Running analysis at {now.strftime('%Y-%m-%d %H:%M:%S')} -----")
                analysis_data['last_run'] = now.strftime('%Y-%m-%d %H:%M:%S')
                analysis_data['signals'] = []
                analysis_data['oi_analysis'] = {}

                # --- Morning Notifications (9:10 AM) ---
                if now.hour == 9 and now.minute == 10:
                    for index_name, index_symbol in SYMBOLS['INDICES'].items():
                        try:
                            # Strategy 2: Previous day H/L breakout
                            prev_day_data = get_data(index_symbol, period='2d', interval='1d')
                            if prev_day_data is not None and len(prev_day_data) >= 2:
                                levels = strategy2.calculate_strategy2_levels(prev_day_data.iloc[-2])
                                notification = f"{index_name} Support/Resistance for the day: {levels}"
                                await send_notification(notification)
                                analysis_data['signals'].append(notification)
                        except Exception as e:
                            logging.error(f"Error in morning analysis for {index_name}: {e}")

                # --- Intraday Analysis ---
                for index_name, index_symbol in SYMBOLS['INDICES'].items():
                    try:
                        # Fetch 5m and 15m data
                        data_5m = get_data(index_symbol, interval='5m', period='1d')
                        data_15m = get_data(index_symbol, interval='15m', period='1d')

                        if data_5m is not None and not data_5m.empty:
                            # Strategy 1
                            s1_data = strategy1.strategy1(data_5m.copy())
                            last_signal_s1 = s1_data['signal'].iloc[-1]
                            if last_signal_s1 == 1:
                                notification = f"{index_name} (5m) - Strategy 1 Signal: BUY"
                                await send_notification(notification)
                                analysis_data['signals'].append(notification)
                                # Example order placement
                                place_order(zerodha_client, symbol="NIFTY25JULC22500", transaction_type="BUY", quantity=50, price=s1_data['entry_price'].iloc[-1], order_type="LIMIT", product_type="MIS", validity="DAY")
                            elif last_signal_s1 == -1:
                                notification = f"{index_name} (5m) - Strategy 1 Signal: SELL"
                                await send_notification(notification)
                                analysis_data['signals'].append(notification)
                                # Example order placement
                                place_order(zerodha_client, symbol="NIFTY25JULP22500", transaction_type="SELL", quantity=50, price=s1_data['entry_price'].iloc[-1], order_type="LIMIT", product_type="MIS", validity="DAY")

                        if data_15m is not None and not data_15m.empty:
                            # Strategy 3
                            s3_data = strategy3.strategy3(data_15m.copy())
                            last_signal_s3 = s3_data['signal'].iloc[-1]
                            if last_signal_s3 == 1:
                                notification = f"{index_name} (15m) - Strategy 3 Signal: BUY"
                                await send_notification(notification)
                                analysis_data['signals'].append(notification)
                                # Example order placement
                                place_order(zerodha_client, symbol="NIFTY25JULC22500", transaction_type="BUY", quantity=50, price=s3_data['entry_price'].iloc[-1], order_type="LIMIT", product_type="MIS", validity="DAY")
                            elif last_signal_s3 == -1:
                                notification = f"{index_name} (15m) - Strategy 3 Signal: SELL"
                                await send_notification(notification)
                                analysis_data['signals'].append(notification)
                                # Example order placement
                                place_order(zerodha_client, symbol="NIFTY25JULP22500", transaction_type="SELL", quantity=50, price=s3_data['entry_price'].iloc[-1], order_type="LIMIT", product_type="MIS", validity="DAY")

                        # --- OI Analysis ---
                        if index_name in ["NIFTY", "BANKNIFTY"]:
                            oi_data = oi_strategy.get_oi_data(index_name)
                            if oi_data is not None:
                                pcr = oi_strategy.calculate_pcr(oi_data)
                                trend = oi_strategy.oi_trend_analysis(pcr)
                                analysis_data['oi_analysis'][index_name] = {
                                    'pcr': pcr,
                                    'trend': trend
                                }
                                await send_notification(f"{index_name} OI Analysis: PCR={pcr:.2f}, Trend={trend}")

                                # Hero-Zero call on expiry day
                                if is_expiry_day(now.date()):
                                    # Get current price for Hero-Zero call
                                    current_price = data_5m['Close'].iloc[-1] if not data_5m.empty else None
                                    if current_price:
                                        hero_zero_msg = oi_strategy.hero_zero_call(oi_data, current_price)
                                        await send_notification(f"{index_name} Hero-Zero Call: {hero_zero_msg}")
                                        analysis_data['signals'].append(f"{index_name} Hero-Zero Call: {hero_zero_msg}")

                        # --- Strategy 4 (Pivot Points & Fibonacci) ---
                        # Fetch 1-day data for previous day's H/L/C to calculate levels
                        prev_day_data_s4 = get_data(index_symbol, period='2d', interval='1d')
                        if prev_day_data_s4 is not None and len(prev_day_data_s4) >= 2:
                            s4_levels = strategy4.calculate_strategy4_levels(prev_day_data_s4.iloc[-2])
                            current_price_s4 = data_5m['Close'].iloc[-1] if not data_5m.empty else None
                            if current_price_s4:
                                s4_signal = strategy4.strategy4_signal(current_price_s4, s4_levels)
                                if s4_signal != 0:
                                    notification = f"{index_name} (Current Price: {current_price_s4:.2f}) - Strategy 4 Signal: {'BUY (Near Support)' if s4_signal == 1 else 'SELL (Near Resistance)'}"
                                    await send_notification(notification)
                                    analysis_data['signals'].append(notification)
                                analysis_data['strategy4_levels'] = s4_levels

                    except Exception as e:
                        logging.error(f"Error in intraday analysis for {index_name}: {e}")

                # --- Afternoon Notifications (3:10 PM & 3:15 PM) ---
                if (now.hour == 15 and now.minute == 10) or (now.hour == 15 and now.minute == 15):
                    notification = "Please close all open positions."
                    await send_notification(notification)
                    analysis_data['signals'].append(notification)

                # --- Update Dashboard ---
                update_dashboard(analysis_data)

                # Sleep for 5 minutes before the next run
                time.sleep(300)
            else:
                logging.info(f"Outside market hours. Last check at {now.strftime('%Y-%m-%d %H:%M:%S')}. Sleeping for 15 minutes.")
                time.sleep(900)
        except Exception as e:
            logging.critical(f"Critical error in main loop: {e}")
            await send_notification(f"Critical error in Market Analysis App: {e}")
            time.sleep(60) # Sleep for a minute before retrying

if __name__ == "__main__":
    asyncio.run(main())
