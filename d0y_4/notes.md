# Day 4 Notes – IP Intelligence Toolkit

## What is an IP Address?

An **IP Address** (Internet Protocol address) is a unique numerical label assigned to each device connected to a computer network. It serves two main functions:

- **Host or network interface identification**
- **Location addressing**

Think of it like a postal address for your computer on the internet.

---

## IPv4 vs IPv6

| Feature | IPv4 | IPv6 |
|---------|------|------|
| Size | 32-bit (4 bytes) | 128-bit (16 bytes) |
| Format | Dotted decimal (192.168.1.1) | Hexadecimal (2001:0db8:85a3::8a2e:0370:7334) |
| Address Count | ~4.3 billion | 340 undecillion |
| Header | 20-60 bytes | 40 bytes fixed |
| Security | Optional (IPSec) | Built-in (IPSec required) |
| NAT | Commonly used | Not needed |

---

## CIDR Notation

**CIDR** (Classless Inter-Domain Routing) is a method for allocating IP addresses and routing IP packets.

### Format:
IP_ADDRESS/PREFIX_LENGTH

text

### Examples:
- `/24` → 256 addresses (Class C equivalent)
- `/16` → 65,536 addresses (Class B equivalent)
- `/8` → 16,777,216 addresses (Class A equivalent)
- `/27` → 32 addresses
- `/30` → 4 addresses (commonly used for point-to-point links)

### Why CIDR?
Before CIDR, IP addresses were allocated using classes (A, B, C). This was wasteful. CIDR allows more flexible allocation.

---

## Subnet Mask

A **subnet mask** is a 32-bit number that masks an IP address and divides it into network and host portions.

### Common Subnet Masks:

| CIDR | Subnet Mask | Total IPs | Usable IPs |
|------|-------------|-----------|------------|
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |

---

## Network Address

The **Network Address** (also called the network ID) is the first address in a subnet. It identifies the subnet itself and cannot be assigned to a host.

### Example:
192.168.10.0/24
Network Address: 192.168.10.0

text

---

## Broadcast Address

The **Broadcast Address** is the last address in a subnet. It's used to send data to all hosts on that subnet.

### Example:
192.168.10.0/24
Broadcast Address: 192.168.10.255

text

---

## Usable Hosts

The **usable hosts** are all addresses between the network address and the broadcast address.

### Formula:
Usable Hosts = 2^(32 - prefix_length) - 2

text

The `-2` removes the network and broadcast addresses.

### Special cases:
- `/31` has 2 addresses – both are usable in point‑to‑point links (no broadcast).
- `/32` has 1 address – only the host itself, no network or broadcast.

---

## Private vs Public IP Addresses

### Private IP Ranges (RFC 1918):

| Class | Range | CIDR |
|-------|-------|------|
| A | 10.0.0.0 - 10.255.255.255 | 10.0.0.0/8 |
| B | 172.16.0.0 - 172.31.255.255 | 172.16.0.0/12 |
| C | 192.168.0.0 - 192.168.255.255 | 192.168.0.0/16 |

### Public IP Ranges:
Everything else. Public IPs are globally unique and routable on the internet.

### Special Addresses:

| Address | Purpose |
|---------|---------|
| 127.0.0.1 | Localhost (your own machine) |
| 0.0.0.0 | Default route / unspecified address |
| 255.255.255.255 | Limited broadcast |
| 169.254.0.0/16 | Link-local (APIPA) |

---

## IP Address Classes (Historical)

| Class | First Octet Range | Default Mask | Purpose |
|-------|-------------------|--------------|---------|
| A | 0–127 | /8 | Large networks |
| B | 128–191 | /16 | Medium networks |
| C | 192–223 | /24 | Small networks |
| D | 224–239 | N/A | Multicast |
| E | 240–255 | N/A | Experimental |

> **Note**: Classes are mostly obsolete due to CIDR, but they are still useful for understanding legacy networks.

---

## Binary Representation

IP addresses and subnet masks are binary numbers. Converting them to binary is fundamental to understanding subnetting.

### Example:
IP Address : 192.168.10.35
Binary : 11000000.10101000.00001010.00100011

Subnet Mask : 255.255.255.224
Binary : 11111111.11111111.11111111.11100000

text

The **network bits** are the positions where the mask has `1`s; the **host bits** are where it has `0`s.

---

## Python's `ipaddress` Module

Python's `ipaddress` module provides classes for working with IP addresses and networks.

### Key Classes:
- `ipaddress.ip_address()` – Creates an IPv4Address or IPv6Address object.
- `ipaddress.ip_network()` – Creates an IPv4Network or IPv6Network object.
- `ipaddress.ip_interface()` – Creates an IPv4Interface or IPv6Interface object.

### Key Properties and Methods:
- `.is_private` – Returns `True` if the IP is private.
- `.is_global` – Returns `True` if globally routable.
- `.is_loopback` – Returns `True` if it's 127.0.0.1.
- `.is_link_local` – Returns `True` if it's in 169.254.0.0/16.
- `.is_multicast` – Returns `True` for multicast addresses.
- `.network_address` – Returns the network address.
- `.broadcast_address` – Returns the broadcast address.
- `.hosts()` – Returns an iterator over usable hosts (safe to use without converting to list).
- `.num_addresses` – Returns the total number of addresses in the network.

### Using `strict=False`
When creating a network from a host IP (e.g., `192.168.1.10/24`), Python will automatically adjust the network address to `192.168.1.0/24` if `strict=False`. This is useful for analyzing host IPs.

---

## How the Script Works

1. **Detect private IP** – Uses `ip -4 addr` and regex to extract the first non‑loopback IP and its prefix.
2. **Detect public IP** – Queries external services (`api.ipify.org`, `ifconfig.me`, `icanhazip.com`) using either `requests` or `urllib`.
3. **User choice** – Choose to analyze private, public, or both IPs (or enter a custom IP).
4. **Validation** – The IP is validated using `ipaddress.ip_address()`.
5. **Network creation** – `ipaddress.ip_network()` creates a network object.
6. **Information extraction**:
   - Network and broadcast addresses.
   - First and last usable hosts (without creating large lists).
   - Total and usable hosts (with safe handling for `/31` and `/32`).
   - Classification (private, global, loopback, link‑local, multicast).
   - IP class (A, B, C, D, E).
   - Binary representation of IP and subnet mask.
   - Plain‑English summary.
7. **Reporting** – Data is saved as JSON and TXT reports.

---

## Commands Learned Today

```bash
python3 ip_intelligence_live.py
ip -4 addr show
