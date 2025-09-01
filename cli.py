#!/usr/bin/env python3
"""
Command-line interface for Amazon Price Tracker
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import app
from database.models import db
from database.db_manager import DatabaseManager
from scraper.amazon_scraper import AmazonScraper
from notifications.slack_notifier import SlackNotifier
import pytz

# EST timezone
EST = pytz.timezone('US/Eastern')

def add_product_cli(name, url, target_price=None):
    """Add a product via CLI"""
    with app.app_context():
        try:
            scraper = AmazonScraper()
            
            # Extract ASIN
            asin = scraper.extract_asin_from_url(url)
            if not asin:
                print("✗ Could not extract ASIN from URL")
                return False
            
            # Check if already exists
            existing = DatabaseManager.get_product_by_asin(asin)
            if existing:
                print(f"✗ Product with ASIN {asin} already exists")
                return False
            
            # Scrape initial info
            print("Scraping product information...")
            product_info = scraper.scrape_product(url)
            
            if product_info and product_info.get('name') and not name:
                name = product_info['name']
            
            # Add product
            product = DatabaseManager.add_product(
                name=name,
                amazon_url=url,
                asin=asin,
                target_price=target_price,
                image_url=product_info.get('image_url') if product_info else None
            )
            
            # Add initial price
            if product_info and product_info.get('price'):
                DatabaseManager.update_product_price(product.id, product_info['price'])
                print(f"✓ Added product: {name} (${product_info['price']:.2f})")
            else:
                print(f"✓ Added product: {name} (price not available)")
            
            return True
            
        except Exception as e:
            print(f"✗ Error adding product: {e}")
            return False

def list_products():
    """List all tracked products"""
    with app.app_context():
        products = DatabaseManager.get_all_products()
        
        if not products:
            print("No products tracked yet")
            return
        
        print(f"\nTracked Products ({len(products)}):")
        print("-" * 80)
        
        for product in products:
            current = f"${product.current_price:.2f}" if product.current_price else "N/A"
            target = f"${product.target_price:.2f}" if product.target_price else "None"
            
            print(f"ID: {product.id}")
            print(f"Name: {product.name}")
            print(f"ASIN: {product.asin}")
            print(f"Current Price: {current}")
            print(f"Target Price: {target}")
            print(f"Updated: {product.updated_at.strftime('%Y-%m-%d %H:%M')}")
            print("-" * 80)

def check_prices():
    """Check prices for all products"""
    with app.app_context():
        try:
            products = DatabaseManager.get_all_products()
            scraper = AmazonScraper()
            slack_notifier = SlackNotifier()
            
            print(f"Checking prices for {len(products)} products...")
            
            for i, product in enumerate(products, 1):
                print(f"[{i}/{len(products)}] Checking: {product.name}")
                
                try:
                    product_info = scraper.scrape_product(product.amazon_url)
                    
                    if product_info and product_info.get('price'):
                        old_price = product.current_price
                        new_price = product_info['price']
                        
                        DatabaseManager.update_product_price(product.id, new_price)
                        
                        print(f"  Price: ${new_price:.2f}")
                        
                        if old_price:
                            change = new_price - old_price
                            change_percent = (change / old_price) * 100
                            direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                            print(f"  Change: {direction} ${change:+.2f} ({change_percent:+.1f}%)")
                        
                    else:
                        print("  ✗ Could not scrape price")
                        
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                
                # Small delay between products
                import time
                time.sleep(2)
            
            print("✓ Price check completed")
            
        except Exception as e:
            print(f"✗ Error checking prices: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Amazon Price Tracker CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add product command
    add_parser = subparsers.add_parser('add', help='Add a new product')
    add_parser.add_argument('url', help='Amazon product URL')
    add_parser.add_argument('--name', help='Product name (optional)')
    add_parser.add_argument('--target', type=float, help='Target price (optional)')
    
    # List products command
    list_parser = subparsers.add_parser('list', help='List all tracked products')
    
    # Check prices command
    check_parser = subparsers.add_parser('check', help='Check all product prices now')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        success = add_product_cli(args.name, args.url, args.target)
        sys.exit(0 if success else 1)
    elif args.command == 'list':
        list_products()
    elif args.command == 'check':
        check_prices()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
