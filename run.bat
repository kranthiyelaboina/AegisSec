@echo off
:: AegisSec Windows Launcher Script
:: Developed by RunTime Terrors

echo.
echo ========================================
echo   🛡️ AegisSec Security Scanner
echo   Developed by RunTime Terrors
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org and try again
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

:: Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo.
    echo 📦 Installing Python dependencies...
    python -m pip install -r requirements.txt --user
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
)

:: Check if config exists
if not exist "config\config.json" (
    echo.
    echo ⚙️ Configuration not found. Running setup...
    python setup.py
    if errorlevel 1 (
        echo ❌ Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
    echo ✅ Setup completed successfully
)

echo.
echo 🚀 Starting AegisSec...
echo.

:: Run the main application
python main.py

echo.
echo Thank you for using AegisSec! 🛡️
pause
