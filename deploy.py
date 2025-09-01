#!/usr/bin/env python3
"""
Deployment script for Amazon Price Tracker
"""

import os
import sys
import shutil

def create_production_config():
    """Create production configuration files"""
    
    # Create production environment file
    prod_env = """# Production Environment Configuration
SECRET_KEY=your-production-secret-key-here-change-this
DEBUG=False
DATABASE_URL=sqlite:///amazon_tracker_prod.db

# Slack Configuration (Optional)
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_CHANNEL=#price-alerts
ENABLE_SLACK_NOTIFICATIONS=True

# Scraping Configuration
SCRAPE_INTERVAL_HOURS=4
PRICE_CHANGE_THRESHOLD=3.0
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Performance
START_SCHEDULER=True
"""
    
    with open('.env.production', 'w') as f:
        f.write(prod_env.strip())
    
    print("✓ Created .env.production file")

def create_startup_scripts():
    """Create convenient startup scripts"""
    
    # Windows batch file
    windows_script = """@echo off
echo Starting Amazon Price Tracker...
set FLASK_ENV=production
python main.py
pause
"""
    
    with open('start_windows.bat', 'w') as f:
        f.write(windows_script.strip())
    
    # Linux/Mac shell script
    unix_script = """#!/bin/bash
echo "Starting Amazon Price Tracker..."
export FLASK_ENV=production
python3 main.py
"""
    
    with open('start_unix.sh', 'w') as f:
        f.write(unix_script.strip())
    
    # Make shell script executable
    if os.name != 'nt':
        os.chmod('start_unix.sh', 0o755)
    
    print("✓ Created startup scripts")

def main():
    """Run deployment setup"""
    print("Amazon Price Tracker - Deployment Setup")
    print("=" * 40)
    
    create_production_config()
    create_startup_scripts()
    
    print("\nDeployment files created!")
    print("\nFor production deployment:")
    print("1. Edit .env.production with your actual values")
    print("2. Run: python main.py (or use the startup scripts)")
    print("3. Configure reverse proxy (nginx/Apache) if needed")
    print("4. Set up SSL certificate for HTTPS")

if __name__ == '__main__':
    main()
