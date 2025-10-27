@echo off
echo ===================================
echo GDP Forecasting Research Dashboard
echo ===================================
echo.
echo Starting Flask application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Start the application
echo.
echo Starting server...
echo Open your browser and visit: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.

python app.py

pause

