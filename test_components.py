#!/usr/bin/env python3
"""
Test script for Amazon Price Tracker components
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.amazon_scraper import AmazonScraper
from notifications.slack_notifier import SlackNotifier
from config.settings import Config

def test_scraper():
    """Test the Amazon scraper with a sample URL"""
    print("Testing Amazon Scraper...")
    scraper = AmazonScraper()
    
    # Test ASIN extraction
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.amazon.com/gp/product/B08N5WRWNW",
        "https://www.amazon.com/Something-Product-Name/dp/B08N5WRWNW/ref=sr_1_1"
    ]
    
    for url in test_urls:
        asin = scraper.extract_asin_from_url(url)
        print(f"URL: {url}")
        print(f"ASIN: {asin}")
        print()
    
    # Test scraping (use a generic Amazon product for testing)
    test_url = "https://www.amazon.com/dp/B08N5WRWNW"  # Echo Dot example
    print(f"Testing scraping with URL: {test_url}")
    
    try:
        result = scraper.scrape_product(test_url)
        if result:
            print("✓ Scraping successful!")
            print(f"Name: {result.get('name', 'N/A')}")
            print(f"Price: ${result.get('price', 'N/A')}")
            print(f"Image: {result.get('image_url', 'N/A')}")
        else:
            print("✗ Scraping failed - no data returned")
    except Exception as e:
        print(f"✗ Scraping error: {e}")

def test_slack():
    """Test Slack notifications"""
    print("\nTesting Slack Notifications...")
    
    if not Config.SLACK_BOT_TOKEN:
        print("✗ No Slack bot token configured")
        return
    
    notifier = SlackNotifier()
    
    # Test connection
    if notifier.test_connection():
        print("✓ Slack connection successful!")
    else:
        print("✗ Slack connection failed")
        return

def test_config():
    """Test configuration"""
    print("\nTesting Configuration...")
    print(f"Database URL: {Config.SQLALCHEMY_DATABASE_URI}")
    print(f"Scrape Interval: {Config.SCRAPE_INTERVAL_HOURS} hours")
    print(f"Price Change Threshold: {Config.PRICE_CHANGE_THRESHOLD}%")
    print(f"Slack Enabled: {Config.ENABLE_SLACK_NOTIFICATIONS}")
    print(f"Slack Channel: {Config.SLACK_CHANNEL}")

def main():
    """Run all tests"""
    print("Amazon Price Tracker - Test Suite")
    print("=" * 40)
    
    test_config()
    test_scraper()
    test_slack()
    
    print("\nTest completed!")

if __name__ == '__main__':
    main()
