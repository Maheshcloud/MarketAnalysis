# market_analysis_app/notifiers/telegram_notifier.py

import telegram

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

    def send_message(self, message):
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message)
            print(f"Telegram message sent: {message}")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

if __name__ == '__main__':
    # Example usage (requires .env file with credentials)
    import os
    from dotenv import load_dotenv

    load_dotenv()

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        notifier = TelegramNotifier(token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
        import asyncio
        asyncio.run(notifier.send_message("Hello from the Market Analysis App!"))
    else:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file.")
