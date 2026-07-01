# Network Path Explorer

A network diagnostics tool that combines DNS resolution, ICMP reachability testing, and route discovery into a single command-line utility, with JSON and human-readable text reporting.

---

##  Objective

To understand and rebuild the core mechanics behind everyday networking tools (`dig`, `ping`, `traceroute`) instead of just using them — implemented in Python using the standard library plus system `ping`/`tracepath`.

---

##  Features

- **DNS Resolution** – Converts a domain name into its IP address(es)
- **ICMP Ping** – Measures packet loss, RTT (min/avg/max), and reachability
- **Route Discovery** – Traces the path to a target using `tracepath`, with a `traceroute` fallback
  - Displays every hop, intermediate router IP, and per-hop latency
- **Reporting** – Exports results as both a JSON report and a human-readable text report

---

##  Quick Start

```bash
python3 network_path_explorer.py <target>
# e.g.
python3 network_path_explorer.py example.com
```

---
---

##  What It Does, Step by Step

| Step | Action |
|------|--------|
| 1 | Resolve the target hostname to an IP address |
| 2 | Ping the resolved IP and record loss %, min/avg/max RTT |
| 3 | Trace the route to the target, listing each hop and its latency |
| 4 | Write a JSON report and a plain-text report summarizing all of the above |

---

##  Requirements

- Python 3.6+
- System `ping` and `tracepath` (or `traceroute`) binaries available on PATH
- Standard library only — no pip installs required

---

##  License

Educational use only.

---

##  Author

**Team Crypt0n1c** – Day 5 Bootcamp Project
