"""
Script to run the Flask application with proper configuration
"""
import os
from app import app

if __name__ == '__main__':
    # Get configuration from environment or use default
    env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    debug = env == 'development'
    
    print(f"Starting GDP Forecasting Research Dashboard...")
    print(f"Environment: {env}")
    print(f"Debug mode: {debug}")
    print(f"Port: {port}")
    print(f"\nOpen your browser and visit: http://localhost:{port}")
    print(f"\nPress CTRL+C to quit\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

