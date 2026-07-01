# Network Recon Scanner

A subnet-wide host discovery and port scanning tool. Give it a CIDR range, and it finds which hosts are alive and which common ports are open on each, using concurrent scanning for speed.

---

##  Objective

To go beyond scanning a single host and build a tool capable of sweeping an entire subnet — parsing CIDR notation, discovering live hosts via ICMP, and checking common service ports on each one, all in parallel.

---

##  Ethical Use

This tool actively pings and port-scans every address in the subnet you give it. **Only run it against networks you own or have explicit permission to scan.** Scanning subnets you don't control can violate computer-misuse laws and network policies, even without exploiting anything.

---

##  Features

- **CIDR Parsing** – Uses Python's `ipaddress` module; supports `/16`, `/24`, `/29`, `/30`, and other subnet masks
- **Host Discovery** – ICMP ping sweep to detect alive vs. offline hosts
- **Threaded Scanning** – Uses `ThreadPoolExecutor` to scan many hosts simultaneously
- **Port Scanning** – Checks common service ports per live host: SSH, HTTP, HTTPS, DNS, MySQL, Redis, MongoDB, PostgreSQL, and more
- **Reporting** – Produces JSON and TXT reports with scan statistics, live/offline host lists, and response times

---

##  Quick Start

```bash
python3 network_recon_scanner.py <cidr>
# e.g.
python3 network_recon_scanner.py 192.168.1.0/24
```

---

---

##  Scan Flow

| Step | Action |
|------|--------|
| 1 | Parse the CIDR range into individual host addresses |
| 2 | Ping-sweep all hosts concurrently to find which are alive |
| 3 | Port-scan common ports on each live host |
| 4 | Aggregate results — live hosts, offline hosts, open ports, response times |
| 5 | Write JSON and TXT reports |

---

##  Requirements

- Python 3.6+
- System `ping` binary available on PATH
- Standard library only — no pip installs required

---

##  License

Educational use only. Only scan networks you own or have permission to test.

---

##  Author

**Team Crypt0n1c** – Day 6 Bootcamp Project
