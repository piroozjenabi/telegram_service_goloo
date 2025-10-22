from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from unfold.admin import ModelAdmin
from telegram import Bot as TelegramBotClient
from telegram.request import HTTPXRequest
import asyncio
from .models import TelegramBot, BotUser, BotFlow, BotMessage


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


@admin.register(TelegramBot)
class TelegramBotAdmin(ModelAdmin):
    list_display = ['name', 'username', 'bot_type', 'user_count', 'request_count', 'is_webhook_set', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_webhook_set', 'bot_type', 'created_at']
    search_fields = ['name', 'username', 'token']
    readonly_fields = ['id', 'user_count', 'request_count', 'created_at', 'updated_at']
    actions = ['setup_webhook_action', 'check_webhook_info', 'delete_webhook_action']
    
    fieldsets = (
        ('Bot Information', {
            'fields': ('id', 'name', 'token', 'username', 'bot_type')
        }),
        ('Welcome Message Configuration', {
            'fields': ('has_welcome_message', 'welcome_message_text'),
            'classes': ('collapse',)
        }),
        ('Phone Number Collection', {
            'fields': ('has_get_number', 'get_number_text', 'after_phone_number_text'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('user_count', 'request_count')
        }),
        ('Webhook Configuration', {
            'fields': ('auto_setup_webhook', 'is_webhook_set', 'webhook_url')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def setup_webhook_action(self, request, queryset):
        """Setup webhook for selected bots"""
        base_url = getattr(settings, 'BASE_URL', None)
        
        if not base_url:
            self.message_user(
                request,
                "BASE_URL not configured in settings. Please configure it first.",
                level=messages.ERROR
            )
            return
        
        success_count = 0
        error_count = 0
        
        for bot in queryset:
            try:
                # Construct webhook URL
                webhook_url = f"{base_url}/api/webhook/{bot.id}"
                
                # Setup webhook with Telegram
                bot_client = create_telegram_client(bot.token)
                result = asyncio.run(bot_client.set_webhook(url=webhook_url))
                
                # Update bot
                bot.webhook_url = webhook_url
                bot.is_webhook_set = True
                bot.save(update_fields=['webhook_url', 'is_webhook_set'])
                
                success_count += 1
                
                # Show Telegram response
                self.message_user(
                    request,
                    f"✅ {bot.name}: Webhook set successfully. Telegram response: {result}",
                    level=messages.SUCCESS
                )
                
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"❌ {bot.name}: Failed to setup webhook. Error: {str(e)}",
                    level=messages.ERROR
                )
        
        # Summary message
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully set up webhooks for {success_count} bot(s).",
                level=messages.SUCCESS
            )
        if error_count > 0:
            self.message_user(
                request,
                f"Failed to setup webhooks for {error_count} bot(s).",
                level=messages.WARNING
            )
    
    setup_webhook_action.short_description = "🔗 Setup Webhook"
    
    def check_webhook_info(self, request, queryset):
        """Check webhook information from Telegram"""
        for bot in queryset:
            try:
                bot_client = create_telegram_client(bot.token)
                webhook_info = asyncio.run(bot_client.get_webhook_info())
                
                # Format webhook info
                info_lines = [
                    f"📊 Webhook Info for {bot.name}:",
                    f"URL: {webhook_info.url or 'Not set'}",
                    f"Has Custom Certificate: {webhook_info.has_custom_certificate}",
                    f"Pending Update Count: {webhook_info.pending_update_count}",
                ]
                
                if webhook_info.last_error_date:
                    info_lines.append(f"Last Error Date: {webhook_info.last_error_date}")
                if webhook_info.last_error_message:
                    info_lines.append(f"Last Error: {webhook_info.last_error_message}")
                if webhook_info.max_connections:
                    info_lines.append(f"Max Connections: {webhook_info.max_connections}")
                if webhook_info.allowed_updates:
                    info_lines.append(f"Allowed Updates: {', '.join(webhook_info.allowed_updates)}")
                
                info_message = "\n".join(info_lines)
                
                self.message_user(
                    request,
                    info_message,
                    level=messages.INFO
                )
                
            except Exception as e:
                self.message_user(
                    request,
                    f"❌ {bot.name}: Failed to get webhook info. Error: {str(e)}",
                    level=messages.ERROR
                )
    
    check_webhook_info.short_description = "ℹ️ Check Webhook Info"
    
    def delete_webhook_action(self, request, queryset):
        """Delete webhook for selected bots"""
        success_count = 0
        error_count = 0
        
        for bot in queryset:
            try:
                bot_client = create_telegram_client(bot.token)
                result = asyncio.run(bot_client.delete_webhook())
                
                # Update bot
                bot.is_webhook_set = False
                bot.webhook_url = None
                bot.save(update_fields=['is_webhook_set', 'webhook_url'])
                
                success_count += 1
                
                self.message_user(
                    request,
                    f"✅ {bot.name}: Webhook deleted successfully. Telegram response: {result}",
                    level=messages.SUCCESS
                )
                
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"❌ {bot.name}: Failed to delete webhook. Error: {str(e)}",
                    level=messages.ERROR
                )
        
        # Summary message
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully deleted webhooks for {success_count} bot(s).",
                level=messages.SUCCESS
            )
        if error_count > 0:
            self.message_user(
                request,
                f"Failed to delete webhooks for {error_count} bot(s).",
                level=messages.WARNING
            )
    
    delete_webhook_action.short_description = "🗑️ Delete Webhook"


@admin.register(BotUser)
class BotUserAdmin(ModelAdmin):
    list_display = ['chat_id', 'username', 'first_name', 'last_name', 'bot', 'user_state', 'is_active', 'last_interaction']
    list_filter = ['is_active', 'is_blocked', 'user_state', 'bot', 'first_interaction']
    search_fields = ['chat_id', 'username', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['first_interaction', 'last_interaction']
    
    fieldsets = (
        ('Bot', {
            'fields': ('bot',)
        }),
        ('User Information', {
            'fields': ('chat_id', 'username', 'first_name', 'last_name', 'language_code')
        }),
        ('Profile Data', {
            'fields': ('phone_number', 'bio', 'profile_photo')
        }),
        ('Flow State', {
            'fields': ('user_state', 'state_data'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_blocked', 'first_interaction', 'last_interaction')
        }),
    )


@admin.register(BotFlow)
class BotFlowAdmin(ModelAdmin):
    list_display = ['name', 'bot', 'trigger_command', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_default', 'bot', 'created_at']
    search_fields = ['name', 'description', 'trigger_command']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Flow Information', {
            'fields': ('bot', 'name', 'description')
        }),
        ('Flow Configuration', {
            'fields': ('flow_data', 'trigger_command')
        }),
        ('Settings', {
            'fields': ('is_default', 'is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(BotMessage)
class BotMessageAdmin(ModelAdmin):
    list_display = ['bot', 'user', 'message_type', 'direction', 'text_preview', 'created_at']
    list_filter = ['message_type', 'direction', 'bot', 'created_at']
    search_fields = ['text', 'user__username', 'user__chat_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('bot', 'user', 'flow')
        }),
        ('Message Content', {
            'fields': ('message_type', 'direction', 'text', 'file_url')
        }),
        ('Metadata', {
            'fields': ('telegram_message_id', 'created_at')
        }),
    )
    
    def text_preview(self, obj):
        if obj.text:
            return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
        return '-'
    text_preview.short_description = 'Text Preview'
