# File: camera_streamer.py

from controller import Robot
import base64
import asyncio
import websockets
import numpy as np
import cv2
from turbojpeg import TurboJPEG

# Initialize Webots Robot and camera
robot = Robot()
timestep = int(robot.getBasicTimeStep())

jpeg = TurboJPEG()

camera = robot.getDevice('scene_camera')
camera.enable(timestep)
frame_count = 0

# WebSocket handler
async def stream_handler(websocket):
    print("[WS] Viewer connected")
    global frame_count
    try:
        frame_count += 1
        if frame_count % 2 != 0:
            while robot.step(timestep) != -1:
                image = camera.getImageArray()
                if image:
                    height = camera.getHeight()
                    width = camera.getWidth()
                    image_np = np.array(image, dtype=np.uint8).reshape((height, width, 3))
                    bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                    _, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    await websocket.send(jpg_as_text)
                await asyncio.sleep(0.01)  # avoid tight loop
    except websockets.exceptions.ConnectionClosed:
        print("[WS] Viewer disconnected")
    except Exception as e:
        print(f"[WS] Error: {e}")

# Main entrypoint
async def main():
    print("[WS] Starting WebSocket server...")
    async with websockets.serve(stream_handler, "0.0.0.0", 8765):
        print("[WS] Server started on ws://localhost:8765")
        while robot.step(timestep) != -1:
            await asyncio.sleep(0.01)  # Maintain asyncio event loop

# Run the server
asyncio.run(main())
