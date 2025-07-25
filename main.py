import os
from src import create_app
from flask import jsonify

# Create the Flask app instance using the factory
app = create_app()

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify that the service is running.
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # This block is for running the app in development mode.
    # In production, a WSGI server like Gunicorn will be used.
    # The 'debug' flag is set based on the FLASK_DEBUG environment variable.
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=is_debug)
