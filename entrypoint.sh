#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Tell Flask where to find the application factory.
export FLASK_APP=main

# Run database migrations.
echo "Running database migrations..."
flask db upgrade
echo "Migrations complete."

# Start the Gunicorn server with optimized settings for a low-memory environment.
echo "Starting Gunicorn server..."
# --workers 2: Reduces the number of processes to fit within 512MB RAM.
# --preload: Loads the app (and the spaCy model) once before forking workers to save memory.
exec gunicorn --workers 2 --preload --bind 0.0.0.0:${PORT:-5000} main:app
