# Dynamic Telegram Bot Maker

High-performance Django-based system for creating and managing multiple Telegram bots with flow-based conversation handling.

## Features

- **Multi-Bot Management**: Create and manage multiple Telegram bots from a single platform
- **Webhook Support**: Automatic webhook setup with unique UUID-based URLs
- **User Tracking**: Track bot users, interactions, and statistics
- **Flow-Based Conversations**: JSON-based flow configuration for bot logic
- **Message Analytics**: Store and analyze all bot messages
- **Django Ninja API**: Fast, type-safe REST API
- **Unfold Admin**: Modern, beautiful admin interface

## Models

### TelegramBot
Main bot configuration with:
- UUID-based identification
- Token management
- User and request counting
- Webhook configuration
- Activity status

### BotUser
Stores Telegram user data:
- Chat ID and user information
- Profile data (phone, bio, photo)
- Interaction timestamps
- Block status

### BotFlow
JSON-based conversation flows:
- Flow configuration as JSON
- Command triggers
- Default flow support
- Active/inactive status

### BotMessage
Message storage for analytics:
- Message type (text, photo, video, etc.)
- Direction (incoming/outgoing)
- Content and metadata
- Flow association

## API Endpoints

### Bot Management

**Create Bot**
```
POST /api/bots
{
  "name": "My Bot",
  "token": "YOUR_BOT_TOKEN"
}
```

**List Bots**
```
GET /api/bots
```

**Get Bot Details**
```
GET /api/bots/{bot_id}
```

**Setup Webhook**
```
POST /api/bots/{bot_id}/webhook
{
  "webhook_url": "https://yourdomain.com"
}
```

**Delete Webhook**
```
DELETE /api/bots/{bot_id}/webhook
```

**Get Bot Statistics**
```
GET /api/bots/{bot_id}/stats
```

### Webhook Handler

**Receive Updates**
```
POST /api/webhook/{bot_id}
```
This endpoint receives updates from Telegram automatically.

## Setup Instructions

1. **Install Dependencies**
```bash
uv sync
```

2. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Superuser**
```bash
python manage.py createsuperuser
```

4. **Run Server**
```bash
python manage.py runserver
```

5. **Access Admin Panel**
Navigate to `http://localhost:8000/admin`

## Creating a Bot

### Via Admin Panel
1. Go to Admin Panel
2. Click "Telegram Bots" → "Add"
3. Enter bot name and token
4. Save

### Via API
```bash
curl -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{"name": "My Bot", "token": "YOUR_BOT_TOKEN"}'
```

## Setting Up Webhook

### Via Management Command
```bash
python manage.py setup_bot_webhook <bot_id> https://yourdomain.com
```

### Via API
```bash
curl -X POST http://localhost:8000/api/bots/{bot_id}/webhook \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://yourdomain.com"}'
```

## Flow Configuration

Flows are stored as JSON in the `flow_data` field. See `flow_examples.json` for examples.

### Simple Response Flow
```json
{
  "response": "Hello! Welcome to our bot."
}
```

### Multi-Step Flow
```json
{
  "steps": [
    {
      "id": "step1",
      "type": "message",
      "text": "What's your name?",
      "next": "step2"
    },
    {
      "id": "step2",
      "type": "question",
      "text": "What's your email?",
      "save_to": "email",
      "next": null
    }
  ],
  "initial_step": "step1"
}
```

### Menu Flow
```json
{
  "type": "menu",
  "text": "Select an option:",
  "buttons": [
    {
      "text": "Option 1",
      "callback_data": "opt1",
      "response": "You selected Option 1"
    }
  ]
}
```

## Production Deployment

1. **Set Environment Variables**
```bash
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
```

2. **Use Production Database**
Update `DATABASES` in settings.py to use PostgreSQL

3. **Setup HTTPS**
Telegram webhooks require HTTPS

4. **Use Production Server**
```bash
uvicorn MAIN.asgi:application --host 0.0.0.0 --port 8000
```

## Performance Considerations

- Uses async/await for Telegram API calls
- Webhook-based (no polling)
- Indexed database queries
- Efficient message storage
- Request counting for analytics

## Security

- Bot tokens stored securely
- UUID-based webhook URLs
- CSRF protection
- Admin authentication required
- User data privacy compliant
