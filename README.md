# Clone & run your own bot

Requirements:

- Telegram account (Create a new one here https://telegram.org/)
- AWS account (Create a new one here https://aws.amazon.com/)
- OpenAI account (Create a new one here https://platform.openai.com/)
- Serverless Framework (Install it here https://www.serverless.com/framework/docs/getting-started/)
- Python 3.9+ (Install it here https://www.python.org/downloads/)
- Node.js 14+ (Install it here https://nodejs.org/en/download/)

1. Clone the repo
2. Create a new bot in Telegram (https://core.telegram.org/bots#how-do-i-create-a-bot)
3. Create new .env file in the root of the project and fill it:
   ```
   SERVICE_NAME=... (if you plan to monitor the service on serverless platform)
   TELEGRAM_BOT_NAME=... (from @BotFather)
   TELEGRAM_BOT_TOKEN=... (from @BotFather)
   SENTRY_DSN=... (if you plan to use Sentry.io)
   OPENAI_API_KEY=... (from https://openai.com/)
   ```
4. install plugin
   ```
   sls plugin install -n serverless-python-requirements
   ```
5. Deploy the bot
   ```
   sls deploy
   ```
   this will give you the endpoint- copy it
6. Go to the Telegram bot and set the webhook
   ```
   curl -F "url=https://<your-endpoint>" https://api.telegram.org/bot<your-token>/setWebhook
   ```
7. Go to the Telegram bot and start chatting with it


# How to contribute

1. Fork the repo
2. Create a new branch
3. Make changes
4. Create a PR
5. Wait for review
6. ...
7. Profit
