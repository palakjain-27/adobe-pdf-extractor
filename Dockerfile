FROM --platform=linux/amd64 python:3.9-slim

# Set environment variables for UTF-8 support
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main.py file from app directory to /app in container
COPY app/main.py ./

# Set the command
CMD ["python", "main.py"]