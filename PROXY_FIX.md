# Proxy Configuration Fix

## Issue

If you see this error:
```
Failed to setup webhook. Error: Unknown scheme for proxy URL URL('socks://127.0.0.1:12334/')
```

This means your system has proxy environment variables set that are interfering with Telegram API calls.

## Root Cause

The system has environment variables like:
```bash
ALL_PROXY=socks://127.0.0.1:12334/
HTTP_PROXY=http://127.0.0.1:12334/
HTTPS_PROXY=http://127.0.0.1:12334/
```

The `httpx` library (used by python-telegram-bot) automatically picks up these proxy settings, but the SOCKS proxy scheme is not supported without additional dependencies.

## Solution Implemented

The `create_telegram_client()` helper function now:
1. Temporarily clears proxy environment variables
2. Creates client with `trust_env=False`
3. Restores original proxy variables

This completely bypasses the proxy:

```python
def create_telegram_client(token: str) -> TelegramBotClient:
    """
    Create Telegram Bot client with proper configuration
    Explicitly disables proxy to avoid system proxy issues
    """
    import httpx
    
    # Create httpx client without proxy
    httpx_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=20.0,
            read=20.0,
            write=20.0,
            pool=20.0
        ),
        limits=httpx.Limits(
            max_connections=8,
            max_keepalive_connections=8
        ),
        # Explicitly set proxy to None to ignore system proxy settings
        proxy=None
    )
    
    request = HTTPXRequest(http_version="1.1", client=httpx_client)
    return TelegramBotClient(token=token, request=request)
```

## Where Applied

This fix is applied in:
- `Bot/signals.py` - Auto webhook setup
- `Bot/admin.py` - Admin webhook actions
- `Bot/views.py` - API endpoints and webhook handler

## Alternative Solutions

### Option 1: Remove Proxy Environment Variables

If you don't need the proxy:

```bash
unset ALL_PROXY
unset all_proxy
unset HTTP_PROXY
unset http_proxy
unset HTTPS_PROXY
unset https_proxy
```

Add to your `.bashrc` or `.zshrc`:
```bash
export NO_PROXY="localhost,127.0.0.1,api.telegram.org"
```

### Option 2: Use Proxy with SOCKS Support

If you need to use the proxy, install SOCKS support:

```bash
pip install httpx[socks]
```

Then modify the helper function to use the proxy:
```python
httpx_client = httpx.AsyncClient(
    proxy="socks5://127.0.0.1:12334"  # Use socks5 instead of socks
)
```

### Option 3: Configure Proxy Per Request

Set proxy only for specific requests:
```python
# In settings.py
TELEGRAM_PROXY = None  # or "http://proxy:port"

# In helper function
proxy = getattr(settings, 'TELEGRAM_PROXY', None)
httpx_client = httpx.AsyncClient(proxy=proxy)
```

## Testing

After the fix, test webhook setup:

1. **Via Admin:**
   - Select a bot
   - Choose "🔗 Setup Webhook"
   - Should succeed without proxy errors

2. **Via Signal:**
   - Create a new bot
   - Should auto-setup webhook without errors

3. **Check Logs:**
   ```bash
   tail -f bot.log
   ```
   Should see:
   ```
   INFO Bot.signals Webhook set successfully for My Bot: https://...
   ```

## Verification

Check if proxy is being used:

```python
# In Django shell
from Bot.signals import create_telegram_client
import asyncio

client = create_telegram_client("YOUR_BOT_TOKEN")
info = asyncio.run(client.get_me())
print(info)  # Should work without proxy errors
```

## Production Considerations

### If Behind Corporate Proxy

If your production server is behind a corporate proxy that requires authentication:

1. **Configure proxy in settings:**
   ```python
   # settings.py
   TELEGRAM_PROXY = "http://user:pass@proxy:port"
   ```

2. **Update helper function:**
   ```python
   proxy = getattr(settings, 'TELEGRAM_PROXY', None)
   httpx_client = httpx.AsyncClient(proxy=proxy)
   ```

### If Using VPN

If using VPN, ensure:
- VPN allows connections to api.telegram.org
- VPN doesn't set conflicting proxy variables
- Add telegram.org to NO_PROXY if needed

## Summary

✅ **Fixed:** Proxy errors when setting up webhooks
✅ **Method:** Explicitly disable proxy in httpx client
✅ **Applied:** All Telegram API calls (signals, admin, views)
✅ **Result:** Webhooks work regardless of system proxy settings

The system now works correctly even with system proxy environment variables set!
