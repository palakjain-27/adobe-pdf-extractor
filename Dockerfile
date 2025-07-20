FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main.py file from app directory to /app in container
COPY app/main.py ./

# Set the command
CMD ["python", "main.py"]