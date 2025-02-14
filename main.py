from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dataclasses import dataclass
import socket
import threading
import time
import os
import shutil
from typing import List, Optional
import uvicorn
import qrcode
from io import BytesIO
import base64
from tempfile import NamedTemporaryFile

from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files for GitHub Pages
app.mount("/", StaticFiles(directory="static", html=True), name="static")
# Constants
BROADCAST_PORT = 9090
FILE_PORT = 5000
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Mobile File Sharing")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory for HTML templates
templates = Jinja2Templates(directory="templates")

@dataclass
class ServerInfo:
    name: str
    ip: str
    port: int
    qr_code: Optional[str] = None

class BroadcastServer:
    def __init__(self, name: str, broadcast_port: int):
        self.server_name = name
        self.broadcast_port = broadcast_port
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_ip = socket.gethostbyname(socket.gethostname())

    def broadcast_presence(self):
        message = f"Server: {self.server_name}, IP: {self.server_ip}, PORT: {self.broadcast_port}"
        self.broadcast_socket.sendto(message.encode(), ('<broadcast>', self.broadcast_port))

    def close(self):
        self.broadcast_socket.close()

# Initialize broadcaster
broadcaster = BroadcastServer("MobileShareApp", BROADCAST_PORT)

def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Start broadcasting in background
def broadcast_thread():
    while True:
        broadcaster.broadcast_presence()
        time.sleep(1)

threading.Thread(target=broadcast_thread, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/discover")
async def discover_servers() -> List[ServerInfo]:
    """Discover available servers on the network"""
    servers = []
    discover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discover_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    discover_socket.bind(('', BROADCAST_PORT))
    discover_socket.settimeout(2)

    for _ in range(3):
        try:
            data, addr = discover_socket.recvfrom(1024)
            message = data.decode()
            
            name_start = message.find("Server: ") + 8
            name_end = message.find(", IP: ")
            ip_end = message.find(", PORT: ")
            
            server = ServerInfo(
                name=message[name_start:name_end],
                ip=message[name_end + 6:ip_end],
                port=int(message[ip_end + 8:])
            )
            
            if not any(s.ip == server.ip for s in servers):
                # Generate QR code for easy mobile connection
                qr_data = f"http://{server.ip}:8000"
                server.qr_code = generate_qr_code(qr_data)
                servers.append(server)
        except socket.timeout:
            continue
        time.sleep(1)

    discover_socket.close()
    return servers

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the server with progress tracking"""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Check file size
        file_size = 0
        with NamedTemporaryFile("wb") as temp_file:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File too large")
                temp_file.write(chunk)
            
            # Move the file to the upload directory
            shutil.move(temp_file.name, file_path)
            
        return {
            "filename": file.filename,
            "size": file_size,
            "status": "success",
            "download_url": f"/download/{file.filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    """List all available files with metadata"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            stats = os.stat(file_path)
            files.append({
                "name": filename,
                "size": stats.st_size,
                "modified": stats.st_mtime,
                "download_url": f"/download/{filename}"
            })
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a specific file with range support for streaming"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.get("/server-info")
async def get_server_info():
    """Get current server information including QR code"""
    server_url = f"http://{broadcaster.server_ip}:8000"
    qr_code = generate_qr_code(server_url)
    return {
        "name": broadcaster.server_name,
        "ip": broadcaster.server_ip,
        "port": BROADCAST_PORT,
        "url": server_url,
        "qr_code": qr_code
    }

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)