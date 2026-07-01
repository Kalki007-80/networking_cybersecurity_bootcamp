#!/usr/bin/env python3

import socket
import ssl
import concurrent.futures
import json
import csv
import time
import sys
import os
from datetime import datetime

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    111: "RPCbind",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1723: "PPTP",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    27017: "MongoDB",
}

COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "reset": "\033[0m",
}

def print_banner():
    banner = r"""
============================================================
        SERVICE WHISPERER v3.0
        Day 8 Project
        Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def resolve_hostname(target):
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None

def grab_banner(ip, hostname, port, timeout=2.0):
    if port == 53:
        return None
    try:
        if port in [443, 993, 995, 8443]:
            with socket.create_connection((ip, port), timeout=timeout) as sock:
                context = ssl.create_default_context()
                ssl_sock = context.wrap_socket(sock, server_hostname=hostname)
                ssl_sock.send(b"HEAD / HTTP/1.1\r\nHost: " + hostname.encode() + b"\r\nConnection: close\r\n\r\n")
                response = ssl_sock.recv(4096).decode(errors="ignore")
                ssl_sock.close()
                return extract_server_header(response)
        else:
            with socket.create_connection((ip, port), timeout=timeout) as sock:
                if port in [80, 8080, 8000]:
                    sock.send(b"HEAD / HTTP/1.1\r\nHost: " + hostname.encode() + b"\r\nConnection: close\r\n\r\n")
                    response = sock.recv(4096).decode(errors="ignore")
                    return extract_server_header(response)
                elif port == 21:
                    response = sock.recv(1024).decode(errors="ignore")
                    return response.strip()
                elif port in [25, 110, 143]:
                    response = sock.recv(1024).decode(errors="ignore")
                    return response.strip()
                elif port == 22:
                    response = sock.recv(1024).decode(errors="ignore")
                    return response.strip()
                else:
                    sock.send(b"\n")
                    response = sock.recv(1024).decode(errors="ignore")
                    return response.strip()
    except socket.timeout:
        return None
    except socket.error:
        return None
    except Exception as e:
        return None

def extract_server_header(response):
    if not response:
        return None
    for line in response.splitlines():
        if line.lower().startswith("server:"):
            return line.strip()
    return response[:200] if response else None

def detect_webserver(header):
    if not header:
        return "Unknown"
    header_lower = header.lower()
    if "nginx" in header_lower:
        return "nginx"
    elif "apache" in header_lower:
        return "Apache"
    elif "cloudflare" in header_lower:
        return "Cloudflare"
    elif "iis" in header_lower:
        return "Microsoft IIS"
    elif "caddy" in header_lower:
        return "Caddy"
    elif "lighttpd" in header_lower:
        return "Lighttpd"
    else:
        return "Other"

def color_text(text, color):
    if sys.stdout.isatty():
        return f"{COLORS[color]}{text}{COLORS['reset']}"
    return text

def scan_port(ip, hostname, port, timeout=2.0):
    start = time.time()
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            connect_time = (time.time() - start) * 1000
            banner = grab_banner(ip, hostname, port, timeout)
            read_time = (time.time() - start) * 1000 - connect_time
            service = COMMON_PORTS.get(port, "Unknown")
            webserver = detect_webserver(banner) if banner and port in [80, 443, 8080, 8443] else "N/A"
            return port, True, service, banner, round(connect_time, 2), round(read_time, 2), webserver
    except socket.timeout:
        return port, False, None, None, None, None, None
    except ConnectionRefusedError:
        return port, False, None, None, None, None, None
    except Exception:
        return port, False, None, None, None, None, None

def scan_ports(ip, hostname, ports, timeout=2.0, max_workers=50, progress=True):
    results = []
    total = len(ports)
    done = 0
    cancelled = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {executor.submit(scan_port, ip, hostname, port, timeout): port for port in ports}
        try:
            for future in concurrent.futures.as_completed(future_to_port):
                if cancelled:
                    break
                done += 1
                port, is_open, service, banner, connect_time, read_time, webserver = future.result()
                if is_open:
                    results.append({
                        "port": port,
                        "state": "OPEN",
                        "service": service,
                        "banner": banner,
                        "connect_time_ms": connect_time,
                        "read_time_ms": read_time,
                        "webserver": webserver
                    })
                if progress:
                    sys.stdout.write(f"\r[{done}/{total}] ports scanned (open: {len(results)})   ")
                    sys.stdout.flush()
        except KeyboardInterrupt:
            cancelled = True
            print("\n\n[!] Scan cancelled by user. Saving partial results...")
    if progress:
        sys.stdout.write("\n")
    return results, cancelled

def get_user_ports():
    print("\nChoose port list:")
    print("  1. Common ports (recommended)")
    print("  2. Well-known ports (1-1024)")
    print("  3. Custom range (e.g., 20-100, 443, 8080)")
    choice = input("Enter choice (1/2/3): ").strip()
    if choice == "2":
        return list(range(1, 1025))
    elif choice == "3":
        custom = input("Enter ports/ranges (comma-separated, e.g., 22,80,443,1000-2000): ").strip()
        ports = []
        for part in custom.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                ports.extend(range(int(start), int(end)+1))
            else:
                ports.append(int(part))
        return ports
    else:
        return list(COMMON_PORTS.keys())

def ensure_scan_dir():
    date_dir = datetime.now().strftime("%Y%m%d")
    scan_dir = f"scan_history/{date_dir}"
    if not os.path.exists(scan_dir):
        os.makedirs(scan_dir)
    return scan_dir

def main():
    print_banner()
    target_input = input("Enter target (IP or hostname): ").strip()
    if not target_input:
        print("No target provided.")
        return
    ip = resolve_hostname(target_input)
    if not ip:
        print(f"Could not resolve hostname: {target_input}")
        return
    print(f"Resolved {target_input} -> {ip}")

    ports = get_user_ports()
    timeout_input = input("Timeout (seconds, default 2.0): ").strip()
    try:
        timeout = float(timeout_input)
    except ValueError:
        timeout = 2.0

    workers_input = input("Max workers (default 50): ").strip()
    try:
        max_workers = int(workers_input)
    except ValueError:
        max_workers = 50

    print(f"\nScanning {len(ports)} ports on {ip} with {max_workers} workers...")
    print("Press Ctrl+C to cancel.\n")
    start_time = time.time()
    open_ports, cancelled = scan_ports(ip, target_input, ports, timeout, max_workers, progress=True)
    duration = time.time() - start_time

    data = {
        "target": target_input,
        "ip": ip,
        "scan_start": datetime.now().isoformat(),
        "duration_seconds": round(duration, 2),
        "ports_scanned": len(ports),
        "open_ports": open_ports,
        "closed": len(ports) - len(open_ports),
        "cancelled": cancelled
    }

    print("\n" + "=" * 50)
    print("SERVICE WHISPERER SUMMARY")
    print("=" * 50)
    print(f"Target       : {target_input} ({ip})")
    print(f"Ports scanned: {data['ports_scanned']}")
    print(f"Open ports   : {len(open_ports)}")
    print(f"Closed       : {data['closed']}")
    print(f"Duration     : {data['duration_seconds']} s")
    if cancelled:
        print(color_text("[!] Scan was cancelled (partial results)", "yellow"))
    if open_ports:
        print("\nOpen ports with banners:")
        for p in open_ports:
            port_display = f"{p['port']:5}"
            if p['port'] in [22, 80, 443, 21, 25, 3306, 5432]:
                port_display = color_text(port_display, "green")
            elif p['port'] in [23, 445, 3389]:
                port_display = color_text(port_display, "yellow")
            banner_short = p['banner'][:60] if p['banner'] else "(no banner)"
            webserver_info = f" [{p['webserver']}]" if p['webserver'] != "N/A" else ""
            print(f"  {port_display} {p['service']:12} CONNECT:{p['connect_time_ms']:.2f}ms READ:{p['read_time_ms']:.2f}ms -> {banner_short}{webserver_info}")
    print("=" * 50)

    scan_dir = ensure_scan_dir()
    ts = datetime.now().strftime("%H%M%S")
    base_filename = f"service_scan_{ts}"
    json_file = f"{scan_dir}/{base_filename}.json"
    txt_file = f"{scan_dir}/{base_filename}.txt"
    csv_file = f"{scan_dir}/{base_filename}.csv"

    try:
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {json_file}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

    try:
        with open(txt_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("        SERVICE WHISPERER REPORT\n")
            f.write(f"  Generated: {data['scan_start']}\n")
            if cancelled:
                f.write("  [!] Scan was cancelled (partial results)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Target: {data['target']} ({data['ip']})\n")
            f.write(f"Ports scanned: {data['ports_scanned']}\n")
            f.write(f"Duration: {data['duration_seconds']} s\n\n")
            f.write("OPEN PORTS WITH BANNERS\n")
            f.write("-" * 40 + "\n")
            for p in open_ports:
                f.write(f"Port {p['port']:5} : {p['service']:12}\n")
                f.write(f"      Connect Time: {p['connect_time_ms']:.2f}ms\n")
                f.write(f"      Read Time   : {p['read_time_ms']:.2f}ms\n")
                if p['banner']:
                    f.write(f"      Banner      : {p['banner']}\n")
                else:
                    f.write(f"      Banner      : (none)\n")
                if p['webserver'] != "N/A":
                    f.write(f"      Web Server  : {p['webserver']}\n")
                f.write("\n")
            f.write("\n" + "=" * 60 + "\n")
        print(f"Text report saved to {txt_file}")
    except Exception as e:
        print(f"Failed to save text report: {e}")

    try:
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["port", "service", "connect_time_ms", "read_time_ms", "banner", "webserver"])
            for p in open_ports:
                writer.writerow([p["port"], p["service"], p["connect_time_ms"], p["read_time_ms"], p["banner"] or "", p["webserver"]])
        print(f"CSV report saved to {csv_file}")
    except Exception as e:
        print(f"Failed to save CSV: {e}")

    print("\nMission complete. Service Whisperer signing off.")

if __name__ == "__main__":
    main()
