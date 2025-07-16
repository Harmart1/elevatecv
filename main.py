from src import create_app

# Create the Flask app instance using the factory
app = create_app()

if __name__ == '__main__':
    # Run the app
    # The host='0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)
