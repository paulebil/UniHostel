# Use official Python image
FROM python:3.12.3-slim

# Set work directory
WORKDIR /usr/src/app

# Install Reflex globally
RUN pip install reflex

# Copy project files
COPY . /usr/src/app/

# Expose Reflex frontend port
EXPOSE 3000

# Run Reflex app
CMD ["reflex", "run", "--host", "0.0.0.0"]
