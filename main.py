from src import create_app

# Create the Flask app instance using the factory
app = create_app()

if __name__ == '__main__':
    # This block is for running the app in development (debug) mode.
    # In production, a WSGI server like Gunicorn will be used,
    # as configured in the Dockerfile.
    app.run(host='0.0.0.0', port=5000, debug=True)
