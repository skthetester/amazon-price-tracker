#!/usr/bin/env python3
"""
Amazon Price Tracker - Main Application Entry Point

A web application for tracking Amazon product prices with automated monitoring,
notifications, and trend analysis.
"""

import sys
import os
import logging
from flask import Flask

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import app
from scraper.scheduler import PriceScheduler
from config.settings import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_tracker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Application factory"""
    # Initialize scheduler
    scheduler = PriceScheduler(app)
    
    # Add scheduler to app context
    app.scheduler = scheduler
    
    # Start scheduler if not in debug mode or if explicitly enabled
    if not Config.DEBUG or os.getenv('START_SCHEDULER', 'false').lower() == 'true':
        scheduler.start()
        logger.info("Background scheduler started")
    else:
        logger.info("Background scheduler disabled in debug mode")
    
    return app

def main():
    """Main entry point"""
    try:
        # Create application
        app = create_app()
        
        logger.info("Starting Amazon Price Tracker...")
        logger.info(f"Debug mode: {Config.DEBUG}")
        logger.info(f"Database: {Config.SQLALCHEMY_DATABASE_URI}")
        logger.info(f"Scrape interval: {Config.SCRAPE_INTERVAL_HOURS} hours")
        logger.info(f"Slack notifications: {'Enabled' if Config.ENABLE_SLACK_NOTIFICATIONS else 'Disabled'}")
        
        # Run the application
        app.run(
            debug=Config.DEBUG,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to prevent scheduler conflicts
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    finally:
        # Cleanup scheduler on exit
        if hasattr(app, 'scheduler'):
            app.scheduler.stop()
            logger.info("Scheduler stopped")

if __name__ == '__main__':
    main()
