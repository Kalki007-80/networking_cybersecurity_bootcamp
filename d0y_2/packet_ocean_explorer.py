#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime

def print_banner():
    banner = r"""
============================================================
           PACKET OCEAN EXPLORER v1.0
           Day 2 Project
           Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def get_connections():
    try:
        output = subprocess.check_output(["ss", "-tun"], text=True)
        return output
    except subprocess.CalledProcessError:
        return ""

def parse_connections(output):
    connections = []
    lines = output.strip().splitlines()
    if len(lines) < 2:
        return connections
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        protocol = parts[0]
        state = parts[1]
        local = parts[4]
        remote = parts[5]
        connections.append({
            "protocol": protocol,
            "state": state,
            "local": local,
            "remote": remote
        })
    return connections

def identify_service(port):
    common_ports = {
        "22": "SSH",
        "23": "Telnet",
        "25": "SMTP",
        "53": "DNS",
        "80": "HTTP",
        "110": "POP3",
        "143": "IMAP",
        "443": "HTTPS",
        "3306": "MySQL",
        "5432": "PostgreSQL",
        "6379": "Redis",
        "27017": "MongoDB"
    }
    return common_ports.get(str(port), "Unknown")

def count_protocols(connections):
    tcp = 0
    udp = 0
    for conn in connections:
        if conn["protocol"] == "tcp":
            tcp += 1
        elif conn["protocol"] == "udp":
            udp += 1
    return {"tcp": tcp, "udp": udp}

def save_json(data, filename="packet_connections.json"):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {filename}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

def save_report(data, filename="packet_connections.txt"):
    try:
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("     PACKET OCEAN EXPLORER REPORT\n")
            f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write("ACTIVE CONNECTIONS\n")
            f.write("-" * 60 + "\n")
            for idx, conn in enumerate(data["connections"], 1):
                local = conn["local"]
                remote = conn["remote"]
                protocol = conn["protocol"].upper()
                state = conn["state"]
                port = local.split(":")[-1] if ":" in local else ""
                service = identify_service(port) if port.isdigit() else "Unknown"
                f.write(f"{idx:2}. {protocol:3} {state:8} {local:25} -> {remote:25} [{service}]\n")
            f.write("\n")
            f.write("PROTOCOL COUNTS\n")
            f.write("-" * 60 + "\n")
            f.write(f"TCP : {data['counts']['tcp']}\n")
            f.write(f"UDP : {data['counts']['udp']}\n")
            f.write("\n" + "=" * 60 + "\n")
        print(f"Text report saved to {filename}")
    except Exception as e:
        print(f"Failed to save text report: {e}")

def main():
    print_banner()
    print("Packet Ocean Explorer - Scanning active network connections...\n")
    output = get_connections()
    connections = parse_connections(output)
    counts = count_protocols(connections)
    full_data = {
        "timestamp": datetime.now().isoformat(),
        "connections": connections,
        "counts": counts
    }
    print("=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Total TCP connections : {counts['tcp']}")
    print(f"Total UDP connections : {counts['udp']}")
    print(f"Total active sockets  : {len(connections)}")
    print("=" * 60)
    print()
    save_json(full_data)
    save_report(full_data)
    print("\nScan complete.")

if __name__ == "__main__":
    main()
