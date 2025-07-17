# Use a specific, stable version of the Python slim image
FROM python:3.9.18-slim

# Set environment variables for best practices
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the SpaCy Language Model
RUN python -m spacy download en_core_web_sm

# Copy your application code
COPY . .

# --- Add and Set Permissions for the Entrypoint Script ---
# Copy the script into the container
COPY entrypoint.sh /app/entrypoint.sh
# Make it executable
RUN chmod +x /app/entrypoint.sh

# --- Expose the Port ---
EXPOSE 5000

# --- Set the Entrypoint ---
# This tells Docker to run our script when the container starts.
# The script will handle migrations and then start Gunicorn.
ENTRYPOINT ["/app/entrypoint.sh"]
