
---

# Day 10 – TCP Client Explorer v2.0

A Python tool that sends raw HTTP requests over TCP, with full TLS/SSL support, certificate inspection, timing breakdown (DNS, connect, TLS, transfer), and professional reports in JSON and TXT formats.

---

##  Objective

To build a professional TCP client that:
- Establishes TCP connections (plain or TLS)
- Sends HTTP requests (GET, HEAD, POST, PUT, DELETE)
- Receives and parses HTTP responses
- Measures timing breakdown (DNS, connect, TLS, transfer)
- Inspects TLS certificates
- Splits headers from body
- Generates structured reports

---

##  Features

- **Raw TCP sockets** – Full control
- **TLS/SSL support** – HTTPS with certificate inspection
- **HTTP methods** – GET, HEAD, POST, PUT, DELETE
- **Custom headers** – User-defined request headers
- **POST/PUT data** – Send data in request body
- **Timing breakdown** – DNS, connect, TLS, transfer, total
- **Certificate inspection** – Subject, issuer, validity
- **Response parsing** – Splits headers and body
- **Status code extraction** – Shows HTTP status
- **Reports** – JSON and TXT output

---

##  Technologies

- Python 3.6+
- `socket` – Core networking
- `ssl` – TLS/SSL encryption
- `json` – Structured output
- `re` – Status line parsing
- `datetime` – Timestamps
- `urllib.parse` – URL parsing

---

##  How to Use

```bash
python3 tcp_client.py
