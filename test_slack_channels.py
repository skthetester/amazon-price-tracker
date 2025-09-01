#!/usr/bin/env python3
"""
Test Slack bot with different channels
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

def test_channels():
    print("🔄 Testing Slack Bot Access to Different Channels...")
    
    client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    
    # Common channel names to try
    channels_to_try = ['#general', '#random', '#price-alerts', '#test', '#notifications']
    
    for channel in channels_to_try:
        try:
            print(f"\n📝 Testing channel: {channel}")
            
            # Try to send a simple test message
            response = client.chat_postMessage(
                channel=channel,
                text="🤖 Test message from Amazon Price Tracker bot - please ignore!"
            )
            
            if response['ok']:
                print(f"✅ SUCCESS! Bot can post to {channel}")
                print(f"💡 Update your .env file: SLACK_CHANNEL={channel}")
                return channel
                
        except SlackApiError as e:
            error_msg = e.response['error']
            if error_msg == 'not_in_channel':
                print(f"❌ Bot not in {channel} - use `/invite @autobot` in that channel")
            elif error_msg == 'channel_not_found':
                print(f"❌ Channel {channel} doesn't exist")
            elif error_msg == 'invalid_auth':
                print(f"❌ Authentication failed")
                break
            else:
                print(f"❌ Error: {error_msg}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print(f"\n🔧 No accessible channels found. Please:")
    print(f"   1. Go to any Slack channel")
    print(f"   2. Type: /invite @autobot")
    print(f"   3. Run this test again")
    
    return None

if __name__ == "__main__":
    working_channel = test_channels()
