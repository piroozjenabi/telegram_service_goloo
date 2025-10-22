#!/usr/bin/env python
"""
Quick test script to verify the bot system setup
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAIN.settings')
django.setup()

from Bot.models import TelegramBot, BotUser, BotFlow, BotMessage
from django.contrib.auth.models import User

def test_models():
    """Test that all models are accessible"""
    print("✓ Testing models...")
    
    # Check model counts
    bot_count = TelegramBot.objects.count()
    user_count = BotUser.objects.count()
    flow_count = BotFlow.objects.count()
    message_count = BotMessage.objects.count()
    
    print(f"  - Telegram Bots: {bot_count}")
    print(f"  - Bot Users: {user_count}")
    print(f"  - Bot Flows: {flow_count}")
    print(f"  - Bot Messages: {message_count}")
    
    return True

def test_admin_user():
    """Check if admin user exists"""
    print("\n✓ Checking admin users...")
    
    admin_count = User.objects.filter(is_superuser=True).count()
    
    if admin_count > 0:
        print(f"  - Found {admin_count} admin user(s)")
        return True
    else:
        print("  ⚠ No admin users found. Run: python manage.py createsuperuser")
        return False

def test_api_import():
    """Test that API can be imported"""
    print("\n✓ Testing API import...")
    
    try:
        from Bot.views import api
        print("  - API imported successfully")
        print(f"  - API endpoints: {len(api._registry)} registered")
        return True
    except Exception as e:
        print(f"  ✗ Error importing API: {e}")
        return False

def main():
    print("=" * 50)
    print("Dynamic Telegram Bot Maker - Setup Test")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(test_models())
        results.append(test_admin_user())
        results.append(test_api_import())
        
        print("\n" + "=" * 50)
        if all(results):
            print("✓ All tests passed! System is ready.")
            print("\nNext steps:")
            print("1. Create admin user: python manage.py createsuperuser")
            print("2. Start server: python manage.py runserver")
            print("3. Access admin: http://localhost:8000/admin")
            print("4. Create your first bot!")
        else:
            print("⚠ Some tests failed. Please check the output above.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
