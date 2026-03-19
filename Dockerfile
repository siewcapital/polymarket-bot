FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY .env.example .

# Create volume for persistent data
VOLUME ["/app/data"]

# Environment variables (override at runtime)
ENV PYTHONUNBUFFERED=1
ENV WEBHOOK_PORT=8080

# Expose webhook port
EXPOSE 8080

# Default command
CMD ["python", "polymarket_bot.py"]
