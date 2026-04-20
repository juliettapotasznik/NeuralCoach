FROM python:3.10

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cd pose_extractor && \
    rm -rf build && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    cp pose_extractor.so .. && \
    cd ..
RUN omz_downloader --name human-pose-estimation-3d-0001 && \
    omz_converter --name human-pose-estimation-3d-0001 

RUN mkdir -p /usr/src/app/csv_results /usr/src/app/users_videos

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "openvino_service:app", "--host", "0.0.0.0", "--port", "8001"]
