#!/usr/bin/env python3

import socket
import platform
import subprocess
import json
import re
from datetime import datetime


def print_banner():
    banner = r"""
============================================================
             NETWORK INSPECTOR v1.0
             Day 1 Project
             Author : Team Crypt0n1c
============================================================
"""
    print(banner)


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }


def get_network_info():
    try:
        output = subprocess.check_output(["ip", "-br", "addr"], text=True)
        lines = output.strip().splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) < 3:
                continue
            iface, state, addr_info = parts[0], parts[1], " ".join(parts[2:])
            if iface == "lo" or state != "UP":
                continue
            ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)/\d+", addr_info)
            if ip_match:
                ip = ip_match.group(1)
                mac = get_mac_for_interface(iface)
                return {
                    "interface": iface,
                    "ip": ip,
                    "mac": mac if mac else "N/A"
                }
    except subprocess.CalledProcessError:
        pass
    try:
        output = subprocess.check_output(["ip", "addr"], text=True)
        for line in output.splitlines():
            if "inet " in line and "lo" not in line:
                ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                if ip:
                    return {"interface": "unknown", "ip": ip.group(1), "mac": "N/A"}
    except:
        pass
    return {"interface": "unknown", "ip": "N/A", "mac": "N/A"}


def get_mac_for_interface(iface):
    try:
        output = subprocess.check_output(["ip", "link", "show", iface], text=True)
        mac_match = re.search(r"ether ([0-9a-fA-F:]{17})", output)
        if mac_match:
            return mac_match.group(1)
    except:
        pass
    return None


def get_gateway():
    try:
        output = subprocess.check_output(["ip", "route"], text=True)
        for line in output.splitlines():
            if line.startswith("default via"):
                parts = line.split()
                if len(parts) >= 3:
                    return parts[2]
    except:
        pass
    return "N/A"


def get_dns():
    dns_servers = []
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    parts = line.split()
                    if len(parts) >= 2:
                        dns_servers.append(parts[1])
    except FileNotFoundError:
        pass
    return dns_servers if dns_servers else ["N/A"]


def check_internet():
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                                stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def save_json(data, filename="report.json"):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {filename}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")


def save_report(data, filename="report.txt"):
    try:
        with open(filename, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("  NETWORK INSPECTOR REPORT\n")
            f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write("SYSTEM INFORMATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Hostname    : {data['system']['hostname']}\n")
            f.write(f"OS          : {data['system']['os']}\n")
            f.write(f"Release     : {data['system']['release']}\n")
            f.write(f"Architecture: {data['system']['machine']}\n")
            f.write(f"Processor   : {data['system']['processor']}\n\n")
            f.write("NETWORK INFORMATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Interface   : {data['network']['interface']}\n")
            f.write(f"IP Address  : {data['network']['ip']}\n")
            f.write(f"MAC Address : {data['network']['mac']}\n")
            f.write(f"Gateway     : {data['gateway']}\n\n")
            f.write("DNS SERVERS\n")
            f.write("-" * 30 + "\n")
            for dns in data['dns']:
                f.write(f"  {dns}\n")
            f.write("\n")
            f.write("INTERNET CONNECTIVITY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Status      : {'Connected' if data['internet'] else 'Disconnected'}\n")
            f.write("\n" + "=" * 50 + "\n")
        print(f"Text report saved to {filename}")
    except Exception as e:
        print(f"Failed to save text report: {e}")


def main():
    print_banner()
    print("Network Inspector - Starting scan...\n")
    system_info = get_system_info()
    network_info = get_network_info()
    gateway = get_gateway()
    dns_servers = get_dns()
    internet_status = check_internet()
    full_data = {
        "system": system_info,
        "network": network_info,
        "gateway": gateway,
        "dns": dns_servers,
        "internet": internet_status,
        "timestamp": datetime.now().isoformat()
    }

    # Enhanced summary block (your new design)
    print("=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Hostname      : {system_info['hostname']}")
    print(f"Operating Sys : {system_info['os']} {system_info['release']}")
    print(f"Interface     : {network_info['interface']}")
    print(f"IP Address    : {network_info['ip']}")
    print(f"MAC Address   : {network_info['mac']}")
    print(f"Gateway       : {gateway}")
    print(f"DNS Server(s) : {', '.join(dns_servers)}")
    print(f"Internet      : {'Connected ✓' if internet_status else 'Disconnected ✗'}")
    print("=" * 60)
    print()

    save_json(full_data)
    save_report(full_data)
    print("\nScan complete.")


if __name__ == "__main__":
    main()
