# Day 4 – Transport Layer & Linux Networking Tools

Study of TCP vs. UDP, ports, and standard services — plus hands-on practice with Linux command-line networking tools to observe these concepts directly before reimplementing them in Python.

---

##  Objective

To understand how a single IP address can serve many simultaneous connections and services, and to get hands-on with the standard tools (`ping`, `tracepath`, `curl`, raw sockets) that later projects reimplement from scratch.

---

##  Topics Covered

### Transport Layer
- **TCP vs UDP** – connection-oriented vs. connectionless transport, and when each is used
- **Ports** – how a single IP address serves many simultaneous services
- **Services** – standard services conventionally bound to well-known ports (SSH/22, HTTP/80, HTTPS/443, DNS/53, etc.)

### Linux Networking Tools Practiced
Hands-on use of standard Linux networking utilities, ahead of reimplementing their core logic in Python from Day 5 onward:

- `ping` – ICMP reachability testing
- `tracepath` / `traceroute` – route/hop discovery
- `curl` – manual HTTP requests
- Raw TCP sockets – low-level connection testing

---

##  Why This Matters

| Concept learned here | Applied in |
|---|---|
| TCP vs UDP | TCP Client Explorer (Day 10), Shadow Web Server (Day 11) |
| Ports / services | Network Recon Scanner (Day 6), Service Whisperer (Day 8) |
| `ping` / `tracepath` (CLI) | Reimplemented via `subprocess` in Network Path Explorer (Day 5), Shadow NOC (Day 12) |
| `curl` (CLI) | Reimplemented via raw sockets in TCP Client Explorer (Day 10), HTTP Investigator (Day 9) |

---

##  Notes

No standalone code was produced on this day — purely theoretical groundwork and CLI tool practice, later reimplemented from scratch in Python starting with the Day 5 project.

---

##  Author

**Team Crypt0n1c** – Day 4, Bootcamp Foundations
