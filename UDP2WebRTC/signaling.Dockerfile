FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# 安裝必要的依賴
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gobject-introspection \
    gir1.2-gst-plugins-bad-1.0 \
    libcairo2-dev pkg-config python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
RUN pip install websockets pygobject

WORKDIR /app

# 複製 WebRTC 服務程式
COPY ./signaling_server.py /app/signaling_server.py


