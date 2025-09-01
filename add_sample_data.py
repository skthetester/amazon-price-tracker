#!/usr/bin/env python3
"""
Add sample products for screenshot purposes
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.app import app
from database.db_manager import DatabaseManager
from database.models import db, Product, PriceHistory, get_est_now

def add_sample_data():
    """Add sample products and price history for screenshots"""
    
    with app.app_context():
        print("🔄 Adding sample data for screenshots...")
        
        # Sample products with realistic data
        sample_products = [
            {
                'name': 'Apple AirPods Pro (2nd Generation)',
                'amazon_url': 'https://www.amazon.com/dp/B0BDHWDR12',
                'current_price': 199.99,
                'target_price': 179.99,
                'description': 'Wireless Earbuds with Active Noise Cancellation'
            },
            {
                'name': 'Echo Dot (5th Gen) Smart Speaker',
                'amazon_url': 'https://www.amazon.com/dp/B09B8V1LZ3',
                'current_price': 49.99,
                'target_price': 39.99,
                'description': 'Smart speaker with Alexa'
            },
            {
                'name': 'Fire TV Stick 4K Max',
                'amazon_url': 'https://www.amazon.com/dp/B08MQZXN1X',
                'current_price': 54.99,
                'target_price': 39.99,
                'description': 'Streaming device with Wi-Fi 6 support'
            },
            {
                'name': 'Kindle Paperwhite (11th Generation)',
                'amazon_url': 'https://www.amazon.com/dp/B08KTZ8249',
                'current_price': 139.99,
                'target_price': 119.99,
                'description': 'Waterproof e-reader with adjustable warm light'
            }
        ]
        
        # Add products if they don't exist
        for product_data in sample_products:
            existing = Product.query.filter_by(amazon_url=product_data['amazon_url']).first()
            if not existing:
                product = Product(
                    name=product_data['name'],
                    amazon_url=product_data['amazon_url'],
                    current_price=product_data['current_price'],
                    target_price=product_data['target_price'],
                    description=product_data['description'],
                    created_at=get_est_now()
                )
                db.session.add(product)
                db.session.commit()
                
                # Add some sample price history for trends
                add_sample_price_history(product)
                
                print(f"✅ Added: {product.name}")
            else:
                print(f"⏭️  Exists: {product_data['name']}")
        
        print("\n🎯 Sample data added! Your app now has:")
        print("   - Multiple products to showcase")
        print("   - Price history for trend charts") 
        print("   - Different price trends (up/down/stable)")
        print("\n📸 Ready for screenshots at http://localhost:5000")

def add_sample_price_history(product):
    """Add realistic price history for a product"""
    
    base_price = product.current_price
    current_time = get_est_now()
    
    # Generate 30 days of price history
    for days_ago in range(30, 0, -1):
        timestamp = current_time - timedelta(days=days_ago)
        
        # Create realistic price variations
        if days_ago > 20:
            # Older prices - slightly higher on average
            price_variation = random.uniform(-0.05, 0.15)
        elif days_ago > 10:
            # Recent prices - more volatile
            price_variation = random.uniform(-0.12, 0.08)
        else:
            # Very recent - trending toward current price
            price_variation = random.uniform(-0.08, 0.03)
        
        historical_price = base_price * (1 + price_variation)
        historical_price = round(historical_price, 2)
        
        # Ensure price is reasonable (not negative)
        historical_price = max(historical_price, base_price * 0.5)
        
        price_entry = PriceHistory(
            product_id=product.id,
            price=historical_price,
            timestamp=timestamp
        )
        db.session.add(price_entry)
    
    db.session.commit()

if __name__ == "__main__":
    add_sample_data()
