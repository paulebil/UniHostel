# Use the official Python image
FROM python:3.12.3-slim

# Set work directory
WORKDIR /usr/src/app

# Set environment variables for performance & logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only requirements first to leverage Docker cache
COPY ./requirements.txt /usr/src/app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy project files
COPY . /usr/src/app/

# Change to non-root user
USER ubuntu

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with auto-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
