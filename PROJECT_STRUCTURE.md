# Project Structure - Dynamic Telegram Bot Maker

## Overview
High-performance Django application for creating and managing multiple Telegram bots with JSON-based flow configuration.

## Technology Stack
- **Django 5.2.7**: Web framework
- **Django Ninja 1.4.5**: Fast, type-safe REST API
- **Django Unfold 0.68.0**: Modern admin interface
- **python-telegram-bot 22.5**: Telegram Bot API wrapper
- **SQLite/PostgreSQL**: Database
- **Uvicorn**: ASGI server

## Directory Structure

```
telegram_service/
├── Bot/                          # Main bot application
│   ├── migrations/               # Database migrations
│   ├── management/               # Management commands
│   │   └── commands/
│   │       └── setup_bot_webhook.py
│   ├── models.py                 # Data models
│   ├── views.py                  # API endpoints
│   ├── admin.py                  # Admin configuration
│   ├── flow_examples.json        # Example flow configurations
│   └── README.md                 # Bot app documentation
├── Core/                         # Core application (future use)
├── MAIN/                         # Django project settings
│   ├── settings.py               # Project settings
│   ├── urls.py                   # URL routing
│   ├── asgi.py                   # ASGI config
│   └── wsgi.py                   # WSGI config
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── manage.py                     # Django management script
├── pyproject.toml                # Project dependencies
├── QUICKSTART.md                 # Quick start guide
├── PROJECT_STRUCTURE.md          # This file
└── test_setup.py                 # Setup verification script
```

## Data Models

### TelegramBot
**Purpose**: Store bot configuration and statistics

**Fields**:
- `id` (UUID): Unique identifier
- `name` (str): Bot display name
- `token` (str): Telegram bot token
- `username` (str): Bot username
- `user_count` (int): Total users
- `request_count` (int): Total requests
- `is_webhook_set` (bool): Webhook status
- `webhook_url` (str): Webhook URL
- `is_active` (bool): Bot status
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relations**:
- One-to-Many with BotUser
- One-to-Many with BotFlow
- One-to-Many with BotMessage

### BotUser
**Purpose**: Store Telegram user information

**Fields**:
- `bot` (FK): Associated bot
- `chat_id` (int): Telegram chat ID
- `username` (str): Telegram username
- `first_name` (str): User first name
- `last_name` (str): User last name
- `language_code` (str): User language
- `phone_number` (str): Phone number
- `bio` (text): User bio
- `profile_photo` (url): Profile photo URL
- `is_blocked` (bool): Block status
- `is_active` (bool): Active status
- `first_interaction` (datetime): First message
- `last_interaction` (datetime): Last message

**Unique Constraint**: (bot, chat_id)

### BotFlow
**Purpose**: Define conversation flows

**Fields**:
- `bot` (FK): Associated bot
- `name` (str): Flow name
- `description` (text): Flow description
- `flow_data` (JSON): Flow configuration
- `is_default` (bool): Default flow flag
- `is_active` (bool): Active status
- `trigger_command` (str): Command trigger
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

**Flow Data Structure**: See flow_examples.json

### BotMessage
**Purpose**: Store message history

**Fields**:
- `bot` (FK): Associated bot
- `user` (FK): Associated user
- `message_type` (choice): Message type
- `direction` (choice): incoming/outgoing
- `text` (text): Message text
- `file_url` (url): File URL
- `telegram_message_id` (int): Telegram message ID
- `flow` (FK): Associated flow
- `created_at` (datetime): Timestamp

**Message Types**: text, photo, video, document, audio, voice, sticker, location, contact

## API Endpoints

### Bot Management
- `POST /api/bots` - Create bot
- `GET /api/bots` - List bots
- `GET /api/bots/{id}` - Get bot details
- `POST /api/bots/{id}/webhook` - Setup webhook
- `DELETE /api/bots/{id}/webhook` - Remove webhook
- `GET /api/bots/{id}/stats` - Get statistics

### Webhook Handler
- `POST /api/webhook/{bot_id}` - Receive Telegram updates

## Flow System

### Flow Types

1. **Simple Response**
```json
{
  "response": "Hello World"
}
```

2. **Multi-Step Flow**
```json
{
  "steps": [...],
  "initial_step": "step1"
}
```

3. **Menu Flow**
```json
{
  "type": "menu",
  "text": "Select option",
  "buttons": [...]
}
```

### Flow Processing
1. Incoming message received via webhook
2. User identified/created in database
3. Flow matched by command or default
4. Flow executed based on flow_data
5. Response sent to user
6. Message logged to database

## Admin Interface

### Features
- Modern Unfold UI
- Bot management
- User tracking
- Flow configuration
- Message history
- Statistics dashboard

### Access
- URL: `/admin/`
- Requires superuser account

## Webhook System

### How It Works
1. Bot created with unique UUID
2. Webhook URL: `{BASE_URL}/api/webhook/{UUID}`
3. Telegram sends updates to webhook
4. System processes update asynchronously
5. Response sent back to user

### Requirements
- HTTPS (required by Telegram)
- Public URL (use ngrok for local testing)
- Fast response time (<5 seconds)

## Performance Features

- **Async Processing**: Uses async/await for Telegram API
- **Webhook-Based**: No polling overhead
- **Database Indexing**: Optimized queries
- **Request Counting**: Built-in analytics
- **Efficient Storage**: Minimal data duplication

## Security Features

- Token encryption (recommended for production)
- UUID-based webhook URLs
- CSRF protection
- Admin authentication
- User data privacy

## Scalability

### Current Setup
- SQLite database
- Single server
- Suitable for: 1-10 bots, <1000 users each

### Production Recommendations
- PostgreSQL database
- Redis for caching
- Celery for background tasks
- Load balancer for multiple instances
- CDN for media files

## Development Workflow

1. **Create Bot**: Via admin or API
2. **Configure Flows**: Add flows in admin
3. **Setup Webhook**: Use management command or API
4. **Test**: Send messages to bot
5. **Monitor**: Check admin for statistics
6. **Iterate**: Update flows as needed

## Testing

### Local Testing
```bash
# Run test script
python test_setup.py

# Start server
python manage.py runserver

# Use ngrok for webhook
ngrok http 8000
```

### Production Testing
- Use staging environment
- Test webhook connectivity
- Monitor error logs
- Check response times
- Verify message delivery

## Deployment Checklist

- [ ] Set DEBUG=False
- [ ] Configure SECRET_KEY
- [ ] Setup PostgreSQL
- [ ] Configure ALLOWED_HOSTS
- [ ] Setup HTTPS
- [ ] Configure static files
- [ ] Setup logging
- [ ] Configure backup
- [ ] Setup monitoring
- [ ] Test webhooks

## Future Enhancements

- [ ] Inline keyboard support
- [ ] File upload handling
- [ ] Advanced flow logic (conditions, loops)
- [ ] Flow visual editor
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Template system
- [ ] Broadcast messaging
- [ ] User segmentation
- [ ] A/B testing

## Support & Documentation

- Bot App README: `Bot/README.md`
- Quick Start: `QUICKSTART.md`
- Flow Examples: `Bot/flow_examples.json`
- Django Docs: https://docs.djangoproject.com/
- Django Ninja: https://django-ninja.rest-framework.com/
- Telegram Bot API: https://core.telegram.org/bots/api
