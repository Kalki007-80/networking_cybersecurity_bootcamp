
#!/usr/bin/env python3

import ipaddress
import subprocess
import json
import socket
import platform
import time
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

COMMON_PORTS = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    27017: "MongoDB"
}

def print_banner():
    banner = r"""
============================================================
        NETWORK RECON SCANNER v4.0
        Day 6 Project
        Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def get_ping_args():
    """Return OS‑specific ping command and arguments."""
    system = platform.system().lower()
    if system == "windows":
        return ["ping", "-n", "1", "-w", "1000"]  
    else:
        return ["ping", "-c", "1", "-W", "1"]    

def ping_host(ip):
    """Ping a host and return (alive, rtt_ms)."""
    cmd = get_ping_args() + [ip]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)

        match = re.search(r"time[<=]([\d.]+)\s*ms", output, re.IGNORECASE)
        rtt = float(match.group(1)) if match else None
        return True, rtt
    except subprocess.CalledProcessError:
        return False, None
    except Exception:
        return False, None

def scan_ports(ip, ports, timeout=1.5):
    """TCP connect scan on a list of ports."""
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
        except socket.error:
            pass
        except Exception:
            pass
    return open_ports

def scan_host(ip, scan_ports_flag=False, ports_to_scan=None):
    """Scan a single host: ping, optionally ports."""
    alive, rtt = ping_host(ip)
    result = {
        "ip": str(ip),
        "alive": alive,
        "rtt_ms": rtt,
        "open_ports": []
    }
    if alive and scan_ports_flag and ports_to_scan:
        result["open_ports"] = scan_ports(str(ip), ports_to_scan)
    return result

def scan_network(subnet, workers=50, scan_ports=False, ports_to_scan=None):
    """Scan all hosts in a subnet concurrently."""
    network = ipaddress.ip_network(subnet, strict=False)
    total_hosts = network.num_addresses - 2  
    results = []
    completed = 0
    start_time = time.time()


    with ThreadPoolExecutor(max_workers=workers) as executor:

        future_to_ip = {}
        for ip in network.hosts():
            future = executor.submit(scan_host, ip, scan_ports, ports_to_scan)
            future_to_ip[future] = str(ip)


        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            completed += 1
            try:
                res = future.result()
                results.append(res)
            except Exception as e:

                print(f"Error scanning {ip}: {e}")
                results.append({"ip": ip, "alive": False, "rtt_ms": None, "open_ports": []})


            percent = (completed / total_hosts) * 100
            status = "ALIVE" if res.get("alive", False) else "OFFLINE"
            print(f"[{completed:3}/{total_hosts}] {percent:5.1f}% {ip:16} {status}")

    scan_duration = time.time() - start_time
    return results, scan_duration

def main():
    print_banner()


    subnet_input = input("Enter subnet (e.g., 192.168.1.0/24): ").strip()
    try:
        network = ipaddress.ip_network(subnet_input, strict=False)
    except ValueError as e:
        print(f"Invalid subnet: {e}")
        return


    workers_input = input("Workers (default 50): ").strip()
    workers = int(workers_input) if workers_input.isdigit() else 50


    port_scan_input = input("Scan common ports on live hosts? (y/n): ").strip().lower()
    scan_ports_flag = port_scan_input == 'y'
    ports_to_scan = list(COMMON_PORTS.keys()) if scan_ports_flag else []

    print(f"\nScanning {network.num_addresses - 2} hosts with {workers} workers...")
    print("Press Ctrl+C to cancel.\n")

    results = []
    scan_duration = 0
    try:
        results, scan_duration = scan_network(subnet_input, workers, scan_ports_flag, ports_to_scan)
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user. Saving partial results...")


    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Saving partial results...")
    finally:

        if results:

            alive_hosts = [r for r in results if r.get("alive", False)]
            offline_hosts = [r for r in results if not r.get("alive", False)]


            alive_hosts.sort(key=lambda h: ipaddress.ip_address(h["ip"]))
            offline_hosts.sort(key=lambda h: ipaddress.ip_address(h["ip"]))

            total_hosts = len(results)

            data = {
                "subnet": subnet_input,
                "scan_time": datetime.now().isoformat(),
                "total_hosts": total_hosts,
                "alive_count": len(alive_hosts),
                "offline_count": len(offline_hosts),
                "duration_seconds": round(scan_duration, 2),
                "alive_hosts": alive_hosts,
                "offline_hosts": [h["ip"] for h in offline_hosts],
                "port_scan_enabled": scan_ports_flag,
                "ports_scanned": ports_to_scan,
                "service_map": COMMON_PORTS,
                "workers": workers
            }


            print("\n" + "=" * 60)
            print("SCAN COMPLETE")
            print("=" * 60)
            print(f"Subnet            : {data['subnet']}")
            print(f"Total hosts       : {data['total_hosts']}")
            print(f"Alive hosts       : {data['alive_count']}")
            print(f"Offline hosts     : {data['offline_count']}")
            print(f"Scan duration     : {data['duration_seconds']} seconds")
            if alive_hosts:
                print("Live hosts:")
                for h in alive_hosts[:5]:
                    ports_str = ", ".join([f"{p}({COMMON_PORTS.get(p, 'Unknown')})" for p in h.get("open_ports", [])])
                    if ports_str:
                        print(f"  - {h['ip']}    RTT: {h['rtt_ms']} ms  Ports: {ports_str}")
                    else:
                        print(f"  - {h['ip']}    RTT: {h['rtt_ms']} ms")
                if len(alive_hosts) > 5:
                    print(f"  ... and {len(alive_hosts)-5} more")
            print("=" * 60)


            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = f"scan_report_{ts}.json"
            txt_file = f"scan_report_{ts}.txt"

            try:
                with open(json_file, "w") as f:
                    json.dump(data, f, indent=4)
                print(f"JSON report saved to {json_file}")
            except Exception as e:
                print(f"Failed to save JSON: {e}")


            try:
                with open(txt_file, "w") as f:
                    f.write("=" * 60 + "\n")
                    f.write("        NETWORK RECON SCANNER REPORT\n")
                    f.write(f"  Generated: {data['scan_time']}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"SUBNET: {data['subnet']}\n")
                    f.write(f"TOTAL HOSTS: {data['total_hosts']}\n")
                    f.write(f"ALIVE: {data['alive_count']}\n")
                    f.write(f"OFFLINE: {data['offline_count']}\n")
                    f.write(f"DURATION: {data['duration_seconds']} seconds\n")
                    f.write(f"WORKERS: {data['workers']}\n\n")

                    f.write("LIVE HOSTS\n")
                    f.write("=" * 60 + "\n")
                    for h in alive_hosts:
                        f.write(f"{h['ip']}\n")
                        f.write(f"  RTT: {h['rtt_ms']} ms\n")
                        if h.get("open_ports"):
                            f.write("  Ports Open:\n")
                            for p in h["open_ports"]:
                                service = COMMON_PORTS.get(p, "Unknown")
                                f.write(f"    - {p:5} {service}\n")
                        else:
                            f.write("  Ports Open: None\n")
                        f.write("\n")

                    f.write("OFFLINE HOSTS (first 10 shown)\n")
                    f.write("=" * 60 + "\n")
                    for ip in data["offline_hosts"][:10]:
                        f.write(f"{ip}\n")
                    if len(data["offline_hosts"]) > 10:
                        f.write(f"... and {len(data['offline_hosts'])-10} more\n")
                    f.write("\n" + "=" * 60 + "\n")
                print(f"Text report saved to {txt_file}")
            except Exception as e:
                print(f"Failed to save text report: {e}")
        else:
            print("No results to save.")

    print("\nScan complete.")

if __name__ == "__main__":
    main()
