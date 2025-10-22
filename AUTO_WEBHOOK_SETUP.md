# Automatic Webhook Setup

## Overview

The system now automatically sets up webhooks when you save a bot in the admin panel. No need to manually run commands or API calls!

## How It Works

When you save a bot (create or update), the system automatically:

1. ✅ Checks if `auto_setup_webhook` is enabled (default: True)
2. ✅ Verifies bot is active (`is_active=True`)
3. ✅ Checks if bot has a valid token
4. ✅ Constructs webhook URL: `{BASE_URL}/api/webhook/{bot_id}`
5. ✅ Calls Telegram API to set webhook
6. ✅ Updates bot with webhook URL and status
7. ✅ Fetches bot username from Telegram if not set

## Configuration

### BASE_URL Setting

The webhook URL is constructed using `BASE_URL` from settings:

**In `MAIN/settings.py`:**
```python
BASE_URL = os.getenv('BASE_URL', 'https://your-domain.com')
```

**In `.env` file:**
```env
BASE_URL=https://your-domain.com
```

**For local testing with ngrok:**
```env
BASE_URL=https://abc123.ngrok.io
```

### Auto Setup Control

Each bot has an `auto_setup_webhook` field (default: True):

- **Enabled (True)**: Webhook is automatically set when bot is saved
- **Disabled (False)**: Manual webhook setup required

## Usage

### Method 1: Automatic (Recommended)

1. **Configure BASE_URL** in `.env`:
   ```env
   BASE_URL=https://your-domain.com
   ```

2. **Create bot in admin**:
   - Go to Admin → Telegram Bots → Add
   - Fill in name and token
   - Ensure `auto_setup_webhook` is checked ✓
   - Save

3. **Done!** Webhook is automatically set up.

### Method 2: Manual Setup

If you prefer manual control:

1. **Disable auto setup**:
   - Uncheck `auto_setup_webhook` when creating bot

2. **Setup webhook manually**:
   ```bash
   python manage.py setup_bot_webhook <bot_id> <webhook_url>
   ```
   
   Or via API:
   ```bash
   curl -X POST http://localhost:8000/api/bots/{bot_id}/webhook \
     -H "Content-Type: application/json" \
     -d '{"webhook_url": "https://your-domain.com"}'
   ```

## Triggers

Webhook is automatically set up when:

1. **New bot is created** (if `auto_setup_webhook=True`)
2. **Bot is saved and webhook not set** (if `auto_setup_webhook=True`)

Webhook is NOT set up when:
- `auto_setup_webhook=False`
- `is_active=False`
- Token is empty
- `BASE_URL` is not configured

## Logging

All webhook operations are logged:

**Log file:** `bot.log` in project root

**Example logs:**
```
INFO Bot.signals New bot created: My Bot (550e8400-e29b-41d4-a716-446655440000)
INFO Bot.signals Webhook set successfully for My Bot: https://domain.com/api/webhook/550e8400-e29b-41d4-a716-446655440000
INFO Bot.signals Username fetched for My Bot: @my_bot
```

**Error logs:**
```
ERROR Bot.signals Failed to setup webhook for My Bot: Invalid token
WARNING Bot.signals BASE_URL not configured in settings. Skipping webhook setup.
```

## Local Development with ngrok

### Step 1: Start ngrok
```bash
ngrok http 8000
```

### Step 2: Copy HTTPS URL
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

### Step 3: Update .env
```env
BASE_URL=https://abc123.ngrok.io
```

### Step 4: Update settings.py (or restart server)
```python
BASE_URL = os.getenv('BASE_URL', 'https://abc123.ngrok.io')
```

### Step 5: Create bot in admin
Webhook will be automatically set to:
```
https://abc123.ngrok.io/api/webhook/{bot_id}
```

## Troubleshooting

### Webhook not being set

**Check 1: BASE_URL configured?**
```python
# In settings.py
print(settings.BASE_URL)  # Should print your domain
```

**Check 2: auto_setup_webhook enabled?**
- Go to Admin → Telegram Bots → Your Bot
- Check if `auto_setup_webhook` is checked

**Check 3: Bot is active?**
- Verify `is_active` is True

**Check 4: Valid token?**
- Test token with Telegram API
- Check for typos

**Check 5: Check logs**
```bash
tail -f bot.log
```

### Webhook URL is wrong

**Update BASE_URL:**
1. Update `.env` file
2. Restart Django server
3. Edit bot in admin and save (triggers webhook update)

Or manually update:
```bash
python manage.py setup_bot_webhook <bot_id> <correct_url>
```

### Multiple webhook setups

If you're seeing multiple webhook setup attempts:
- This is normal on first save (creates bot + sets webhook)
- Subsequent saves won't re-set webhook if already set
- Check `is_webhook_set` field in admin

### BASE_URL not configured warning

Add to `.env`:
```env
BASE_URL=https://your-domain.com
```

Or set in `settings.py`:
```python
BASE_URL = 'https://your-domain.com'
```

## Production Deployment

### Step 1: Set BASE_URL
```env
BASE_URL=https://your-production-domain.com
```

### Step 2: Ensure HTTPS
Telegram requires HTTPS for webhooks. Use:
- Let's Encrypt SSL certificate
- Cloudflare
- AWS Certificate Manager
- Any valid SSL provider

### Step 3: Update ALLOWED_HOSTS
```python
ALLOWED_HOSTS = ['your-production-domain.com']
```

### Step 4: Create bots
All bots will automatically use production webhook URL.

## Advanced Configuration

### Disable auto-setup for specific bots

In admin, when creating/editing bot:
- Uncheck `auto_setup_webhook`
- Save
- Setup webhook manually when needed

### Custom webhook logic

Edit `Bot/signals.py` to customize:

```python
@receiver(post_save, sender=TelegramBot)
def auto_setup_webhook(sender, instance, created, **kwargs):
    # Add your custom logic here
    if instance.name.startswith('Test'):
        # Don't setup webhook for test bots
        return
    
    # ... rest of the code
```

### Webhook with custom parameters

Modify signal to add custom parameters:

```python
# Add secret token for webhook verification
webhook_url = f"{base_url}/api/webhook/{instance.id}?secret={SECRET_TOKEN}"
```

## Benefits

✅ **No manual steps**: Just create bot and it's ready
✅ **Automatic username fetch**: Bot username is fetched from Telegram
✅ **Error handling**: Logs errors if webhook setup fails
✅ **Flexible**: Can disable auto-setup per bot
✅ **Production ready**: Works with any HTTPS domain
✅ **Development friendly**: Easy to use with ngrok

## Comparison

### Before (Manual)
```bash
# 1. Create bot in admin
# 2. Copy bot ID
# 3. Run command:
python manage.py setup_bot_webhook <bot_id> <webhook_url>
# 4. Or use API
```

### After (Automatic)
```bash
# 1. Create bot in admin
# 2. Done! ✅
```

## Signal Flow

```
Bot Saved in Admin
    ↓
post_save signal triggered
    ↓
auto_setup_webhook() function
    ↓
Check auto_setup_webhook flag
    ↓
Check is_active and token
    ↓
Get BASE_URL from settings
    ↓
Construct webhook URL
    ↓
Call Telegram API
    ↓
Update bot record
    ↓
Log success/error
```

## Testing

### Test automatic setup

1. Configure BASE_URL
2. Create new bot in admin
3. Check logs:
   ```bash
   tail -f bot.log
   ```
4. Verify in admin:
   - `is_webhook_set` should be True
   - `webhook_url` should be set
   - `username` should be fetched

### Test manual setup

1. Create bot with `auto_setup_webhook=False`
2. Verify webhook is NOT set
3. Setup manually:
   ```bash
   python manage.py setup_bot_webhook <bot_id> <url>
   ```
4. Verify webhook is set

## FAQ

**Q: Can I change the webhook URL later?**
A: Yes, just update BASE_URL and save the bot again (or use manual setup).

**Q: What if BASE_URL is not configured?**
A: Webhook setup is skipped with a warning in logs.

**Q: Can I disable auto-setup globally?**
A: Set `auto_setup_webhook=False` for each bot, or modify the signal.

**Q: Does it work with multiple bots?**
A: Yes! Each bot gets its own unique webhook URL.

**Q: What about webhook security?**
A: Telegram uses HTTPS and bot token for security. You can add additional verification in the webhook handler.

**Q: Can I see webhook setup history?**
A: Check `bot.log` file for all webhook operations.

## Next Steps

1. ✅ Configure BASE_URL in `.env`
2. ✅ Create your first bot in admin
3. ✅ Verify webhook is set (check logs)
4. ✅ Test bot in Telegram
5. ✅ Monitor logs for any issues

For more information:
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [BOT_TYPES_GUIDE.md](BOT_TYPES_GUIDE.md) - Bot types
- [README.md](README.md) - Main documentation
