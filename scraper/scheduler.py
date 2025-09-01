from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database.models import db, Product
from database.db_manager import DatabaseManager
from scraper.amazon_scraper import AmazonScraper
from notifications.slack_notifier import SlackNotifier
from config.settings import Config
import logging
import time
import random
from datetime import datetime, timedelta
import pytz

# EST timezone  
EST = pytz.timezone('US/Eastern')

class PriceScheduler:
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.scraper = AmazonScraper()
        self.slack_notifier = SlackNotifier()
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start the scheduler"""
        try:
            # Schedule price checks every N hours as configured
            self.scheduler.add_job(
                func=self.check_all_prices,
                trigger=IntervalTrigger(hours=Config.SCRAPE_INTERVAL_HOURS),
                id='price_check_job',
                name='Check all product prices',
                replace_existing=True
            )
            
            # Schedule daily cleanup at 3 AM
            self.scheduler.add_job(
                func=self.cleanup_old_data,
                trigger='cron',
                hour=3,
                minute=0,
                id='cleanup_job',
                name='Clean up old price data',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.logger.info(f"Price scheduler started - checking every {Config.SCRAPE_INTERVAL_HOURS} hours")
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            self.logger.info("Price scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    def check_all_prices(self):
        """Check prices for all active products"""
        with self.app.app_context():
            try:
                products = DatabaseManager.get_all_products()
                self.logger.info(f"Starting price check for {len(products)} products")
                
                for product in products:
                    try:
                        self.check_product_price(product)
                        # Add delay between requests to avoid being blocked
                        time.sleep(random.uniform(Config.MIN_SCRAPE_DELAY, Config.MAX_SCRAPE_DELAY))
                    except Exception as e:
                        self.logger.error(f"Error checking price for product {product.id}: {e}")
                        if Config.ENABLE_SLACK_NOTIFICATIONS:
                            self.slack_notifier.send_error_alert(product, str(e))
                
                self.logger.info("Completed price check cycle")
                
            except Exception as e:
                self.logger.error(f"Error in check_all_prices: {e}")
    
    def check_product_price(self, product):
        """Check price for a single product"""
        try:
            self.logger.info(f"Checking price for: {product.name}")
            
            # Scrape current price
            product_info = self.scraper.scrape_product(product.amazon_url)
            
            if not product_info or not product_info.get('price'):
                self.logger.warning(f"Could not scrape price for product {product.id}")
                return
            
            new_price = product_info['price']
            old_price = product.current_price
            
            # Update price in database
            DatabaseManager.update_product_price(product.id, new_price)
            
            self.logger.info(f"Price updated for {product.name}: ${new_price:.2f}")
            
            # Check for significant price changes
            if old_price and Config.ENABLE_SLACK_NOTIFICATIONS:
                price_change_percent = ((new_price - old_price) / old_price) * 100
                
                # Send notification for significant price changes
                if abs(price_change_percent) >= Config.PRICE_CHANGE_THRESHOLD:
                    self.slack_notifier.send_price_drop_alert(
                        product, old_price, new_price, price_change_percent
                    )
                
                # Send notification if target price is reached
                if product.target_price and new_price <= product.target_price:
                    self.slack_notifier.send_target_price_alert(product)
            
        except Exception as e:
            self.logger.error(f"Error checking product {product.id}: {e}")
            raise
    
    def cleanup_old_data(self):
        """Clean up old price history data (keep last 90 days)"""
        with self.app.app_context():
            try:
                from database.models import PriceHistory, get_est_now
                
                cutoff_date = get_est_now() - timedelta(days=90)
                
                old_entries = PriceHistory.query.filter(
                    PriceHistory.timestamp < cutoff_date
                ).delete()
                
                db.session.commit()
                
                self.logger.info(f"Cleaned up {old_entries} old price history entries")
                
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        return {
            'running': self.scheduler.running if self.scheduler else False,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ] if self.scheduler else []
        }
