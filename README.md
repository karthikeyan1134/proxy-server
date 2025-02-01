# Proxy HTTP/HTTPS Server

## 📌 Overview
A proxy server supporting **HTTP/HTTPS** protocols, built with Python. Features include **caching**, **dynamic site blocking**, **real-time statistics**, **comprehensive logging**, and a **menu-driven management interface**.

## 🚀 Features
- **Caching Mechanism**: Speeds up browsing by storing frequently accessed content.
- **Dynamic Site Blocking**: Block access to specific sites in real-time.
- **Real-time Statistics**: Monitor requests, cache hits, and blocked sites.
- **Logging System**: Tracks access logs, errors, and security events.
- **Centralized Management Interface**: Easily configure, monitor, and control the proxy.
- **Graceful Shutdown & Data Persistence**: Saves logs, cache, and settings before exiting.

## 🛠️ Technologies Used
- **Python**
- **Flask**
- **Socket Programming**
- **Threading**
- **Logging**
- **SQLite**
- **HTTP/HTTPS Protocols**

## 🔧 Installation
### Prerequisites
Ensure you have **Python 3.x** installed on your system.

### Steps to Install
```sh
# Clone the repository
git clone https://github.com/your-username/proxy-http-https-server.git
cd proxy-http-https-server

# Install dependencies
pip install -r requirements.txt

# Run the proxy server
python proxy_server.py
```

## 🚀 Usage
1. **Start the Proxy Server**
   ```sh
   python proxy.py
   ```
2. **Configure Your Browser or System to Use the Proxy**
   - HTTP Proxy: `http://localhost:8080`
   - HTTPS Proxy: `http://localhost:8080`
3. **Manage the Proxy Using the Interface**
   - View logs & statistics
   - Modify blocklists
   - Stop the server gracefully

## 🚧 Challenges Faced
- **Handling HTTPS Traffic**: Implemented SSL/TLS certificate handling for secure tunneling.
- **Efficient Caching**: Used hash-based storage with expiration policies.
- **Real-time Blocklist Updates**: Used thread-safe data structures for smooth updates.
- **Graceful Shutdown**: Implemented signal handling to save data before exiting.

## Directory Structure
```
Final_V/
│── cache/                 # Stores cached web pages
│── logs/                  # Stores logs for access and errors
│── blocked_sites.pkl      # Pickle file for blocked websites
│── cached_sites.pkl       # Pickle file for cached websites
│── proxy.py               # Main proxy server script
│── README.md              # Project documentation
```

## Logs & Cache Management
- Logs are stored in the `logs/` directory.
- Cached responses are stored in `cache/`.
- Run `proxy.py` with appropriate flags for additional functionalities.

## Author
**Karthikeyan**
