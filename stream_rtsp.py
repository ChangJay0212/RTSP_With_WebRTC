import cv2

# GStreamer RTSP
gst_rtsp_pipeline = (
    "appsrc ! videoconvert ! video/x-raw,format=YUY2 ! videoconvert ! video/x-raw,format=I420 ! "
    "x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=127.0.0.1 port=8554"
)

camera = cv2.VideoCapture("/dev/video0")


camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)

# init GStreamer
gst_out = cv2.VideoWriter(
    gst_rtsp_pipeline,
    cv2.CAP_GSTREAMER,
    0,
    30,
    (640, 480),
)

if not gst_out.isOpened():
    print("GStreamer init failed！")
    exit()

print("Streaming started... Press 'q' to quit.")

while True:
    ret, frame = camera.read()
    if not ret:
        print("Can't get frame！")
        break

    # Upload to GStreamer
    gst_out.write(frame)

    # exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# clear
camera.release()
gst_out.release()
cv2.destroyAllWindows()
