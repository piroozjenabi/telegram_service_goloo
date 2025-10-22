# Quick Reference Card

## Bot Types

| Type | Use Case | Key Features |
|------|----------|--------------|
| `simple` | Testing, Echo | Basic responses |
| `registration` | User onboarding | Multi-step registration |
| `survey` | Feedback collection | Multiple questions |
| `support` | Customer service | Ticket system, FAQ |
| `custom` | Any use case | Flow-based config |

## Bot Configuration Fields

```python
# Required
name = "My Bot"
token = "123456:ABC..."
bot_type = "simple"  # or registration, survey, support, custom

# Optional
has_welcome_message = True
welcome_message_text = "Welcome! 👋"
has_get_number = True
get_number_text = "Please share your phone number."
auto_setup_webhook = True  # Automatically setup webhook on save
```

## Auto Webhook Setup

Webhooks are automatically configured when you save a bot!

**Requirements:**
- Set `BASE_URL` in `.env` or `settings.py`
- Enable `auto_setup_webhook` (default: True)
- Bot must be active

**Configuration:**
```env
# .env
BASE_URL=https://your-domain.com
```

**For local testing:**
```bash
ngrok http 8000
# Copy HTTPS URL to BASE_URL
```

## User States

```
new → welcomed → awaiting_phone → registered → active
```

Custom states: `survey_q1`, `support_menu`, `creating_ticket`, etc.

## Common Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver

# Setup webhook
python manage.py setup_bot_webhook <bot_id> <webhook_url>

# Check for issues
python manage.py check
```

## API Endpoints

```
POST   /api/bots                    # Create bot
GET    /api/bots                    # List bots
GET    /api/bots/{id}               # Get bot
POST   /api/bots/{id}/webhook       # Setup webhook
DELETE /api/bots/{id}/webhook       # Remove webhook
GET    /api/bots/{id}/stats         # Get stats
POST   /api/webhook/{bot_id}        # Webhook handler
```

## Service Methods

```python
# In any bot service
await self.send_message("Hello!")
await self.request_phone_number()
await self.handle_contact(contact_data)

# Update state
self.bot_user.user_state = 'registered'
self.bot_user.save()

# Store data
self.bot_user.state_data = {'key': 'value'}
self.bot_user.save()
```

## Creating Custom Bot Type

```python
# 1. Create service
from Bot.services.base import BaseBotService

class MyBotService(BaseBotService):
    async def handle_text(self, text, message_data):
        await self.send_message(f"You said: {text}")

# 2. Register
from Bot.services.factory import BotServiceFactory
BotServiceFactory.register_service('my_type', MyBotService)

# 3. Add to choices in models.py
BOT_TYPE_CHOICES = [
    # ...
    ('my_type', 'My Bot Type'),
]

# 4. Migrate
python manage.py makemigrations
python manage.py migrate
```

## Flow Data Examples

### Simple Response
```json
{
  "response": "Hello World!"
}
```

### Multi-Step
```json
{
  "steps": [
    {"id": "step1", "type": "message", "text": "Question?", "next": "step2"},
    {"id": "step2", "type": "question", "text": "Thanks!", "next": null}
  ],
  "initial_step": "step1"
}
```

### Menu
```json
{
  "type": "menu",
  "text": "Choose:",
  "buttons": [
    {"text": "Option 1", "callback_data": "opt1", "response": "You chose 1"}
  ]
}
```

## Testing Locally

```bash
# 1. Start ngrok
ngrok http 8000

# 2. Copy HTTPS URL
# Example: https://abc123.ngrok.io

# 3. Setup webhook
python manage.py setup_bot_webhook <bot_id> https://abc123.ngrok.io

# 4. Test in Telegram
# Search for your bot
# Send /start
```

## Admin Panel

```
URL: http://localhost:8000/admin

Sections:
- Telegram Bots: Create/manage bots
- Bot Users: View users and states
- Bot Flows: Configure custom flows
- Bot Messages: View message history
```

## Admin Actions

**Webhook Management:**
- 🔗 Setup Webhook - Set webhook for selected bots
- ℹ️ Check Webhook Info - Get detailed webhook status from Telegram
- 🗑️ Delete Webhook - Remove webhook for selected bots

**Usage:**
1. Select bots (checkbox)
2. Choose action from dropdown
3. Click "Go"
4. View Telegram's response

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check webhook is set, verify token |
| Phone not collected | Enable `has_get_number`, check button shows |
| Wrong behavior | Verify `bot_type` in admin |
| State not updating | Check `user_state` is being saved |
| Webhook fails | Ensure HTTPS, check URL is accessible |

## File Structure

```
Bot/
├── models.py           # TelegramBot, BotUser, BotFlow, BotMessage
├── views.py            # API endpoints, webhook handler
├── admin.py            # Admin configuration
├── services/
│   ├── base.py         # BaseBotService
│   ├── factory.py      # BotServiceFactory
│   ├── simple_bot.py
│   ├── registration_bot.py
│   ├── survey_bot.py
│   ├── support_bot.py
│   └── custom_bot.py
└── management/
    └── commands/
        └── setup_bot_webhook.py
```

## Documentation

- `README.md` - Main overview
- `QUICKSTART.md` - Setup guide
- `BOT_TYPES_GUIDE.md` - Bot types usage
- `Bot/FACTORY_PATTERN.md` - Technical details
- `COMPLETE_SYSTEM_DIAGRAM.md` - Architecture
- `QUICK_REFERENCE.md` - This file

## Example: Create Registration Bot

```python
# Via Django shell
from Bot.models import TelegramBot

bot = TelegramBot.objects.create(
    name="Registration Bot",
    token="YOUR_BOT_TOKEN",
    bot_type="registration",
    has_welcome_message=True,
    welcome_message_text="Welcome! Let's get you registered.",
    has_get_number=True,
    get_number_text="Please share your phone number."
)

print(f"Bot created: {bot.id}")
```

## State Data Examples

```python
# Survey responses
{
    'q1_satisfaction': '5',
    'q2_recommend': 'Yes',
    'q3_comments': 'Great!'
}

# Support tickets
{
    'tickets': [
        {'id': 'TKT-123', 'description': '...', 'status': 'open'}
    ]
}

# Multi-step flow
{
    'current_step': 'step2',
    'collected_data': {'name': 'John', 'email': 'john@example.com'}
}
```

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `SECRET_KEY`
- [ ] Setup PostgreSQL
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup HTTPS
- [ ] Configure static files
- [ ] Setup logging
- [ ] Configure backups
- [ ] Test webhooks
- [ ] Monitor errors

## Support

For issues or questions:
1. Check documentation files
2. Review `Bot/FACTORY_PATTERN.md` for technical details
3. Check `BOT_TYPES_GUIDE.md` for examples
4. Review admin panel for configuration

---

**Quick Start:** Create admin user → Start server → Create bot in admin → Setup webhook → Test in Telegram!
