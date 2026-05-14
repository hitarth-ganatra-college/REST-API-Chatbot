import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCIceCandidate
from aiortc.contrib.signaling import BYE
import websockets
from config import Config

class AudioFrameBuffer:
    def __init__(self):
        self.frames = []

    def add_frame(self, frame):
        self.frames.append(frame)

    def get_buffered_audio(self):
        out = self.frames
        self.frames = []
        return out

async def consume_audio(on_audio_chunk):
    ws = await websockets.connect(Config.SIGNALING_SERVER_URL)
    await ws.send(json.dumps({"type": "join", "room": Config.SESSION_ID, "side": "agent"}))

    pc = RTCPeerConnection()
    audio_buffer = AudioFrameBuffer()

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            async def recv_audio():
                async for frame in track.recv():
                    pcm = frame.to_ndarray().tobytes()
                    audio_buffer.add_frame(pcm)
                    if len(audio_buffer.frames) > 50:
                        full_audio = b"".join(audio_buffer.get_buffered_audio())
                        await on_audio_chunk(full_audio)
            asyncio.ensure_future(recv_audio())

    async def send_offer():
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await ws.send(json.dumps({"type": "offer", "sdp": pc.localDescription.sdp, "room": Config.SESSION_ID}))

    while True:
        try:
            msg_raw = await ws.recv()
        except Exception:
            break
        msg = json.loads(msg_raw)
        t = msg.get("type")
        if t == "offer":
            offer = RTCSessionDescription(sdp=msg["sdp"], type="offer")
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await ws.send(json.dumps({"type": "answer", "sdp": pc.localDescription.sdp, "room": Config.SESSION_ID}))
        elif t == "answer":
            answer = RTCSessionDescription(sdp=msg["sdp"], type="answer")
            await pc.setRemoteDescription(answer)
        elif t == "ice":
            candidate = msg.get("candidate")
            if candidate:
                ice = RTCIceCandidate(**candidate)
                await pc.addIceCandidate(ice)
        elif t == "ready":
            await send_offer()
        elif t == "peer_left":
            print("Peer left.")
            break
        elif t == BYE:
            print("Received BYE, closing.")
            break
    await ws.close()
    await pc.close()