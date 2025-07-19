import os
from src import create_app

# Create the Flask app instance using the factory
app = create_app()

if __name__ == '__main__':
    # This block is for running the app in development mode.
    # In production, a WSGI server like Gunicorn will be used.
    # The 'debug' flag is set based on the FLASK_DEBUG environment variable.
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=is_debug)
