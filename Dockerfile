# Use a specific, stable version of the Python slim image
FROM python:3.9.18-slim

# Set environment variables for best practices in production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Install System Build Dependencies ---
# This is the most critical step. It installs the 'gcc' compiler.
# Combining them in one RUN command is more efficient and avoids caching issues.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set the application's working directory
WORKDIR /app

# --- Install Python Dependencies ---
# Copy the requirements file first to leverage Docker's layer caching.
COPY requirements.txt .

# Install dependencies. Using --no-cache-dir is good practice in containers.
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
# Copy the rest of the application source code into the container
COPY . .

# --- Expose the Port ---
# Inform Docker that the container listens on port 5000 (for Gunicorn)
EXPOSE 5000

# --- Define the Production Start Command ---
# Use Gunicorn as the production WSGI server. This is more robust than Flask's dev server.
# 'main:app' points to the 'app' object created by the factory in your main.py.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
