
#!/usr/bin/env python3

import subprocess
import socket
import re
import json
from datetime import datetime

def print_banner():
    banner = r"""
============================================================
        NETWORK PATH EXPLORER v1.0
        Day 5 Project
        Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def resolve_host(host):
    try:
        ip = socket.gethostbyname(host)
        return ip
    except socket.gaierror:
        return None

def ping_host(ip, count=4):
    try:
        output = subprocess.check_output(["ping", "-c", str(count), ip], 
                                         stderr=subprocess.DEVNULL, text=True)
        
        loss_match = re.search(r"(\d+)% packet loss", output)
        loss = loss_match.group(1) if loss_match else "100"

        
        rtt_match = re.search(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms", output)
        if rtt_match:
            min_rtt, avg_rtt, max_rtt, mdev = rtt_match.groups()
        else:
            min_rtt = avg_rtt = max_rtt = "N/A"

       
        sent_received = re.search(r"(\d+) packets transmitted, (\d+) received", output)
        if sent_received:
            sent, received = sent_received.groups()
        else:
            sent, received = count, 0

        return {
            "sent": int(sent),
            "received": int(received),
            "loss": float(loss),
            "min_rtt": float(min_rtt) if min_rtt != "N/A" else None,
            "avg_rtt": float(avg_rtt) if avg_rtt != "N/A" else None,
            "max_rtt": float(max_rtt) if max_rtt != "N/A" else None,
        }
    except subprocess.CalledProcessError:
        return {"sent": count, "received": 0, "loss": 100.0, "min_rtt": None, "avg_rtt": None, "max_rtt": None}

def trace_path(host, max_hops=30):
    try:
       
        cmd = ["tracepath", "-n", "-m", str(max_hops), host]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        hops = []
        for line in output.splitlines():
            # Example: " 1: 192.168.1.1                 2.345ms"
            match = re.search(r"^\s*(\d+):\s*([\d.]+)\s+([\d.]+)ms", line)
            if match:
                hop_num = int(match.group(1))
                hop_ip = match.group(2)
                rtt = float(match.group(3))
                hops.append({"hop": hop_num, "ip": hop_ip, "rtt_ms": rtt})

            if "reached" in line:
                break
        return hops
    except (subprocess.CalledProcessError, FileNotFoundError):

        try:
            cmd = ["traceroute", "-n", "-m", str(max_hops), host]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            hops = []
            for line in output.splitlines():

                match = re.search(r"^\s*(\d+)\s+([\d.]+)\s+([\d.]+) ms", line)
                if match:
                    hop_num = int(match.group(1))
                    hop_ip = match.group(2)
                    rtt = float(match.group(3))
                    hops.append({"hop": hop_num, "ip": hop_ip, "rtt_ms": rtt})
            return hops
        except:
            return []

def analyze_path(target):

    ip = resolve_host(target)
    if not ip:
        print(f"Could not resolve {target}")
        return None


    ping_result = ping_host(ip)


    route = trace_path(target)

    return {
        "target": target,
        "resolved_ip": ip,
        "ping": ping_result,
        "route": route,
        "hop_count": len(route),
        "timestamp": datetime.now().isoformat()
    }

def save_json(data, filename="path_report.json"):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {filename}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

def save_report(data, filename="path_report.txt"):
    try:
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("        NETWORK PATH EXPLORER REPORT\n")
            f.write(f"  Generated: {data['timestamp']}\n")
            f.write("=" * 60 + "\n\n")
            f.write("TARGET\n")
            f.write("-" * 40 + "\n")
            f.write(f"Host: {data['target']}\n")
            f.write(f"IP  : {data['resolved_ip']}\n\n")

            f.write("PING RESULTS\n")
            f.write("-" * 40 + "\n")
            ping = data['ping']
            f.write(f"Packets sent: {ping['sent']}\n")
            f.write(f"Packets received: {ping['received']}\n")
            f.write(f"Packet loss: {ping['loss']}%\n")
            f.write(f"Min RTT: {ping['min_rtt']} ms\n")
            f.write(f"Avg RTT: {ping['avg_rtt']} ms\n")
            f.write(f"Max RTT: {ping['max_rtt']} ms\n\n")

            f.write("TRACEROUTE\n")
            f.write("-" * 40 + "\n")
            for hop in data['route']:
                f.write(f"Hop {hop['hop']:2}: {hop['ip']:20} {hop['rtt_ms']:6.2f} ms\n")
            f.write(f"\nTotal hops: {data['hop_count']}\n")
            f.write("\n" + "=" * 60 + "\n")
        print(f"Text report saved to {filename}")
    except Exception as e:
        print(f"Failed to save text report: {e}")

def main():
    print_banner()
    target = input("Enter target (domain or IP): ").strip()
    if not target:
        print("No target entered.")
        return

    data = analyze_path(target)
    if not data:
        return


    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Target     : {data['target']} ({data['resolved_ip']})")
    print(f"Packets sent: {data['ping']['sent']}, received: {data['ping']['received']}, loss: {data['ping']['loss']}%")
    print(f"RTT (min/avg/max): {data['ping']['min_rtt']}/{data['ping']['avg_rtt']}/{data['ping']['max_rtt']} ms")
    print(f"Hops       : {data['hop_count']}")
    if data['route']:
        print("First hop :", data['route'][0]['ip'])
        print("Last hop  :", data['route'][-1]['ip'])
    print("=" * 60 + "\n")

    # Save reports
    save_json(data)
    save_report(data)
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()
