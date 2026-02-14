# Dockerfile for Sentinel API

# 1. Base Image
FROM python:3.11-slim

# 2. Setup Env
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# 3. Install Dependencies
# We copy requirements first to cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Application Code
COPY src/ src/

# 5. Runtime Command
# Uses standard uvicorn worker
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
