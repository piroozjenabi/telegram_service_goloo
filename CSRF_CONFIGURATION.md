# CSRF Configuration Guide

## Problem
When accessing your Django application through a domain (e.g., `https://tgservice.sarafirasmi.co.uk`), you may encounter:

```
Forbidden (403)
CSRF verification failed. Request aborted.
Reason: Origin checking failed - https://tgservice.sarafirasmi.co.uk does not match any trusted origins.
```

## Solution

Django requires you to explicitly trust origins for CSRF protection. This is now configured via environment variables.

## Configuration

### Option 1: Environment Variables (Recommended)

Add to your `.env` file:

```bash
# Comma-separated list of allowed hosts
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,tgservice.sarafirasmi.co.uk

# Comma-separated list of trusted origins (must include https://)
CSRF_TRUSTED_ORIGINS=https://tgservice.sarafirasmi.co.uk,https://your-other-domain.com

# Your base URL for webhooks
BASE_URL=https://tgservice.sarafirasmi.co.uk
```

### Option 2: Direct Settings (Not Recommended)

Edit `MAIN/settings.py`:

```python
ALLOWED_HOSTS = ['tgservice.sarafirasmi.co.uk', 'localhost']

CSRF_TRUSTED_ORIGINS = [
    'https://tgservice.sarafirasmi.co.uk',
]
```

## Docker Deployment

When deploying with Docker, ensure your `.env` file is properly configured:

```bash
# .env
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=tgservice.sarafirasmi.co.uk
CSRF_TRUSTED_ORIGINS=https://tgservice.sarafirasmi.co.uk
BASE_URL=https://tgservice.sarafirasmi.co.uk
```

Then restart your Docker services:

```bash
docker-compose down
docker-compose up -d
```

Or use the rebuild script:

```bash
./docker-rebuild.sh
```

## Multiple Domains

If you have multiple domains, separate them with commas:

```bash
DJANGO_ALLOWED_HOSTS=domain1.com,domain2.com,localhost
CSRF_TRUSTED_ORIGINS=https://domain1.com,https://domain2.com
```

## Development vs Production

### Development
```bash
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

### Production
```bash
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

## Wildcard Hosts (Not Recommended for Production)

For development only, you can use:

```bash
DJANGO_ALLOWED_HOSTS=*
```

But you still need to specify CSRF_TRUSTED_ORIGINS explicitly.

## Troubleshooting

### Still Getting CSRF Errors?

1. **Check your .env file is loaded:**
   ```bash
   docker-compose exec web python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.CSRF_TRUSTED_ORIGINS)
   >>> print(settings.ALLOWED_HOSTS)
   ```

2. **Restart Docker services:**
   ```bash
   docker-compose restart
   ```

3. **Rebuild if needed:**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

4. **Check logs:**
   ```bash
   docker-compose logs -f web
   ```

### Common Mistakes

❌ **Wrong:** `CSRF_TRUSTED_ORIGINS=tgservice.sarafirasmi.co.uk`
✅ **Correct:** `CSRF_TRUSTED_ORIGINS=https://tgservice.sarafirasmi.co.uk`

❌ **Wrong:** Using spaces in comma-separated list
✅ **Correct:** `domain1.com,domain2.com` (no spaces)

❌ **Wrong:** Forgetting to restart after changes
✅ **Correct:** Always restart Docker after .env changes

## Security Notes

1. **Never use `ALLOWED_HOSTS=['*']` in production**
2. **Always use HTTPS in production** (https://, not http://)
3. **Keep DJANGO_SECRET_KEY secret** and unique per environment
4. **Set DJANGO_DEBUG=0 in production**
5. **Regularly update CSRF_TRUSTED_ORIGINS** when adding new domains

## Testing

After configuration, test your setup:

```bash
# Check health endpoint
curl https://tgservice.sarafirasmi.co.uk/api/health/

# Test webhook (from Telegram)
# Should not return 403 anymore
```

## Current Configuration

Your current setup in `.env`:

```bash
DJANGO_ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=https://tgservice.sarafirasmi.co.uk,https://3559f12d6e93.ngrok-free.app
BASE_URL=https://tgservice.sarafirasmi.co.uk
```

This allows:
- All hosts (development mode)
- CSRF protection for your production domain and ngrok tunnel
- Webhooks configured for your production domain
