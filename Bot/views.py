from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import TelegramBot, BotUser, BotFlow, BotMessage
from telegram import Update, Bot as TelegramBotClient
from telegram.request import HTTPXRequest
from telegram.ext import Application
import asyncio
from typing import Optional, Dict, Any
import json

api = NinjaAPI(urls_namespace='bot_api')


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


# Schemas
class WebhookUpdateSchema(Schema):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    edited_message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None


class BotCreateSchema(Schema):
    name: str
    token: str


class BotResponseSchema(Schema):
    id: str
    name: str
    username: str
    user_count: int
    request_count: int
    is_webhook_set: bool
    webhook_url: Optional[str]
    is_active: bool


class WebhookSetupSchema(Schema):
    webhook_url: str


# Bot Management Endpoints
@api.post("/bots", response=BotResponseSchema)
def create_bot(request, payload: BotCreateSchema):
    """Create a new telegram bot"""
    try:
        # Verify token with Telegram
        bot_client = create_telegram_client(payload.token)
        bot_info = asyncio.run(bot_client.get_me())
        
        bot = TelegramBot.objects.create(
            name=payload.name,
            token=payload.token,
            username=bot_info.username
        )
        
        return bot
    except Exception as e:
        return api.create_response(
            request,
            {"error": str(e)},
            status=400
        )


@api.get("/bots", response=list[BotResponseSchema])
def list_bots(request):
    """List all bots"""
    return TelegramBot.objects.all()


@api.get("/bots/{bot_id}", response=BotResponseSchema)
def get_bot(request, bot_id: str):
    """Get bot details"""
    bot = get_object_or_404(TelegramBot, id=bot_id)
    return bot


@api.post("/bots/{bot_id}/webhook")
def setup_webhook(request, bot_id: str, payload: WebhookSetupSchema):
    """Setup webhook for a bot"""
    bot = get_object_or_404(TelegramBot, id=bot_id)
    
    try:
        # Construct webhook URL with bot UUID
        webhook_url = f"{payload.webhook_url}/api/webhook/{bot.id}"
        
        # Set webhook with Telegram
        bot_client = create_telegram_client(bot.token)
        asyncio.run(bot_client.set_webhook(url=webhook_url))
        
        # Update bot
        bot.webhook_url = webhook_url
        bot.is_webhook_set = True
        bot.save()
        
        return {"success": True, "webhook_url": webhook_url}
    except Exception as e:
        return api.create_response(
            request,
            {"error": str(e)},
            status=400
        )


@api.delete("/bots/{bot_id}/webhook")
def delete_webhook(request, bot_id: str):
    """Remove webhook for a bot"""
    bot = get_object_or_404(TelegramBot, id=bot_id)
    
    try:
        bot_client = create_telegram_client(bot.token)
        asyncio.run(bot_client.delete_webhook())
        
        bot.is_webhook_set = False
        bot.webhook_url = None
        bot.save()
        
        return {"success": True}
    except Exception as e:
        return api.create_response(
            request,
            {"error": str(e)},
            status=400
        )


# Webhook Handler
@api.post("/webhook/{bot_id}")
def webhook_handler(request, bot_id: str):
    """Handle incoming webhook updates from Telegram"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        bot = get_object_or_404(TelegramBot, id=bot_id)
        
        # Parse update
        update_data = json.loads(request.body)
        logger.info(f"Received webhook update for bot {bot.name}: {update_data}")
        
        # Increment request count
        bot.increment_request_count()
        
        # Process the update synchronously (services handle async Telegram calls internally)
        process_telegram_update_sync(bot, update_data)
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error for bot_id {bot_id}: {str(e)}", exc_info=True)
        return api.create_response(
            request,
            {"error": str(e)},
            status=400
        )


def process_telegram_update_sync(bot: TelegramBot, update_data: dict):
    """Process incoming Telegram update using Factory Pattern (synchronous version)"""
    from .services.factory import BotServiceFactory
    
    message = update_data.get('message')
    contact = update_data.get('contact')
    
    if not message:
        return
    
    # Extract user data
    from_user = message.get('from', {})
    chat_id = message.get('chat', {}).get('id')
    
    if not chat_id:
        return
    
    # Get or create bot user
    bot_user, created = BotUser.objects.get_or_create(
        bot=bot,
        chat_id=chat_id,
        defaults={
            'username': from_user.get('username'),
            'first_name': from_user.get('first_name'),
            'last_name': from_user.get('last_name'),
            'language_code': from_user.get('language_code'),
        }
    )
    
    # Update user count if new user
    if created:
        bot.user_count += 1
        bot.save(update_fields=['user_count'])
    else:
        # Update user info
        bot_user.username = from_user.get('username') or bot_user.username
        bot_user.first_name = from_user.get('first_name') or bot_user.first_name
        bot_user.last_name = from_user.get('last_name') or bot_user.last_name
        bot_user.save()
    
    # Determine message type
    message_type = 'text'
    text = message.get('text', '')
    file_url = None
    
    if 'contact' in message:
        message_type = 'contact'
        contact = message['contact']
    elif 'photo' in message:
        message_type = 'photo'
        file_url = message['photo'][-1].get('file_id') if message['photo'] else None
    elif 'video' in message:
        message_type = 'video'
        file_url = message['video'].get('file_id')
    elif 'document' in message:
        message_type = 'document'
        file_url = message['document'].get('file_id')
    elif 'audio' in message:
        message_type = 'audio'
        file_url = message['audio'].get('file_id')
    elif 'voice' in message:
        message_type = 'voice'
        file_url = message['voice'].get('file_id')
    
    # Save incoming message
    BotMessage.objects.create(
        bot=bot,
        user=bot_user,
        message_type=message_type,
        direction='incoming',
        text=text,
        file_url=file_url,
        telegram_message_id=message.get('message_id')
    )
    
    # Create Telegram client
    bot_client = create_telegram_client(bot.token)
    
    # Use Factory Pattern to get appropriate service
    bot_service = BotServiceFactory.create_service(bot, bot_user, bot_client)
    
    # Handle contact sharing or regular message
    # Use a new thread with proper Django async setup
    import threading
    from django.db import close_old_connections
    
    def run_service():
        # Close any existing database connections in this thread
        close_old_connections()
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Mark this thread as sync-safe for Django
        import os
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
        
        try:
            if message_type == 'contact':
                loop.run_until_complete(bot_service.handle_contact(message['contact']))
            else:
                loop.run_until_complete(bot_service.handle_message(message))
        finally:
            loop.close()
            close_old_connections()
    
    thread = threading.Thread(target=run_service)
    thread.start()
    thread.join(timeout=30)  # Wait max 30 seconds


async def process_telegram_update(bot: TelegramBot, update_data: dict):
    """Process incoming Telegram update using Factory Pattern"""
    from asgiref.sync import sync_to_async
    from .services.factory import BotServiceFactory
    
    message = update_data.get('message')
    contact = update_data.get('contact')
    
    if not message:
        return
    
    # Extract user data
    from_user = message.get('from', {})
    chat_id = message.get('chat', {}).get('id')
    
    if not chat_id:
        return
    
    # Get or create bot user (sync operation wrapped in async)
    @sync_to_async
    def get_or_create_user():
        return BotUser.objects.get_or_create(
            bot=bot,
            chat_id=chat_id,
            defaults={
                'username': from_user.get('username'),
                'first_name': from_user.get('first_name'),
                'last_name': from_user.get('last_name'),
                'language_code': from_user.get('language_code'),
            }
        )
    
    bot_user, created = await get_or_create_user()
    
    # Update user count if new user
    if created:
        @sync_to_async
        def update_user_count():
            bot.user_count += 1
            bot.save(update_fields=['user_count'])
        
        await update_user_count()
    else:
        # Update user info
        @sync_to_async
        def update_user_info():
            bot_user.username = from_user.get('username') or bot_user.username
            bot_user.first_name = from_user.get('first_name') or bot_user.first_name
            bot_user.last_name = from_user.get('last_name') or bot_user.last_name
            bot_user.save()
        
        await update_user_info()
    
    # Determine message type
    message_type = 'text'
    text = message.get('text', '')
    file_url = None
    
    if 'contact' in message:
        message_type = 'contact'
        contact = message['contact']
    elif 'photo' in message:
        message_type = 'photo'
        file_url = message['photo'][-1].get('file_id') if message['photo'] else None
    elif 'video' in message:
        message_type = 'video'
        file_url = message['video'].get('file_id')
    elif 'document' in message:
        message_type = 'document'
        file_url = message['document'].get('file_id')
    elif 'audio' in message:
        message_type = 'audio'
        file_url = message['audio'].get('file_id')
    elif 'voice' in message:
        message_type = 'voice'
        file_url = message['voice'].get('file_id')
    
    # Save incoming message
    @sync_to_async
    def save_message():
        return BotMessage.objects.create(
            bot=bot,
            user=bot_user,
            message_type=message_type,
            direction='incoming',
            text=text,
            file_url=file_url,
            telegram_message_id=message.get('message_id')
        )
    
    await save_message()
    
    # Create Telegram client
    bot_client = create_telegram_client(bot.token)
    
    # Use Factory Pattern to get appropriate service
    bot_service = BotServiceFactory.create_service(bot, bot_user, bot_client)
    
    # Handle contact sharing
    if message_type == 'contact':
        await bot_service.handle_contact(message['contact'])
    else:
        # Handle regular message
        await bot_service.handle_message(message)


# Statistics Endpoints
@api.get("/bots/{bot_id}/stats")
def get_bot_stats(request, bot_id: str):
    """Get bot statistics"""
    bot = get_object_or_404(TelegramBot, id=bot_id)
    
    total_messages = BotMessage.objects.filter(bot=bot).count()
    incoming_messages = BotMessage.objects.filter(bot=bot, direction='incoming').count()
    outgoing_messages = BotMessage.objects.filter(bot=bot, direction='outgoing').count()
    
    return {
        "bot_id": str(bot.id),
        "user_count": bot.user_count,
        "request_count": bot.request_count,
        "total_messages": total_messages,
        "incoming_messages": incoming_messages,
        "outgoing_messages": outgoing_messages,
    }
