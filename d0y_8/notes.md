# Day 8 Notes – Service Whisperer

## Banner Grabbing

Banner grabbing is a technique used to obtain service information by reading the initial response a server sends upon connection. It reveals software name, version, and sometimes operating system details.

### How it works:
- Connect to an open port.
- Send a simple probe (or just wait).
- Read the first bytes sent by the server.
- Parse the response to extract relevant data.

---

## Service-Specific Probes

Different services require different probes:

- **SSH (22)** – The server immediately sends its banner.
- **FTP (21)** – Server sends a welcome message.
- **SMTP (25)** – Server sends a greeting.
- **HTTP (80)** – Must send a `HEAD / HTTP/1.0` request.
- **HTTPS (443)** – Must use SSL/TLS before sending HTTP request.

---

## SSL/TLS Wrapping

For HTTPS, we wrap the socket with `ssl.create_default_context().wrap_socket()`. This enables encrypted communication so we can send a GET request and read headers.

---

## Ethical Considerations

Banner grabbing is passive and non‑intrusive. It only reads information the service voluntarily sends. However, automated scanning may still be considered suspicious; always have permission.

---

## Key Takeaways

- Banners reveal software and versions.
- Different protocols need different probes.
- TLS adds a layer of complexity.
- Threading speeds up scanning.
- Service identification helps in vulnerability assessment.
