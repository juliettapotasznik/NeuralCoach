# syntax=docker/dockerfile:1.7
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=2

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/reqs.txt
RUN pip install --upgrade pip && pip install -r /tmp/reqs.txt

COPY autoencoder_service.py /app/autoencoder_service.py
COPY draw_keypoints.py /app/draw_keypoints.py
COPY metrics.py /app/metrics.py
COPY draw_keypoints.py /app/draw_keypoints.py
COPY lstm_architecture.json /app/lstm_architecture.json
COPY lstm_weights.weights.h5 /app/lstm_weights.weights.h5
COPY mean.npy /app/mean.npy
COPY std.npy /app/std.npy
COPY extrinsics.json /app/extrinsics.json

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost:8000/docs || exit 1

CMD ["uvicorn", "autoencoder_service:app", "--host", "0.0.0.0", "--port", "8000"]
