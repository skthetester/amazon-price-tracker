@echo off
echo ====================================
echo  Amazon Price Tracker - PRODUCTION
echo ====================================
echo.

REM Check if Python is available
"C:/Program Files/Python311/python.exe" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found at "C:/Program Files/Python311/python.exe"
    echo Please check your Python installation.
    pause
    exit /b 1
)

REM Check if production env file exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Copying from .env.example...
    copy ".env.example" ".env"
    echo.
    echo Please edit .env file with your actual configuration before running again.
    pause
    exit /b 1
)

echo Starting Amazon Price Tracker (Production Mode)...
echo Web interface will be available at: http://localhost:5000
echo.
echo Features enabled:
echo - Background price monitoring every 6 hours
echo - Slack notifications (if configured)
echo - Database cleanup and maintenance
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

REM Set environment for production
set FLASK_ENV=production
set DEBUG=False

REM Start the production server
"C:/Program Files/Python311/python.exe" main.py

REM If the server stops, show message
echo.
echo ====================================
echo Production server stopped.
echo ====================================
pause
