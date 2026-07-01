# Day 3 Notes – Live Packet Analyzer

## What is a Packet?

A **packet** is a small unit of data transmitted over a network. It contains:
- **Header** – control information (source/destination IP, ports, protocol, flags)
- **Payload** – the actual data being sent

Packets are the fundamental building blocks of all network communication.

---

## Packet Structure 

| Ethernet Header || (MAC addresses, type) || IP Header || (source IP, dest IP, protocol) |
| TCP/UDP Header |
| (source port, dest port, flags) |
| Payload (Data) |

---

## DNS Queries

**DNS (Domain Name System)** translates human-readable domain names (like `chatgpt.com`) into IP addresses.

### A Record
- Maps a domain to an **IPv4** address.
- Example: `chatgpt.com. 60 IN A 104.18.12.90`

### AAAA Record
- Maps a domain to an **IPv6** address.

When a client requests `chatgpt.com`, it sends a DNS query to a DNS server (usually on port 53). The server responds with the A (or AAAA) record.

---

## TCP Flags

TCP uses flags to manage the state of a connection. Common flags:

| Flag | Name          | Purpose                                      |
|------|---------------|----------------------------------------------|
| SYN  | Synchronize   | Start a connection (handshake)              |
| ACK  | Acknowledge   | Confirm receipt of data                     |
| PSH  | Push          | Immediately push data to application        |
| FIN  | Finish        | Gracefully close connection                 |
| RST  | Reset         | Abort connection abruptly                   |
| URG  | Urgent        | Urgent data (rarely used)                   |

We saw flags like `[S.]` = SYN-ACK, `[.]` = ACK, `[P.]` = PUSH-ACK.

---

## HTTPS – Secure HTTP

HTTPS (HTTP over SSL/TLS) uses **port 443** and encrypts the data between client and server. It adds a layer of security using TLS handshake before any HTTP data is exchanged.

Packets on port 443 are usually encrypted; we can only see that they are HTTPS, but not the actual content.

---

## The `tcpdump` Tool

`tcpdump` is a command-line packet analyzer. It captures network traffic and prints packet details.

### Common flags used:
- `-c N` – capture only N packets
- `-n` – don't resolve hostnames (show IPs only)
- `-vv` – verbose output
- `-e` – show MAC addresses

Example:
```bash
tcpdump -c 5 -n -vv -e
