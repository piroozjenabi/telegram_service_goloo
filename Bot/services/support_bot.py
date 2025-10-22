"""
Support Bot Service - Handles customer support interactions
"""
from .base import BaseBotService
from typing import Dict, Any


class SupportBotService(BaseBotService):
    """Bot that handles customer support tickets"""
    
    async def handle_text(self, text: str, message_data: Dict[str, Any]) -> None:
        """Handle support messages"""
        
        state = self.bot_user.user_state
        
        if state == 'new':
            await self.send_message("Please use /start to begin.")
        
        elif state == 'welcomed':
            if self.bot.has_get_number and not self.bot_user.phone_number:
                await self.request_phone_number()
            else:
                await self.show_support_menu()
        
        elif state == 'awaiting_phone':
            await self.send_message("Please use the button to share your phone number.")
        
        elif state == 'support_menu':
            await self.handle_menu_selection(text)
        
        elif state == 'creating_ticket':
            await self.create_support_ticket(text)
        
        else:
            await self.show_support_menu()
    
    async def after_phone_number_received(self) -> None:
        """Called after phone number is received"""
        await self.show_support_menu()
    
    async def show_support_menu(self) -> None:
        """Show support menu options"""
        menu = "🎧 Support Menu\n\n"
        menu += "1. Create a ticket\n"
        menu += "2. Check ticket status\n"
        menu += "3. FAQ\n"
        menu += "4. Contact support\n\n"
        menu += "Please enter a number (1-4):"
        
        await self.send_message(menu)
        self.bot_user.user_state = 'support_menu'
        self.bot_user.save(update_fields=['user_state'])
    
    async def handle_menu_selection(self, text: str) -> None:
        """Handle menu selection"""
        
        if text == '1':
            await self.send_message("Please describe your issue:")
            self.bot_user.user_state = 'creating_ticket'
            self.bot_user.save(update_fields=['user_state'])
        
        elif text == '2':
            await self.check_ticket_status()
        
        elif text == '3':
            await self.show_faq()
        
        elif text == '4':
            await self.show_contact_info()
        
        else:
            await self.send_message("Invalid option. Please enter 1-4.")
    
    async def create_support_ticket(self, issue_description: str) -> None:
        """Create a support ticket"""
        # Save ticket info in state_data
        state_data = self.bot_user.state_data or {}
        ticket_id = f"TKT-{self.bot_user.id}-{len(state_data.get('tickets', []))}"
        
        ticket = {
            'id': ticket_id,
            'description': issue_description,
            'status': 'open'
        }
        
        if 'tickets' not in state_data:
            state_data['tickets'] = []
        state_data['tickets'].append(ticket)
        
        self.bot_user.state_data = state_data
        self.bot_user.user_state = 'registered'
        self.bot_user.save(update_fields=['state_data', 'user_state'])
        
        message = f"✅ Ticket created!\n\n"
        message += f"Ticket ID: {ticket_id}\n"
        message += f"Status: Open\n\n"
        message += "Our team will respond shortly."
        
        await self.send_message(message)
    
    async def check_ticket_status(self) -> None:
        """Check status of user's tickets"""
        state_data = self.bot_user.state_data or {}
        tickets = state_data.get('tickets', [])
        
        if not tickets:
            await self.send_message("You don't have any tickets.")
        else:
            message = "Your tickets:\n\n"
            for ticket in tickets:
                message += f"ID: {ticket['id']}\n"
                message += f"Status: {ticket['status']}\n"
                message += f"Description: {ticket['description'][:50]}...\n\n"
            
            await self.send_message(message)
    
    async def show_faq(self) -> None:
        """Show FAQ"""
        faq = "❓ Frequently Asked Questions\n\n"
        faq += "Q: How do I reset my password?\n"
        faq += "A: Use the 'Forgot Password' link on the login page.\n\n"
        faq += "Q: How long does shipping take?\n"
        faq += "A: Usually 3-5 business days.\n\n"
        faq += "Q: How do I contact support?\n"
        faq += "A: Select option 4 from the menu."
        
        await self.send_message(faq)
    
    async def show_contact_info(self) -> None:
        """Show contact information"""
        contact = "📞 Contact Information\n\n"
        contact += "Email: support@example.com\n"
        contact += "Phone: +1-234-567-8900\n"
        contact += "Hours: Mon-Fri 9AM-5PM"
        
        await self.send_message(contact)
