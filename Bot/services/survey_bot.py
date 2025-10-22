"""
Survey Bot Service - Handles survey/questionnaire flows
"""
from .base import BaseBotService
from typing import Dict, Any


class SurveyBotService(BaseBotService):
    """Bot that conducts surveys with multiple questions"""
    
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle text based on survey state"""
        
        state = self.bot_user.user_state
        state_data = self.bot_user.state_data or {}
        
        if state == 'new':
            await self.send_message("Please use /start to begin the survey.")
        
        elif state == 'welcomed':
            await self.start_survey()
        
        elif state == 'awaiting_phone':
            await self.send_message("Please use the button to share your phone number.")
        
        elif state.startswith('survey_'):
            # Handle survey responses
            await self.handle_survey_response(text, state, state_data)
        
        else:
            await self.send_message("Survey completed! Use /start to take it again.")
    
    async def start_survey(self) -> None:
        """Start the survey"""
        if self.bot.has_get_number and not self.bot_user.phone_number:
            await self.request_phone_number()
        else:
            await self.ask_question_1()
    
    async def after_phone_number_received(self) -> None:
        """Called after phone number is received"""
        await self.ask_question_1()
    
    async def ask_question_1(self) -> None:
        """Ask first survey question"""
        await self.send_message("Question 1: How satisfied are you with our service? (1-5)")
        self.bot_user.user_state = 'survey_q1'
        self.bot_user.save(update_fields=['user_state'])
    
    async def ask_question_2(self) -> None:
        """Ask second survey question"""
        await self.send_message("Question 2: Would you recommend us to others? (Yes/No)")
        self.bot_user.user_state = 'survey_q2'
        self.bot_user.save(update_fields=['user_state'])
    
    async def ask_question_3(self) -> None:
        """Ask third survey question"""
        await self.send_message("Question 3: Any additional comments?")
        self.bot_user.user_state = 'survey_q3'
        self.bot_user.save(update_fields=['user_state'])
    
    async def handle_survey_response(self, text: str, state: str, state_data: Dict) -> None:
        """Handle survey responses"""
        
        if state == 'survey_q1':
            # Save answer to question 1
            state_data['q1_satisfaction'] = text
            self.bot_user.state_data = state_data
            self.bot_user.save(update_fields=['state_data'])
            await self.ask_question_2()
        
        elif state == 'survey_q2':
            # Save answer to question 2
            state_data['q2_recommend'] = text
            self.bot_user.state_data = state_data
            self.bot_user.save(update_fields=['state_data'])
            await self.ask_question_3()
        
        elif state == 'survey_q3':
            # Save answer to question 3
            state_data['q3_comments'] = text
            self.bot_user.state_data = state_data
            self.bot_user.user_state = 'registered'
            self.bot_user.save(update_fields=['state_data', 'user_state'])
            
            await self.send_message("✅ Thank you for completing the survey!")
            await self.show_survey_results(state_data)
    
    async def show_survey_results(self, state_data: Dict) -> None:
        """Show survey results to user"""
        results = "Your responses:\n\n"
        results += f"Satisfaction: {state_data.get('q1_satisfaction', 'N/A')}\n"
        results += f"Recommend: {state_data.get('q2_recommend', 'N/A')}\n"
        results += f"Comments: {state_data.get('q3_comments', 'N/A')}\n"
        
        await self.send_message(results)
