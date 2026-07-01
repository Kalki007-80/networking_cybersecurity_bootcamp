# Day 9 Notes – HTTP Investigator

## HTTP Protocol Basics

HTTP (Hypertext Transfer Protocol) is the foundation of data communication on the World Wide Web. It is a **request-response** protocol where a client sends a request and a server returns a response.

### HTTP Methods

| Method | Description |
|--------|-------------|
| GET | Retrieve data from the server |
| HEAD | Same as GET but without response body |
| POST | Submit data to the server |
| PUT | Replace or create a resource |
| DELETE | Remove a resource |

### HTTP Status Codes

**2xx – Success**
- `200 OK` – Request successful

**3xx – Redirection**
- `301 Moved Permanently` – Resource moved permanently
- `302 Found` – Temporary redirect
- `303 See Other` – Redirect to another resource

**4xx – Client Errors**
- `400 Bad Request` – Invalid request
- `401 Unauthorized` – Authentication required
- `403 Forbidden` – Access denied
- `404 Not Found` – Resource not found

**5xx – Server Errors**
- `500 Internal Server Error` – Generic server error
- `502 Bad Gateway` – Invalid response from upstream
- `503 Service Unavailable` – Server overloaded or down

---

## HTTP Headers

Headers provide metadata about the request or response.

### Request Headers
- `Host` – Target domain
- `User-Agent` – Client identification
- `Cookie` – Session data
- `Authorization` – Authentication credentials
- `Content-Type` – Format of request body

### Response Headers
- `Server` – Web server software
- `Set-Cookie` – Server sets a cookie in the browser
- `Content-Type` – Format of response body
- `Content-Length` – Size of response body

---

## Security Headers

These headers improve web application security.

| Header | Purpose |
|--------|---------|
| `Strict-Transport-Security` (HSTS) | Enforces HTTPS connections |
| `Content-Security-Policy` (CSP) | Prevents XSS and injection attacks |
| `X-Frame-Options` | Prevents clickjacking |
| `X-Content-Type-Options` | Prevents MIME sniffing |
| `Referrer-Policy` | Controls referrer information |
| `X-XSS-Protection` | Legacy XSS protection (deprecated) |

---

## Cookies and Sessions

A **session** maintains state between client and server across multiple requests. **Cookies** are small pieces of data stored by the browser.

### How Sessions Work
1. User logs in with credentials
2. Server validates credentials and creates a session ID
3. Server sends `Set-Cookie: session=abc123` in response
4. Browser stores the cookie
5. Subsequent requests include `Cookie: session=abc123`
6. Server validates the session ID

### Cookie Security Flags
- **Secure** – Only sent over HTTPS
- **HttpOnly** – Inaccessible to JavaScript (prevents XSS cookie theft)
- **SameSite** – Controls cross-site request behavior

---

## DNS Resolution

DNS translates human-readable domain names to IP addresses. The process involves:

1. **Local cache** – Browser/OS cache check
2. **Recursive resolver** – ISP or public DNS (e.g., 8.8.8.8)
3. **Root servers** – Point to TLD servers
4. **TLD servers** – Point to authoritative name servers
5. **Authoritative name servers** – Return the IP address

---

## TLS Handshake

TLS (Transport Layer Security) encrypts communication. The handshake involves:

1. **ClientHello** – Client announces supported ciphers and TLS version
2. **ServerHello** – Server chooses cipher and sends certificate
3. **Certificate Verification** – Client verifies the certificate
4. **Key Exchange** – Both sides generate session keys
5. **Finished** – Secure channel established

### Certificate Information
- **Subject** – Domain name and organization
- **Issuer** – Certificate Authority (CA)
- **Not Before/After** – Validity period
- **Serial Number** – Unique identifier

---

## Timing Breakdown

Our script measures each phase of the request:

| Phase | Description |
|-------|-------------|
| DNS | Time to resolve hostname to IP |
| Connect | TCP handshake time |
| TLS | SSL/TLS handshake time (HTTPS only) |
| Transfer | Time to send request and receive response |
| Total | Sum of all phases |

---

## Proxy Support

The script supports HTTP/HTTPS proxies using the `CONNECT` method:

1. Connect to the proxy server
2. Send `CONNECT target:port HTTP/1.1`
3. Receive `200 Connection established`
4. Tunnel traffic through the proxy

---

## Response Validation with JSON Schema

JSON Schema is a vocabulary that allows you to annotate and validate JSON documents.

### Example Schema
```json
{
  "type": "object",
  "properties": {
    "status": { "type": "string" },
    "data": { "type": "object" }
  },
  "required": ["status"]
}
