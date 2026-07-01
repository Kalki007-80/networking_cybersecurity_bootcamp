#!/usr/bin/env python3

import socket
import subprocess
import json
import ssl
import re
import time
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# CONFIGURATION
# ============================================================

LOG_FILE = "logs/noc.log"
REPORTS_DIR = "reports"

# Common ports for scanning
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432, 6379, 8080, 8443, 27017]

# Service mapping
PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    993: "IMAPS", 995: "POP3S", 3306: "MySQL", 5432: "PostgreSQL",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
}

# Technology detection patterns
TECH_PATTERNS = {
    "WordPress": ["wp-content", "wp-includes", "wp-json"],
    "React": ["react.production.min.js", "react-dom", "_reactRoot"],
    "Angular": ["angular.js", "ng-app"],
    "Vue": ["vue.js", "v-app"],
    "Bootstrap": ["bootstrap.css", "bootstrap.min.css"],
    "jQuery": ["jquery.js", "jquery.min.js"],
    "Django": ["csrftoken", "django"],
    "Flask": ["flask"],
    "Laravel": ["laravel", "_token"],
    "Cloudflare": ["cf-ray", "cloudflare"],
    "nginx": ["nginx"],
    "Apache": ["apache"],
    "IIS": ["iis", "microsoft-iis"],
    "Caddy": ["caddy"]
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def print_banner():
    banner = """
============================================================
            SHADOW NETWORK OPERATION CENTER v1.0
            Final Bootcamp Project
            Author : Team Crypt0n1c
============================================================

NOTE: For educational use. Only scan hosts you own or have
explicit permission to test.
"""
    print(banner)

def log_message(msg, level="INFO"):
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] [{level}] {msg}\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
    print(msg)

def ensure_dirs():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def load_config(config_path="config/config.json"):
    """Load optional configuration; falls back to built-in defaults."""
    defaults = {
        "common_ports": COMMON_PORTS,
        "port_scan_workers": 50,
        "port_scan_timeout": 1.5,
        "ping_count": 4,
        "http_timeout": 5,
    }
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(defaults, f, indent=4)
        return defaults
    with open(config_path, "r") as f:
        cfg = json.load(f)
    for k, v in defaults.items():
        cfg.setdefault(k, v)
    return cfg

# ============================================================
# MISSION MANAGER
# ============================================================

class Mission:
    def __init__(self, target):
        self.target = target
        self.mission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.timestamp = datetime.now().isoformat()
        self.results = {}
        self.start_time = time.time()

    def add_phase(self, name, data):
        self.results[name] = data

    def elapsed(self):
        return round(time.time() - self.start_time, 2)

    def finalize(self):
        return {
            "mission_id": self.mission_id,
            "timestamp": self.timestamp,
            "target": self.target,
            "duration_seconds": self.elapsed(),
            "status": "complete",
            "results": self.results
        }

# ============================================================
# PHASE 1: DNS INTELLIGENCE
# ============================================================

def dns_resolve(host):
    result = {"ipv4": [], "ipv6": [], "reverse": None}
    try:
        addrinfo = socket.getaddrinfo(host, None)
        for addr in addrinfo:
            ip = addr[4][0]
            if ":" in ip:
                result["ipv6"].append(ip)
            else:
                result["ipv4"].append(ip)
        result["ipv4"] = list(set(result["ipv4"]))
        result["ipv6"] = list(set(result["ipv6"]))
        if result["ipv4"]:
            try:
                result["reverse"] = socket.gethostbyaddr(result["ipv4"][0])[0]
            except Exception:
                pass
    except Exception:
        pass
    return result

# ============================================================
# PHASE 2: PING
# ============================================================

def ping_host(ip, count=4):
    result = {"alive": False, "sent": count, "received": 0, "loss": 100.0,
              "min_rtt": None, "avg_rtt": None, "max_rtt": None}
    try:
        output = subprocess.check_output(
            ["ping", "-c", str(count), "-W", "1", ip],
            stderr=subprocess.DEVNULL, text=True
        )
        loss_match = re.search(r"(\d+)% packet loss", output)
        if loss_match:
            result["loss"] = float(loss_match.group(1))
        rtt_match = re.search(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)", output)
        if rtt_match:
            result["min_rtt"] = float(rtt_match.group(1))
            result["avg_rtt"] = float(rtt_match.group(2))
            result["max_rtt"] = float(rtt_match.group(3))
        sent_match = re.search(r"(\d+) packets transmitted, (\d+) received", output)
        if sent_match:
            result["sent"] = int(sent_match.group(1))
            result["received"] = int(sent_match.group(2))
        result["alive"] = result["received"] > 0
    except Exception:
        pass
    return result

# ============================================================
# PHASE 3: TRACEROUTE
# ============================================================

def traceroute(target, max_hops=30):
    result = {"hops": [], "count": 0}
    try:
        output = subprocess.check_output(
            ["tracepath", "-n", "-m", str(max_hops), target],
            stderr=subprocess.DEVNULL, text=True
        )
        for line in output.splitlines():
            match = re.search(r"^\s*(\d+):\s*([\d.]+)\s+([\d.]+)ms", line)
            if match:
                result["hops"].append({
                    "hop": int(match.group(1)),
                    "ip": match.group(2),
                    "rtt_ms": float(match.group(3))
                })
            if "reached" in line:
                break
        result["count"] = len(result["hops"])
    except Exception:
        pass
    return result

# ============================================================
# PHASE 4: PORT SCANNER (Threaded)
# ============================================================

def scan_port(ip, port, timeout=1.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = time.time()
        result = sock.connect_ex((ip, port))
        rtt = (time.time() - start) * 1000
        sock.close()
        return port, result == 0, round(rtt, 2)
    except Exception:
        return port, False, None

def port_scan(ip, ports=None, workers=50, timeout=1.5):
    if ports is None:
        ports = COMMON_PORTS
    results = {"open": [], "closed": []}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scan_port, ip, port, timeout): port for port in ports}
        for future in as_completed(futures):
            port, is_open, rtt = future.result()
            if is_open:
                results["open"].append({"port": port, "rtt_ms": rtt})
            else:
                results["closed"].append(port)
    results["open"].sort(key=lambda p: p["port"])
    results["closed"].sort()
    return results

# ============================================================
# PHASE 5: BANNER GRABBING
# ============================================================

def grab_banner(ip, port, timeout=2.0):
    service = PORT_SERVICES.get(port, "Unknown")
    banner = None
    try:
        if port in [443, 8443, 993, 995]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=ip)
            ssl_sock.send(b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
            response = ssl_sock.recv(4096).decode(errors="ignore")
            ssl_sock.close()
            for line in response.splitlines():
                if line.lower().startswith("server:"):
                    banner = line.strip()
                    break
            if not banner:
                banner = response[:200]
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            if port in [80, 8080]:
                sock.send(b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
                response = sock.recv(4096).decode(errors="ignore")
                for line in response.splitlines():
                    if line.lower().startswith("server:"):
                        banner = line.strip()
                        break
                if not banner:
                    banner = response[:200]
            else:
                sock.send(b"\n")
                response = sock.recv(1024).decode(errors="ignore")
                banner = response.strip()[:200]
            sock.close()
    except Exception:
        pass
    return {"port": port, "service": service, "banner": banner}

# ============================================================
# PHASE 6: SSL INSPECTION
# ============================================================

def ssl_inspect(ip, port=443):
    result = {
        "valid": False,
        "subject": None,
        "issuer": None,
        "not_before": None,
        "not_after": None,
        "serial": None,
        "tls_version": None,
        "cipher": None
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, port))
        context = ssl.create_default_context()
        ssl_sock = context.wrap_socket(sock, server_hostname=ip)
        cert = ssl_sock.getpeercert()
        result["valid"] = True
        result["subject"] = dict(x[0] for x in cert.get("subject", [])) if cert else None
        result["issuer"] = dict(x[0] for x in cert.get("issuer", [])) if cert else None
        result["not_before"] = cert.get("notBefore")
        result["not_after"] = cert.get("notAfter")
        result["serial"] = cert.get("serialNumber")
        result["tls_version"] = ssl_sock.version()
        result["cipher"] = ssl_sock.cipher()
        ssl_sock.close()
    except Exception:
        pass
    return result

# ============================================================
# PHASE 7: HTTP EXPLORER
# ============================================================

def http_explore(ip, port, host=None, use_ssl=False, timeout=5):
    if host is None:
        host = ip
    result = {
        "status_code": 0,
        "status_message": "Unknown",
        "headers": {},
        "body_preview": "",
        "body_size": 0,
        "redirects": 0,
        "final_url": None
    }
    try:
        if use_ssl:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_sock.settimeout(timeout)
            raw_sock.connect((ip, port))
            context = ssl.create_default_context()
            sock = context.wrap_socket(raw_sock, server_hostname=host)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
        request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        sock.close()
        text = response.decode(errors="ignore")
        if "\r\n\r\n" in text:
            headers_part, body_part = text.split("\r\n\r\n", 1)
        else:
            headers_part = text
            body_part = ""
        lines = headers_part.splitlines()
        if lines:
            status_match = re.search(r"HTTP/\d\.\d\s+(\d+)\s+(.*)", lines[0])
            if status_match:
                result["status_code"] = int(status_match.group(1))
                result["status_message"] = status_match.group(2)
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                result["headers"][key.strip().lower()] = value.strip()
        result["body_size"] = len(body_part)
        result["body_preview"] = body_part[:500]
        if result["status_code"] in [301, 302, 303, 307, 308]:
            location = result["headers"].get("location")
            if location:
                result["redirects"] = 1
                result["final_url"] = location
        else:
            result["final_url"] = f"{'https' if use_ssl else 'http'}://{host}"
    except Exception:
        pass
    return result

# ============================================================
# PHASE 8: SECURITY HEADERS
# ============================================================

def analyze_security_headers(headers):
    security = {
        "strict_transport_security": {"present": False, "value": "Not Set"},
        "content_security_policy": {"present": False, "value": "Not Set"},
        "x_frame_options": {"present": False, "value": "Not Set"},
        "x_content_type_options": {"present": False, "value": "Not Set"},
        "referrer_policy": {"present": False, "value": "Not Set"},
        "permissions_policy": {"present": False, "value": "Not Set"}
    }
    # HTTP headers use hyphens; our security dict keys use underscores.
    normalized = {k.replace("-", "_"): v for k, v in headers.items()}
    for key in security:
        if key in normalized:
            security[key]["present"] = True
            security[key]["value"] = normalized[key]
    return security

# ============================================================
# PHASE 9: COOKIES
# ============================================================

def analyze_cookies(headers):
    cookies = []
    set_cookie = headers.get("set-cookie", "")
    if set_cookie:
        for cookie in set_cookie.split(","):
            cookie = cookie.strip()
            parts = cookie.split(";")
            name_value = parts[0].strip()
            flags = {}
            for part in parts[1:]:
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    flags[k.lower().strip()] = v.strip()
                else:
                    flags[part.lower().strip()] = True
            if "=" in name_value:
                name, value = name_value.split("=", 1)
            else:
                name, value = name_value, ""
            cookie_data = {
                "name": name,
                "value": value,
                "secure": flags.get("secure", False),
                "httponly": flags.get("httponly", False),
                "samesite": flags.get("samesite", "None"),
                "expires": flags.get("expires", "Session"),
                "domain": flags.get("domain", None),
                "path": flags.get("path", "/")
            }
            cookies.append(cookie_data)
    return cookies

# ============================================================
# PHASE 10: TECHNOLOGY DETECTION
# ============================================================

def detect_technologies(headers, body):
    detected = []
    full_text = body.lower() if body else ""
    headers_text = " ".join([f"{k}: {v}" for k, v in headers.items()]).lower()
    combined = full_text + " " + headers_text
    for tech, patterns in TECH_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in combined:
                detected.append(tech)
                break
    return list(set(detected))

# ============================================================
# REPORT GENERATOR
# ============================================================

def _esc(value):
    """Minimal HTML escaping for report output."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def generate_report(report_data):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(REPORTS_DIR, f"noc_report_{ts}.json")
    txt_file = os.path.join(REPORTS_DIR, f"noc_report_{ts}.txt")
    html_file = os.path.join(REPORTS_DIR, f"noc_report_{ts}.html")

    with open(json_file, "w") as f:
        json.dump(report_data, f, indent=4)

    with open(txt_file, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  SHADOW NETWORK OPERATION CENTER REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Mission ID: {report_data['mission_id']}\n")
        f.write(f"Target    : {report_data['target']}\n")
        f.write(f"Timestamp : {report_data['timestamp']}\n")
        f.write(f"Duration  : {report_data['duration_seconds']}s\n")
        f.write(f"Status    : {report_data['status']}\n\n")
        for phase, data in report_data["results"].items():
            f.write(f"\n{phase.upper()}\n")
            f.write("-" * 40 + "\n")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        f.write(f"  {key}: {len(value)} items\n")
                    else:
                        f.write(f"  {key}: {value}\n")
            elif isinstance(data, list):
                for item in data[:10]:
                    f.write(f"  {item}\n")
                if len(data) > 10:
                    f.write(f"  ... and {len(data)-10} more\n")

    with open(html_file, "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head><title>SNOC Report</title>
<style>
body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:30px;max-width:1200px;margin:auto}
h1{color:#58a6ff;border-bottom:2px solid #30363d;padding-bottom:10px}
h2{color:#58a6ff;margin-top:30px}
.section{background:#161b22;padding:20px;border-radius:10px;margin:15px 0;border-left:4px solid #58a6ff}
.status-ok{color:#3fb950}
.status-err{color:#f85149}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:15px}
.host-item{background:#0d1117;padding:10px;border-radius:6px;border:1px solid #30363d}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:8px;border-bottom:2px solid #30363d;color:#8b949e}
td{padding:8px;border-bottom:1px solid #21262d}
</style>
</head>
<body>
<h1>Shadow Network Operation Center Report</h1>
<p><strong>Mission:</strong> """ + _esc(report_data['mission_id']) + """</p>
<p><strong>Target:</strong> """ + _esc(report_data['target']) + """</p>
<p><strong>Timestamp:</strong> """ + _esc(report_data['timestamp']) + """</p>
<p><strong>Duration:</strong> """ + _esc(report_data['duration_seconds']) + """s</p>
""")
        for phase, data in report_data["results"].items():
            f.write(f'<div class="section"><h2>{_esc(phase.replace("_"," ").title())}</h2>')
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        f.write(f"<p><strong>{_esc(key)}:</strong> {len(value)} items</p>")
                        f.write('<table><tr><th>Details</th></tr>')
                        for item in value[:10]:
                            f.write(f"<tr><td>{_esc(item)}</td></tr>")
                        if len(value) > 10:
                            f.write(f"<tr><td>... and {len(value)-10} more</td></tr>")
                        f.write('</table>')
                    else:
                        f.write(f"<p><strong>{_esc(key)}:</strong> {_esc(value)}</p>")
            elif isinstance(data, list):
                f.write('<table><tr><th>Item</th></tr>')
                for item in data[:10]:
                    f.write(f"<tr><td>{_esc(item)}</td></tr>")
                if len(data) > 10:
                    f.write(f"<tr><td>... and {len(data)-10} more</td></tr>")
                f.write('</table>')
            f.write('</div>')
        f.write("</body></html>")

    return json_file, txt_file, html_file

# ============================================================
# MAIN ORCHESTRATION
# ============================================================

def main():
    print_banner()
    ensure_dirs()
    config = load_config()

    if len(sys.argv) > 1:
        target = sys.argv[1].strip()
    else:
        target = input("Enter target (domain or IP): ").strip()

    if not target:
        print("No target provided.")
        return

    mission = Mission(target)
    log_message(f"[*] Starting mission: {mission.mission_id} -> {target}")

    # Phase 1: DNS
    print("\n[Phase 1] DNS Intelligence")
    dns = dns_resolve(target)
    mission.add_phase("dns", dns)
    print(f"  IPv4: {', '.join(dns['ipv4']) if dns['ipv4'] else 'None'}")
    if not dns['ipv4']:
        log_message("[!] No IPv4 found. Aborting.", "ERROR")
        report = mission.finalize()
        report["status"] = "aborted_no_dns"
        generate_report(report)
        return
    ip = dns['ipv4'][0]

    # Phase 2: Ping
    print("\n[Phase 2] Reachability")
    ping = ping_host(ip, count=config["ping_count"])
    mission.add_phase("ping", ping)
    status = "ALIVE" if ping['alive'] else "DEAD"
    print(f"  Status: {status}")
    if ping['alive']:
        print(f"  Avg RTT: {ping['avg_rtt']} ms")

    # Phase 3: Traceroute
    print("\n[Phase 3] Route Intelligence")
    trace = traceroute(target)
    mission.add_phase("traceroute", trace)
    print(f"  Hops: {trace['count']}")
    if trace['hops']:
        for hop in trace['hops'][:5]:
            print(f"  Hop {hop['hop']:2}: {hop['ip']:20} {hop['rtt_ms']:.2f}ms")
        if trace['count'] > 5:
            print(f"  ... and {trace['count']-5} more")

    # Phase 4: Port Scan
    print("\n[Phase 4] Port Intelligence")
    scan = port_scan(ip, config["common_ports"], config["port_scan_workers"], config["port_scan_timeout"])
    mission.add_phase("port_scan", scan)
    print(f"  Open: {len(scan['open'])}")
    for p in scan['open']:
        print(f"    {p['port']:5} OPEN  RTT: {p['rtt_ms']:.2f}ms")

    # Phase 5: Banners
    print("\n[Phase 5] Service Intelligence")
    banners = []
    for p in scan['open']:
        b = grab_banner(ip, p['port'])
        banners.append(b)
        preview = (b['banner'][:60] if b['banner'] else '(none)')
        print(f"  {p['port']:5} {b['service']:12} -> {preview}")
    mission.add_phase("banners", banners)

    # Phase 6: SSL
    print("\n[Phase 6] TLS Intelligence")
    ssl_info = None
    if any(p['port'] == 443 for p in scan['open']):
        ssl_info = ssl_inspect(ip)
        mission.add_phase("ssl", ssl_info)
        if ssl_info['valid']:
            print("  Valid: Yes")
            print(f"  Subject: {ssl_info['subject'].get('commonName', 'N/A') if ssl_info['subject'] else 'N/A'}")
            print(f"  Issuer: {ssl_info['issuer'].get('organizationName', 'N/A') if ssl_info['issuer'] else 'N/A'}")
        else:
            print("  Valid: No")
    else:
        print("  No HTTPS port found")

    # Phase 7: HTTP
    print("\n[Phase 7] HTTP Intelligence")
    http_port = None
    if any(p['port'] == 443 for p in scan['open']):
        http_port = 443
    elif any(p['port'] == 80 for p in scan['open']):
        http_port = 80
    http = None
    if http_port:
        use_ssl = http_port == 443
        http = http_explore(ip, http_port, target, use_ssl, config["http_timeout"])
        mission.add_phase("http", http)
        print(f"  Status: {http['status_code']} {http['status_message']}")
        print(f"  Server: {http['headers'].get('server', 'Unknown')}")
    else:
        print("  No HTTP/HTTPS port found")

    # Phase 8: Security Headers
    print("\n[Phase 8] Security Analysis")
    security = {}
    if http and http['headers']:
        security = analyze_security_headers(http['headers'])
        mission.add_phase("security", security)
        score = 0
        for key, value in security.items():
            status_icon = "OK " if value['present'] else "MISS"
            print(f"  [{status_icon}] {key}: {value['value']}")
            if value['present']:
                score += 1
        rating = "Poor" if score < 3 else "Fair" if score < 5 else "Good"
        print(f"  Security Rating: {rating} ({score}/6)")

    # Phase 9: Cookies
    print("\n[Phase 9] Cookie Intelligence")
    cookies = []
    if http and http['headers']:
        cookies = analyze_cookies(http['headers'])
        mission.add_phase("cookies", cookies)
        if cookies:
            for c in cookies:
                print(f"  {c['name']}: Secure={c['secure']}, HttpOnly={c['httponly']}, SameSite={c['samesite']}")
        else:
            print("  No cookies found")

    # Phase 10: Technology Detection
    print("\n[Phase 10] Technology Detection")
    tech = []
    if http and http['headers'] and http['body_preview']:
        tech = detect_technologies(http['headers'], http['body_preview'])
        mission.add_phase("technologies", tech)
        if tech:
            print(f"  Detected: {', '.join(tech)}")
        else:
            print("  No technologies detected")

    # Finalize & Report
    report = mission.finalize()
    json_file, txt_file, html_file = generate_report(report)
    print("\n[+] Reports generated:")
    print(f"    JSON: {json_file}")
    print(f"    TXT : {txt_file}")
    print(f"    HTML: {html_file}")
    print(f"\nTotal duration: {mission.elapsed()}s")
    log_message("[+] Mission complete.")

if __name__ == "__main__":
    main()
