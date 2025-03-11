# Use official Python image (match backend version)
FROM python:3.12.3-slim

# Set work directory
WORKDIR /app

# Install system dependencies for Reflex
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun (JavaScript runtime)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Install Reflex globally
RUN pip install --no-cache-dir reflex

# Set the REFLEX_DIR environment variable to a path where the app can write
ENV REFLEX_DIR=/app/.local/share/reflex

# Ensure the REFLEX_DIR and .web directories exist and have proper permissions
RUN mkdir -p /app/.local/share/reflex /app/.web && chmod -R 777 /app/.local /app/.web

# Copy the requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rxconfig.py file
COPY rxconfig.py /app/

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose Reflex frontend port
EXPOSE 3000

# Run Reflex frontend app
CMD ["reflex", "run"]