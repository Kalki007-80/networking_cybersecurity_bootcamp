#!/usr/bin/env python3

import socket
import ipaddress
import concurrent.futures
import json
import csv
import time
import sys
import platform
from datetime import datetime

COMMON_PORTS = {
    20: "FTP-Data",
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

def print_banner():
    banner = r"""
============================================================
            PORT GATEKEEPER SCANNER v4.0
            Day 7 Project
            Author : Mukesh S
============================================================
"""
    print(banner)

def resolve_hostname(target):
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None

def scan_port(ip, port, timeout=2.0):
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        rtt = (time.time() - start) * 1000  # ms
        if result == 0:
            banner = grab_banner(sock, port)
            sock.close()
            service = identify_service(port)
            return port, True, service, banner, round(rtt, 2)
        sock.close()
        return port, False, None, None, None
    except Exception:
        return port, False, None, None, None

def grab_banner(sock, port):
    try:
        sock.settimeout(1.0)
        if port in [80, 443, 8080, 8443]:
            sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        elif port == 22:
            sock.send(b"\n")
        elif port == 21:
            pass
        else:
            sock.send(b"\n")
        banner = sock.recv(1024).decode(errors="ignore").strip()
        return banner[:200] if banner else None
    except Exception:
        return None

def identify_service(port):
    return COMMON_PORTS.get(port, "Unknown")

def scan_ports(ip, ports, timeout=2.0, max_workers=50, progress=True):
    results = []
    total = len(ports)
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {executor.submit(scan_port, ip, port, timeout): port for port in ports}
        for future in concurrent.futures.as_completed(future_to_port):
            done += 1
            port, is_open, service, banner, rtt = future.result()
            if is_open:
                results.append({
                    "port": port,
                    "state": "OPEN",
                    "service": service,
                    "banner": banner,
                    "rtt_ms": rtt
                })
            if progress:
                sys.stdout.write(f"\r[{done}/{total}] ports scanned (open: {len(results)})   ")
                sys.stdout.flush()
    if progress:
        sys.stdout.write("\n")
    return results

def get_ports_for_mode(mode):
    if mode == "fast":
        return list(COMMON_PORTS.keys())
    elif mode == "normal":
        return list(range(1, 1025))
    else:  # deep
        return list(range(1, 65536))

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

    print("\nScan modes:")
    print("  fast   - scan common ports only (fastest)")
    print("  normal - scan ports 1-1024 (common + well-known)")
    print("  deep   - scan all ports 1-65535 (slowest)")
    mode = input("Choose mode (fast/normal/deep): ").strip().lower()
    if mode not in ["fast", "normal", "deep"]:
        print("Invalid mode, defaulting to normal.")
        mode = "normal"

    timeout_input = input("Connection timeout (seconds, default 2.0): ").strip()
    try:
        timeout = float(timeout_input)
    except ValueError:
        timeout = 2.0

    workers_input = input("Max workers (default 50): ").strip()
    try:
        max_workers = int(workers_input)
    except ValueError:
        max_workers = 50

    ports = get_ports_for_mode(mode)
    print(f"\nScanning {len(ports)} ports on {ip} with {max_workers} workers...\n")
    start_time = time.time()
    open_ports = scan_ports(ip, ports, timeout, max_workers, progress=True)
    scan_duration = time.time() - start_time

    # Prepare data for reports
    data = {
        "target": target_input,
        "ip": ip,
        "mode": mode,
        "timeout": timeout,
        "workers": max_workers,
        "scan_start": datetime.now().isoformat(),
        "duration_seconds": round(scan_duration, 2),
        "ports_scanned": len(ports),
        "open_ports": open_ports,
        "closed_ports": len(ports) - len(open_ports)
    }

    # Display summary
    print("\n" + "=" * 50)
    print("SCAN SUMMARY")
    print("=" * 50)
    print(f"Target       : {target_input} ({ip})")
    print(f"Mode         : {mode}")
    print(f"Ports scanned: {data['ports_scanned']}")
    print(f"Open ports   : {len(open_ports)}")
    print(f"Closed       : {data['closed_ports']}")
    print(f"Duration     : {data['duration_seconds']} s")
    if open_ports:
        print("\nOpen ports:")
        for p in open_ports:
            banner_info = f" - {p['banner'][:60]}" if p['banner'] else ""
            print(f"  {p['port']:5} {p['state']:4} {p['service']:12} RTT:{p['rtt_ms']:.2f}ms{banner_info}")
    print("=" * 50)

    # Save reports
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"port_scan_{ts}.json"
    txt_file = f"port_scan_{ts}.txt"
    csv_file = f"port_scan_{ts}.csv"

    # JSON
    try:
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {json_file}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

    # TXT
    try:
        with open(txt_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("        PORT GATEKEEPER SCAN REPORT\n")
            f.write(f"  Generated: {data['scan_start']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Target: {data['target']} ({data['ip']})\n")
            f.write(f"Mode: {data['mode']}\n")
            f.write(f"Ports scanned: {data['ports_scanned']}\n")
            f.write(f"Duration: {data['duration_seconds']} s\n\n")
            f.write("OPEN PORTS\n")
            f.write("-" * 40 + "\n")
            for p in open_ports:
                f.write(f"Port {p['port']:5} : {p['state']:4} {p['service']:12} RTT:{p['rtt_ms']:.2f}ms\n")
                if p['banner']:
                    f.write(f"      Banner: {p['banner'][:150]}\n")
            f.write("\n" + "=" * 60 + "\n")
        print(f"Text report saved to {txt_file}")
    except Exception as e:
        print(f"Failed to save text report: {e}")

    # CSV
    try:
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["port", "state", "service", "rtt_ms", "banner"])
            for p in open_ports:
                writer.writerow([p["port"], p["state"], p["service"], p["rtt_ms"], p["banner"] or ""])
        print(f"CSV report saved to {csv_file}")
    except Exception as e:
        print(f"Failed to save CSV: {e}")

    print("\nScan complete.")

if __name__ == "__main__":
    main()
