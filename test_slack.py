#!/usr/bin/env python3
"""
Test Slack connection independently
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our Slack notifier
from notifications.slack_notifier import SlackNotifier

def test_slack_connection():
    print("🔄 Testing Slack Connection...")
    print(f"Bot Token: {os.getenv('SLACK_BOT_TOKEN', 'NOT SET')[:20]}...")
    print(f"Channel: {os.getenv('SLACK_CHANNEL', 'NOT SET')}")
    print(f"Notifications Enabled: {os.getenv('ENABLE_SLACK_NOTIFICATIONS', 'NOT SET')}")
    
    notifier = SlackNotifier()
    
    # Test authentication
    try:
        success = notifier.test_connection()
        if success:
            print("✅ Slack connection successful!")
            
            # Try to send a test message
            print("\n🔄 Sending test message...")
            
            # Create a dummy product for testing
            class TestProduct:
                def __init__(self):
                    self.name = "Test Product - Amazon Price Tracker"
                    self.amazon_url = "https://amazon.com/test"
                    self.target_price = 85.00
                    self.id = 999
            
            test_product = TestProduct()
            
            message_success = notifier.send_price_drop_alert(
                test_product,
                old_price=109.99,
                new_price=99.99,
                price_change_percent=-9.1
            )
            
            if message_success:
                print("✅ Test message sent successfully!")
                print("📱 Check your Slack channel for the notification.")
            else:
                print("❌ Failed to send test message")
                
        else:
            print("❌ Slack connection failed!")
            print("\n🔧 Troubleshooting steps:")
            print("1. Check that your SLACK_BOT_TOKEN is correct")
            print("2. Ensure the bot has been added to your workspace")
            print("3. Verify the bot has permission to post messages")
            print("4. Check that the channel exists and bot has access")
            
    except Exception as e:
        print(f"❌ Error testing Slack: {e}")

if __name__ == "__main__":
    test_slack_connection()
