# Use Python 3.12 slim image
FROM python:3.12-slim-bookworm

# Install system dependencies (curl for installing uv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies using uv (creates virtualenv)
RUN uv venv /app/.venv && \
    uv pip install -r requirements.txt

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy project files
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
