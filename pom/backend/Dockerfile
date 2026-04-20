FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and python-magic
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
