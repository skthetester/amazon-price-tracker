@echo off
echo ====================================
echo  Amazon Price Tracker - SETUP
echo ====================================
echo.

echo Checking Python installation...
"C:/Program Files/Python311/python.exe" --version
if %errorlevel% neq 0 (
    echo Error: Python not found!
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

echo.
echo Installing required packages...
"C:/Program Files/Python311/python.exe" -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install packages!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Running setup script...
"C:/Program Files/Python311/python.exe" setup.py

echo.
echo Initializing database...
"C:/Program Files/Python311/python.exe" database/init_db.py

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run start_server.bat to start development server
echo 3. Or run start_production.bat for production mode
echo.
echo Optional: Run the following to add sample data:
echo   python database/sample_data.py
echo.
pause
