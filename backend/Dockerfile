# Use official Python image
FROM python:3.12.3-slim

# Set work directory
WORKDIR /usr/src/app

# Set environment variables for performance & logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /usr/src/app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy project files (exclude .env and sensitive files)
COPY . /usr/src/app/

# Set permissions to ensure non-root access
#RUN chown -R 1000:1000 /usr/src/app

# Expose FastAPI port
EXPOSE 8050

# Run FastAPI (remove --reload for production)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8050"]
