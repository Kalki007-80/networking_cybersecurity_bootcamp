# Day 1 – Networking Models

Introduction to the conceptual frameworks used to describe how network communication works, laying the groundwork for every later networking concept in the bootcamp.

---

##  Objective

To understand the layered models that describe how data moves from an application on one machine to an application on another — before touching addressing, protocols, or code.

---

##  Topics Covered

### OSI Model
The 7-layer conceptual model for network communication:

1. Physical
2. Data Link
3. Network
4. Transport
5. Session
6. Presentation
7. Application

Used as a reference framework for reasoning about where a given protocol or problem "lives" (e.g. Ethernet = Layer 2, IP = Layer 3, TCP = Layer 4, HTTP = Layer 7).

### TCP/IP Model
The practical 4-layer model the real internet actually runs on:

1. Network Access (Link)
2. Internet
3. Transport
4. Application

Mapped against the OSI model to understand how the two relate — TCP/IP collapses OSI's top three layers into one "Application" layer, and the bottom two into "Network Access."

---

##  Why This Matters

Every later project references these layers implicitly:

| Layer | Where it shows up later |
|---|---|
| Network / Internet | IP addressing, routing, DNS (Day 2–3) |
| Transport | TCP vs UDP, ports, sockets (Day 4, Day 10) |
| Application | HTTP protocol work (Day 9, Day 11) |

---

##  Notes

No standalone code was produced on this day — purely theoretical groundwork.

---

##  Author

**Team Crypt0n1c** – Day 1, Bootcamp Foundations
