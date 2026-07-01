#!/usr/bin/env python3

import socket
import ssl
import json
import time
import sys
import re
import base64
from datetime import datetime
from urllib.parse import urlparse

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

def print_banner():
    banner = """
============================================================
            HTTP INVESTIGATOR v3.0
            Day 9 Project
            Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def parse_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
        parsed = urlparse(url)
    return parsed

def resolve_hostname_with_time(host):
    start = time.time()
    try:
        addrs = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)
        ip = addrs[0][4][0]
        elapsed = (time.time() - start) * 1000
        return ip, elapsed
    except socket.gaierror:
        return None, None

def build_http_request(method, path, host, headers, data=None, auth=None):
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    request += "User-Agent: HTTP-Investigator/3.0\r\n"
    if not headers.get("Connection", ""):
        request += "Connection: close\r\n"
    if auth:
        credentials = f"{auth['username']}:{auth['password']}"
        encoded = base64.b64encode(credentials.encode()).decode()
        request += f"Authorization: Basic {encoded}\r\n"
    for key, value in headers.items():
        request += f"{key}: {value}\r\n"
    if data and method in ["POST", "PUT"]:
        request += f"Content-Length: {len(data)}\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
    request += "\r\n"
    if data and method in ["POST", "PUT"]:
        request += data
    return request

def connect_via_proxy(proxy_url, target_host, target_port, timeout=10):
    proxy_parsed = parse_url(proxy_url)
    proxy_host = proxy_parsed.hostname
    proxy_port = proxy_parsed.port or 8080
    proxy_ssl = proxy_parsed.scheme == "https"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((proxy_host, proxy_port))
    if proxy_ssl:
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=proxy_host)
    connect_req = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n"
    sock.send(connect_req.encode())
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
        if b"\r\n\r\n" in response:
            break
    if b"200" not in response:
        raise Exception("Proxy CONNECT failed")
    return sock

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

def send_http_request(host, port, path, method="GET", headers=None, data=None, auth=None, use_ssl=False, timeout=10, proxy=None, keep_alive=False):
    if headers is None:
        headers = {}
    if keep_alive:
        headers["Connection"] = "keep-alive"
    
    ip, dns_time = resolve_hostname_with_time(host)
    if not ip:
        return None, {
            "dns_ms": None,
            "connect_ms": None,
            "tls_ms": None,
            "transfer_ms": None,
            "total_ms": None
        }, None
    
    connect_start = time.time()
    try:
        if proxy:
            sock = connect_via_proxy(proxy, host, port, timeout)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
        connect_time = (time.time() - connect_start) * 1000
    except Exception:
        total = (dns_time or 0)
        timings = {
            "dns_ms": round(dns_time, 2) if dns_time else None,
            "connect_ms": None,
            "tls_ms": None,
            "transfer_ms": None,
            "total_ms": round(total, 2)
        }
        return None, timings, None
    
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
            total = (dns_time or 0) + (connect_time or 0)
            timings = {
                "dns_ms": round(dns_time, 2) if dns_time else None,
                "connect_ms": round(connect_time, 2) if connect_time else None,
                "tls_ms": None,
                "transfer_ms": None,
                "total_ms": round(total, 2)
            }
            return None, timings, None
    else:
        ssl_sock = sock
    
    request = build_http_request(method, path, host, headers, data, auth)
    transfer_start = time.time()
    
    try:
        if use_ssl:
            ssl_sock.send(request.encode())
        else:
            sock.send(request.encode())
    except Exception:
        total = (dns_time or 0) + (connect_time or 0) + (tls_time or 0)
        timings = {
            "dns_ms": round(dns_time, 2) if dns_time else None,
            "connect_ms": round(connect_time, 2) if connect_time else None,
            "tls_ms": round(tls_time, 2) if use_ssl else 0,
            "transfer_ms": None,
            "total_ms": round(total, 2)
        }
        return None, timings, None
    
    response = b""
    try:
        while True:
            if use_ssl:
                chunk = ssl_sock.recv(4096)
            else:
                chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except Exception:
        pass
    
    transfer_time = (time.time() - transfer_start) * 1000
    
    if not keep_alive:
        if use_ssl:
            ssl_sock.close()
        else:
            sock.close()
    else:
        if use_ssl:
            ssl_sock.close()
        else:
            sock.close()
    
    total = (dns_time or 0) + (connect_time or 0) + (tls_time or 0) + (transfer_time or 0)
    timings = {
        "dns_ms": round(dns_time, 2) if dns_time else None,
        "connect_ms": round(connect_time, 2) if connect_time else None,
        "tls_ms": round(tls_time, 2) if use_ssl else 0,
        "transfer_ms": round(transfer_time, 2) if transfer_time else None,
        "total_ms": round(total, 2)
    }
    
    try:
        response_text = response.decode(errors="ignore")
    except:
        response_text = ""
    
    return response_text, timings, cert

def parse_http_response(response):
    if not response:
        return None
    lines = response.splitlines()
    if not lines:
        return None
    status_line = lines[0]
    status_match = re.search(r'HTTP/\d\.\d\s+(\d+)\s+(.*)', status_line)
    if not status_match:
        return None
    status_code = int(status_match.group(1))
    status_message = status_match.group(2)
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
    return {
        "status_code": status_code,
        "status_message": status_message,
        "headers": headers,
        "body": body,
        "raw": response[:500] + ("..." if len(response) > 500 else "")
    }

def validate_response(parsed, schema=None):
    if not parsed:
        return False, "No response"
    if parsed["status_code"] < 200 or parsed["status_code"] >= 300:
        return False, f"HTTP error {parsed['status_code']}"
    if schema and HAS_JSONSCHEMA:
        try:
            body = parsed["body"]
            if not body:
                return False, "Empty response body"
            json_data = json.loads(body)
            jsonschema.validate(json_data, schema)
            return True, "Schema validation passed"
        except json.JSONDecodeError:
            return False, "Response is not valid JSON"
        except jsonschema.ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
    elif schema:
        return False, "jsonschema module not installed"
    else:
        return True, "Status OK"

def get_security_headers(headers):
    security = {}
    security["strict_transport_security"] = headers.get("strict-transport-security", "Not Set")
    security["content_security_policy"] = headers.get("content-security-policy", "Not Set")
    security["x_frame_options"] = headers.get("x-frame-options", "Not Set")
    security["x_content_type_options"] = headers.get("x-content-type-options", "Not Set")
    security["referrer_policy"] = headers.get("referrer-policy", "Not Set")
    security["x_xss_protection"] = headers.get("x-xss-protection", "Not Set")
    return security

def get_cookies(headers):
    cookies = []
    set_cookie = headers.get("set-cookie", "")
    if set_cookie:
        for cookie in set_cookie.split(","):
            cookie = cookie.strip()
            if ";" in cookie:
                name_value = cookie.split(";")[0].strip()
            else:
                name_value = cookie
            cookies.append(name_value)
    return cookies

def follow_redirects(url, method="GET", max_redirects=5, proxy=None):
    current_url = url
    redirect_count = 0
    final_url = url
    for i in range(max_redirects):
        parsed = parse_url(current_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        use_ssl = parsed.scheme == "https"
        response, timings, cert = send_http_request(host, port, path, method="HEAD", use_ssl=use_ssl, proxy=proxy)
        if not response:
            break
        parsed_response = parse_http_response(response)
        if not parsed_response:
            break
        if parsed_response["status_code"] in [301, 302, 303, 307, 308]:
            location = parsed_response["headers"].get("location")
            if not location:
                break
            if location.startswith("/"):
                current_url = f"{parsed.scheme}://{host}{location}"
            elif location.startswith("http"):
                current_url = location
            else:
                current_url = f"{parsed.scheme}://{host}/{location}"
            redirect_count += 1
            final_url = current_url
        else:
            break
    return final_url, redirect_count

def analyze_url(url, method="GET", headers=None, data=None, auth=None, proxy=None, keep_alive=False, validation_schema=None):
    parsed = parse_url(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    use_ssl = parsed.scheme == "https"
    
    result = {
        "url": url,
        "host": host,
        "port": port,
        "path": path,
        "ssl": use_ssl,
        "method": method,
        "proxy": proxy,
        "keep_alive": keep_alive,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n[*] Investigating {url}")
    print(f"[*] Resolved: {host}:{port}")
    print(f"[*] Method: {method}")
    if proxy:
        print(f"[*] Using proxy: {proxy}")
    
    response, timings, cert = send_http_request(host, port, path, method=method, headers=headers, data=data, auth=auth, use_ssl=use_ssl, proxy=proxy, keep_alive=keep_alive)
    
    if not response:
        print("[!] Failed to connect")
        return None
    
    parsed_response = parse_http_response(response)
    if not parsed_response:
        print("[!] Invalid response")
        return None
    
    valid, validation_msg = validate_response(parsed_response, validation_schema)
    result["validation"] = {
        "valid": valid,
        "message": validation_msg,
        "schema_used": validation_schema is not None
    }
    result["timings"] = timings
    result["certificate"] = cert
    result["head"] = {
        "status_code": parsed_response["status_code"],
        "status_message": parsed_response["status_message"],
        "headers": parsed_response["headers"],
        "response_time_ms": timings["total_ms"]
    }
    
    final_url, redirect_count = follow_redirects(url, method=method, proxy=proxy)
    result["redirects"] = {
        "count": redirect_count,
        "final_url": final_url
    }
    
    if method in ["GET", "POST", "PUT", "DELETE"]:
        result["body"] = {
            "status_code": parsed_response["status_code"],
            "status_message": parsed_response["status_message"],
            "headers": parsed_response["headers"],
            "response_time_ms": timings["total_ms"],
            "body_size": len(parsed_response["body"]),
            "body_preview": parsed_response["body"][:500] if parsed_response["body"] else ""
        }
    
    result["security"] = get_security_headers(parsed_response["headers"])
    result["cookies"] = get_cookies(parsed_response["headers"])
    
    return result

def save_report(data, filename=None):
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"http_investigation_{ts}"
    json_file = f"{filename}.json"
    txt_file = f"{filename}.txt"
    
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[+] JSON report: {json_file}")
    
    with open(txt_file, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("        HTTP INVESTIGATOR REPORT\n")
        f.write(f"  Generated: {data['timestamp']}\n")
        f.write("=" * 60 + "\n\n")
        f.write("TARGET\n")
        f.write("-" * 40 + "\n")
        f.write(f"URL    : {data['url']}\n")
        f.write(f"Host   : {data['host']}:{data['port']}\n")
        f.write(f"SSL    : {'Yes' if data['ssl'] else 'No'}\n")
        f.write(f"Method : {data['method']}\n")
        if data.get('proxy'):
            f.write(f"Proxy  : {data['proxy']}\n")
        if data.get('keep_alive'):
            f.write("Keep-Alive : Yes\n")
        f.write("\n")
        
        f.write("TIMING BREAKDOWN (ms)\n")
        f.write("-" * 40 + "\n")
        for key in ['dns_ms', 'connect_ms', 'tls_ms', 'transfer_ms', 'total_ms']:
            val = data['timings'].get(key)
            if val is not None:
                f.write(f"{key.replace('_', ' ').title():12}: {val}\n")
            else:
                f.write(f"{key.replace('_', ' ').title():12}: N/A\n")
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
        
        f.write("REDIRECTS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Count     : {data['redirects']['count']}\n")
        f.write(f"Final URL : {data['redirects']['final_url']}\n\n")
        
        f.write("HEAD RESPONSE\n")
        f.write("-" * 40 + "\n")
        f.write(f"Status : {data['head']['status_code']} {data['head']['status_message']}\n")
        f.write(f"Time   : {data['head']['response_time_ms']:.2f}ms\n")
        f.write("Headers:\n")
        for key, value in data['head']['headers'].items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
        if "body" in data:
            f.write("BODY RESPONSE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Status      : {data['body']['status_code']} {data['body']['status_message']}\n")
            f.write(f"Time        : {data['body']['response_time_ms']:.2f}ms\n")
            f.write(f"Body Size   : {data['body']['body_size']} bytes\n")
            f.write("\n")
            f.write("VALIDATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"Valid       : {data['validation']['valid']}\n")
            f.write(f"Message     : {data['validation']['message']}\n")
            if data['validation']['schema_used']:
                f.write("Schema      : Provided\n")
            f.write("\n")
        
        f.write("SECURITY HEADERS\n")
        f.write("-" * 40 + "\n")
        for key, value in data['security'].items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
        if data['cookies']:
            f.write("COOKIES\n")
            f.write("-" * 40 + "\n")
            for cookie in data['cookies']:
                f.write(f"  {cookie}\n")
            f.write("\n")
        
        if "body" in data and data['body']['body_preview']:
            f.write("BODY PREVIEW\n")
            f.write("-" * 40 + "\n")
            f.write(data['body']['body_preview'])
            if data['body']['body_size'] > 500:
                f.write("\n... (truncated)")
            f.write("\n")
        
        f.write("=" * 60 + "\n")
    print(f"[+] Text report: {txt_file}")
    return json_file, txt_file

def main():
    print_banner()
    url = input("Enter URL (e.g., https://example.com): ").strip()
    if not url:
        print("No URL provided.")
        return
    
    method = input("HTTP method (GET/HEAD/POST/PUT/DELETE, default GET): ").strip().upper()
    if method not in ["GET", "HEAD", "POST", "PUT", "DELETE"]:
        method = "GET"
    
    data = None
    if method in ["POST", "PUT"]:
        data = input("Request data (e.g., key1=value1&key2=value2): ").strip()
        if not data:
            data = ""
    
    custom_headers = {}
    headers_input = input("Custom headers (key1:value1,key2:value2): ").strip()
    if headers_input:
        for pair in headers_input.split(","):
            if ":" in pair:
                k, v = pair.split(":", 1)
                custom_headers[k.strip()] = v.strip()
    
    auth = None
    auth_input = input("Basic Auth (username:password): ").strip()
    if auth_input and ":" in auth_input:
        u, p = auth_input.split(":", 1)
        auth = {"username": u, "password": p}
    
    proxy = input("Proxy URL (e.g., http://proxy:8080, or empty): ").strip()
    if not proxy:
        proxy = None
    
    keep_alive_input = input("Use keep-alive connection? (y/n): ").strip().lower()
    keep_alive = keep_alive_input == 'y'
    
    # HTTP/2 is disabled - we'll add a proper implementation later
    print("[*] HTTP/2 support will be added in a future version.")
    print("[*] Using HTTP/1.1 for this scan.")
    
    validation = None
    schema_input = input("Response validation schema (JSON file path, or empty): ").strip()
    if schema_input:
        try:
            with open(schema_input, 'r') as f:
                validation = json.load(f)
            print("[*] Schema loaded for validation.")
        except Exception as e:
            print(f"[!] Failed to load schema: {e}")
    
    result = analyze_url(url, method=method, headers=custom_headers, data=data, auth=auth, proxy=proxy, keep_alive=keep_alive, validation_schema=validation)
    
    if not result:
        print("[!] Investigation failed.")
        return
    
    print("\n" + "=" * 50)
    print("HTTP INVESTIGATOR SUMMARY")
    print("=" * 50)
    print(f"URL        : {url}")
    print(f"Final URL  : {result['redirects']['final_url']}")
    print(f"Redirects  : {result['redirects']['count']}")
    print(f"Status     : {result['head']['status_code']} {result['head']['status_message']}")
    print(f"Server     : {result['head']['headers'].get('server', 'Unknown')}")
    
    if result['timings']['total_ms']:
        print(f"Timing     : {result['timings']['total_ms']:.2f}ms total")
        if result['timings']['dns_ms']:
            print(f"   DNS: {result['timings']['dns_ms']:.2f}ms")
        if result['timings']['connect_ms']:
            print(f"   Connect: {result['timings']['connect_ms']:.2f}ms")
        if result['timings']['tls_ms']:
            print(f"   TLS: {result['timings']['tls_ms']:.2f}ms")
        if result['timings']['transfer_ms']:
            print(f"   Transfer: {result['timings']['transfer_ms']:.2f}ms")
    
    if "body" in result:
        print(f"Body Size  : {result['body']['body_size']} bytes")
        print(f"Cookies    : {len(result['cookies'])} found")
        
        sec = result['security']
        score = 0
        if sec['strict_transport_security'] != "Not Set":
            score += 1
        if sec['x_frame_options'] != "Not Set":
            score += 1
        if sec['x_content_type_options'] == "nosniff":
            score += 1
        rating = "Poor" if score < 2 else "Fair" if score < 3 else "Good"
        print(f"Security   : {rating} ({score}/3)")
        print(f"Validation : {'Valid' if result['validation']['valid'] else 'Invalid'} - {result['validation']['message']}")
    
    if result.get('certificate'):
        issuer_org = get_issuer_org(result['certificate'])
        print(f"SSL Cert   : {issuer_org}")
    
    print("=" * 50)
    save_report(result)
    print("\n[+] Investigation complete.")

if __name__ == "__main__":
    main()
