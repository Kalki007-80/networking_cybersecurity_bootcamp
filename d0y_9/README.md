# HTTP Investigator

A comprehensive HTTP inspection utility for understanding exactly how HTTP clients work internally — custom methods, headers, authentication, timing breakdowns, and full response parsing, with report export.

---

##  Objective

To learn the internal working of HTTP clients by building one from the ground up in terms of *behavior* — full control over methods, headers, auth, and connection handling — rather than treating `requests`/`curl` as a black box.

---

##  Features

- **Custom HTTP Methods** – GET, POST, HEAD, PUT, DELETE
- **Custom Headers** – attach arbitrary request headers
- **Basic Authentication** – send `Authorization: Basic` credentials
- **Proxy Support** – route requests through an HTTP proxy
- **Keep-Alive** – persistent connection support
- **HTTP/2 Support** – requests negotiated over HTTP/2 where available
- **Timing Analysis** – breaks a request down into:
  - DNS lookup time
  - Connection time
  - Transfer time
  - Total request time
- **Response Parsing** – status code, headers, and body, with JSON validation of the response body when applicable
- **Report Export** – saves inspection results for later review

---

##  Quick Start

```bash
python3 http_investigator.py <url>
# e.g.
python3 http_investigator.py https://example.com

# with a custom method and headers
python3 http_investigator.py https://example.com --method POST --header "X-Test: 1"

# with basic auth
python3 http_investigator.py https://example.com --user admin --pass secret
```

---

##  What It Does, Step by Step

| Step | Action |
|------|--------|
| 1 | Resolve the target host and time the DNS lookup |
| 2 | Open the connection (optionally through a proxy, optionally kept alive) and time the connect phase |
| 3 | Send the request with the chosen method, headers, and auth |
| 4 | Time the transfer and total request duration |
| 5 | Parse the response — status code, headers, body — and validate JSON bodies where applicable |
| 6 | Export a report of the full request/response/timing breakdown |

---

##  Requirements

- Python 3.6+
- Standard library only for core HTTP/1.1 behavior; HTTP/2 support depends on what's available in the environment

---

##  License

Educational use only.

---

##  Author

**Team Crypt0n1c** – Day 9 Bootcamp Project
