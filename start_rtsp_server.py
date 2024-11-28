import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer


class RTSPServer(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        super().__init__()
        self.set_launch(
            "( v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,format=I420 ! "
            "x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 )"
        )


server = GstRtspServer.RTSPServer()
factory = RTSPServer()
factory.set_shared(True)

mount_points = server.get_mount_points()
mount_points.add_factory("/test", factory)

print("RTSP server running at rtsp://127.0.0.1:8554/test")
server.attach(None)

Gst.init(None)
from gi.repository import GLib

loop = GLib.MainLoop()
loop.run()
