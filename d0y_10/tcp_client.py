#!/usr/bin/env python3

import socket
import ssl
import json
import time
import re
from datetime import datetime
from urllib.parse import urlparse

BUFFER_SIZE = 4096
TIMEOUT = 10

def print_banner():
    banner = """
============================================================
            TCP CLIENT EXPLORER v2.0
            Day 10 Project
            Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def parse_target(input_str):
    if "://" in input_str:
        parsed = urlparse(input_str)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        use_ssl = parsed.scheme == "https"
        return host, port, path, use_ssl
    else:
        parts = input_str.split(":")
        if len(parts) == 2:
            host = parts[0]
            try:
                port = int(parts[1])
            except:
                port = 80
            return host, port, "/", False
        else:
            return input_str, 80, "/", False

def build_http_request(method, path, host, headers=None, data=None, auth=None):
    if headers is None:
        headers = {}
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    request += "User-Agent: TCP-Client-Explorer/2.0\r\n"
    request += "Connection: close\r\n"
    request += "Accept: */*\r\n"
    request += "Accept-Encoding: identity\r\n"
    for key, value in headers.items():
        request += f"{key}: {value}\r\n"
    if data:
        request += f"Content-Length: {len(data)}\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
    request += "\r\n"
    if data:
        request += data
    return request

def send_tcp_request(host, port, request, use_ssl=False, timeout=TIMEOUT):
    start_total = time.time()
    try:
        ip = socket.gethostbyname(host)
        dns_time = (time.time() - start_total) * 1000
    except socket.gaierror:
        return None, {"dns_ms": None, "connect_ms": None, "tls_ms": None, "transfer_ms": None, "total_ms": None}, None

    connect_start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        connect_time = (time.time() - connect_start) * 1000
    except Exception:
        return None, {"dns_ms": dns_time, "connect_ms": None, "tls_ms": None, "transfer_ms": None, "total_ms": None}, None

    tls_time = 0
    cert = None
    if use_ssl:
        tls_start = time.time()
        try:
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            tls_time = (time.time() - tls_start) * 1000
            cert = ssl_sock.getpeercert()
        except Exception:
            return None, {"dns_ms": dns_time, "connect_ms": connect_time, "tls_ms": None, "transfer_ms": None, "total_ms": None}, None
    else:
        ssl_sock = sock

    transfer_start = time.time()
    try:
        ssl_sock.sendall(request.encode())
        response = b""
        while True:
            chunk = ssl_sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            response += chunk
        transfer_time = (time.time() - transfer_start) * 1000
        ssl_sock.close()
    except Exception:
        return None, {"dns_ms": dns_time, "connect_ms": connect_time, "tls_ms": tls_time, "transfer_ms": None, "total_ms": None}, None

    total_time = (time.time() - start_total) * 1000
    timings = {
        "dns_ms": round(dns_time, 2),
        "connect_ms": round(connect_time, 2),
        "tls_ms": round(tls_time, 2) if use_ssl else 0,
        "transfer_ms": round(transfer_time, 2),
        "total_ms": round(total_time, 2)
    }
    return response, timings, cert

def parse_http_response(response):
    try:
        text = response.decode("utf-8", errors="replace")
    except:
        return None, None, None

    if "\r\n\r\n" in text:
        header_part, body_part = text.split("\r\n\r\n", 1)
    else:
        header_part = text
        body_part = ""

    lines = header_part.splitlines()
    status_line = lines[0] if lines else ""

    parts = status_line.split(" ", 2)
    if len(parts) >= 3:
        version = parts[0]
        try:
            status_code = int(parts[1])
        except:
            status_code = 0
        status_message = parts[2]
    else:
        status_code = 0
        status_message = "Unknown"

    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    return headers, body_part, {"status_code": status_code, "status_message": status_message}

def get_issuer_org(cert):
    if not cert:
        return "Unknown"
    issuer = cert.get("issuer")
    if not issuer:
        return "Unknown"
    for item in issuer:
        if isinstance(item, tuple) and len(item) == 2:
            if item[0] == "organizationName":
                return item[1]
    return "Unknown"

def save_report(data, host, port):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_host = host.replace(".", "_")
    json_file = f"tcp_scan_{safe_host}_{ts}.json"
    txt_file = f"tcp_scan_{safe_host}_{ts}.txt"

    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[+] JSON report: {json_file}")

    with open(txt_file, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("        TCP CLIENT EXPLORER REPORT\n")
        f.write(f"  Generated: {data['timestamp']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Target: {host}:{port}\n")
        f.write(f"SSL   : {'Yes' if data['ssl'] else 'No'}\n")
        f.write(f"Method: {data['method']}\n")
        f.write(f"Path  : {data['path']}\n")
        f.write("\n")
        f.write("TIMING BREAKDOWN (ms)\n")
        f.write("-" * 40 + "\n")
        for key in ['dns_ms', 'connect_ms', 'tls_ms', 'transfer_ms', 'total_ms']:
            f.write(f"{key.replace('_', ' ').title():12}: {data['timings'][key]}\n")
        f.write("\n")

        if data.get('certificate'):
            f.write("TLS CERTIFICATE\n")
            f.write("-" * 40 + "\n")
            cert = data['certificate']
            f.write(f"Subject  : {cert.get('subject', {})}\n")
            f.write(f"Issuer   : {cert.get('issuer', {})}\n")
            f.write(f"Not Before: {cert.get('not_before', 'N/A')}\n")
            f.write(f"Not After : {cert.get('not_after', 'N/A')}\n")
            f.write(f"Serial   : {cert.get('serial_number', 'N/A')}\n\n")

        if data['status_code']:
            f.write("RESPONSE STATUS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Status : {data['status_code']} {data['status_message']}\n\n")

        f.write("HEADERS\n")
        f.write("-" * 40 + "\n")
        for key, value in data['headers'].items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")

        f.write("BODY PREVIEW (first 500 chars)\n")
        f.write("-" * 40 + "\n")
        f.write(data['body_preview'])
        if len(data['body_preview']) >= 500:
            f.write("\n... (truncated)")
        f.write("\n")
        f.write("=" * 60 + "\n")
    print(f"[+] Text report: {txt_file}")
    return json_file, txt_file

def main():
    print_banner()
    target = input("Enter target (e.g., example.com:80 or https://example.com): ").strip()
    if not target:
        print("No target provided.")
        return

    host, port, path, use_ssl = parse_target(target)
    print(f"[*] Target resolved: {host}:{port}, path: {path}, SSL: {use_ssl}")

    method = input("HTTP method (GET/HEAD/POST/PUT/DELETE, default GET): ").strip().upper()
    if method not in ["GET", "HEAD", "POST", "PUT", "DELETE"]:
        method = "GET"

    data = None
    if method in ["POST", "PUT"]:
        data = input("Request data (key1=value1&key2=value2): ").strip()
        if not data:
            data = ""

    custom_headers = {}
    headers_input = input("Custom headers (key1:value1,key2:value2): ").strip()
    if headers_input:
        for pair in headers_input.split(","):
            if ":" in pair:
                k, v = pair.split(":", 1)
                custom_headers[k.strip()] = v.strip()

    request = build_http_request(method, path, host, custom_headers, data)
    print(f"\n[*] Sending request...\n{request}")

    response, timings, cert = send_tcp_request(host, port, request, use_ssl)
    if not response:
        print("[!] Failed to connect or receive response.")
        return

    headers, body, status_info = parse_http_response(response)

    print("\n" + "=" * 50)
    print("TCP CLIENT EXPLORER SUMMARY")
    print("=" * 50)
    print(f"Target    : {host}:{port}")
    print(f"SSL       : {'Yes' if use_ssl else 'No'}")
    print(f"Status    : {status_info['status_code']} {status_info['status_message']}")
    print(f"Timing    : {timings['total_ms']:.2f}ms total")
    print(f"   DNS: {timings['dns_ms']:.2f}ms")
    print(f"   Connect: {timings['connect_ms']:.2f}ms")
    if use_ssl:
        print(f"   TLS: {timings['tls_ms']:.2f}ms")
    print(f"   Transfer: {timings['transfer_ms']:.2f}ms")
    print(f"Headers   : {len(headers)}")
    print(f"Body Size : {len(body)} bytes")
    if cert:
        issuer = get_issuer_org(cert)
        print(f"SSL Cert  : {issuer}")
    print("=" * 50)

    data_report = {
        "timestamp": datetime.now().isoformat(),
        "target": f"{host}:{port}",
        "host": host,
        "port": port,
        "ssl": use_ssl,
        "path": path,
        "method": method,
        "timings": timings,
        "certificate": cert,
        "status_code": status_info['status_code'],
        "status_message": status_info['status_message'],
        "headers": headers,
        "body_preview": body[:500] if body else "",
        "body_size": len(body)
    }

    save_report(data_report, host, port)
    print("\n[+] Investigation complete.")

if __name__ == "__main__":
    main()
