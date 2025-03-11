# Use official Python image (match backend version)
FROM python:3.12.3-slim

# Set work directory
WORKDIR /usr/src/app

# Install system dependencies for Reflex
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Reflex globally
RUN pip install --no-cache-dir reflex

# Copy project files (exclude node_modules)
COPY . /usr/src/app/

# Set permissions to ensure non-root access
RUN chown -R 1000:1000 /usr/src/app

# Expose Reflex frontend port
EXPOSE 3000

# Run Reflex app
CMD ["reflex", "run", "--host", "0.0.0.0"]
