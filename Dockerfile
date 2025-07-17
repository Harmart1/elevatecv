# Stage 1: Use an official, lean Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Install System-Level Dependencies ---
# This is the most critical step to fix the error.
# It updates the package manager and installs 'build-essential',
# which provides the 'gcc' compiler needed for packages like 'blis' (a spaCy dependency).
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# --- Install Python Dependencies ---
# Copy only the requirements file first to leverage Docker's layer caching.
# This step will only be re-run if the requirements.txt file changes.
COPY requirements.txt .

# Install the Python dependencies from the requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
# Copy the rest of your application's code into the container.
COPY . .

# --- Expose Port ---
# Make the Gunicorn port available to the outside world.
# Render will automatically detect this and use it.
EXPOSE 5000

# --- Define the Production Start Command ---
# Use Gunicorn to run the application. It's a production-ready WSGI server.
# 'main:app' refers to the 'app' object created by the 'create_app' factory in your 'main.py'.
# The number of workers can be tuned based on your Render instance plan.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
