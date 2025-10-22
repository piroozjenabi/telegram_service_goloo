from django.core.management.base import BaseCommand
from Bot.models import TelegramBot
from telegram import Bot as TelegramBotClient
import asyncio


class Command(BaseCommand):
    help = 'Setup webhook for a telegram bot'

    def add_arguments(self, parser):
        parser.add_argument('bot_id', type=str, help='Bot UUID')
        parser.add_argument('webhook_url', type=str, help='Base webhook URL')

    def handle(self, *args, **options):
        bot_id = options['bot_id']
        webhook_url = options['webhook_url']
        
        try:
            bot = TelegramBot.objects.get(id=bot_id)
            
            # Construct full webhook URL
            full_webhook_url = f"{webhook_url}/api/webhook/{bot.id}"
            
            # Setup webhook
            bot_client = TelegramBotClient(token=bot.token)
            asyncio.run(bot_client.set_webhook(url=full_webhook_url))
            
            # Update bot
            bot.webhook_url = full_webhook_url
            bot.is_webhook_set = True
            bot.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully setup webhook for bot {bot.name}')
            )
            self.stdout.write(f'Webhook URL: {full_webhook_url}')
            
        except TelegramBot.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Bot with ID {bot_id} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up webhook: {str(e)}')
            )
