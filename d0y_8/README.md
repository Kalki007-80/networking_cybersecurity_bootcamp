# Service Whisperer

An advanced TCP service detection tool: scans ports, grabs banners to identify what's actually running behind them, and supports TLS for HTTPS-style services — with parallel scanning and JSON/TXT/CSV reporting.

---

##  Objective

To go beyond "is this port open?" and answer "what service is actually running here?" — by connecting to open ports and reading whatever banner or response the service offers, the same technique tools like `nmap -sV` use.

---

##  Ethical Use

This tool connects directly to services on a target host to read their banners. **Only run it against systems you own or have explicit permission to test.** Unauthorized service enumeration of third-party hosts can violate computer-misuse laws even when nothing is exploited.

---

##  Features

- **TCP Port Scanning** – Common ports, well-known ports, or a custom port range
- **Banner Grabbing** – Reads identifying banners from SSH, HTTP, HTTPS, SMTP, FTP, POP3, IMAP, and other services
- **SSL/TLS Support** – Performs a TLS handshake for HTTPS-style ports and extracts server headers / response info over the encrypted connection
- **Parallel Scanning** – `ThreadPoolExecutor` with a configurable worker count
- **Reporting** – Exports results as JSON, TXT, and CSV

---

##  Quick Start

```bash
python3 service_whisperer.py <target>
# e.g.
python3 service_whisperer.py example.com

# custom port range
python3 service_whisperer.py example.com --ports 1-1024
```

---

## 📖 Scan Flow

| Step | Action |
|------|--------|
| 1 | Scan the target's ports (common, well-known, or a custom range) |
| 2 | For each open port, connect and attempt to grab a service banner |
| 3 | For HTTPS-style ports, perform a TLS handshake and extract server headers |
| 4 | Aggregate all findings per port: service guess, banner text, timing |
| 5 | Write JSON, TXT, and CSV reports |

---

##  Requirements

- Python 3.6+
- Standard library only — no pip installs required (uses `socket`, `ssl`, `concurrent.futures`)

---

##  License

Educational use only. Only scan systems you own or have permission to test.

---

##  Author

**Team Crypt0n1c** – Day 8 Bootcamp Project
