#!/usr/bin/env python3
"""
Check what channels the Slack bot has access to
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

def check_bot_permissions():
    print("🔄 Checking Slack Bot Permissions...")
    
    client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    
    try:
        # Test authentication
        auth_response = client.auth_test()
        print(f"✅ Bot authenticated as: {auth_response['user']}")
        print(f"📝 Bot User ID: {auth_response['user_id']}")
        print(f"🏢 Team: {auth_response['team']}")
        
        # Get bot info
        bot_info = client.bots_info(bot=auth_response['user_id'])
        print(f"🤖 Bot Name: {bot_info['bot']['name']}")
        
        # List conversations the bot is in
        print("\n📂 Checking accessible channels...")
        conversations = client.conversations_list(types="public_channel,private_channel")
        
        accessible_channels = []
        for channel in conversations['channels']:
            try:
                # Try to get channel info to see if bot has access
                channel_info = client.conversations_info(channel=channel['id'])
                if channel_info['ok']:
                    accessible_channels.append(f"#{channel['name']}")
            except SlackApiError:
                pass  # Bot doesn't have access to this channel
        
        if accessible_channels:
            print(f"✅ Bot has access to: {', '.join(accessible_channels)}")
            print(f"\n💡 Try changing SLACK_CHANNEL to one of these channels")
        else:
            print("❌ Bot doesn't have access to any channels")
            print("\n🔧 Solution: Invite the bot to a channel:")
            print("   1. Go to any Slack channel")
            print("   2. Type: /invite @your-bot-name")
            print("   3. Or go to channel settings → Integrations → Add apps")
        
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_bot_permissions()
