// tab.js
const img = document.getElementById("cameraStream");

const ws = new WebSocket("ws://localhost:8765");

ws.onopen = () => {
  console.log("[WS] Connected to Webots camera stream");
};

ws.onmessage = (event) => {
  console.log("[WS] Received image");
  img.src = 'data:image/jpeg;base64,' + event.data;
};

ws.onerror = (error) => {
  console.error("[WS] Error:", error);
};

ws.onclose = () => {
  console.warn("[WS] WebSocket closed");
};
