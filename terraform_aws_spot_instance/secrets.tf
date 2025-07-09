resource "aws_secretsmanager_secret" "market_analysis_secrets" {
  name        = "market-analysis-app-secrets"
  description = "Secrets for the Market Analysis application"
}

resource "aws_secretsmanager_secret_version" "market_analysis_secret_version" {
  secret_id     = aws_secretsmanager_secret.market_analysis_secrets.id
  secret_string = jsonencode({
    "ZERODHA_API_KEY": "your_zerodha_api_key",
    "ZERODHA_API_SECRET": "your_zerodha_api_secret",
    "TELEGRAM_BOT_TOKEN": "your_telegram_bot_token",
    "TELEGRAM_CHAT_ID": "your_telegram_chat_id",
    "EMAIL_USERNAME": "your_email_username",
    "EMAIL_PASSWORD": "your_email_password"
    # Add any other sensitive variables from your .env file here
  })
}
