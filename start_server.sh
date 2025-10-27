#!/bin/bash

echo "==================================="
echo "GDP Forecasting Research Dashboard"
echo "==================================="
echo ""
echo "Starting Flask application..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    exit 1
fi

# Check if required packages are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
fi

# Start the application
echo ""
echo "Starting server..."
echo "Open your browser and visit: http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 app.py

