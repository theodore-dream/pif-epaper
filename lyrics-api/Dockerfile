# Use an official Python runtime as a parent image
FROM --platform=linux/arm/v6 python:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install any necessary dependencies
#RUN apt update && apt install -y && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip 

# Create working directory
RUN mkdir /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application scripts
COPY lyrics_api.py /app/lyrics_api.py

# Make the script executable
RUN ["chmod", "+x", "/app/lyrics_api.py"]

# Run the application
CMD ["python", "/app/lyrics_api.py"]
