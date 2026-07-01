#!/usr/bin/env python3

import ipaddress
import json
import subprocess
import re
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

TIMEOUT = 5
DEFAULT_PUBLIC_PREFIX = 32

def print_banner():
    banner = r"""
============================================================
        IP INTELLIGENCE TOOLKIT – ENHANCED
        Day 4 Project
        Author : Team Crypt0n1c
============================================================
"""
    print(banner)

def separator(length=50):
    print("=" * length)

def get_private_ip_and_netmask():
    try:
        output = subprocess.check_output(["ip", "-4", "addr", "show"], text=True)
        for line in output.splitlines():
            if "inet " in line and "lo" not in line:
                match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", line)
                if match:
                    ip = match.group(1)
                    prefix = int(match.group(2))
                    return ip, prefix
    except Exception:
        pass
    return None, None

def get_public_ip():
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]
    for url in services:
        try:
            if HAS_REQUESTS:
                response = requests.get(url, timeout=TIMEOUT)
                if response.status_code == 200:
                    ip = response.text.strip()
                    try:
                        ipaddress.ip_address(ip)
                        return ip
                    except ValueError:
                        continue
            else:
                with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
                    ip = response.read().decode().strip()
                    try:
                        ipaddress.ip_address(ip)
                        return ip
                    except ValueError:
                        continue
        except Exception:
            continue
    return None

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def ip_to_binary(ip_str):
    parts = ip_str.split('.')
    binary_parts = [format(int(p), '08b') for p in parts]
    return '.'.join(binary_parts)

def get_ip_class(ip_str):
    first_octet = int(ip_str.split('.')[0])
    if 0 <= first_octet <= 127:
        return "A"
    elif 128 <= first_octet <= 191:
        return "B"
    elif 192 <= first_octet <= 223:
        return "C"
    elif 224 <= first_octet <= 239:
        return "D (Multicast)"
    elif 240 <= first_octet <= 255:
        return "E (Experimental)"
    return "Unknown"

def analyze_ip(ip, cidr):
    ip_with_cidr = f"{ip}/{cidr}"
    network = ipaddress.ip_network(ip_with_cidr, strict=False)

    # Safe usable hosts calculation
    total = network.num_addresses
    if total <= 2:
        usable = max(0, total)
    else:
        usable = total - 2

    # Get first and last host without creating large lists
    if usable > 0:
        first_host = network.network_address + 1
        last_host = network.broadcast_address - 1
    else:
        first_host = "N/A"
        last_host = "N/A"

    details = {
        "ip_address": ip,
        "cidr": cidr,
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "first_host": str(first_host),
        "last_host": str(last_host),
        "total_hosts": total,
        "usable_hosts": usable,
        "is_private": network.is_private,
        "is_global": network.is_global,
        "is_loopback": network.is_loopback,
        "is_link_local": network.is_link_local,
        "is_multicast": network.is_multicast,
        "subnet_mask": str(network.netmask),
        "prefix_length": network.prefixlen,
        "ip_binary": ip_to_binary(ip),
        "mask_binary": ip_to_binary(str(network.netmask)),
        "ip_class": get_ip_class(ip),
    }

    # Generate plain‑English summary
    summary_parts = [
        f"IP Address      : {ip}",
        f"Network         : {details['network_address']}/{cidr}",
        f"Broadcast       : {details['broadcast_address']}",
        f"Host Range      : {first_host} - {last_host}" if usable > 0 else "Host Range      : N/A",
        f"Total Addresses : {total}",
        f"Usable Hosts    : {usable}",
        f"Type            : {'Private' if network.is_private else 'Public'} Class {details['ip_class']} Network",
    ]
    details["summary"] = "\n".join(summary_parts)

    details["timestamp"] = datetime.now().isoformat()
    return details

def save_json(data, filename="ip_report.json"):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"JSON report saved to {filename}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

def save_report(data, filename="ip_report.txt"):
    try:
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("        IP INTELLIGENCE REPORT\n")
            f.write(f"  Generated: {data['timestamp']}\n")
            f.write("=" * 60 + "\n\n")
            f.write("IP ADDRESS INFORMATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"IP Address      : {data['ip_address']}\n")
            f.write(f"CIDR Prefix     : {data['cidr']}\n")
            f.write(f"Subnet Mask     : {data['subnet_mask']}\n")
            f.write(f"Prefix Length   : {data['prefix_length']}\n")
            f.write(f"IP Class        : {data['ip_class']}\n\n")
            f.write("BINARY REPRESENTATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"IP Address      : {data['ip_binary']}\n")
            f.write(f"Subnet Mask     : {data['mask_binary']}\n\n")
            f.write("NETWORK DETAILS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Network Address : {data['network_address']}\n")
            f.write(f"Broadcast       : {data['broadcast_address']}\n")
            f.write(f"First Host      : {data['first_host']}\n")
            f.write(f"Last Host       : {data['last_host']}\n")
            f.write(f"Total Addresses : {data['total_hosts']}\n")
            f.write(f"Usable Hosts    : {data['usable_hosts']}\n\n")
            f.write("CLASSIFICATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"Private     : {'Yes' if data['is_private'] else 'No'}\n")
            f.write(f"Global      : {'Yes' if data['is_global'] else 'No'}\n")
            f.write(f"Loopback    : {'Yes' if data['is_loopback'] else 'No'}\n")
            f.write(f"Link-local  : {'Yes' if data['is_link_local'] else 'No'}\n")
            f.write(f"Multicast   : {'Yes' if data['is_multicast'] else 'No'}\n\n")
            f.write("NETWORK SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(data['summary'] + "\n")
            f.write("\n" + "=" * 60 + "\n")
        print(f"Text report saved to {filename}")
    except Exception as e:
        print(f"Failed to save text report: {e}")

def main():
    print_banner()
    print("Detecting your live IP addresses...\n")

    priv_ip, priv_prefix = get_private_ip_and_netmask()
    if priv_ip:
        print(f"Private IP detected: {priv_ip}/{priv_prefix}")
    else:
        print("Could not detect private IP. You can still enter one manually.")

    pub_ip = get_public_ip()
    if pub_ip:
        print(f"Public IP detected : {pub_ip}")
        print("(Public IP analysis requires a CIDR – we'll use /32 by default)")
        pub_prefix = DEFAULT_PUBLIC_PREFIX
    else:
        print("Could not fetch public IP (no internet or service down).")
        pub_ip = None
        pub_prefix = None

    print("\nWhat would you like to analyze?")
    print("1. Private IP")
    if pub_ip:
        print("2. Public IP")
        print("3. Both")
    else:
        print("2. Enter a custom IP")
    choice = input("Enter choice (1/2/3): ").strip()

    targets = []
    if choice == "1":
        if priv_ip:
            cidr_input = input(f"Enter CIDR for {priv_ip} (default {priv_prefix}): ").strip()
            if cidr_input:
                try:
                    priv_prefix = int(cidr_input)
                except ValueError:
                    print("Invalid CIDR, using default.")
            targets.append((priv_ip, priv_prefix, "Private"))
        else:
            print("No private IP available. Please enter IP manually.")
            ip = input("Enter IP: ").strip()
            if not validate_ip(ip):
                print("Invalid IP.")
                return
            cidr = int(input("Enter CIDR: ").strip())
            targets.append((ip, cidr, "Custom"))
    elif choice == "2":
        if pub_ip:
            cidr_input = input(f"Enter CIDR for {pub_ip} (default {pub_prefix}): ").strip()
            if cidr_input:
                try:
                    pub_prefix = int(cidr_input)
                except ValueError:
                    print("Invalid CIDR, using default.")
            targets.append((pub_ip, pub_prefix, "Public"))
        else:
            ip = input("Enter IP to analyze: ").strip()
            if not validate_ip(ip):
                print("Invalid IP.")
                return
            cidr = int(input("Enter CIDR: ").strip())
            targets.append((ip, cidr, "Custom"))
    elif choice == "3":
        if priv_ip and pub_ip:
            cidr_priv = input(f"Enter CIDR for Private IP (default {priv_prefix}): ").strip()
            if cidr_priv:
                try:
                    priv_prefix = int(cidr_priv)
                except ValueError:
                    print("Invalid, using default.")
            cidr_pub = input(f"Enter CIDR for Public IP (default 32): ").strip()
            if cidr_pub:
                try:
                    pub_prefix = int(cidr_pub)
                except ValueError:
                    print("Invalid, using default.")
            targets.append((priv_ip, priv_prefix, "Private"))
            targets.append((pub_ip, pub_prefix, "Public"))
        else:
            print("Both IPs not available. Falling back to manual.")
            ip = input("Enter IP: ").strip()
            if not validate_ip(ip):
                print("Invalid IP.")
                return
            cidr = int(input("Enter CIDR: ").strip())
            targets.append((ip, cidr, "Custom"))

    if not targets:
        print("No targets to analyze.")
        return

    for idx, (ip, cidr, label) in enumerate(targets):
        print(f"\nAnalyzing {label} IP: {ip}/{cidr}")
        details = analyze_ip(ip, cidr)

        separator(50)
        print(f"{label.upper()} IP SUMMARY")
        separator(50)
        print(f"Network     : {details['network_address']}/{cidr}")
        print(f"Broadcast   : {details['broadcast_address']}")
        print(f"Usable Hosts: {details['usable_hosts']}")
        print(f"Private     : {'Yes' if details['is_private'] else 'No'}")
        print(f"Class       : {details['ip_class']}")
        separator(50)

        json_fname = f"ip_report_{label.lower()}.json" if len(targets) > 1 else "ip_report.json"
        txt_fname = f"ip_report_{label.lower()}.txt" if len(targets) > 1 else "ip_report.txt"
        save_json(details, json_fname)
        save_report(details, txt_fname)

    print("\nAll scans complete.")

if __name__ == "__main__":
    main()
