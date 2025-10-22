"""
Custom Bot Service - Uses flow-based configuration
"""
from .base import BaseBotService
from typing import Dict, Any


class CustomBotService(BaseBotService):
    """Custom bot that uses BotFlow configurations"""
    
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle text using flow configuration"""
        
        state = self.bot_user.user_state
        
        if state == 'awaiting_phone':
            await self.send_message("Please use the button to share your phone number.")
            return
        
        # Try to find a matching flow
        from Bot.models import BotFlow
        
        # Get default flow
        flow = BotFlow.objects.filter(
            bot=self.bot,
            is_active=True,
            is_default=True
        ).first()
        
        if flow:
            await self.execute_flow(flow, text)
        else:
            await self.send_message("No flow configured for this bot.")
    
    async def handle_custom_command(self, command: str, message_data: Dict[str, Any]) -> None:
        """Handle custom commands using flows"""
        from Bot.models import BotFlow
        
        # Find flow with matching trigger command
        flow = BotFlow.objects.filter(
            bot=self.bot,
            is_active=True,
            trigger_command=command
        ).first()
        
        if flow:
            await self.execute_flow(flow, command)
        else:
            await self.send_message(f"Unknown command: {command}")
    
    async def execute_flow(self, flow, user_input: str) -> None:
        """Execute a bot flow"""
        flow_data = flow.flow_data
        
        # Simple response flow
        if 'response' in flow_data:
            await self.send_message(flow_data['response'])
        
        # Multi-step flow
        elif 'steps' in flow_data:
            await self.execute_multi_step_flow(flow_data, user_input)
        
        # Menu flow
        elif flow_data.get('type') == 'menu':
            await self.execute_menu_flow(flow_data)
    
    async def execute_multi_step_flow(self, flow_data: Dict, user_input: str) -> None:
        """Execute multi-step flow"""
        steps = flow_data.get('steps', [])
        initial_step = flow_data.get('initial_step', 'step1')
        
        # Get current step from user state
        state_data = self.bot_user.state_data or {}
        current_step_id = state_data.get('current_step', initial_step)
        
        # Find current step
        current_step = next((s for s in steps if s['id'] == current_step_id), None)
        
        if current_step:
            # Send message
            await self.send_message(current_step.get('text', ''))
            
            # Save data if needed
            if 'save_to' in current_step:
                state_data[current_step['save_to']] = user_input
            
            # Move to next step
            next_step_id = current_step.get('next')
            if next_step_id:
                state_data['current_step'] = next_step_id
            else:
                # Flow complete
                state_data.pop('current_step', None)
                self.bot_user.user_state = 'registered'
            
            self.bot_user.state_data = state_data
            self.bot_user.save(update_fields=['state_data', 'user_state'])
    
    async def execute_menu_flow(self, flow_data: Dict) -> None:
        """Execute menu flow"""
        text = flow_data.get('text', 'Choose an option:')
        buttons = flow_data.get('buttons', [])
        
        menu_text = text + "\n\n"
        for i, button in enumerate(buttons, 1):
            menu_text += f"{i}. {button.get('text', '')}\n"
        
        await self.send_message(menu_text)
