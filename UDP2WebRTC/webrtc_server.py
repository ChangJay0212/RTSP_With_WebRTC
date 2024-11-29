import asyncio
import json
import time

import gi
import websockets

gi.require_version("Gst", "1.0")
gi.require_version("GstWebRTC", "1.0")
from gi.repository import Gst, GstWebRTC

# WebRTC signaling server details
SIGNALING_SERVER = "ws://signaling-container:8080"  # Replace with your signaling server
ROOM_ID = "test-room"

time.sleep(10)


class WebRTCServer:
    def __init__(self):
        self.pipeline = None
        self.webrtcbin = None

    def start_pipeline(self):
        # GStreamer pipeline for UDP to WebRTC
        self.pipeline = Gst.parse_launch(
            "udpsrc port=5000 caps=application/x-rtp,media=video,encoding-name=H264,payload=96 ! "
            "rtph264depay ! h264parse ! queue ! rtph264pay config-interval=-1 ! application/x-rtp,media=video,encoding-name=H264,payload=96 ! "
            "webrtcbin name=webrtcbin stun-server=stun:stun.l.google.com:19302"
        )
        self.webrtcbin = self.pipeline.get_by_name("webrtcbin")
        self.webrtcbin.connect("on-negotiation-needed", self.on_negotiation_needed)
        self.webrtcbin.connect("on-ice-candidate", self.on_ice_candidate)
        self.webrtcbin.connect(
            "pad-added", self.on_pad_added
        )  # Handle new media stream
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_negotiation_needed(self, element):
        print("Negotiation needed")
        promise = Gst.Promise.new()
        element.emit("create-offer", None, promise)

        # Wait for promise to complete
        result = promise.wait()
        if result != Gst.PromiseResult.REPLIED:
            print("Failed to create offer")
            return

        reply = promise.get_reply()
        if reply is None:
            print("Failed to get reply from promise")
            return

        offer = reply.get_value("offer")
        element.emit("set-local-description", offer, Gst.Promise.new())
        asyncio.run(self.send_sdp_to_signaling_server(offer.sdp.as_text()))

    def on_ice_candidate(self, element, mlineindex, candidate):
        print(f"New ICE Candidate: {candidate}")
        asyncio.run(self.send_ice_to_signaling_server(mlineindex, candidate))

    def on_pad_added(self, element, pad):
        print("New pad added to WebRTC: ", pad.get_name())
        caps = pad.query_caps(None)
        print(f"Pad caps: {caps.to_string()}")

        if caps.is_fixed() and caps.to_string().startswith("application/x-rtp"):
            # Dynamically link the pad to a sink
            appsink = Gst.ElementFactory.make("fakesink", None)
            self.pipeline.add(appsink)
            appsink.sync_state_with_parent()
            pad.link(appsink.get_static_pad("sink"))

    async def send_sdp_to_signaling_server(self, sdp):
        async with websockets.connect(SIGNALING_SERVER) as websocket:
            message = {
                "type": "offer",
                "sdp": sdp,
                "room": ROOM_ID,
            }
            await websocket.send(json.dumps(message))

    async def send_ice_to_signaling_server(self, mlineindex, candidate):
        async with websockets.connect(SIGNALING_SERVER) as websocket:
            message = {
                "type": "ice",
                "candidate": candidate,
                "sdpMLineIndex": mlineindex,
                "room": ROOM_ID,
            }
            await websocket.send(json.dumps(message))

    async def handle_signaling_server(self):
        async with websockets.connect(SIGNALING_SERVER) as websocket:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "answer":
                    print("Received SDP Answer")
                    answer = GstWebRTC.WebRTCSessionDescription.new(
                        GstWebRTC.WebRTCSDPType.ANSWER, data["sdp"]
                    )
                    self.webrtcbin.emit(
                        "set-remote-description", answer, Gst.Promise.new()
                    )
                elif data["type"] == "ice":
                    print(f"Received ICE Candidate: {data['candidate']}")
                    self.webrtcbin.emit(
                        "add-ice-candidate", data["sdpMLineIndex"], data["candidate"]
                    )
                else:
                    print("Unknown message type from signaling server:", data)


async def main():
    Gst.init(None)
    webrtc_server = WebRTCServer()
    webrtc_server.start_pipeline()

    # Start signaling server communication
    await webrtc_server.handle_signaling_server()


if __name__ == "__main__":
    asyncio.run(main())
