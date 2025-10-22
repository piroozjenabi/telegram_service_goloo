"""
Django signals for automatic webhook setup
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from telegram import Bot as TelegramBotClient
from telegram.request import HTTPXRequest
import asyncio
import logging

from .models import TelegramBot

logger = logging.getLogger(__name__)


def create_telegram_client(token: str) -> TelegramBotClient:
    """
    Create Telegram Bot client with proper configuration
    Clears proxy environment variables to avoid proxy issues
    """
    import os
    
    # Save original proxy env vars
    original_proxies = {}
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 
                  'FTP_PROXY', 'ftp_proxy', 'NO_PROXY', 'no_proxy']
    
    # Temporarily clear proxy environment variables
    for var in proxy_vars:
        if var in os.environ:
            original_proxies[var] = os.environ[var]
            del os.environ[var]
    
    try:
        # Create Telegram client - it will now not use any proxy
        return TelegramBotClient(token=token)
    finally:
        # Restore original proxy env vars
        for var, value in original_proxies.items():
            os.environ[var] = value


@receiver(post_save, sender=TelegramBot)
def auto_setup_webhook(sender, instance, created, **kwargs):
    """
    Automatically setup webhook when bot is saved
    
    Triggers when:
    - New bot is created
    - Bot token is changed
    - Bot is activated (is_active=True)
    - auto_setup_webhook is enabled
    """
    # Only setup webhook if auto_setup_webhook is enabled
    if not instance.auto_setup_webhook:
        logger.info(f"Auto webhook setup disabled for bot: {instance.name}")
        return
    
    # Only setup webhook if bot is active and has token
    if not instance.is_active or not instance.token:
        return
    
    # Check if we should setup webhook
    should_setup = False
    
    if created:
        # New bot created
        should_setup = True
        logger.info(f"New bot created: {instance.name} ({instance.id})")
    elif not instance.is_webhook_set:
        # Webhook not set yet
        should_setup = True
        logger.info(f"Webhook not set for bot: {instance.name} ({instance.id})")
    
    if should_setup:
        try:
            # Get base URL from settings
            base_url = getattr(settings, 'BASE_URL', None)
            
            if not base_url:
                logger.warning("BASE_URL not configured in settings. Skipping webhook setup.")
                return
            
            # Construct webhook URL
            webhook_url = f"{base_url}/api/webhook/{instance.id}"
            
            # Setup webhook with Telegram
            bot_client = create_telegram_client(instance.token)
            asyncio.run(bot_client.set_webhook(url=webhook_url))
            
            # Update bot instance
            instance.webhook_url = webhook_url
            instance.is_webhook_set = True
            
            # Use update() to avoid triggering signal again
            TelegramBot.objects.filter(pk=instance.pk).update(
                webhook_url=webhook_url,
                is_webhook_set=True
            )
            
            logger.info(f"Webhook set successfully for {instance.name}: {webhook_url}")
            
        except Exception as e:
            logger.error(f"Failed to setup webhook for {instance.name}: {str(e)}")


@receiver(post_save, sender=TelegramBot)
def fetch_bot_username(sender, instance, created, **kwargs):
    """
    Automatically fetch bot username from Telegram if not set
    """
    if not instance.username and instance.token:
        try:
            bot_client = create_telegram_client(instance.token)
            bot_info = asyncio.run(bot_client.get_me())
            
            # Update username using update() to avoid triggering signal again
            TelegramBot.objects.filter(pk=instance.pk).update(
                username=bot_info.username
            )
            
            logger.info(f"Username fetched for {instance.name}: @{bot_info.username}")
            
        except Exception as e:
            logger.error(f"Failed to fetch username for {instance.name}: {str(e)}")
