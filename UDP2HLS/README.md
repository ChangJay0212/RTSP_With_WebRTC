# RTP with UDP to HLS

## Overview
This setup is designed to **stream camera footage to a frontend page** using **UDP** for transmission. The process involves three servers: `src-send`, `src-receive`, and `nginx`.

### **Workflow Overview**
1. **src-send**:
   - Uses **GStreamer** to convert camera footage into **RTP packets**.
   - Encodes the packets in **H.264** format.
   - Transmits the packets via **UDP** to the `src-receive` server.

2. **src-receive**:
   - Receives **RTP packets** from `src-send`.
   - Converts the packets into **HLS (HTTP Live Streaming)** format.
   - Provides the location of the **HLS playlist**.

3. **nginx**:
   - Listens on **port 8003**.
   - Serves the static **HLS playlist** to the frontend page.

### **GStreamer Setup**
Installs the following GStreamer components:
- **gstreamer1.0-tools**: Core GStreamer tools.
- **gstreamer1.0-plugins-base**: Essential plugins for basic media handling.
- **gstreamer1.0-plugins-good**: Plugins considered to have good code quality and proper documentation.
- **gstreamer1.0-plugins-bad**: Plugins that are not yet of sufficient quality for `-good`.
- **gstreamer1.0-plugins-ugly**: Plugins that might have licensing issues but are otherwise good quality.
- **gstreamer1.0-libav**: Adds support for a wide variety of codecs through libav.


## Usage

### **Starting and Stopping the service**
To start the service:
```bash
./start.sh
```
To stop the service:
```bash
./stop.sh
```