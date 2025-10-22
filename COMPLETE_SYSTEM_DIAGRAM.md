# Complete System Architecture with Factory Pattern

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT MAKER SYSTEM                         │
│                     with Factory Pattern                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Telegram   │         │   Admin UI   │         │  REST API    │
│   Platform   │         │   (Unfold)   │         │(Django Ninja)│
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ Webhooks               │ Bot Management         │ HTTP
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DJANGO APPLICATION                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Webhook Handler (views.py)                    │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │  process_telegram_update()                               │  │ │
│  │  │  - Extract user data                                     │  │ │
│  │  │  - Get/Create BotUser                                    │  │ │
│  │  │  - Save incoming message                                 │  │ │
│  │  │  - Create Telegram client                                │  │ │
│  │  └────────────────────┬─────────────────────────────────────┘  │ │
│  │                       │                                         │ │
│  │                       ▼                                         │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │         BotServiceFactory.create_service()               │  │ │
│  │  │         - Check bot.bot_type                             │  │ │
│  │  │         - Return appropriate service instance            │  │ │
│  │  └────────────────────┬─────────────────────────────────────┘  │ │
│  └───────────────────────┼──────────────────────────────────────────┘ │
│                          │                                            │
│         ┌────────────────┼────────────────┬────────────┬────────────┐
│         │                │                │            │            │
│         ▼                ▼                ▼            ▼            ▼
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │ Simple   │    │Registration│   │ Survey   │  │ Support  │  │ Custom   │
│  │ Bot      │    │   Bot      │   │  Bot     │  │  Bot     │  │  Bot     │
│  │ Service  │    │  Service   │   │ Service  │  │ Service  │  │ Service  │
│  └────┬─────┘    └────┬───────┘   └────┬─────┘  └────┬─────┘  └────┬─────┘
│       │               │                │             │             │
│       └───────────────┴────────────────┴─────────────┴─────────────┘
│                                  │
│                                  ▼
│  ┌────────────────────────────────────────────────────────────────┐
│  │                    BaseBotService                               │
│  │  - handle_message()                                            │
│  │  - handle_command()                                            │
│  │  - handle_start() → Send welcome, request phone               │
│  │  - handle_contact() → Save phone number                       │
│  │  - request_phone_number() → Show keyboard button              │
│  │  - send_message()                                              │
│  └────────────────────────────────────────────────────────────────┘
│                                  │
│                                  ▼
│  ┌────────────────────────────────────────────────────────────────┐
│  │                    Database Models                              │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  │ TelegramBot  │  │   BotUser    │  │  BotFlow     │        │
│  │  │              │  │              │  │              │        │
│  │  │ + bot_type   │  │ + user_state │  │ + flow_data  │        │
│  │  │ + has_welcome│  │ + state_data │  │ + trigger_cmd│        │
│  │  │ + has_get_num│  │              │  │              │        │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │
│  └────────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────┘
```

## Bot Type Flow Diagrams

### Simple Bot Flow
```
User: /start
    ↓
SimpleBotService.handle_start()
    ↓
Send welcome_message_text (if has_welcome_message)
    ↓
Request phone (if has_get_number)
    ↓
User: [message]
    ↓
SimpleBotService.handle_text()
    ↓
Echo message back
```

### Registration Bot Flow
```
User: /start
    ↓
RegistrationBotService.handle_start()
    ↓
Send welcome_message_text
Set state: 'welcomed'
    ↓
Request phone (if has_get_number)
Set state: 'awaiting_phone'
    ↓
User: [shares phone]
    ↓
handle_contact()
Save phone_number
Set state: 'registered'
    ↓
complete_registration()
Show summary
```

### Survey Bot Flow
```
User: /start
    ↓
SurveyBotService.handle_start()
    ↓
Send welcome_message_text
    ↓
Request phone (if has_get_number)
    ↓
User: [shares phone]
    ↓
ask_question_1()
Set state: 'survey_q1'
    ↓
User: [answer 1]
    ↓
Save to state_data['q1_satisfaction']
ask_question_2()
Set state: 'survey_q2'
    ↓
User: [answer 2]
    ↓
Save to state_data['q2_recommend']
ask_question_3()
Set state: 'survey_q3'
    ↓
User: [answer 3]
    ↓
Save to state_data['q3_comments']
Set state: 'registered'
show_survey_results()
```

### Support Bot Flow
```
User: /start
    ↓
SupportBotService.handle_start()
    ↓
Send welcome_message_text
    ↓
Request phone (if has_get_number)
    ↓
User: [shares phone]
    ↓
show_support_menu()
Set state: 'support_menu'
    ↓
User: 1 (Create ticket)
    ↓
Set state: 'creating_ticket'
Ask for issue description
    ↓
User: [describes issue]
    ↓
create_support_ticket()
Save to state_data['tickets']
Set state: 'registered'
Show ticket ID
```

### Custom Bot Flow
```
User: /start
    ↓
CustomBotService.handle_start()
    ↓
Send welcome_message_text
    ↓
Request phone (if has_get_number)
    ↓
User: /command
    ↓
Find BotFlow with trigger_command
    ↓
execute_flow()
    ↓
If simple response:
    Send flow_data['response']
    ↓
If multi-step:
    Execute steps based on state_data['current_step']
    ↓
If menu:
    Show menu options
```

## State Management

### User States
```
┌─────────┐
│   new   │ → First interaction
└────┬────┘
     │ /start
     ▼
┌─────────┐
│welcomed │ → Welcome message sent
└────┬────┘
     │ if has_get_number
     ▼
┌──────────────┐
│awaiting_phone│ → Waiting for phone number
└──────┬───────┘
       │ [shares phone]
       ▼
┌──────────┐
│registered│ → Registration complete
└────┬─────┘
     │
     ▼
┌────────┐
│ active │ → Normal operation
└────────┘
```

### Custom States (Survey Example)
```
welcomed → survey_q1 → survey_q2 → survey_q3 → registered
```

### Custom States (Support Example)
```
welcomed → support_menu → creating_ticket → registered
```

## Data Flow

### Message Processing
```
1. Telegram sends webhook
   POST /api/webhook/{bot_id}
   
2. Extract message data
   - user info
   - message type
   - text/file
   
3. Get/Create BotUser
   - Update user info
   - Increment user_count if new
   
4. Save BotMessage
   - direction: incoming
   - message_type
   - text/file_url
   
5. Create service via Factory
   service = BotServiceFactory.create_service(bot, bot_user, client)
   
6. Handle message
   if contact:
       service.handle_contact()
   else:
       service.handle_message()
           ↓
       if command:
           service.handle_command()
       else:
           service.handle_text()
   
7. Service processes based on:
   - bot.bot_type
   - bot_user.user_state
   - bot_user.state_data
   
8. Service sends response
   - Updates user_state
   - Updates state_data
   - Sends message to Telegram
   
9. Save outgoing message
   - direction: outgoing
   - text
```

## Configuration Flow

### Bot Creation
```
Admin/API
    ↓
Create TelegramBot
    ├─ name
    ├─ token
    ├─ bot_type ← Choose behavior
    ├─ has_welcome_message
    ├─ welcome_message_text
    ├─ has_get_number
    └─ get_number_text
    ↓
Fetch username from Telegram
    ↓
Save to database
    ↓
Setup webhook
    ↓
Bot ready!
```

### Flow Creation (Custom Bot)
```
Admin Panel
    ↓
Create BotFlow
    ├─ bot (select)
    ├─ name
    ├─ trigger_command
    ├─ is_default
    └─ flow_data (JSON)
    ↓
Save to database
    ↓
CustomBotService uses flows
```

## Factory Pattern Details

### Service Selection
```python
def create_service(bot, bot_user, telegram_client):
    bot_type = bot.bot_type
    
    SERVICE_MAP = {
        'simple': SimpleBotService,
        'registration': RegistrationBotService,
        'survey': SurveyBotService,
        'support': SupportBotService,
        'custom': CustomBotService,
    }
    
    service_class = SERVICE_MAP.get(bot_type, SimpleBotService)
    return service_class(bot, bot_user, telegram_client)
```

### Service Inheritance
```
BaseBotService (Abstract)
    │
    ├─ Common methods:
    │  ├─ handle_message()
    │  ├─ handle_command()
    │  ├─ handle_start()
    │  ├─ handle_help()
    │  ├─ request_phone_number()
    │  ├─ handle_contact()
    │  └─ send_message()
    │
    └─ Abstract method:
       └─ handle_text() ← Must implement
    
    ↓ Inherited by
    
SimpleBotService
    └─ handle_text() → Echo messages

RegistrationBotService
    └─ handle_text() → Registration flow

SurveyBotService
    └─ handle_text() → Survey questions

SupportBotService
    └─ handle_text() → Support menu

CustomBotService
    └─ handle_text() → Execute flows
```

## Complete Example: Registration Bot

```
1. Admin creates bot:
   - bot_type: 'registration'
   - has_welcome_message: True
   - welcome_message_text: "Welcome! Let's register."
   - has_get_number: True
   - get_number_text: "Share your phone please."

2. User opens bot in Telegram

3. User sends: /start

4. Telegram → Webhook → process_telegram_update()

5. Get/Create BotUser (state: 'new')

6. Factory creates RegistrationBotService

7. Service.handle_start():
   - Send "Welcome! Let's register."
   - Set state: 'welcomed'
   - Call request_phone_number()
   - Send "Share your phone please."
   - Show keyboard button
   - Set state: 'awaiting_phone'

8. User clicks button, shares phone

9. Telegram → Webhook → process_telegram_update()

10. Service.handle_contact():
    - Save phone_number
    - Set state: 'registered'
    - Call after_phone_number_received()
    - Call complete_registration()
    - Send summary

11. Done! User registered.
```

## Extensibility

### Adding New Bot Type

```
1. Create service class:
   Bot/services/my_bot.py
   
2. Inherit from BaseBotService:
   class MyBotService(BaseBotService):
       async def handle_text(self, text, message_data):
           # Your logic
           pass
   
3. Register with factory:
   BotServiceFactory.register_service('my_type', MyBotService)
   
4. Add to model choices:
   BOT_TYPE_CHOICES = [
       ...
       ('my_type', 'My Bot'),
   ]
   
5. Create migration:
   python manage.py makemigrations
   python manage.py migrate
   
6. Use in admin:
   Create bot with bot_type='my_type'
```

## Summary

The system now provides:
- ✅ 5 ready-to-use bot types
- ✅ Factory pattern for extensibility
- ✅ Welcome message configuration
- ✅ Phone number collection
- ✅ User state management
- ✅ Clean separation of concerns
- ✅ Easy to test and maintain
- ✅ Production-ready architecture
