# temp_get_token.py

import os
from dotenv import load_dotenv
from market_analysis_app.zerodha.zerodha_client import ZerodhaClient

load_dotenv()

ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
REQUEST_TOKEN = "KfUVhPNCVRxLEA8ghn2b7KaVG56hVRhG"

if ZERODHA_API_KEY and ZERODHA_API_SECRET:
    client = ZerodhaClient(api_key=ZERODHA_API_KEY, api_secret=ZERODHA_API_SECRET, access_token=None)
    new_access_token = client.set_access_token_from_request_token(REQUEST_TOKEN)
    if new_access_token:
        print(f"SUCCESS:{new_access_token}")
    else:
        print("ERROR:Failed to generate access token.")
else:
    print("ERROR:Zerodha API key or secret not found in .env file.")
