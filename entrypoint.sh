#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
# This is a simple example, in a real-world scenario you might want to use a more robust solution
# For example, you could use a tool like wait-for-it.sh or a custom script that checks the database connection
sleep 10

# Run database migrations
flask db upgrade

# Start Gunicorn server
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 4 --worker-class gthread wsgi:app
