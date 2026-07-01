# Day 5 – Network Path Explorer

## What is Ping?

**Ping** is a network diagnostic tool that tests reachability of a host on an IP network. It sends **ICMP Echo Request** packets and waits for **ICMP Echo Reply** packets.

### How it works:
1. Source sends an ICMP Echo Request to the destination.
2. Destination replies with an ICMP Echo Reply.
3. The round‑trip time (RTT) is measured.

### Common ping options:
- `-c` – count of packets
- `-i` – interval between packets
- `-t` – TTL (Time To Live)
- `-s` – packet size

### Why ping is useful:
- Check if a host is online.
- Measure network latency.
- Detect packet loss.
- Basic troubleshooting.

---

## What is Traceroute?

**Traceroute** is a diagnostic tool that shows the path (route) packets take from source to destination. It lists each hop (router) along the way.

### How it works:
1. Sends packets with incrementing TTL (Time To Live) values.
2. Each router decrements TTL; when TTL reaches 0, the router sends back an ICMP Time Exceeded message.
3. The source records the router's IP address.
4. Repeats until the destination is reached.

### Traceroute vs. Tracepath:
- **traceroute** – Uses UDP packets by default (Linux) or ICMP (Windows). Requires root for some options.
- **tracepath** – Uses UDP and does not require root; also discovers MTU along the path.

We'll use `tracepath` because it's simpler and works without root.

---

## DNS Resolution

**DNS (Domain Name System)** translates domain names to IP addresses.

### Tools for DNS resolution:
- `socket.gethostbyname()` – returns an IPv4 address.
- `socket.getaddrinfo()` – returns all address info (IPv4, IPv6, port, etc.).
- `dig` and `nslookup` – command‑line tools for detailed DNS queries.

We'll use Python's `socket` module for resolution.

---

## TTL (Time To Live)

TTL is a field in IP packets that limits the lifespan of a packet. Each router decrements the TTL by 1. When TTL reaches 0, the packet is discarded and an ICMP Time Exceeded message is sent back.

- **Purpose** – Prevents packets from looping forever in routing loops.
- **Default TTL** – 64 (Linux), 128 (Windows), 255 (some routers).

---

## ICMP (Internet Control Message Protocol)

ICMP is a supporting protocol used for error reporting and diagnostic functions.

### Common ICMP types:
- **Type 8** – Echo Request (ping)
- **Type 0** – Echo Reply (ping response)
- **Type 11** – Time Exceeded (traceroute)
- **Type 3** – Destination Unreachable

---

## How the Script Works

1. **Input** – User enters a target (domain or IP) and optionally a maximum hops value.
2. **DNS resolution** – Resolves the target to an IP address.
3. **Ping** – Sends 4 ICMP Echo Requests and measures RTT, packet loss, and min/max/avg latency.
4. **Traceroute** – Uses `tracepath` to discover the route and measures hop count and latency per hop.
5. **Reporting** – Saves all data to JSON and TXT files.
6. **Summary** – Displays a clean summary in the terminal.

---

## Commands Learned Today

```bash
ping -c 4 google.com
traceroute google.com
tracepath google.com
