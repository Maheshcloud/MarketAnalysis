# market_analysis_app/zerodha/zerodha_client.py

from kiteconnect import KiteConnect

class ZerodhaClient:
    def __init__(self, api_key, api_secret, access_token):
        self.kite = KiteConnect(api_key=api_key)
        self.api_secret = api_secret
        self.access_token = access_token
        self.kite.set_access_token(access_token)

    def get_profile(self):
        """Fetches the user's profile."""
        try:
            return self.kite.profile()
        except Exception as e:
            print(f"Error fetching Zerodha profile: {e}")
            return None

    def get_login_url(self):
        """Generates a login URL for obtaining a new access token."""
        # This is a simplified approach. In a real application, you would
        # need a web server to handle the redirect and get the request token.
        # For this CLI application, we will print the login URL and the user
        # can manually generate the access token.
        return self.kite.login_url()

    def set_access_token_from_request_token(self, request_token):
        """Generates and sets a new access token from a request token."""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.kite.set_access_token(data["access_token"])
            print("New access token generated and set successfully.")
            return data["access_token"]
        except Exception as e:
            print(f"Error generating access token: {e}")
            return None

if __name__ == '__main__':
    # Example usage (requires .env file with credentials)
    import os
    from dotenv import load_dotenv

    load_dotenv()

    ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
    ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
    ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

    if ZERODHA_API_KEY and ZERODHA_API_SECRET:
        client = ZerodhaClient(api_key=ZERODHA_API_KEY, api_secret=ZERODHA_API_SECRET, access_token=ZERODHA_ACCESS_TOKEN)

        if ZERODHA_ACCESS_TOKEN:
            profile = client.get_profile()
            if profile:
                print(f"Successfully connected to Zerodha. Profile: {profile['user_name']}")
        else:
            print("Zerodha access token not found.")
            login_url = client.get_login_url()
            print(f"Please login to Zerodha using this URL: {login_url}")
            request_token = input("Enter the request token from the redirect URL: ")
            if request_token:
                new_access_token = client.set_access_token_from_request_token(request_token)
                if new_access_token:
                    print(f"New access token: {new_access_token}")
                    print("Please update your .env file with this new access token.")

    else:
        print("Please set ZERODHA_API_KEY and ZERODHA_API_SECRET in your .env file.")
