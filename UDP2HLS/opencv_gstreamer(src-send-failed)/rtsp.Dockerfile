FROM ubuntu:20.04

# 設置環境變量以避免交互式安裝
ENV DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    gstreamer1.0-gl \
    gstreamer1.0-opencv \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-tools \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer1.0-0 \
    libgstreamer1.0-dev \
    build-essential cmake git pkg-config \
    libgtk-3-dev libavcodec-dev libavformat-dev \
    libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
    libjpeg-dev libpng-dev libtiff-dev gfortran openexr \
    libatlas-base-dev python3-dev python3-numpy \
    libtbb2 libtbb-dev libdc1394-22-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
# 定義 OpenCV 版本
ENV OPENCV_VER="master"

# 編譯並安裝 OpenCV
RUN TMPDIR=$(mktemp -d) && \
    cd "${TMPDIR}" && \
    git clone --branch ${OPENCV_VER} --depth 1 --recurse-submodules --shallow-submodules https://github.com/opencv/opencv-python.git opencv-python-${OPENCV_VER} && \
    cd opencv-python-${OPENCV_VER} && \
    export ENABLE_CONTRIB=0 && \
    export ENABLE_HEADLESS=0 && \
    export CMAKE_ARGS="-DWITH_GSTREAMER=ON -DWITH_QT=ON -DWITH_OPENGL=ON" && \
    python3 -m pip wheel . --verbose && \
    python3 -m pip install opencv_python*.whl && \
    rm -rf "${TMPDIR}"

# 設置工作目錄
WORKDIR /app

# 複製 Python 腳本到容器
COPY stream_rtsp.py /app/

# 啟動 Python 腳本
CMD ["python3", "stream_rtsp.py"]
