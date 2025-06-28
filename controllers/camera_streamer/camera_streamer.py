# File: camera_streamer.py
from controller import Robot
import base64
import threading
import asyncio
import websockets
import numpy as np
import cv2

# Webots setup
robot = Robot()
timestep = int(robot.getBasicTimeStep())

camera = robot.getDevice('scene_camera')
camera.enable(timestep)

# WebSocket server to send JPEG frames
async def stream_handler(websocket, path):
    print("[WS] Viewer connected")
    while True:
        image = camera.getImageArray()
        if image:
            height = camera.getHeight()
            width = camera.getWidth()
            image_np = np.array(image, dtype=np.uint8).reshape((height, width, 4))
            bgr = cv2.cvtColor(image_np[:, :, :3], cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', bgr)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            await websocket.send(jpg_as_text)
        await asyncio.sleep(timestep / 1000.0)

def start_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    server = websockets.serve(stream_handler, "0.0.0.0", 8765)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server)
    loop.run_forever()

# Start WebSocket in separate thread
threading.Thread(target=start_server, daemon=True).start()

# Webots simulation loop
while robot.step(timestep) != -1:
    pass
