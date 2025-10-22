# Admin Webhook Actions

## Overview

The admin panel now includes powerful actions to manage webhooks directly from the bot list. You can setup, check, and delete webhooks with full Telegram API response visibility.

## Available Actions

### 1. 🔗 Setup Webhook

Manually setup webhook for selected bots.

**How to use:**
1. Go to Admin → Telegram Bots
2. Select one or more bots (checkbox)
3. Choose "🔗 Setup Webhook" from Actions dropdown
4. Click "Go"

**What it does:**
- Constructs webhook URL: `{BASE_URL}/api/webhook/{bot_id}`
- Calls Telegram API to set webhook
- Updates bot record with webhook URL and status
- Shows Telegram's response for each bot

**Success message:**
```
✅ My Bot: Webhook set successfully. Telegram response: True
Successfully set up webhooks for 1 bot(s).
```

**Error message:**
```
❌ My Bot: Failed to setup webhook. Error: Invalid token
Failed to setup webhooks for 1 bot(s).
```

---

### 2. ℹ️ Check Webhook Info

Get detailed webhook information from Telegram.

**How to use:**
1. Go to Admin → Telegram Bots
2. Select one or more bots
3. Choose "ℹ️ Check Webhook Info" from Actions
4. Click "Go"

**What it shows:**
- Current webhook URL
- Has custom certificate
- Pending update count
- Last error date (if any)
- Last error message (if any)
- Max connections
- Allowed updates

**Example response:**
```
📊 Webhook Info for My Bot:
URL: https://yourdomain.com/api/webhook/550e8400-e29b-41d4-a716-446655440000
Has Custom Certificate: False
Pending Update Count: 0
Max Connections: 40
Allowed Updates: message, callback_query
```

**With errors:**
```
📊 Webhook Info for My Bot:
URL: https://yourdomain.com/api/webhook/550e8400-e29b-41d4-a716-446655440000
Has Custom Certificate: False
Pending Update Count: 5
Last Error Date: 2024-10-22 20:30:00
Last Error: Wrong response from the webhook: 500 Internal Server Error
```

---

### 3. 🗑️ Delete Webhook

Remove webhook for selected bots.

**How to use:**
1. Go to Admin → Telegram Bots
2. Select one or more bots
3. Choose "🗑️ Delete Webhook" from Actions
4. Click "Go"

**What it does:**
- Calls Telegram API to delete webhook
- Updates bot record (is_webhook_set=False, webhook_url=None)
- Shows Telegram's response

**Success message:**
```
✅ My Bot: Webhook deleted successfully. Telegram response: True
Successfully deleted webhooks for 1 bot(s).
```

---

## Use Cases

### Use Case 1: Bulk Webhook Setup

**Scenario:** You have 10 bots and want to setup webhooks for all of them.

**Steps:**
1. Select all 10 bots
2. Choose "🔗 Setup Webhook"
3. Click "Go"
4. Review success/error messages for each bot

**Result:** All bots have webhooks configured in seconds.

---

### Use Case 2: Troubleshooting Webhook Issues

**Scenario:** Bot not receiving messages.

**Steps:**
1. Select the bot
2. Choose "ℹ️ Check Webhook Info"
3. Click "Go"
4. Review the response:
   - Check if URL is correct
   - Check for error messages
   - Check pending update count

**Common issues:**
- URL is wrong → Use "🔗 Setup Webhook" to fix
- Last error shows SSL error → Fix SSL certificate
- Pending updates > 0 → Telegram couldn't deliver updates

---

### Use Case 3: Switching from Webhook to Polling

**Scenario:** You want to test bot locally with polling.

**Steps:**
1. Select the bot
2. Choose "🗑️ Delete Webhook"
3. Click "Go"
4. Now you can use polling in your local tests

---

### Use Case 4: Changing Webhook URL

**Scenario:** You moved to a new domain.

**Steps:**
1. Update `BASE_URL` in settings/env
2. Restart Django server
3. Select all bots
4. Choose "🔗 Setup Webhook"
5. Click "Go"

**Result:** All bots now use the new domain.

---

## Action Comparison

| Action | Purpose | Updates DB | Calls Telegram API |
|--------|---------|------------|-------------------|
| Setup Webhook | Set webhook URL | ✅ Yes | ✅ set_webhook() |
| Check Webhook Info | Get webhook status | ❌ No | ✅ get_webhook_info() |
| Delete Webhook | Remove webhook | ✅ Yes | ✅ delete_webhook() |

---

## Telegram API Responses

### set_webhook() Response

**Success:**
```python
True
```

**Failure:**
```python
telegram.error.InvalidToken: Invalid token
telegram.error.NetworkError: Connection timeout
```

### get_webhook_info() Response

**Object with fields:**
```python
WebhookInfo(
    url='https://domain.com/api/webhook/uuid',
    has_custom_certificate=False,
    pending_update_count=0,
    last_error_date=None,
    last_error_message=None,
    max_connections=40,
    allowed_updates=['message', 'callback_query']
)
```

### delete_webhook() Response

**Success:**
```python
True
```

---

## Error Messages

### Common Errors

**1. BASE_URL not configured**
```
BASE_URL not configured in settings. Please configure it first.
```

**Solution:** Add BASE_URL to settings.py or .env

**2. Invalid token**
```
❌ My Bot: Failed to setup webhook. Error: Invalid token
```

**Solution:** Check bot token from BotFather

**3. Network error**
```
❌ My Bot: Failed to setup webhook. Error: Connection timeout
```

**Solution:** Check internet connection

**4. Invalid URL**
```
❌ My Bot: Failed to setup webhook. Error: Bad Request: bad webhook: HTTPS url must be provided for webhook
```

**Solution:** Ensure BASE_URL uses HTTPS

**5. SSL certificate error**
```
Last Error: Wrong response from the webhook: SSL certificate problem
```

**Solution:** Fix SSL certificate on your server

---

## Best Practices

### 1. Check Before Setup

Always check webhook info before setting up:
1. Check Webhook Info
2. Review current status
3. Setup Webhook if needed

### 2. Verify After Setup

After setting up webhook:
1. Check Webhook Info
2. Verify URL is correct
3. Check for errors
4. Test bot in Telegram

### 3. Monitor Regularly

Periodically check webhook info:
- Look for error messages
- Check pending update count
- Verify URL is still correct

### 4. Bulk Operations

When managing multiple bots:
- Select all bots at once
- Use bulk actions
- Review all messages
- Fix errors individually if needed

---

## Troubleshooting Guide

### Webhook not working after setup

**Check 1: Verify webhook is set**
```
Action: Check Webhook Info
Look for: URL should be set
```

**Check 2: Check for errors**
```
Action: Check Webhook Info
Look for: Last Error Message
```

**Check 3: Test webhook URL**
```bash
curl https://yourdomain.com/api/webhook/{bot_id}
```

**Check 4: Check server logs**
```bash
tail -f bot.log
```

### Pending updates increasing

**Cause:** Telegram can't deliver updates to your webhook

**Solutions:**
1. Check webhook URL is accessible
2. Verify SSL certificate is valid
3. Check server is responding quickly (<5 seconds)
4. Review error messages in webhook info

### Multiple bots, some work, some don't

**Check each bot individually:**
1. Select one bot
2. Check Webhook Info
3. Look for specific error messages
4. Fix issues per bot

---

## Advanced Usage

### Custom Webhook Parameters

If you need custom webhook parameters, modify the action in `Bot/admin.py`:

```python
def setup_webhook_action(self, request, queryset):
    # Add custom parameters
    webhook_url = f"{base_url}/api/webhook/{bot.id}?secret={SECRET_TOKEN}"
    
    # Set with custom options
    result = asyncio.run(bot_client.set_webhook(
        url=webhook_url,
        max_connections=100,
        allowed_updates=['message', 'callback_query']
    ))
```

### Webhook with Certificate

For self-signed certificates:

```python
with open('cert.pem', 'rb') as cert_file:
    result = asyncio.run(bot_client.set_webhook(
        url=webhook_url,
        certificate=cert_file
    ))
```

---

## Screenshots Guide

### How to use actions:

1. **Select bots:**
   ```
   [✓] My Bot 1
   [✓] My Bot 2
   [ ] My Bot 3
   ```

2. **Choose action:**
   ```
   Actions: [🔗 Setup Webhook ▼] [Go]
   ```

3. **View results:**
   ```
   ✅ My Bot 1: Webhook set successfully. Telegram response: True
   ✅ My Bot 2: Webhook set successfully. Telegram response: True
   Successfully set up webhooks for 2 bot(s).
   ```

---

## API Equivalent

These admin actions are equivalent to API calls:

### Setup Webhook
```bash
curl -X POST http://localhost:8000/api/bots/{bot_id}/webhook \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://yourdomain.com"}'
```

### Check Webhook Info
```bash
# Not available in API yet, but you can add it
```

### Delete Webhook
```bash
curl -X DELETE http://localhost:8000/api/bots/{bot_id}/webhook
```

---

## Summary

The admin webhook actions provide:

✅ **Easy webhook management** - No command line needed
✅ **Bulk operations** - Manage multiple bots at once
✅ **Full visibility** - See Telegram's responses
✅ **Error handling** - Clear error messages
✅ **Troubleshooting** - Detailed webhook info
✅ **Production ready** - Works with any number of bots

**Time saved:** ~5 minutes per bot for manual webhook management
**User experience:** Point-and-click simplicity
**Reliability:** Direct Telegram API integration with full response visibility
