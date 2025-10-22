"""
Simple Bot Service - Basic bot with simple responses
"""
from .base import BaseBotService
from typing import Dict, Any


class SimpleBotService(BaseBotService):
    """Simple bot that responds to messages with basic replies"""
    
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle text messages with simple echo or predefined responses"""
        
        # Check user state
        if self.bot_user.user_state == 'awaiting_phone':
            await self.send_message("Please use the button below to share your phone number.")
            return
        
        # Simple echo response
        response = f"You said: {text}"
        await self.send_message(response)
