from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Bot'
    
    def ready(self):
        """Import signals when app is ready"""
        import Bot.signals  # noqa
