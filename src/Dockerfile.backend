# Use Python slim image for a smaller footprint
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Create a non-root user
RUN useradd -m -s /bin/bash app_user

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/

# Change ownership to non-root user
RUN chown -R app_user:app_user /app

# Switch to non-root user
USER app_user

# Create volume for SQLite database
VOLUME ["/app/data"]

# Set environment variable for database path
ENV DATABASE_URL="sqlite+aiosqlite:///data/incidents.db"

# Expose port
EXPOSE $PORT

# Run the application
CMD ["sh", "-c", "cd src && uvicorn app.main:app --host 0.0.0.0 --port $PORT"]