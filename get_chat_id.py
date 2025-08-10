#!/usr/bin/env python3
"""
Get Your User Chat ID
Run this script to find your personal Telegram user ID.
"""

import asyncio
import os
from telegram import Bot
import json
from dotenv import load_dotenv

async def get_chat_id():
    """Get your chat ID by checking recent updates."""
    
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("\n📝 Please set your bot token:")
        print("1. Create a .env file in the project root")
        print("2. Add: TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("3. Run this script again")
        return
    
    bot = Bot(bot_token)
    
    try:
        print("🔍 Checking for recent messages to find your chat ID...")
        print("Make sure you've sent at least one message to your bot first!\n")
        
        # Get recent updates
        updates = await bot.get_updates()
        
        if not updates:
            print("❌ No recent messages found!")
            print("\n📱 To get your chat ID:")
            print("1. Open Telegram and find your bot: @PySpotGridNotiBot")
            print("2. Send any message to your bot (like 'hello')")
            print("3. Run this script again")
            return
        
        print("📬 Found recent messages:")
        print("=" * 50)
        
        user_ids = set()
        
        for update in updates:
            if update.message:
                user = update.message.from_user
                chat = update.message.chat
                
                # Mask sensitive information in output
                username = f"@{user.username}" if user.username else "[no username]"
                first_name = user.first_name or "[no name]"
                
                print(f"Message from: {first_name} ({username})")
                print(f"User ID: {user.id}")
                print(f"Chat ID: {chat.id}")
                print(f"Chat type: {chat.type}")
                
                # Only show first 50 characters of message to avoid exposing sensitive content
                message_text = update.message.text or "[no text]"
                if len(message_text) > 50:
                    message_text = message_text[:50] + "..."
                print(f"Message preview: {message_text}")
                print("-" * 30)
                
                user_ids.add(user.id)
        
        if user_ids:
            print("\n✅ Found user IDs:")
            for user_id in user_ids:
                print(f"   {user_id}")
            
            print(f"\n📝 Update your .env file:")
            print(f"   DEFAULT_CHAT_IDS={','.join(map(str, user_ids))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await bot.shutdown()

if __name__ == "__main__":
    asyncio.run(get_chat_id())
