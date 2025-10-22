"""
Base Bot Service - Abstract class for all bot type handlers
"""
from abc import ABC, abstractmethod
from telegram import Bot as TelegramBotClient, ReplyKeyboardMarkup, KeyboardButton
from typing import Dict, Any, Optional


class BaseBotService(ABC):
    """Base class for bot service handlers"""
    
    def __init__(self, bot, bot_user, telegram_client: TelegramBotClient):
        """
        Initialize bot service
        
        Args:
            bot: TelegramBot model instance
            bot_user: BotUser model instance
            telegram_client: Telegram Bot API client
        """
        self.bot = bot
        self.bot_user = bot_user
        self.telegram_client = telegram_client
    
    async def handle_message(self, message_data: Dict[str, Any]) -> None:
        """
        Main entry point for handling incoming messages
        
        Args:
            message_data: Telegram message data
        """
        text = message_data.get('text', '')
        
        # Check if it's a command
        if text.startswith('/'):
            await self.handle_command(text, message_data)
        else:
            await self.handle_text(text, message_data)
    
    async def handle_command(self, command: str, message_data: Dict[str, Any]) -> None:
        """Handle bot commands"""
        command_name = command.split()[0].lower()
        
        if command_name == '/start':
            await self.handle_start(message_data)
        elif command_name == '/help':
            await self.handle_help(message_data)
        else:
            await self.handle_custom_command(command_name, message_data)
    
    async def handle_start(self, message_data: Dict[str, Any]) -> None:
        """Handle /start command"""
        # If phone number is required and not yet provided
        if self.bot.has_get_number and not self.bot_user.phone_number:
            # Combine welcome message with phone request in one message
            combined_message = ""
            if self.bot.has_welcome_message and self.bot.welcome_message_text:
                combined_message = self.bot.welcome_message_text + "\n\n"
            
            combined_message += self.bot.get_number_text or "Please share your phone number to continue."
            
            # Send combined message with phone button
            from telegram import ReplyKeyboardMarkup, KeyboardButton
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton("📱 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            
            await self.telegram_client.send_message(
                chat_id=self.bot_user.chat_id,
                text=combined_message,
                reply_markup=keyboard
            )
            
            self.bot_user.user_state = 'awaiting_phone'
            self.bot_user.save(update_fields=['user_state'])
        else:
            # Phone already provided or not required - show welcome or registered message
            if self.bot_user.phone_number:
                # User already registered
                welcome_back = f"Welcome back! 👋\n\nYour phone: {self.bot_user.phone_number}"
                await self.send_message(welcome_back)
                self.bot_user.user_state = 'registered'
                self.bot_user.save(update_fields=['user_state'])
            elif self.bot.has_welcome_message and self.bot.welcome_message_text:
                # Just send welcome message
                await self.send_message(self.bot.welcome_message_text)
                self.bot_user.user_state = 'welcomed'
                self.bot_user.save(update_fields=['user_state'])
    
    async def handle_help(self, message_data: Dict[str, Any]) -> None:
        """Handle /help command"""
        help_text = "Available commands:\n/start - Start the bot\n/help - Show this help"
        await self.send_message(help_text)
    
    async def request_phone_number(self) -> None:
        """Request phone number from user"""
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Share Phone Number", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        text = self.bot.get_number_text or "Please share your phone number to continue."
        
        await self.telegram_client.send_message(
            chat_id=self.bot_user.chat_id,
            text=text,
            reply_markup=keyboard
        )
        
        self.bot_user.user_state = 'awaiting_phone'
        self.bot_user.save(update_fields=['user_state'])
    
    async def handle_contact(self, contact_data: Dict[str, Any]) -> None:
        """Handle contact (phone number) sharing"""
        from telegram import ReplyKeyboardRemove
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"handle_contact called with: {contact_data}")
        phone_number = contact_data.get('phone_number')
        logger.info(f"Extracted phone number: {phone_number}")
        
        if phone_number:
            self.bot_user.phone_number = phone_number
            self.bot_user.user_state = 'registered'
            self.bot_user.save(update_fields=['phone_number', 'user_state'])
            
            # Get custom message or use default
            thank_you_message = self.bot.after_phone_number_text or "✅ Thank you! Your phone number has been saved."
            
            # Send message and remove keyboard
            await self.send_message(
                thank_you_message,
                reply_markup=ReplyKeyboardRemove()  # Remove the phone number button
            )
            await self.after_phone_number_received()
    
    async def send_message(self, text: str, **kwargs) -> None:
        """Send message to user"""
        await self.telegram_client.send_message(
            chat_id=self.bot_user.chat_id,
            text=text,
            **kwargs
        )
    
    @abstractmethod
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle regular text messages - must be implemented by subclasses"""
        pass
    
    async def handle_custom_command(self, command: str, message_data: Dict[str, Any]) -> None:
        """Handle custom commands - can be overridden by subclasses"""
        await self.send_message(f"Unknown command: {command}")
    
    async def after_phone_number_received(self) -> None:
        """Called after phone number is received - can be overridden"""
        pass
