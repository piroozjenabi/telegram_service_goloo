# Factory Pattern - Bot Service Architecture

## Overview

The bot system uses the **Factory Design Pattern** to handle different bot types with specialized behaviors. Each bot type has its own service class that handles message processing according to its specific requirements.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Incoming Message                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BotServiceFactory                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  create_service(bot, bot_user, telegram_client)      │  │
│  │  - Checks bot.bot_type                               │  │
│  │  - Returns appropriate service instance              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┬────────────┐
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Simple   │  │Registration│ │ Survey   │  │ Support  │  │ Custom   │
│ Bot      │  │   Bot      │ │  Bot     │  │  Bot     │  │  Bot     │
│ Service  │  │  Service   │ │ Service  │  │ Service  │  │ Service  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Bot Types

### 1. Simple Bot (`simple`)
Basic bot with simple echo responses.

**Use Cases:**
- Testing
- Simple Q&A
- Echo bots

**Features:**
- Welcome message support
- Phone number collection
- Simple text responses

### 2. Registration Bot (`registration`)
Handles user registration with multi-step flow.

**Use Cases:**
- User onboarding
- Account creation
- Data collection

**Features:**
- Welcome message
- Phone number collection
- Name collection
- Registration completion

**Flow:**
```
/start → Welcome → Request Phone → Complete Registration
```

### 3. Survey Bot (`survey`)
Conducts surveys with multiple questions.

**Use Cases:**
- Customer feedback
- Market research
- Satisfaction surveys

**Features:**
- Multi-question flow
- Answer storage in state_data
- Results summary

**Flow:**
```
/start → Welcome → Phone (optional) → Q1 → Q2 → Q3 → Results
```

### 4. Support Bot (`support`)
Customer support ticket system.

**Use Cases:**
- Customer support
- Help desk
- Issue tracking

**Features:**
- Support menu
- Ticket creation
- Ticket status checking
- FAQ
- Contact information

**Flow:**
```
/start → Welcome → Phone (optional) → Menu → Create Ticket/Check Status/FAQ
```

### 5. Custom Bot (`custom`)
Uses BotFlow configurations for flexible behavior.

**Use Cases:**
- Complex custom flows
- E-commerce
- Any custom logic

**Features:**
- Flow-based configuration
- Command triggers
- Multi-step flows
- Menu flows

## Bot Configuration

### TelegramBot Model Fields

```python
# Bot Type
bot_type = 'simple' | 'registration' | 'survey' | 'support' | 'custom'

# Welcome Message
has_welcome_message = True/False
welcome_message_text = "Welcome to our bot! 👋"

# Phone Number Collection
has_get_number = True/False
get_number_text = "Please share your phone number to continue."
```

### Example Configuration

**Simple Bot:**
```python
bot = TelegramBot.objects.create(
    name="Echo Bot",
    token="YOUR_TOKEN",
    bot_type="simple",
    has_welcome_message=True,
    welcome_message_text="Hello! I'll echo your messages.",
    has_get_number=False
)
```

**Registration Bot:**
```python
bot = TelegramBot.objects.create(
    name="Registration Bot",
    token="YOUR_TOKEN",
    bot_type="registration",
    has_welcome_message=True,
    welcome_message_text="Welcome! Let's get you registered.",
    has_get_number=True,
    get_number_text="Please share your phone number for verification."
)
```

**Survey Bot:**
```python
bot = TelegramBot.objects.create(
    name="Feedback Bot",
    token="YOUR_TOKEN",
    bot_type="survey",
    has_welcome_message=True,
    welcome_message_text="Thank you for taking our survey!",
    has_get_number=True
)
```

## User State Management

### BotUser States

```python
USER_STATE_CHOICES = [
    ('new', 'New User'),
    ('welcomed', 'Welcomed'),
    ('awaiting_phone', 'Awaiting Phone Number'),
    ('registered', 'Registered'),
    ('active', 'Active'),
    ('blocked', 'Blocked'),
]
```

### State Flow Example

```
new → welcomed → awaiting_phone → registered
```

### State Data

The `state_data` JSON field stores additional information:

```python
# Survey responses
state_data = {
    'q1_satisfaction': '5',
    'q2_recommend': 'Yes',
    'q3_comments': 'Great service!'
}

# Support tickets
state_data = {
    'tickets': [
        {
            'id': 'TKT-123',
            'description': 'Issue description',
            'status': 'open'
        }
    ]
}

# Multi-step flow
state_data = {
    'current_step': 'step2',
    'name': 'John Doe',
    'email': 'john@example.com'
}
```

## Creating Custom Bot Services

### Step 1: Create Service Class

```python
# Bot/services/my_custom_bot.py
from .base import BaseBotService
from typing import Dict, Any

class MyCustomBotService(BaseBotService):
    """My custom bot implementation"""
    
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle text messages"""
        # Your custom logic here
        await self.send_message(f"Custom response: {text}")
```

### Step 2: Register with Factory

```python
# In your app initialization or settings
from Bot.services.factory import BotServiceFactory
from Bot.services.my_custom_bot import MyCustomBotService

BotServiceFactory.register_service('my_custom', MyCustomBotService)
```

### Step 3: Add to Model Choices

```python
# Bot/models.py
BOT_TYPE_CHOICES = [
    # ... existing choices
    ('my_custom', 'My Custom Bot'),
]
```

## Base Service Methods

All bot services inherit from `BaseBotService`:

### Core Methods

```python
# Handle incoming message
async def handle_message(message_data: Dict) -> None

# Handle commands
async def handle_command(command: str, message_data: Dict) -> None
async def handle_start(message_data: Dict) -> None
async def handle_help(message_data: Dict) -> None

# Handle text (must be implemented by subclass)
async def handle_text(text: str, message_data: Dict) -> None

# Phone number handling
async def request_phone_number() -> None
async def handle_contact(contact_data: Dict) -> None
async def after_phone_number_received() -> None

# Utility methods
async def send_message(text: str, **kwargs) -> None
```

## Message Flow

### 1. Message Received
```
Telegram → Webhook → process_telegram_update()
```

### 2. User Management
```
Get/Create BotUser → Update user info → Save message
```

### 3. Service Creation
```
BotServiceFactory.create_service(bot, bot_user, telegram_client)
```

### 4. Message Handling
```
if contact:
    service.handle_contact()
else:
    service.handle_message()
        ↓
    if command:
        service.handle_command()
    else:
        service.handle_text()
```

## Testing Bot Types

### Via Admin Panel

1. Create bot
2. Set `bot_type` to desired type
3. Configure welcome message and phone collection
4. Save and setup webhook
5. Test in Telegram

### Via API

```python
import requests

# Create registration bot
response = requests.post('http://localhost:8000/api/bots', json={
    'name': 'Registration Bot',
    'token': 'YOUR_TOKEN'
})

bot_id = response.json()['id']

# Update bot type via admin panel
# (API endpoint for updating bot type can be added)
```

## Best Practices

1. **State Management**: Always update user_state appropriately
2. **Error Handling**: Wrap async operations in try-except
3. **User Feedback**: Provide clear messages at each step
4. **Data Validation**: Validate user input before saving
5. **Logging**: Log important events for debugging

## Example: Complete Registration Flow

```python
# User sends /start
→ handle_start()
  → Send welcome message
  → Set state to 'welcomed'
  → If has_get_number: request_phone_number()

# User shares phone
→ handle_contact()
  → Save phone number
  → Set state to 'registered'
  → after_phone_number_received()
    → complete_registration()

# User sends message
→ handle_text()
  → Check state
  → Process based on state
  → Update state if needed
```

## Extending the System

### Add New Bot Type

1. Create service class in `Bot/services/`
2. Inherit from `BaseBotService`
3. Implement `handle_text()` method
4. Register with factory
5. Add to `BOT_TYPE_CHOICES`
6. Create migrations
7. Document behavior

### Add New Features

1. Add fields to models if needed
2. Update service base class
3. Implement in specific services
4. Update admin interface
5. Create migrations
6. Update documentation

## Troubleshooting

### Bot not responding
- Check bot_type is set correctly
- Verify service is registered in factory
- Check logs for errors
- Verify webhook is set

### State not updating
- Check user_state is being saved
- Verify state_data is valid JSON
- Check for race conditions

### Phone number not collected
- Verify has_get_number is True
- Check get_number_text is set
- Verify keyboard is showing in Telegram

## Performance Considerations

- Services are created per message (stateless)
- State stored in database (BotUser model)
- Async operations for Telegram API
- Factory pattern adds minimal overhead
- Consider caching for high-traffic bots
