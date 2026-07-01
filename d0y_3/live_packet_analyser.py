#!/usr/bin/env python3

import subprocess
import json
import re
from datetime import datetime

def print_banner():
    banner = r"""
============================================================
             LIVE PACKET ANALYZER v1.0

               Day 3 Project

                Author : Mukesh S

============================================================
"""
    print(banner)

def capture_packets(count=10):
    try:
        cmd = ["tcpdump", "-c", str(count), "-n", "-vv", "-e"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return output
    except subprocess.CalledProcessError:
        return ""
    except FileNotFoundError:
        print("tcpdump not found. Please install it or run with sudo.")
        return ""

def parse_packets(raw_output):
    packets = []
    lines = raw_output.strip().splitlines()
    for line in lines:
        if not line or "captured" in line or "dropped" in line:
            continue
        packet = parse_single_packet(line)
        if packet:
            packets.append(packet)
    return packets

def parse_single_packet(line):
    # Basic parsing: try to extract IP, port, protocol
    packet = {}
    # Look for IP addresses
    ip_pattern = r'(\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+)'
    match = re.search(ip_pattern, line)
    if match:
        src_ip, src_port, dst_ip, dst_port = match.groups()
        packet["src_ip"] = src_ip
        packet["src_port"] = src_port
        packet["dst_ip"] = dst_ip
        packet["dst_port"] = dst_port
        # Determine protocol by port
        if dst_port == "53" or src_port == "53":
            packet["protocol"] = "DNS"
        elif dst_port == "443" or src_port == "443":
            packet["protocol"] = "HTTPS"
        elif dst_port == "80" or src_port == "80":
            packet["protocol"] = "HTTP"
        elif dst_port == "22" or src_port == "22":
            packet["protocol"] = "SSH"
        else:
            packet["protocol"] = "TCP" if "tcp" in line.lower() else "UDP" if "udp" in line.lower() else "Unknown"
        # Try to extract DNS query if any
        if packet["protocol"] == "DNS":
            dns_match = re.search(r'([a-zA-Z0-9.-]+)\?', line)
            if dns_match:
                packet["query"] = dns_match.group(1)
            else:
                packet["query"] = "Unknown"
        # Extract flags
        flags_match = re.search(r'\[([A-Z.]+)\]', line)
        if flags_match:
            packet["flags"] = flags_match.group(1)
        else:
            packet["flags"] = "N/A"
        return packet
    # Fallback: try to get some info anyway
    return None

def count_protocols(packets):
    counts = {"TCP": 0, "UDP": 0, "DNS": 0, "HTTPS": 0, "HTTP": 0, "SSH": 0, "Other": 0}
    for p in packets:
        proto = p.get("protocol", "Other")
        if proto in counts:
            counts[proto] += 1
        else:
            counts["Other"] += 1
    return counts

def save_json(data, filename="packet_capture.json"):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {filename}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

def save_report(data, filename="packet_capture.txt"):
    try:
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("        PACKET DETECTIVE REPORT\n")
            f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for idx, pkt in enumerate(data["packets"], 1):
                f.write(f"Packet {idx}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Protocol   : {pkt.get('protocol', 'Unknown')}\n")
                f.write(f"Source     : {pkt.get('src_ip', '?')}:{pkt.get('src_port', '?')}\n")
                f.write(f"Destination: {pkt.get('dst_ip', '?')}:{pkt.get('dst_port', '?')}\n")
                if "query" in pkt:
                    f.write(f"DNS Query  : {pkt['query']}\n")
                if "flags" in pkt:
                    f.write(f"Flags      : {pkt['flags']}\n")
                f.write("\n")
            f.write("PROTOCOL COUNTS\n")
            f.write("-" * 30 + "\n")
            for proto, count in data["counts"].items():
                if count > 0:
                    f.write(f"{proto:8} : {count}\n")
            f.write("\n" + "=" * 60 + "\n")
        print(f"Text report saved to {filename}")
    except Exception as e:
        print(f"Failed to save text report: {e}")

def main():
    print_banner()
    print("Live Packet Analyzer - Capturing 10 packets... (may need sudo)\n")
    raw = capture_packets(10)
    if not raw:
        print("No packets captured. Try running with sudo or install tcpdump.")
        return
    packets = parse_packets(raw)
    counts = count_protocols(packets)
    full_data = {
        "timestamp": datetime.now().isoformat(),
        "packets": packets,
        "counts": counts
    }
    print("=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Total packets captured : {len(packets)}")
    print("Protocol breakdown:")
    for proto, count in counts.items():
        if count > 0:
            print(f"  {proto:8} : {count}")
    print("=" * 60)
    print()
    save_json(full_data)
    save_report(full_data)
    print("\nScan complete.")

if __name__ == "__main__":
    main()
