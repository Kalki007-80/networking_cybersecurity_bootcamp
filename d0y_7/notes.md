# Day 7 Notes – Port Gatekeeper Scanner

## What is a Port?

A port is a logical endpoint for network communication. Port numbers range from 0 to 65535.

- **Well-known ports (0–1023)** – assigned to common services (e.g., HTTP on 80, SSH on 22).
- **Registered ports (1024–49151)** – used by user applications.
- **Dynamic/private ports (49152–65535)** – ephemeral ports for client connections.

---

## TCP Handshake

A port is **open** if a TCP connection can be established.
- Client: SYN
- Server: SYN-ACK
- Client: ACK


If the server responds with RST, the port is closed. If no response, it's filtered (firewall).

---

## Socket Programming in Python

- `socket.socket()` – create a socket.
- `socket.connect_ex()` – attempt connection, returns 0 on success.
- `socket.settimeout()` – set timeout for blocking operations.

---

## Concurrent Scanning with Threads

Using `ThreadPoolExecutor`, we can scan many ports simultaneously, greatly reducing scan time.

---

## Banner Grabbing

After connecting, we can send a simple probe (e.g., `HEAD /` for HTTP, `\n` for SSH) and read the service's welcome banner. This reveals software versions.

---

## Scan Modes

- **Fast** – only common ports (≈20 ports).
- **Normal** – ports 1–1024 (≈1024 ports).
- **Deep** – all 1–65535 ports (≈65535 ports).

---

## Commands

```bash
python3 port_gatekeeper.py
