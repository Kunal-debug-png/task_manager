FROM python:3.11-slim

# Install system dependencies for confluent-kafka
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render uses PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
