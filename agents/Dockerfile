FROM python:3.9-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY agents/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents /app/agents

# Set working directory to agents
WORKDIR /app/agents

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5001

# Use --app to specify the application file
CMD ["flask", "--app", "agent_server:app", "run", "--host=0.0.0.0", "--port=5001"] 