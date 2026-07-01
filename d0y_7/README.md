# Day 7 – Security & Web Communication Concepts

Study of the protocols and practices that secure network communication and services, bridging the port-scanning work of Day 6 and the banner-grabbing/TLS work of Day 8.

---

##  Objective

To understand *what* is running behind an open port beyond just its number — the security posture of common services, how encryption and authentication work, and how HTTP headers carry meaning — before building the Day 8 Service Whisperer, which puts this into practice.

---

##  Topics Covered

### Secure Access & Transport
- **SSH** – encrypted remote shell access; why it replaced Telnet
- **HTTPS** – HTTP layered over TLS; how it differs from plain HTTP at the transport level
- **Encryption** – symmetric vs. asymmetric encryption, and where each is used in TLS handshakes

### Authentication & Data Security
- **Authentication** – how services verify identity (passwords, keys, tokens)
- **Database Security** – common protections and risks around exposed database ports (MySQL, PostgreSQL, Redis, MongoDB)

### Web Communication
- **Web Server Communication** – the request/response cycle between client and server
- **HTTP Headers** – how headers carry metadata (content type, caching, security policy, authentication) alongside the actual payload

---

##  Why This Matters

| Concept learned here | Applied in |
|---|---|
| SSH / service identification | Service Whisperer (Day 8) — banner grabbing across services |
| HTTPS / encryption | Service Whisperer (Day 8) TLS support, Shadow NOC (Day 12) SSL inspection |
| Database security / exposed ports | Network Recon Scanner (Day 6) common-port list, Service Whisperer (Day 8) |
| HTTP headers | HTTP Investigator (Day 9), Shadow Web Server (Day 11), Shadow NOC (Day 12) security-header analysis |

---

##  Notes

No standalone code was produced on this day — purely theoretical groundwork, directly setting up the Day 8 Service Whisperer project.

---

##  Author

**Team Crypt0n1c** – Day 7, Bootcamp Foundations
