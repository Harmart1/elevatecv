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

# --- Download the SpaCy Language Model ---
# This command downloads the model so it's available to your application
RUN python -m spacy download en_core_web_sm

# Copy your application code
COPY . .

# --- Make entrypoint script executable and set it as the command ---
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# --- Expose the Port ---
EXPOSE 5000

# --- Define the Production Start Command ---
CMD ["/app/entrypoint.sh"]
