@echo off
echo ====================================
echo  Amazon Price Tracker - STOP
echo ====================================
echo.

echo Stopping Amazon Price Tracker server...

REM Find and kill Python processes running the price tracker
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /i "python.exe"') do (
    echo Stopping process %%i
    taskkill /pid %%i /f >nul 2>&1
)

REM Also try to kill by process name
taskkill /im python.exe /f >nul 2>&1

echo.
echo Server stopped successfully.
echo.
echo You can restart the server by running start_server.bat
echo ====================================
pause
