@echo off
echo ====================================
echo  Amazon Price Tracker - START
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

echo Starting Amazon Price Tracker...
echo Web interface will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

REM Start the development server
"C:/Program Files/Python311/python.exe" run_dev.py

REM If the server stops, show message
echo.
echo ====================================
echo Server stopped.
echo ====================================
pause
