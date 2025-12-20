import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # run.py is only executed directly in development mode via entrypoint.sh or manual python run.py
    # Gunicorn uses 'run:app' and does not execute this block.
    app.run(debug=True, host='0.0.0.0', port=5000)
