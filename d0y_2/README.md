# Day 2 – IP Addressing & Network Types

Deep dive into how IPv4 addresses are structured, how networks are divided into subnets, and the distinction between private and public address space.

---

##  Objective

To understand how individual hosts are identified and grouped on a network — the foundation for everything from home routers to the subnet scanning built later in the bootcamp (Day 6).

---

##  Topics Covered

### IP Addressing
- **IPv4 Addressing** – structure and format of IP addresses (32-bit, dotted-decimal notation)
- **CIDR Notation** – compact representation of IP ranges (e.g. `192.168.1.0/24`)
- **Subnetting** – dividing networks into smaller sub-networks
- **Network Address** – the identifier for a subnet as a whole (first address in a range)
- **Broadcast Address** – the address that reaches every host on a subnet (last address in a range)
- **Host Address** – the identifier for an individual device on a network

### Network Types
- **Private Networks** – non-routable address ranges reserved for internal use (e.g. `10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`)
- **Public Networks** – globally routable, internet-facing addresses

---

##  Why This Matters

| Concept learned here | Applied in |
|---|---|
| CIDR / subnetting | Network Recon Scanner (Day 6) — parses CIDR ranges with Python's `ipaddress` module |
| Network / broadcast / host address | Understanding scan ranges and valid host addresses within a subnet |
| Private vs. public networks | Reasoning about what's reachable/scannable from a given vantage point |

---

##  Notes

No standalone code was produced on this day — purely theoretical groundwork, later applied directly in the Day 6 subnet scanner.

---

##  Author

**Team Crypt0n1c** – Day 2, Bootcamp Foundations
