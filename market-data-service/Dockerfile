FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Ensure app directory is in PYTHONPATH
ENV PYTHONPATH=/app

# Default: run the FastAPI app (can be overridden by docker-compose)
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]