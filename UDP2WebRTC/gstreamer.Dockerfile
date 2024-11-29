FROM ubuntu:20.04

# Install GStreamer 
RUN apt-get update && apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# folder to save hls
RUN mkdir -p /hls && chmod -R 777 /hls

# Command
CMD ["bash", "-c", "gst-launch-1.0 -v \
    rtspsrc location=rtsp://127.0.0.1:8554/test latency=100 ! \
    rtph264depay ! h264parse ! mpegtsmux ! \
    hlssink location=/hls/segment%05d.ts playlist-location=/hls/playlist.m3u8 target-duration=2 max-files=10"]
    