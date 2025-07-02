// tab.js
let gameRunning = false;
let selectedTeam = null;
let currentFile = null;
let originalContent = '';
const img = document.getElementById("cameraStream");
let ws = null;

function connectWebSocket() {
    ws = new WebSocket("ws://localhost:8765");
    
    ws.onopen = () => {
        console.log("[WS] Connected to Webots camera stream");
        const placeholder = document.getElementById('streamPlaceholder');
        if (placeholder) placeholder.textContent = 'Connected to Webots camera stream';
    };
    
    ws.onmessage = (event) => {
        console.log("[WS] Received image");
        const img = document.getElementById("cameraStream");
        const placeholder = document.getElementById('streamPlaceholder');
        
        if (img) {
            img.src = 'data:image/jpeg;base64,' + event.data;
            img.style.display = 'block';
            if (placeholder) placeholder.style.display = 'none';
        } else {
            console.error("cameraStream element not found!");
        }
    };

    ws.onerror = (error) => {
        console.error("[WS] Error:", error);
        document.getElementById('streamPlaceholder').textContent = 'WebSocket connection error';
        document.getElementById('streamPlaceholder').style.display = 'block';
        img.style.display = 'none';
    };
    
    ws.onclose = () => {
        console.warn("[WS] WebSocket closed");
        document.getElementById('streamPlaceholder').textContent = 'WebSocket connection closed';
        document.getElementById('streamPlaceholder').style.display = 'block';
        img.style.display = 'none';
    };
}

function selectTeam(team) {
    selectedTeam = team;
    console.log(`Selected team: ${team}`);
    
    // Update button states
    document.querySelectorAll('.team-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.querySelector(`.team-btn[onclick="selectTeam('${team}')"]`).classList.add('selected');
}

function loadFile(event) {
    const file = event.target.files[0];
    if (file) {
        currentFile = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            originalContent = e.target.result;
            document.getElementById('codeEditor').value = originalContent;
            document.getElementById('fileInfo').textContent = `Loaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            console.log('File loaded:', file.name);
        };
        reader.readAsText(file);
    }
}

function loadCode() {
    const code = document.getElementById('codeEditor').value;
    if (code.trim()) {
        console.log('Loading code into simulation...');
        // Here you would integrate with your soccer simulation engine
        alert('Code loaded into simulation!');
    } else {
        alert('No code to load!');
    }
}

function saveCode() {
    const code = document.getElementById('codeEditor').value;
    if (code.trim()) {
        const filename = currentFile ? currentFile.name : 'soccer_sim_code.txt';
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('Code saved!');
    } else {
        alert('No code to save!');
    }
}

function playGame() {
    if (!gameRunning) {
        gameRunning = true;
        console.log('Game started!');
        
        // Update button states
        document.getElementById('playBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        
        // Connect to Webots camera stream
        connectWebSocket();
    }
}

function pauseGame() {
    if (gameRunning) {
        gameRunning = false;
        console.log('Game paused!');
        
        // Update button states
        document.getElementById('playBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        
        // Hide camera stream
        const streamImg = document.getElementById('cameraStream');
        const placeholder = document.getElementById('streamPlaceholder');
        
        streamImg.style.display = 'none';
        placeholder.style.display = 'block';
        placeholder.textContent = 'Stream paused - click Play to resume';
    }
}

// Handle camera stream errors
document.getElementById('cameraStream').addEventListener('error', function() {
    document.getElementById('streamPlaceholder').textContent = 'Stream connection failed';
    document.getElementById('streamPlaceholder').style.display = 'block';
    this.style.display = 'none';
});

// Check for unsaved changes
document.getElementById('codeEditor').addEventListener('input', function() {
    const current = this.value;
    if (current !== originalContent && currentFile) {
        document.getElementById('fileInfo').textContent = `${currentFile.name} (modified)`;
    }
});