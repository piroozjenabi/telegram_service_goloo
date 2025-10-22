from django.db import models
import uuid
from django.utils import timezone


class TelegramBot(models.Model):
    """Main bot configuration"""
    
    BOT_TYPE_CHOICES = [
        ('simple', 'Simple Bot'),
        ('registration', 'Registration Bot'),
        ('survey', 'Survey Bot'),
        ('support', 'Support Bot'),
        ('ecommerce', 'E-commerce Bot'),
        ('custom', 'Custom Bot'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=True)
    
    # Bot Type and Configuration
    bot_type = models.CharField(
        max_length=50, 
        choices=BOT_TYPE_CHOICES, 
        default='simple',
        help_text="Type of bot determines the flow handling strategy"
    )
    
    # Welcome Message Configuration
    has_welcome_message = models.BooleanField(
        default=True,
        help_text="Send welcome message on /start"
    )
    welcome_message_text = models.TextField(
        blank=True,
        null=True,
        help_text="Welcome message text (supports markdown)"
    )
    
    # Phone Number Collection
    has_get_number = models.BooleanField(
        default=False,
        help_text="Request phone number after welcome message"
    )
    get_number_text = models.TextField(
        blank=True,
        null=True,
        default="Please share your phone number to continue.",
        help_text="Text to show when requesting phone number"
    )
    after_phone_number_text = models.TextField(
        blank=True,
        null=True,
        default="✅ Thank you! Your phone number has been saved.",
        help_text="Message to show after phone number is received"
    )
    
    # Statistics
    user_count = models.IntegerField(default=0)
    request_count = models.IntegerField(default=0)
    
    # Webhook configuration
    auto_setup_webhook = models.BooleanField(
        default=True,
        help_text="Automatically setup webhook when bot is saved"
    )
    is_webhook_set = models.BooleanField(default=False)
    webhook_url = models.URLField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Telegram Bot"
        verbose_name_plural = "Telegram Bots"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (@{self.username})"
    
    def increment_request_count(self):
        self.request_count += 1
        self.save(update_fields=['request_count'])


class BotUser(models.Model):
    """Bot users - stores telegram user data"""
    
    USER_STATE_CHOICES = [
        ('new', 'New User'),
        ('welcomed', 'Welcomed'),
        ('awaiting_phone', 'Awaiting Phone Number'),
        ('registered', 'Registered'),
        ('active', 'Active'),
        ('blocked', 'Blocked'),
    ]
    
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE, related_name='users')
    chat_id = models.BigIntegerField()
    
    # User data
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    
    # Profile data
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.URLField(blank=True, null=True)
    
    # User State for Flow Management
    user_state = models.CharField(
        max_length=50,
        choices=USER_STATE_CHOICES,
        default='new',
        help_text="Current state in the bot flow"
    )
    state_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional state data for flow processing"
    )
    
    # Status
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    first_interaction = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bot User"
        verbose_name_plural = "Bot Users"
        unique_together = ['bot', 'chat_id']
        ordering = ['-last_interaction']
    
    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} (@{self.username}) - {self.chat_id}"


class BotFlow(models.Model):
    """Bot conversation flows - JSON based flow configuration"""
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE, related_name='flows')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Flow configuration as JSON
    flow_data = models.JSONField(
        help_text="JSON structure defining the bot flow logic"
    )
    
    # Flow settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    trigger_command = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bot Flow"
        verbose_name_plural = "Bot Flows"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bot.name} - {self.name}"


class BotMessage(models.Model):
    """Store bot messages for analytics"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('voice', 'Voice'),
        ('sticker', 'Sticker'),
        ('location', 'Location'),
        ('contact', 'Contact'),
    ]
    
    DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='messages')
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    
    # Message content
    text = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    
    # Metadata
    telegram_message_id = models.BigIntegerField()
    flow = models.ForeignKey(BotFlow, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bot Message"
        verbose_name_plural = "Bot Messages"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bot', 'user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.direction} - {self.message_type} - {self.created_at}"
