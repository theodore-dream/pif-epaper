FROM python:latest

# Set api key
ARG OPENAI_API_KEY

# Copy the application files
COPY requirements.txt /app/
COPY getmodels.py /app/getmodels.py

# Install dependencies
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Start the application
CMD ["python", "getmodels.py", "--api_key=$OPENAI_API_KEY"]
