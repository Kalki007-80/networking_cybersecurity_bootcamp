# Day 1 notes
### What is Networking?

**Networking** is the practice of connecting two or more computing devices (computers, servers, mobile devices, printers, IoT gadgets) together to share resources, exchange data, and communicate with each other. It involves both the **physical hardware** (cables, routers, switches) and **software/protocols** (rules that govern how data is sent and received, like TCP/IP). The ultimate goal is to enable seamless and secure communication, whether across a room or across the globe.

---

### Types of Networks

| Type | Full Form | Scope | Example |
| :--- | :--- | :--- | :--- |
| **PAN** | Personal Area Network | Very short range (within a few meters) | Bluetooth connection between a phone and a smartwatch, or a USB connection. |
| **LAN** | Local Area Network | Confined to a small geographic area (building, office, home) | Wi-Fi in your home, or the wired network in an office floor. |
| **MAN** | Metropolitan Area Network | Covers a city or a large campus | Cable TV networks, or a city-wide Wi-Fi project. |
| **WAN** | Wide Area Network | Covers a large geographic area (country, continent, globe) | The **Internet** itself is the largest WAN, connecting all LANs worldwide. |

---

### Network Devices

| Device | Function |
| :--- | :--- |
| **Hub** | A basic, "dumb" device that connects multiple devices. It broadcasts incoming data to **all** other ports, creating unnecessary traffic. Rarely used today. |
| **Switch** | A smarter device than a hub. It learns the **MAC addresses** of connected devices and forwards data **only** to the specific port of the intended recipient. Used within a LAN. |
| **Router** | Connects **different networks** (e.g., your home LAN to the Internet). It uses **IP addresses** to determine the best path for data to travel and routes packets between networks. |
| **Modem** | **Mo**dulates and **Dem**odulates signals. It converts digital data from your computer into analog signals for transmission over phone/cable lines, and vice versa. It connects your home network to your ISP. |
| **Access Point** | A device that allows wireless devices (Wi-Fi) to connect to a wired network (LAN). It acts as a bridge between the wired and wireless parts of the network. |

---

### Addressing

| Address Type | Description |
| :--- | :--- |
| **MAC Address** | **Media Access Control** address. A unique, permanent, 48-bit hardware identifier burned into the **Network Interface Card (NIC)** of a device (e.g., `00:1A:2B:3C:4D:5E`). Used for communication **within** a local network (Layer 2). |
| **IP Address** | **Internet Protocol** address. A logical, 32-bit (IPv4) or 128-bit (IPv6) identifier assigned to a device. It can change based on location. Used for communication **between** networks (Layer 3). Example: `192.168.1.10`. |
| **Private IP** | An IP address used **only within a private network** (home, office). They are not routable on the public internet. Ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. |
| **Public IP** | A globally unique IP address assigned by your ISP. It is routable on the internet, allowing your device to communicate with servers worldwide. |

---

### Services

| Service | Full Form & Function |
| :--- | :--- |
| **DNS** | **Domain Name System**. Acts like the internet's phonebook. It translates human-friendly domain names (e.g., `google.com`) into machine-readable IP addresses (e.g., `142.250.190.46`). |
| **DHCP** | **Dynamic Host Configuration Protocol**. Automatically assigns dynamic IP addresses, subnet masks, default gateways, and DNS server information to devices on a network so they can communicate without manual configuration. |
| **Gateway** | A **node** (usually a router) that acts as an entry/exit point to another network. For a device on a LAN, the default gateway is the router that forwards traffic to the internet or other external networks. |

---

### Commands Learned (Explained)

| Command | What it does |
| :--- | :--- |
| `ip addr` | Shows all network interfaces on your system, along with their assigned IP addresses (both IPv4 and IPv6), MAC addresses, and state (UP/DOWN). |
| `ip route` | Displays the system's routing table. It shows which gateway (router) to use to reach specific networks, including the **default gateway**. |
| `hostname` | Prints the current system's hostname (the name assigned to the machine on the network). |
| `hostname -I` | Displays **all** IP addresses assigned to the machine, in a clean, space-separated list (without extra interface details). |
| `ping` | Sends ICMP echo request packets to a target IP or domain to test **network connectivity** and measure round-trip time (latency). (e.g., `ping 8.8.8.8`). |
| `cat /etc/resolv.conf` | Displays the contents of the DNS resolver configuration file. This file lists the IP addresses of the DNS servers your system uses to resolve domain names. |
| `ip link` | Shows information about the **data link layer (Layer 2)** – namely, all network interfaces and their MAC addresses, and whether they are up or down. |

---

### Key Takeaways (Sample summary to write)

> *"Day 1 gave me a solid foundation. I learned that networking is fundamentally about moving data using hardware and rules. The key distinction I grasped is the difference between a **MAC address** (physical, fixed, local) and an **IP address** (logical, changeable, global). I also understood the layered purpose of devices: switches work inside a LAN using MACs, while routers connect networks using IPs. The practical commands (`ip addr`, `ping`, `ip route`) were invaluable for actually seeing these concepts in action on my own Linux system. DNS and DHCP are the invisible assistants that make the internet usable without memorizing numbers."*

---

### Doubts (Questions to research later)

1.  **What is the exact difference between a Switch and a Router in terms of the OSI model layers they operate on?** (Switch = Layer 2, Router = Layer 3 – but what does that practically mean for data handling?)
2.  **What is Subnetting and CIDR notation (e.g., /24)?** How does the subnet mask determine which part of an IP is the network and which is the host?
3.  **What are the complete steps of the DHCP handshake?** (DORA – Discover, Offer, Request, Acknowledge – how does it work step-by-step?)

---

### Interview Questions (with Answers)

**1. What is the difference between a Hub, a Switch, and a Router?**
> * **Hub:** Operates at Layer 1 (Physical). It floods data to all ports. It is outdated and inefficient.
> * **Switch:** Operates at Layer 2 (Data Link). It reads MAC addresses and forwards data intelligently only to the intended recipient port within the same LAN. It is efficient and secure.
> * **Router:** Operates at Layer 3 (Network). It reads IP addresses and forwards data packets between different networks (e.g., LAN to WAN). It makes routing decisions based on the destination IP and routing tables.

**2. Can you explain the difference between a Public IP and a Private IP, and how they work together?**
> * **Private IPs** are used within a local network (e.g., `192.168.x.x`) and are not routable on the internet. Multiple devices across different private networks can use the same private IP.
> * **Public IPs** are globally unique and routable on the internet. They are assigned by the ISP.
> * They work together via **NAT (Network Address Translation)** – a feature on the router that translates the private IP of an internal device into the router's public IP when traffic goes out to the internet, and translates it back when the response returns. This allows many devices to share one public IP.

**3. How does DNS work when you type `www.example.com` in a browser?**
> 1.  The browser checks its local cache.
> 2.  If not found, the OS checks its local hosts file (`/etc/hosts`) and DNS cache.
> 3.  The request is sent to the **Recursive Resolver** (often provided by ISP or public DNS like 8.8.8.8).
> 4.  The Resolver queries the **Root DNS server** to find the TLD (Top-Level Domain) server for `.com`.
> 5.  The Resolver queries the **TLD DNS server** to find the authoritative name server for `example.com`.
> 6.  The Resolver queries the **Authoritative Name Server** to get the actual IPv4/IPv6 address for `www.example.com`.
> 7.  The IP address is returned to the browser, which can then initiate a connection to the web server.
