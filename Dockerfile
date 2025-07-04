FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for content and uploads
RUN mkdir -p /app/encrypted_output /app/temp_uploads /app/logs

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash ethicaldrm && \
    chown -R ethicaldrm:ethicaldrm /app

USER ethicaldrm

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["ethicaldrm-api", "--host", "0.0.0.0", "--port", "5000"]