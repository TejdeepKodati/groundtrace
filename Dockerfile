# Multi-stage Dockerfile for GroundTrace
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/

EXPOSE 8001

ENV PYTHONPATH=/app/backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
