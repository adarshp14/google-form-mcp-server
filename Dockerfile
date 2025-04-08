FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY server/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server /app/server
COPY .env /app/.env

# Set working directory to server
WORKDIR /app/server

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the server
CMD ["python", "app.py"]
