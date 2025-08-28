# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv for faster dependency management
RUN pip install uv

# Install dependencies
RUN uv pip install --system .

# Copy application code
COPY . .

# Expose port
EXPOSE 15925

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=15925

# Run the application
CMD ["python", "start_mcp_server.py"]
