"""
Registration Bot Service - Handles user registration flow
"""
from .base import BaseBotService
from typing import Dict, Any


class RegistrationBotService(BaseBotService):
    """Bot that handles user registration with multiple steps"""
    
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle text based on registration state"""
        
        state = self.bot_user.user_state
        
        if state == 'new':
            await self.send_message("Please use /start to begin registration.")
        
        elif state == 'welcomed':
            # After welcome, ask for name if not provided
            if not self.bot_user.first_name:
                await self.ask_for_name()
            elif self.bot.has_get_number and not self.bot_user.phone_number:
                await self.request_phone_number()
            else:
                await self.complete_registration()
        
        elif state == 'awaiting_phone':
            await self.send_message("Please use the button to share your phone number.")
        
        elif state == 'registered':
            await self.handle_registered_user_message(text)
        
        else:
            await self.send_message("I'm not sure what to do. Try /start")
    
    async def ask_for_name(self) -> None:
        """Ask user for their name"""
        await self.send_message("What's your name?")
        self.bot_user.user_state = 'awaiting_name'
        self.bot_user.save(update_fields=['user_state'])
    
    async def after_phone_number_received(self) -> None:
        """Called after phone number is received"""
        await self.complete_registration()
    
    async def complete_registration(self) -> None:
        """Complete the registration process"""
        self.bot_user.user_state = 'registered'
        self.bot_user.save(update_fields=['user_state'])
        
        message = f"✅ Registration complete!\n\n"
        message += f"Name: {self.bot_user.first_name or 'Not provided'}\n"
        if self.bot_user.phone_number:
            message += f"Phone: {self.bot_user.phone_number}\n"
        
        await self.send_message(message)
    
    async def handle_registered_user_message(self, text: str) -> None:
        """Handle messages from registered users"""
        await self.send_message(f"Thanks for your message: {text}")
