"""
Bot Service Factory - Creates appropriate bot service based on bot type
"""
from telegram import Bot as TelegramBotClient
from .base import BaseBotService
from .simple_bot import SimpleBotService
from .registration_bot import RegistrationBotService
from .survey_bot import SurveyBotService
from .support_bot import SupportBotService
from .custom_bot import CustomBotService


class BotServiceFactory:
    """Factory for creating bot service instances based on bot type"""
    
    # Map bot types to service classes
    SERVICE_MAP = {
        'simple': SimpleBotService,
        'registration': RegistrationBotService,
        'survey': SurveyBotService,
        'support': SupportBotService,
        'ecommerce': CustomBotService,  # Use custom for ecommerce
        'custom': CustomBotService,
    }
    
    @classmethod
    def create_service(cls, bot, bot_user, telegram_client: TelegramBotClient) -> BaseBotService:
        """
        Create appropriate bot service based on bot type
        
        Args:
            bot: TelegramBot model instance
            bot_user: BotUser model instance
            telegram_client: Telegram Bot API client
        
        Returns:
            BaseBotService instance
        """
        bot_type = bot.bot_type
        service_class = cls.SERVICE_MAP.get(bot_type, SimpleBotService)
        
        return service_class(bot, bot_user, telegram_client)
    
    @classmethod
    def register_service(cls, bot_type: str, service_class: type):
        """
        Register a new bot service type
        
        Args:
            bot_type: Type identifier
            service_class: Service class to handle this type
        """
        cls.SERVICE_MAP[bot_type] = service_class
    
    @classmethod
    def get_available_types(cls):
        """Get list of available bot types"""
        return list(cls.SERVICE_MAP.keys())
