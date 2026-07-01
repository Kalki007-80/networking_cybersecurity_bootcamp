# Day 2 – Packet Ocean Explorer

## What is a Socket?

A **socket** is an endpoint for sending or receiving data across a computer network. It is a combination of an **IP address** and a **port number**.

> Think of it like a door: the IP address is the building address, and the port is the specific apartment number.

Sockets are used by applications to communicate over the network using protocols like TCP and UDP.

---

## TCP vs UDP – A Quick Recap

| Feature          | TCP (Transmission Control Protocol)                | UDP (User Datagram Protocol)            |
|------------------|----------------------------------------------------|-----------------------------------------|
| Connection       | Connection-oriented (handshake)                    | Connectionless                          |
| Reliability      | Guaranteed delivery, retransmission                | No guarantee, packets may be lost       |
| Order            | Preserves order                                    | No order guarantee                      |
| Speed            | Slower due to overhead                             | Faster, lightweight                     |
| Use Cases        | HTTP, HTTPS, SSH, FTP, Email                       | DNS, VoIP, video streaming, gaming      |

---

## The `ss` Command

`ss` (socket statistics) is a Linux utility used to display detailed information about sockets. It is faster and more modern than `netstat`.

### Common options:
- `-t` : Show TCP sockets
- `-u` : Show UDP sockets
- `-n` : Show numerical addresses (no DNS resolution)
- `-l` : Show only listening sockets
- `-p` : Show process using the socket

In our project we used:
```bash
ss -tun
