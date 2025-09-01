import os
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///amazon_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Timezone settings
    TIMEZONE = os.getenv('TIMEZONE', 'US/Eastern')  # EST/EDT
    TZ = pytz.timezone(TIMEZONE)
    
    # Scraping settings
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 6))
    PRICE_CHANGE_THRESHOLD = float(os.getenv('PRICE_CHANGE_THRESHOLD', 5.0))  # Percentage
    
    # Slack settings
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '#price-alerts')
    
    # Notification settings
    ENABLE_SLACK_NOTIFICATIONS = bool(os.getenv('ENABLE_SLACK_NOTIFICATIONS', 'True').lower() == 'true')
    
    # Amazon settings
    AMAZON_BASE_URL = 'https://www.amazon.com'
    
    # Rate limiting
    MIN_SCRAPE_DELAY = 2  # Minimum seconds between requests
    MAX_SCRAPE_DELAY = 5  # Maximum seconds between requests
