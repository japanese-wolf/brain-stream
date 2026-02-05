# BrainStream Backend Dockerfile
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /data

# Set environment variables
ENV BRAINSTREAM_DATA_DIR=/data
ENV BRAINSTREAM_HOST=0.0.0.0
ENV BRAINSTREAM_DEBUG=false
ENV BRAINSTREAM_SCHEDULER=true
ENV BRAINSTREAM_FETCH_INTERVAL=30

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "brainstream.main:app", "--host", "0.0.0.0", "--port", "8000"]
