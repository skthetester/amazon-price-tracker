#!/usr/bin/env python3
"""
Setup script for Amazon Price Tracker
"""

import os
import shutil
import sys

def create_env_file():
    """Create .env file from example"""
    env_example = ".env.example"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"✓ {env_file} already exists")
        return
    
    if os.path.exists(env_example):
        shutil.copy(env_example, env_file)
        print(f"✓ Created {env_file} from {env_example}")
        print("  Please edit .env file with your actual configuration")
    else:
        print(f"✗ {env_example} not found")

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        import requests
        import bs4
        import selenium
        import apscheduler
        import plotly
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        return False

def setup_directories():
    """Ensure all necessary directories exist"""
    directories = [
        'static/css',
        'static/js', 
        'static/images',
        'templates',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def main():
    """Run setup"""
    print("Amazon Price Tracker - Setup")
    print("=" * 30)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    setup_directories()
    create_env_file()
    
    if not check_requirements():
        print("\nPlease install missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. For Slack notifications, set SLACK_BOT_TOKEN and SLACK_CHANNEL")
    print("3. Run the application with: python main.py")
    print("4. Open http://localhost:5000 in your browser")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
