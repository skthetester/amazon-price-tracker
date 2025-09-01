#!/usr/bin/env python3
"""
Sample data for testing the Amazon Price Tracker
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.app import app
from database.db_manager import DatabaseManager
from database.models import PriceHistory, db, get_est_now
from datetime import datetime, timedelta
import random
import pytz

# EST timezone
EST = pytz.timezone('US/Eastern')

def add_sample_products():
    """Add sample products for testing"""
    with app.app_context():
        sample_products = [
            {
                'name': 'Echo Dot (5th Gen, 2022 release)',
                'amazon_url': 'https://www.amazon.com/dp/B09B8V1LZ3',
                'asin': 'B09B8V1LZ3',
                'target_price': 35.00,
                'current_price': 49.99
            },
            {
                'name': 'Fire TV Stick 4K Max',
                'amazon_url': 'https://www.amazon.com/dp/B08MQZXN1X',
                'asin': 'B08MQZXN1X', 
                'target_price': 40.00,
                'current_price': 54.99
            },
            {
                'name': 'Kindle Paperwhite (11th Generation)',
                'amazon_url': 'https://www.amazon.com/dp/B08KTZ8249',
                'asin': 'B08KTZ8249',
                'target_price': 100.00,
                'current_price': 139.99
            }
        ]
        
        for product_data in sample_products:
            # Check if product already exists
            existing = DatabaseManager.get_product_by_asin(product_data['asin'])
            if existing:
                print(f"Product {product_data['name']} already exists")
                continue
            
            # Add product
            product = DatabaseManager.add_product(
                name=product_data['name'],
                amazon_url=product_data['amazon_url'],
                asin=product_data['asin'],
                target_price=product_data['target_price']
            )
            
            # Add some sample price history
            base_price = product_data['current_price']
            for i in range(10, 0, -1):
                # Generate price variations over the past 10 days
                price_variation = random.uniform(-5, 5)  # ±$5 variation
                historical_price = base_price + price_variation
                timestamp = get_est_now() - timedelta(days=i)
                
                price_entry = PriceHistory(
                    product_id=product.id,
                    price=historical_price,
                    timestamp=timestamp
                )
                db.session.add(price_entry)
            
            # Set current price
            DatabaseManager.update_product_price(product.id, product_data['current_price'])
            
            print(f"✓ Added sample product: {product_data['name']}")
        
        print(f"✓ Sample data setup complete!")

if __name__ == '__main__':
    print("Adding sample products for testing...")
    add_sample_products()
