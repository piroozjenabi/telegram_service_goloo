# Bot Types Quick Guide

## Creating Different Bot Types

### 1. Simple Echo Bot

**Via Admin:**
1. Go to Admin → Telegram Bots → Add
2. Fill in:
   - Name: "Echo Bot"
   - Token: Your bot token
   - Bot Type: **Simple Bot**
   - Has Welcome Message: ✓
   - Welcome Message Text: "Hello! I'll echo your messages."
3. Save

**Behavior:**
- Sends welcome message on /start
- Echoes back user messages
- Simple and straightforward

---

### 2. Registration Bot

**Via Admin:**
1. Go to Admin → Telegram Bots → Add
2. Fill in:
   - Name: "Registration Bot"
   - Token: Your bot token
   - Bot Type: **Registration Bot**
   - Has Welcome Message: ✓
   - Welcome Message Text: "Welcome! Let's get you registered."
   - Has Get Number: ✓
   - Get Number Text: "Please share your phone number."
3. Save

**User Flow:**
```
User: /start
Bot: Welcome! Let's get you registered.
Bot: Please share your phone number.
[Shows phone number button]

User: [Shares phone]
Bot: ✅ Registration complete!
     Name: John Doe
     Phone: +1234567890
```

---

### 3. Survey Bot

**Via Admin:**
1. Go to Admin → Telegram Bots → Add
2. Fill in:
   - Name: "Feedback Survey"
   - Token: Your bot token
   - Bot Type: **Survey Bot**
   - Has Welcome Message: ✓
   - Welcome Message Text: "Thank you for taking our survey!"
   - Has Get Number: ✓ (optional)
3. Save

**User Flow:**
```
User: /start
Bot: Thank you for taking our survey!
Bot: Please share your phone number. [if enabled]

User: [Shares phone]
Bot: Question 1: How satisfied are you with our service? (1-5)

User: 5
Bot: Question 2: Would you recommend us to others? (Yes/No)

User: Yes
Bot: Question 3: Any additional comments?

User: Great service!
Bot: ✅ Thank you for completing the survey!
     Your responses:
     Satisfaction: 5
     Recommend: Yes
     Comments: Great service!
```

---

### 4. Support Bot

**Via Admin:**
1. Go to Admin → Telegram Bots → Add
2. Fill in:
   - Name: "Support Bot"
   - Token: Your bot token
   - Bot Type: **Support Bot**
   - Has Welcome Message: ✓
   - Welcome Message Text: "Welcome to support! How can we help?"
   - Has Get Number: ✓
3. Save

**User Flow:**
```
User: /start
Bot: Welcome to support! How can we help?
Bot: Please share your phone number.

User: [Shares phone]
Bot: 🎧 Support Menu
     1. Create a ticket
     2. Check ticket status
     3. FAQ
     4. Contact support
     Please enter a number (1-4):

User: 1
Bot: Please describe your issue:

User: My account is locked
Bot: ✅ Ticket created!
     Ticket ID: TKT-123
     Status: Open
     Our team will respond shortly.
```

---

### 5. Custom Bot (Flow-Based)

**Via Admin:**
1. Create Bot:
   - Name: "Custom Bot"
   - Token: Your bot token
   - Bot Type: **Custom Bot**
   - Has Welcome Message: ✓
   - Welcome Message Text: "Welcome!"

2. Create Flow (Admin → Bot Flows → Add):
   - Bot: Select your custom bot
   - Name: "Start Flow"
   - Trigger Command: `/start`
   - Is Default: ✓
   - Flow Data:
   ```json
   {
     "response": "Welcome! Use /help for commands."
   }
   ```

3. Create Help Flow:
   - Trigger Command: `/help`
   - Flow Data:
   ```json
   {
     "response": "Available commands:\n/start - Start\n/help - Help\n/menu - Show menu"
   }
   ```

---

## Comparison Table

| Feature | Simple | Registration | Survey | Support | Custom |
|---------|--------|--------------|--------|---------|--------|
| Welcome Message | ✓ | ✓ | ✓ | ✓ | ✓ |
| Phone Collection | ✓ | ✓ | ✓ | ✓ | ✓ |
| Multi-step Flow | - | ✓ | ✓ | ✓ | ✓ |
| State Management | Basic | ✓ | ✓ | ✓ | ✓ |
| Custom Logic | - | - | - | - | ✓ |
| Ticket System | - | - | - | ✓ | - |
| Survey Questions | - | - | ✓ | - | - |
| Flow Configuration | - | - | - | - | ✓ |

---

## Configuration Examples

### Welcome Message Examples

**Friendly:**
```
👋 Welcome! I'm here to help you.
```

**Professional:**
```
Welcome to [Company Name] Bot.
How may I assist you today?
```

**With Instructions:**
```
Welcome! 🎉

I can help you with:
• Registration
• Support tickets
• FAQs

Send /help to see all commands.
```

### Phone Number Request Examples

**Simple:**
```
Please share your phone number to continue.
```

**With Reason:**
```
We need your phone number to:
• Verify your identity
• Send important updates
• Provide better support

Please use the button below to share.
```

**Optional:**
```
Would you like to share your phone number?
(This is optional but helps us serve you better)
```

---

## Testing Your Bot

### 1. Setup Webhook

```bash
# Using ngrok for local testing
ngrok http 8000

# Setup webhook
python manage.py setup_bot_webhook <bot_id> https://your-ngrok-url.ngrok.io
```

### 2. Test in Telegram

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Follow the flow

### 3. Monitor in Admin

1. Go to Admin → Bot Users
2. See new users appear
3. Check their state
4. View state_data for responses

---

## Common Patterns

### Pattern 1: Welcome + Phone + Action

```
/start → Welcome → Request Phone → Main Action
```

**Use for:** Registration, Support, Survey

### Pattern 2: Welcome + Menu

```
/start → Welcome → Show Menu → Handle Selection
```

**Use for:** Support, Custom bots

### Pattern 3: Welcome + Questions

```
/start → Welcome → Q1 → Q2 → Q3 → Complete
```

**Use for:** Surveys, Forms

---

## Switching Bot Types

You can change bot type anytime:

1. Go to Admin → Telegram Bots
2. Click on your bot
3. Change "Bot Type"
4. Update welcome message if needed
5. Save

**Note:** Existing users will continue from their current state. Consider resetting user states if needed.

---

## Best Practices

### 1. Welcome Messages
- Keep it short and clear
- Explain what the bot does
- Include next steps

### 2. Phone Number Collection
- Explain why you need it
- Make it optional if possible
- Use the keyboard button (don't ask for manual input)

### 3. User States
- Always provide clear feedback
- Handle unexpected input gracefully
- Allow users to restart with /start

### 4. Error Handling
- Provide helpful error messages
- Offer alternatives
- Include /help command

---

## Troubleshooting

### Bot not responding to /start
- Check webhook is set
- Verify bot token is correct
- Check bot is active
- Review server logs

### Phone number not being collected
- Verify `has_get_number` is True
- Check `get_number_text` is set
- Ensure user is using the button (not typing)

### Wrong bot type behavior
- Check `bot_type` field in admin
- Verify migrations are applied
- Restart server if needed

### State not updating
- Check user_state in admin
- Verify state_data is valid JSON
- Review service implementation

---

## Next Steps

1. **Create your first bot** using one of the types above
2. **Test the flow** in Telegram
3. **Monitor users** in admin panel
4. **Customize** welcome messages and flows
5. **Extend** with custom bot types if needed

For more details, see:
- [FACTORY_PATTERN.md](Bot/FACTORY_PATTERN.md) - Technical details
- [Bot/README.md](Bot/README.md) - Bot app documentation
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
