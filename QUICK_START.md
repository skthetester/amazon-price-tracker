# Amazon Price Tracker - Quick Start Guide

## 🚀 Windows Batch Files

### Initial Setup
```
Double-click: setup_project.bat
```
- Installs all required Python packages
- Sets up the database
- Creates configuration files
- **Run this first!**

### Start Development Server
```
Double-click: start_server.bat
```
- Starts the web application in development mode
- Auto-reloads when you make code changes
- Runs at: http://localhost:5000
- Shows debug information

### Start Production Server
```
Double-click: start_production.bat
```
- Starts the application in production mode
- Enables background price monitoring every 6 hours
- Enables Slack notifications (if configured)
- Optimized for 24/7 operation

### Stop Server
```
Double-click: stop_server.bat
```
- Safely stops all running Python processes
- Stops both development and production servers
- Use this to completely shut down the application

## ⏰ Time Zone: Eastern Standard Time (EST)

All timestamps in the application now display in EST/EDT:
- Database stores times in EST
- Web interface shows "EST" suffix
- Charts and statistics use EST
- Slack notifications include EST times

## 📝 Usage Examples

1. **First time setup:**
   - Run `setup_project.bat`
   - Edit `.env` file for Slack (optional)
   - Run `start_server.bat`

2. **Daily use:**
   - Run `start_server.bat` to start
   - Open http://localhost:5000 in browser
   - Add Amazon product URLs
   - Run `stop_server.bat` when done

3. **24/7 monitoring:**
   - Configure `.env` with Slack settings
   - Run `start_production.bat`
   - Leave running for automatic price checks

## 🔧 Configuration

Edit `.env` file to customize:
```
TIMEZONE=US/Eastern          # Time zone (EST/EDT)
SCRAPE_INTERVAL_HOURS=6      # How often to check prices
PRICE_CHANGE_THRESHOLD=5     # % change to trigger alerts
SLACK_BOT_TOKEN=your-token   # Slack integration
SLACK_CHANNEL=#price-alerts  # Slack channel for alerts
```
