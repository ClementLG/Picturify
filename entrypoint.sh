#!/bin/sh

if [ "$FLASK_ENV" = "development" ]; then
    echo "Starting in DEBUG mode with Flask development server..."
    # Enable Force HTTPS False for Talisman in Dev implicitly? 
    # Actually run.py sets debug=False currently.
    # We should probably pass an env var to Python too or rely on run.py reading FLASK_ENV
    # But run.py just does app.run(). 
    
    # We'll use the python command as requested for debug
    exec python run.py
else
    echo "Starting in PRODUCTION mode with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
fi
