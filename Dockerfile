# Stage 1: Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Install python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final stage
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user
RUN adduser --disabled-password --gecos '' myuser
USER myuser

# Copy python dependencies from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
