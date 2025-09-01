#!/usr/bin/env python3
"""
Simple startup script that runs from the project root
"""

import os
import sys
from flask import Flask

# Ensure we're in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

# Import and run the app
from app.app import app

if __name__ == '__main__':
    print(f"Starting from: {os.getcwd()}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    
    # Create database tables
    with app.app_context():
        from database.models import db
        db.create_all()
        print("Database tables created/verified")
    
    # Initialize scheduler
    from app.app import price_scheduler
    import threading
    import logging
    
    def init_scheduler():
        """Initialize and start the price scheduler"""
        try:
            with app.app_context():
                price_scheduler.start()
                logging.info("Price scheduler initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize scheduler: {e}")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=init_scheduler, daemon=True)
    scheduler_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
