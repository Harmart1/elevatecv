#!/bin/sh

# This script is the entrypoint for the Docker container.
# It ensures the database is ready before starting the web server.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Set Flask Environment Variable ---
# Tell Flask where to find the application factory.
# The format is <python_file_or_module>:<factory_function_name>
export FLASK_APP=main:app

# --- Run Database Migrations ---
# This applies any pending database schema changes.
echo "Running database migrations..."
flask db upgrade
echo "Migrations complete."

# --- Start the Production Server ---
# This command starts Gunicorn, which will serve the Flask application.
# The --bind flag tells Gunicorn to listen on all network interfaces on port 5000.
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
