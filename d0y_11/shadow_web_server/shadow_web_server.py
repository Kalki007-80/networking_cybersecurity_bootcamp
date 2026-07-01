#!/usr/bin/env python3

import socket
import threading
import json
import os
import time
import sys
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Default configuration
DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 8080,
    "www_dir": "www",
    "log_file": "logs/server.log",
    "templates_dir": "templates",
    "reports_dir": "reports"
}

HTTP_STATUS = {
    200: "OK",
    201: "Created",
    202: "Accepted",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    429: "Too Many Requests",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".csv": "text/csv; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".gz": "application/gzip",
    ".tar": "application/x-tar",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
}

def load_config(config_path="config/config.json"):
    """Load configuration from JSON file, create default if missing."""
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open(config_path, "r") as f:
        config = json.load(f)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config

def ensure_directories(config):
    """Create necessary directories."""
    dirs = [config["www_dir"], "logs", "reports", "templates"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def print_banner():
    banner = """
============================================================
            SHADOW WEB SERVER v2.0
            Day 11 Project
            Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def parse_request(request):
    lines = request.splitlines()
    if not lines:
        return None
    parts = lines[0].split()
    if len(parts) < 3:
        return None
    method, path, version = parts
    headers = {}
    body_start = 0
    for i, line in enumerate(lines[1:], 1):
        if line == "":
            body_start = i + 1
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    body = "\n".join(lines[body_start:]) if body_start > 0 else ""
    parsed_path = urlparse(path)
    query_params = parse_qs(parsed_path.query) if parsed_path.query else {}
    return {
        "method": method,
        "path": parsed_path.path,
        "full_path": path,
        "version": version,
        "headers": headers,
        "body": body,
        "query": query_params
    }

def build_response(status_code, headers=None, body=None, content_type="text/html; charset=utf-8"):
    if headers is None:
        headers = {}
    status_line = f"HTTP/1.1 {status_code} {HTTP_STATUS.get(status_code, 'Unknown')}"
    headers["Content-Type"] = content_type
    headers["Server"] = "Shadow-Web-Server/2.0"
    headers["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    if body is not None:
        if isinstance(body, str):
            body_bytes = body.encode("utf-8")
        else:
            body_bytes = body
        headers["Content-Length"] = str(len(body_bytes))
    else:
        body_bytes = b""
        headers["Content-Length"] = "0"
    response = status_line + "\r\n"
    for key, value in headers.items():
        response += f"{key}: {value}\r\n"
    response += "\r\n"
    return response.encode("utf-8") + body_bytes

def serve_static_file(path, base_dir):
    # Security: prevent directory traversal
    if ".." in path or path.startswith("/"):
        path = path.lstrip("/")
    path = path.replace("..", "")
    if not path:
        path = "index.html"
    file_path = os.path.join(base_dir, path)
    # Extra safety: ensure resolved path stays within base_dir
    if not os.path.abspath(file_path).startswith(os.path.abspath(base_dir)):
        return None, 403, None
    if not os.path.exists(file_path):
        return None, 404, None
    if os.path.isdir(file_path):
        index_path = os.path.join(file_path, "index.html")
        if os.path.exists(index_path):
            return serve_static_file(os.path.join(path, "index.html"), base_dir)
        return None, 403, None
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        ext = os.path.splitext(file_path)[1].lower()
        content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
        return content, 200, content_type
    except Exception:
        return None, 500, None

def handle_root():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Shadow Web Server</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #1a1a2e; color: #eee; }
        h1 { color: #00d4ff; }
        .card { background: #16213e; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #00d4ff; }
        a { color: #00d4ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .footer { margin-top: 30px; font-size: 12px; color: #888; }
        .routes { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .route { background: #0f3460; padding: 10px; border-radius: 5px; font-family: monospace; }
        .route span { color: #00d4ff; }
        .badge { display: inline-block; background: #00d4ff; color: #1a1a2e; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Shadow Web Server <span class="badge">v2.0</span></h1>
    <p>Welcome to your custom HTTP server!</p>

    <div class="card">
        <h2>Available Routes</h2>
        <div class="routes">
            <div class="route"><span>GET</span> /</div>
            <div class="route"><span>GET</span> /about</div>
            <div class="route"><span>GET</span> /time</div>
            <div class="route"><span>GET</span> /status</div>
            <div class="route"><span>GET</span> /hello?name=...</div>
            <div class="route"><span>GET</span> /json</div>
            <div class="route"><span>POST</span> /echo</div>
            <div class="route"><span>GET</span> /files/</div>
        </div>
    </div>

    <div class="card">
        <h2>Server Stats</h2>
        <p><strong>Status:</strong> Online</p>
        <p><strong>Version:</strong> v2.0</p>
        <p><strong>Author:</strong> Mukesh S</p>
        <p><strong>Threads:</strong> Active clients</p>
    </div>

    <div class="footer">
        <p>Built with Python sockets | Day 11 Bootcamp Project</p>
    </div>
</body>
</html>"""
    return html, 200, "text/html; charset=utf-8"

def handle_about():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>About - Shadow Web Server</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #1a1a2e; color: #eee; }
        h1 { color: #00d4ff; }
        .card { background: #16213e; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #00d4ff; }
        a { color: #00d4ff; text-decoration: none; }
        .feature { display: inline-block; background: #0f3460; padding: 4px 12px; border-radius: 4px; margin: 4px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>About Shadow Web Server</h1>
    <div class="card">
        <p>This is a custom HTTP server built from scratch using Python's <code>socket</code> module.</p>
        <p>No external frameworks like Flask or Django were used.</p>
        <ul>
            <li><strong>Author:</strong> Mukesh S</li>
            <li><strong>Day:</strong> 11 Bootcamp Project</li>
            <li><strong>Tech:</strong> Python, sockets, threading</li>
            <li><strong>Version:</strong> 2.0</li>
        </ul>
        <div style="margin-top: 10px;">
            <span class="feature">Static Files</span>
            <span class="feature">JSON APIs</span>
            <span class="feature">Concurrency</span>
            <span class="feature">Logging</span>
            <span class="feature">MIME Detection</span>
            <span class="feature">Professional Status Codes</span>
        </div>
    </div>
    <p><a href="/">Back to Home</a></p>
</body>
</html>"""
    return html, 200, "text/html; charset=utf-8"

def handle_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Server Time</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #1a1a2e; color: #eee; }}
        h1 {{ color: #00d4ff; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #00d4ff; font-size: 2em; text-align: center; }}
        a {{ color: #00d4ff; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>Server Time</h1>
    <div class="card">{current_time}</div>
    <p><a href="/">Back to Home</a></p>
</body>
</html>"""
    return html, 200, "text/html; charset=utf-8"

def handle_status():
    data = {
        "status": "online",
        "server": "Shadow-Web-Server",
        "version": "2.0",
        "uptime_seconds": 0,
        "features": ["static files", "JSON API", "concurrency", "logging", "MIME detection", "status codes"],
        "author": "Mukesh S"
    }
    return json.dumps(data, indent=4), 200, "application/json; charset=utf-8"

def handle_hello(query):
    name = query.get("name", ["World"])[0]
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Hello!</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #1a1a2e; color: #eee; }}
        h1 {{ color: #00d4ff; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #00d4ff; }}
        a {{ color: #00d4ff; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>Hello, {name}!</h1>
    <div class="card">Welcome to the Shadow Web Server!</div>
    <p><a href="/">Back to Home</a></p>
</body>
</html>"""
    return html, 200, "text/html; charset=utf-8"

def handle_json():
    data = {
        "message": "This is a JSON response",
        "timestamp": datetime.now().isoformat(),
        "server": "Shadow-Web-Server",
        "version": "2.0",
        "features": ["REST API", "JSON responses", "Easy to extend"]
    }
    return json.dumps(data, indent=4), 200, "application/json; charset=utf-8"

def handle_echo(body, method):
    data = {
        "method": method,
        "received": body,
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(data, indent=4), 200, "application/json; charset=utf-8"

def route_request(parsed, config):
    method = parsed["method"]
    path = parsed["path"]
    query = parsed["query"]
    body = parsed["body"]

    if path == "/" and method == "GET":
        return handle_root()
    elif path == "/about" and method == "GET":
        return handle_about()
    elif path == "/time" and method == "GET":
        return handle_time()
    elif path == "/status" and method == "GET":
        return handle_status()
    elif path == "/hello" and method == "GET":
        return handle_hello(query)
    elif path == "/json" and method == "GET":
        return handle_json()
    elif path == "/echo" and method == "POST":
        return handle_echo(body, method)
    elif path.startswith("/files/"):
        return serve_static_file(path[7:], config["www_dir"])
    else:
        return None, 404

def handle_client(client_socket, address, config):
    start_time = time.time()
    log_file = config["log_file"]
    try:
        request_data = client_socket.recv(4096).decode("utf-8", errors="ignore")
        if not request_data:
            client_socket.close()
            return

        parsed = parse_request(request_data)
        if not parsed:
            response = build_response(400, body="Bad Request")
            client_socket.sendall(response)
            client_socket.close()
            return

        log_entry = f"{datetime.now().isoformat()} | {address[0]} | {parsed['method']} {parsed['full_path']}"
        print(f"[+] {log_entry}")

        content, status, content_type = route_request(parsed, config)

        if content is None:
            error_pages = {
                404: """<!DOCTYPE html><html><head><title>404 Not Found</title>
                <style>body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#1a1a2e;color:#eee;}
                h1{color:#ff6b6b;}</style></head>
                <body><h1>404 - Page Not Found</h1><p>The requested page does not exist.</p>
                <p><a href="/">Back to Home</a></p></body></html>""",
                403: """<!DOCTYPE html><html><head><title>403 Forbidden</title>
                <style>body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#1a1a2e;color:#eee;}
                h1{color:#ff6b6b;}</style></head>
                <body><h1>403 - Forbidden</h1><p>You don't have permission to access this.</p>
                <p><a href="/">Back to Home</a></p></body></html>""",
                405: """<!DOCTYPE html><html><head><title>405 Method Not Allowed</title>
                <style>body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#1a1a2e;color:#eee;}
                h1{color:#ff6b6b;}</style></head>
                <body><h1>405 - Method Not Allowed</h1><p>The requested method is not allowed.</p>
                <p><a href="/">Back to Home</a></p></body></html>""",
                500: """<!DOCTYPE html><html><head><title>500 Internal Server Error</title>
                <style>body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#1a1a2e;color:#eee;}
                h1{color:#ff6b6b;}</style></head>
                <body><h1>500 - Internal Server Error</h1><p>Something went wrong.</p>
                <p><a href="/">Back to Home</a></p></body></html>"""
            }
            content = error_pages.get(status, f"<h1>{status} Error</h1>")
            content_type = "text/html; charset=utf-8"

        response = build_response(status, body=content, content_type=content_type)
        client_socket.sendall(response)
        client_socket.close()

        elapsed_ms = (time.time() - start_time) * 1000
        log_line = f"{datetime.now().isoformat()} | {address[0]} | {parsed['method']} {parsed['full_path']} | {status} | {elapsed_ms:.2f}ms\n"
        with open(log_file, "a") as f:
            f.write(log_line)

    except Exception as e:
        print(f"[-] Error handling client {address}: {e}")
        try:
            client_socket.close()
        except:
            pass

class ShadowWebServer:
    def __init__(self, config):
        self.config = config
        self.host = config["host"]
        self.port = config["port"]
        self.running = False
        self.server_socket = None
        self.start_time = None

    def start(self):
        self.start_time = time.time()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
        except PermissionError:
            print(f"Permission denied for port {self.port} (privileged ports below 1024).")
            print("Either run with sudo or choose a port above 1024.")
            sys.exit(1)
        except OSError as e:
            print(f"Error binding to port {self.port}: {e}")
            sys.exit(1)

        self.server_socket.listen(10)
        self.running = True

        print(f"\n[*] Shadow Web Server started on http://{self.host}:{self.port}")
        print(f"[*] Serving static files from: {self.config['www_dir']}")
        print("[*] Press Ctrl+C to stop\n")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                thread = threading.Thread(target=handle_client, args=(client_socket, address, self.config))
                thread.daemon = True
                thread.start()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[-] Error: {e}")

        self.stop()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("\n[*] Server stopped.")

def ensure_default_www_files(www_dir):
    """Create default index.html and style.css if missing (fallback safety net)."""
    index_path = os.path.join(www_dir, "index.html")
    if not os.path.exists(index_path):
        with open(index_path, "w") as f:
            f.write("""<!DOCTYPE html>
<html>
<head><title>Welcome</title>
<style>body{font-family:Arial;max-width:800px;margin:50px auto;padding:20px;background:#1a1a2e;color:#eee;}
h1{color:#00d4ff;}
</style>
</head>
<body><h1>Welcome to the Shadow Web Server!</h1>
<p>This is a static file served from the www/ directory.</p>
<p><a href="/">Back to Home</a></p>
</body>
</html>""")
    css_path = os.path.join(www_dir, "style.css")
    if not os.path.exists(css_path):
        with open(css_path, "w") as f:
            f.write("""body {
    font-family: Arial, sans-serif;
    background: #1a1a2e;
    color: #eee;
    max-width: 800px;
    margin: 50px auto;
    padding: 20px;
}
h1 { color: #00d4ff; }
""")

def main():
    print_banner()
    config = load_config()
    ensure_directories(config)
    ensure_default_www_files(config["www_dir"])

    if len(sys.argv) > 1:
        try:
            config["port"] = int(sys.argv[1])
        except ValueError:
            print("Usage: python shadow_web_server.py [port]")
            sys.exit(1)

    server = ShadowWebServer(config)
    server.start()

if __name__ == "__main__":
    main()
