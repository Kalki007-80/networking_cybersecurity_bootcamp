# Day 10 Notes – TCP Client Explorer

## The TCP Protocol

TCP (Transmission Control Protocol) is a connection-oriented, reliable transport protocol. It ensures:

- **Reliability** – Packets are delivered without loss
- **Ordering** – Packets arrive in the correct sequence
- **Flow control** – Prevents sender from overwhelming receiver
- **Error detection** – Corrupted packets are retransmitted

### TCP Handshake – The Three-Way Handshake

Before data is exchanged, TCP establishes a connection:

Client                   Server
| 
|------ SYN --------------►|
| 
|◄---- SYN-ACK ------------|
| 
|------ ACK --------------►|
| 
|------ Data -------------►|


- **SYN** – Client requests connection
- **SYN-ACK** – Server acknowledges and agrees
- **ACK** – Client confirms
- **Data** – Transmission begins

---

## Sockets in Python

A **socket** is an endpoint for communication. Python's `socket` module provides access to the BSD socket API.

### Creating a TCP Socket

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
