# Quick Start Guide - Dynamic Telegram Bot Maker

## 1. Initial Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (already done)
uv sync

# Migrations (already done)
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

## 2. Start the Server

```bash
python manage.py runserver
```

## 3. Create Your First Bot

### Option A: Via Admin Panel

1. Open browser: `http://localhost:8000/admin`
2. Login with superuser credentials
3. Click "Telegram Bots" → "Add Telegram Bot"
4. Fill in:
   - Name: "My First Bot"
   - Token: Get from [@BotFather](https://t.me/botfather)
5. Save

### Option B: Via API

```bash
curl -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Bot",
    "token": "YOUR_BOT_TOKEN_FROM_BOTFATHER"
  }'
```

## 4. Create Bot Flows

1. In Admin Panel, go to "Bot Flows" → "Add Bot Flow"
2. Select your bot
3. Name: "Welcome Flow"
4. Trigger Command: `/start`
5. Flow Data:
```json
{
  "response": "👋 Welcome! I'm your bot assistant.\n\nUse /help to see available commands."
}
```
6. Check "Is default" and "Is active"
7. Save

Create another flow for `/help`:
```json
{
  "response": "📋 Available Commands:\n\n/start - Start the bot\n/help - Show this help\n/info - Bot information"
}
```

## 5. Setup Webhook (For Production)

### Local Testing with ngrok

```bash
# Install ngrok
# Download from https://ngrok.com/

# Start ngrok
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Set Webhook

```bash
# Get your bot ID from admin panel or API
BOT_ID="your-bot-uuid-here"
WEBHOOK_URL="https://abc123.ngrok.io"

# Setup webhook
python manage.py setup_bot_webhook $BOT_ID $WEBHOOK_URL
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/bots/$BOT_ID/webhook \
  -H "Content-Type: application/json" \
  -d "{\"webhook_url\": \"$WEBHOOK_URL\"}"
```

## 6. Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Bot should respond with welcome message!

## 7. Monitor Activity

### Via Admin Panel
- View "Bot Users" to see all users
- View "Bot Messages" to see message history
- Check bot statistics in "Telegram Bots"

### Via API
```bash
curl http://localhost:8000/api/bots/$BOT_ID/stats
```

## Common Commands

```bash
# Create superuser
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run development server
python manage.py runserver

# Setup webhook
python manage.py setup_bot_webhook <bot_id> <webhook_url>

# Shell access
python manage.py shell
```

## API Endpoints Reference

```bash
# List all bots
GET http://localhost:8000/api/bots

# Get bot details
GET http://localhost:8000/api/bots/{bot_id}

# Create bot
POST http://localhost:8000/api/bots

# Setup webhook
POST http://localhost:8000/api/bots/{bot_id}/webhook

# Delete webhook
DELETE http://localhost:8000/api/bots/{bot_id}/webhook

# Get statistics
GET http://localhost:8000/api/bots/{bot_id}/stats

# Webhook endpoint (used by Telegram)
POST http://localhost:8000/api/webhook/{bot_id}
```

## Troubleshooting

### Bot not responding
1. Check webhook is set: Admin Panel → Telegram Bots → Check "Is webhook set"
2. Verify webhook URL is accessible (HTTPS required)
3. Check bot token is correct
4. View logs for errors

### Webhook setup fails
1. Ensure URL is HTTPS (use ngrok for local testing)
2. Verify bot token is valid
3. Check internet connectivity

### Messages not saving
1. Check database connection
2. Verify migrations are applied
3. Check server logs for errors

## Next Steps

1. **Create Advanced Flows**: Use multi-step flows with questions and menus
2. **Add Custom Logic**: Extend `process_bot_flow()` in `Bot/views.py`
3. **Setup Production**: Deploy to a server with HTTPS
4. **Add Features**: Implement inline keyboards, file handling, etc.
5. **Monitor Performance**: Track user engagement and bot statistics

## Example Flow Configurations

See `Bot/flow_examples.json` for more complex flow examples including:
- Multi-step registration flows
- Menu-based navigation
- Question and answer flows
- Conditional logic flows
