#!/usr/bin/env python3
"""
Database initialization script for Amazon Price Tracker
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app
from database.models import db, Product, PriceHistory

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['product', 'price_history']
            for table in expected_tables:
                if table in tables:
                    print(f"✓ Table '{table}' exists")
                else:
                    print(f"✗ Table '{table}' missing")
            
            print(f"\nDatabase location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("Initializing Amazon Price Tracker database...")
    success = init_database()
    if success:
        print("✓ Database initialization completed successfully")
    else:
        print("✗ Database initialization failed")
        sys.exit(1)
