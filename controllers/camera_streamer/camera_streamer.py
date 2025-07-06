# File: camera_streamer.py

from controller import Robot
import base64
import asyncio
import websockets
import numpy as np
import cv2
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


def start_http_server():
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("0.0.0.0", 8000), handler)
    print("[HTTP] Server running at http://localhost:8000")
    httpd.serve_forever()


# Initialize Webots Robot and camera
robot = Robot()
timestep = int(robot.getBasicTimeStep())

camera = robot.getDevice('scene_camera')
camera.enable(timestep)
frame_count = 0

# WebSocket handler with timing
async def stream_handler(websocket):
    print("[WS] Viewer connected")
    last_time = time.time()
    frames = 0

    try:
        while robot.step(timestep) != -1:
            start = time.time()

            image = camera.getImage()
            if image:
                height = camera.getHeight()
                width = camera.getWidth()
                image_np = np.frombuffer(image, dtype=np.uint8).reshape((height, width, 4))
                bgr = image_np[:, :, :3]

                _, buffer = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                await websocket.send(jpg_as_text)

            frames += 1
            now = time.time()

            # Print FPS every second
            if now - last_time >= 1.0:
                print(f"[FPS] Streaming at {frames} FPS")
                frames = 0
                last_time = now

            await asyncio.sleep(0.001)  # Optional: reduce for higher FPS
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


# Start HTTP server in a background thread
threading.Thread(target=start_http_server, daemon=True).start()

# Run the server
asyncio.run(main())
