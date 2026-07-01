# Shadow Network Operation Center (SNOC)

A comprehensive network observatory that unifies DNS, ping, traceroute, port scanning, banner grabbing, SSL inspection, HTTP analysis, security headers, cookies, and technology detection into one professional-grade tool.

---

##  Objective

To build a complete network reconnaissance system that:

- Resolves DNS (IPv4, IPv6, reverse)
- Tests reachability (ping)
- Traces network route
- Scans common ports
- Grabs service banners
- Inspects SSL/TLS certificates
- Analyzes HTTP responses
- Evaluates security headers
- Parses cookies
- Detects technologies and frameworks
- Generates JSON, TXT, and HTML reports

---

##  Ethical Use

This tool actively connects to and probes network hosts (ping, port scans,
banner grabs, TLS handshakes, HTTP requests). **Only run it against systems
you own or have explicit written permission to test.** Unauthorized scanning
of third-party systems may violate computer-misuse laws (e.g. the US CFAA,
UK Computer Misuse Act) and the target's terms of service, even when no
vulnerability is exploited.

---

##  Features

- **All-in-one** – 10 reconnaissance phases in a single run
- **Concurrent** – Threaded port scanning
- **Professional reporting** – JSON, TXT, HTML, all timestamped
- **Config-driven** – Ports, timeouts, and worker counts live in `config/config.json`
- **Modular design** – Each phase is a standalone, testable function
- **Standard library only** – No external dependencies (uses system `ping` / `tracepath`)

---

##  Quick Start

```bash
cd shadow_noc
python3 shadow_noc.py
# Enter a target (domain or IP) when prompted

# or run non-interactively:
python3 shadow_noc.py example.com
```

---

##  Project Structure

```
shadow_noc/
├── shadow_noc.py
├── requirements.txt
├── README.md
├── notes.md
├── config/
│   └── config.json
├── reports/
│   └── noc_report_*.json / .txt / .html
├── logs/
│   └── noc.log
└── modules/            # reserved for a future split into per-phase files
    └── README.md
```

---

##  Phases

| Phase | Description |
|-------|-------------|
| 1 | DNS Intelligence – Resolves hostname to IPv4/IPv6, reverse DNS |
| 2 | Reachability – Ping test (uses system `ping`) |
| 3 | Route Intelligence – Traceroute (uses system `tracepath`) |
| 4 | Port Intelligence – Threaded scan of common ports |
| 5 | Service Intelligence – Banner grabbing on open ports |
| 6 | TLS Intelligence – SSL certificate inspection (if 443 is open) |
| 7 | HTTP Intelligence – Raw HTTP/HTTPS request/response |
| 8 | Security Analysis – Checks for 6 standard security headers |
| 9 | Cookie Intelligence – Parses `Set-Cookie` flags (Secure/HttpOnly/SameSite) |
| 10 | Technology Detection – Pattern-matches common frameworks/servers |

---

##  Customization

Edit `config/config.json` to change:

- `common_ports` – which ports get scanned
- `port_scan_workers` – thread pool size for the scanner
- `port_scan_timeout` / `http_timeout` – per-connection timeouts
- `ping_count` – number of ICMP echo requests sent

Edit `TECH_PATTERNS` in `shadow_noc.py` to adjust technology detection.

---

##  Fixes vs. the original draft

A few issues were caught and corrected while assembling this build:

- **Security header matching bug** — HTTP headers use hyphens
  (`x-frame-options`) but the check compared against underscore keys
  (`x_frame_options`), so it never matched. Headers are now normalized
  before comparison.
- **Unescaped HTML in reports** — banner text, HTTP headers, and body
  previews come from the network and were being written straight into
  the HTML report. They're now HTML-escaped to avoid a malformed or
  broken report page if a target returns unusual characters.
- **CLI argument support** — `python3 shadow_noc.py <target>` now works
  for scripted/non-interactive runs, in addition to the interactive prompt.
- **Config file wired in** — `config/config.json` is now actually read
  and used (ports, timeouts, worker count), instead of just sitting
  next to the script unused.

---

##  License

Educational use only. Use only on systems you own or have permission to test.

---

##  Author

**Team Crypt0n1c** – Final Bootcamp Project

---

**Complete your journey. Understand the network.** 
