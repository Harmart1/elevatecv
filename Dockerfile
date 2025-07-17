# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# This is done first to leverage Docker's layer caching.
# The dependencies will only be re-installed if requirements.txt changes.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define the command to run your app
# Gunicorn is a production-ready web server, better than Flask's built-in server.
# We will use it for the final command, but provide the debug command as well.
# For debugging:
# CMD ["python", "main.py"]

# For production (after installing gunicorn: pip install gunicorn):
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
