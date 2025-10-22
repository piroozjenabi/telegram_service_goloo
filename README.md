# Dynamic Telegram Bot Maker 🤖

High-performance Django-based platform for creating and managing multiple Telegram bots with JSON-based conversation flows.

## ✨ Features

- **Multi-Bot Management**: Create and manage unlimited Telegram bots from one platform
- **Bot Types with Factory Pattern**: 5 built-in bot types (Simple, Registration, Survey, Support, Custom)
- **Auto Webhook Setup**: Webhooks automatically configured when you save a bot
- **Webhook Architecture**: High-performance webhook-based message handling
- **Welcome Messages**: Configurable welcome messages for each bot
- **Phone Number Collection**: Built-in phone number request with keyboard button
- **User State Management**: Track user progress through flows
- **Flow-Based Conversations**: JSON-configured conversation flows with no coding required
- **User Analytics**: Track users, messages, and bot statistics in real-time
- **Modern Admin**: Beautiful Unfold admin interface for easy management
- **REST API**: Fast, type-safe API built with Django Ninja
- **Scalable**: Designed for high performance and easy scaling

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run migrations (already done)
python manage.py migrate

# 3. Create admin user
python manage.py createsuperuser

# 4. Start server
python manage.py runserver

# 5. Access admin panel
# Open: http://localhost:8000/admin
```

## 📋 Requirements

- Python 3.13+
- Django 5.2.7
- Django Ninja 1.4.5
- Django Unfold 0.68.0
- python-telegram-bot 22.5

All dependencies are managed via `uv` and defined in `pyproject.toml`.

## 🏗️ Architecture

### Models

1. **TelegramBot**: Bot configuration with UUID, token, statistics, and webhook settings
2. **BotUser**: Telegram user data with chat_id, profile info, and interaction history
3. **BotFlow**: JSON-based conversation flows with command triggers
4. **BotMessage**: Complete message history for analytics

### API Endpoints

```
POST   /api/bots                    - Create new bot
GET    /api/bots                    - List all bots
GET    /api/bots/{id}               - Get bot details
POST   /api/bots/{id}/webhook       - Setup webhook
DELETE /api/bots/{id}/webhook       - Remove webhook
GET    /api/bots/{id}/stats         - Get statistics
POST   /api/webhook/{bot_id}        - Webhook handler (Telegram)
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step setup guide
- **[AUTO_WEBHOOK_SETUP.md](AUTO_WEBHOOK_SETUP.md)**: Automatic webhook configuration
- **[ADMIN_WEBHOOK_ACTIONS.md](ADMIN_WEBHOOK_ACTIONS.md)**: Admin webhook management actions
- **[BOT_TYPES_GUIDE.md](BOT_TYPES_GUIDE.md)**: Guide to using different bot types
- **[Bot/FACTORY_PATTERN.md](Bot/FACTORY_PATTERN.md)**: Factory pattern architecture
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**: Complete architecture documentation
- **[Bot/README.md](Bot/README.md)**: Bot app specific documentation
- **[Bot/flow_examples.json](Bot/flow_examples.json)**: Flow configuration examples

## 🤖 Bot Types

The system includes 5 built-in bot types using the Factory Pattern:

1. **Simple Bot**: Basic echo bot with simple responses
2. **Registration Bot**: Multi-step user registration flow
3. **Survey Bot**: Conduct surveys with multiple questions
4. **Support Bot**: Customer support with ticket system
5. **Custom Bot**: Flow-based configuration for any use case

Each bot type can be configured with:
- Welcome message (optional)
- Phone number collection (optional)
- Custom text for each step

See [BOT_TYPES_GUIDE.md](BOT_TYPES_GUIDE.md) for detailed examples.

## 🎯 Usage Example

### 1. Create a Bot

**Via Admin Panel:**
1. Go to http://localhost:8000/admin
2. Add new Telegram Bot
3. Enter name and token from [@BotFather](https://t.me/botfather)

**Via API:**
```bash
curl -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{"name": "My Bot", "token": "YOUR_TOKEN"}'
```

### 2. Create a Flow

In admin panel, create a Bot Flow:

```json
{
  "response": "👋 Welcome! How can I help you today?"
}
```

Set trigger command: `/start`

### 3. Setup Webhook

```bash
# For local testing, use ngrok
ngrok http 8000

# Setup webhook
python manage.py setup_bot_webhook <bot_id> https://your-url.ngrok.io
```

### 4. Test Your Bot

Open Telegram, find your bot, send `/start` - it works! 🎉

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
BASE_URL=https://your-domain.com
```

### Database

Default: SQLite (development)
Production: PostgreSQL recommended

## 📊 Flow Configuration

### Simple Response
```json
{
  "response": "Hello World!"
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
      "text": "Nice to meet you!",
      "next": null
    }
  ],
  "initial_step": "step1"
}
```

See `Bot/flow_examples.json` for more examples.

## 🧪 Testing

```bash
# Run setup test
python test_setup.py

# Check for issues
python manage.py check

# Run Django shell
python manage.py shell
```

## 🚀 Production Deployment

1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Setup HTTPS (required for webhooks)
4. Use production ASGI server:
   ```bash
   uvicorn MAIN.asgi:application --host 0.0.0.0 --port 8000
   ```
5. Configure static files and media storage
6. Setup monitoring and logging

## 📈 Performance

- **Async/Await**: Non-blocking Telegram API calls
- **Webhook-Based**: No polling overhead
- **Database Indexing**: Optimized queries
- **Request Tracking**: Built-in analytics
- **Scalable Design**: Ready for horizontal scaling

## 🔒 Security

- UUID-based webhook URLs
- Token security
- CSRF protection
- Admin authentication
- User data privacy compliant

## 🛠️ Development

### Project Structure
```
telegram_service/
├── Bot/              # Main bot application
├── Core/             # Core utilities
├── MAIN/             # Django settings
├── manage.py         # Django CLI
└── pyproject.toml    # Dependencies
```

### Key Files
- `Bot/models.py`: Data models
- `Bot/views.py`: API endpoints
- `Bot/admin.py`: Admin configuration
- `MAIN/settings.py`: Django settings
- `MAIN/urls.py`: URL routing

## 📝 Management Commands

```bash
# Setup webhook for a bot
python manage.py setup_bot_webhook <bot_id> <webhook_url>

# Create superuser
python manage.py createsuperuser

# Make/apply migrations
python manage.py makemigrations
python manage.py migrate
```

## 🤝 Contributing

This is a production-ready template. Feel free to:
- Add new flow types
- Extend API endpoints
- Improve admin interface
- Add new features

## 📄 License

MIT License - feel free to use for any purpose.

## 🆘 Support

- Check documentation in `/docs` folder
- Review `QUICKSTART.md` for common issues
- Examine `Bot/flow_examples.json` for flow patterns

## 🎓 Learn More

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Ninja](https://django-ninja.rest-framework.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Django Unfold](https://unfoldadmin.com/)

---

Built with ❤️ using Django, Django Ninja, and python-telegram-bot
