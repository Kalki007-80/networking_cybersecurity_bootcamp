# Day 3 – Core Protocols & Concepts

Study of the protocols that make routing, name resolution, and basic diagnostics possible on a network.

---

##  Objective

To understand the protocols operating "underneath" everyday tools like `ping` and browsers — how a hostname becomes an IP, how a packet finds its way across networks, and how devices on the same network find each other.

---

##  Topics Covered

- **DNS Resolution** – how domain names get translated into IP addresses
- **Routing** – how packets find their way from source to destination across networks
- **Gateway** – the exit point a device uses to reach other networks (typically the router)
- **ARP (Address Resolution Protocol)** – mapping IP addresses to MAC addresses on a local network
- **ICMP (Internet Control Message Protocol)** – the protocol behind `ping` and other network diagnostics

---

##  Why This Matters

| Concept learned here | Applied in |
|---|---|
| DNS resolution | Network Path Explorer (Day 5), Shadow NOC (Day 12) |
| ICMP | Network Path Explorer (Day 5) ping phase, Network Recon Scanner (Day 6) host discovery |
| Routing | Traceroute/hop discovery in Network Path Explorer (Day 5), Shadow NOC (Day 12) |
| Gateway / ARP | Understanding what's actually happening one hop away from a host |

---

##  Notes

No standalone code was produced on this day — purely theoretical groundwork, later reimplemented in Python starting with the Day 5 project (DNS resolution and ICMP ping specifically).

---

##  Author

**Team Crypt0n1c** – Day 3, Bootcamp Foundations
