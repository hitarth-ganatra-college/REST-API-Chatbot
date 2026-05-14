# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for aiortc and soundfile (libffi, ffmpeg, libs for audio, etc)
RUN apt-get update && \
    apt-get install -y gcc ffmpeg libsm6 libxext6 libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment defaults (override in prod!)
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Entrypoint!
CMD ["python", "entrypoint.py"]