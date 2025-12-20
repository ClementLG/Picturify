#!/bin/sh

if [ "$FLASK_ENV" = "development" ]; then
    echo "Starting in DEBUG mode with Flask development server..."
    exec python run.py
else
    echo "Starting in PRODUCTION mode with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
fi
