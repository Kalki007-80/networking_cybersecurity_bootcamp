# Day 6 Notes – Network Recon Scanner

## Subnet Scanning

Subnet scanning is the process of identifying all active hosts within a given IP range. It is a fundamental reconnaissance technique used by network administrators and security professionals.

### Why scan a subnet?
- Inventory all devices on a network.
- Detect unauthorized or rogue devices.
- Monitor host availability and uptime.
- Prepare for vulnerability assessments.

---

## ICMP Ping – The Heart of Host Discovery

**Ping** sends an ICMP Echo Request to a target and waits for an Echo Reply. A successful reply indicates the host is **alive**.

### Limitations:
- Some firewalls block ICMP.
- Some hosts may be configured to ignore ping.
- Relies on network reachability.

---

## Concurrency – Speed Up Scans

A sequential scan of 254 hosts with a 1‑second timeout takes **~4 minutes**. Concurrency reduces this dramatically.

### Python `concurrent.futures.ThreadPoolExecutor`
- Creates a pool of threads.
- Each thread scans one host independently.
- The number of workers controls parallelism.

### Benefits:
- Much faster than sequential scanning.
- Efficient use of system resources.
- Simple API.

### Important:
- Too many threads can overwhelm the network or system.
- Use a reasonable number (e.g., 50–100) for home networks.

---

## Port Scanning – Extended Recon

Once a live host is found, scanning its common ports reveals what services are running.

### Common ports we scan:
- **22** – SSH
- **80** – HTTP
- **443** – HTTPS
- **53** – DNS
- **25** – SMTP
- **3306** – MySQL
- **5432** – PostgreSQL
- **6379** – Redis
- **27017** – MongoDB

### How it works:
- Attempt a TCP connection to each port.
- If successful, port is open; a service is likely running.
- Timeout prevents long waits (2 seconds per port).

---

## Performance Considerations

- **ICMP scanning** with concurrency: ~1–2 seconds for a /24 subnet.
- **Port scanning** adds time: each live host multiplies by number of ports.
- A balance: scan all hosts first, then ports on live ones.

---

## Handling Errors and Edge Cases

- Invalid subnet input → catch `ValueError`.
- Ping not available → fallback or error message.
- Permission denied → notify user (some systems require root for raw sockets).
- Network unreachable → handle gracefully.

---

## Commands Used Today

```bash
ping -c 1 -W 1 192.168.1.1
