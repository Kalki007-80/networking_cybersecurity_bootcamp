# Shadow Web Server v2.0

A professional HTTP server built from scratch using Python's `socket` module. Features configuration management, static file serving, JSON APIs, concurrency, logging, and a clean project structure.

---

##  Features

- **HTTP/1.1** – Full status code support
- **Static file serving** – From `www/` directory, mirroring a real document root
- **JSON APIs** – `/status`, `/json`, `/echo`
- **Concurrency** – Thread-based multi-client handling
- **Logging** – Access logs with response times
- **Configuration** – External `config.json`
- **MIME detection** – 30+ file types
- **Clean structure** – Separate folders for code, config, logs, and content

---

##  Project Structure

```
shadow_web_server/
├── shadow_web_server.py       # Main server
├── requirements.txt           # Dependencies (none — stdlib only)
├── README.md                  # This file
├── notes.md                   # Design notes / learning log
│
├── config/
│   └── config.json            # Server configuration
│
├── www/                       # Static website (document root)
│   ├── index.html
│   ├── about.html
│   ├── style.css
│   ├── script.js
│   ├── images/
│   │   └── logo.png
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── app.js
│
├── logs/
│   └── server.log             # Access logs (auto-appended)
│
├── reports/                   # Reserved for future monitoring output
│
└── templates/                 # Reserved for future template engine
    ├── home.html
    ├── error404.html
    └── error500.html
```

---

##  Installation & Usage

1. **Unzip / clone** the project and `cd` into it.
2. **Run the server** (Python 3.6+, no external packages needed):

```bash
python3 shadow_web_server.py
```

3. **Open your browser** at `http://localhost:8080` — this hits the built-in
   home route. To view the static site instead, go to
   `http://localhost:8080/files/index.html`.
4. **Override the port**:

```bash
python3 shadow_web_server.py 9000
```

5. **Stop** with `Ctrl+C`.

---

##  Routes

| Path                | Method | Description                             |
|----------------------|--------|------------------------------------------|
| `/`                  | GET    | Built-in home page (generated in Python) |
| `/about`             | GET    | Built-in about page                      |
| `/time`              | GET    | Current server time                      |
| `/status`            | GET    | Server status (JSON)                     |
| `/hello?name=X`      | GET    | Personalized greeting                    |
| `/json`              | GET    | Example JSON response                    |
| `/echo`              | POST   | Echo POST data (JSON)                    |
| `/files/*`           | GET    | Static files from `www/` (the real site) |

The **static website** lives under `www/` and is reachable at:

- `/files/index.html` — homepage with nav, hero, live API demo button
- `/files/about.html` — about page
- `/files/style.css`, `/files/css/main.css` — stylesheets
- `/files/script.js`, `/files/js/app.js` — client-side scripts
- `/files/images/logo.png` — logo asset

---

##  Configuration

Edit `config/config.json` to change:

- `host` – Server IP (default: `0.0.0.0`)
- `port` – Listening port (default: `8080`)
- `www_dir` – Document root (default: `www`)
- `log_file` – Log file path (default: `logs/server.log`)

---

##  Logging

Access logs are written to `logs/server.log` in the format:

```
2026-07-01T10:45:23 | 127.0.0.1 | GET / | 200 | 12.34ms
```

---

##  Future Enhancements

- HTTPS/TLS support
- Session management / authentication
- Database integration
- WebSocket support
- A real template engine wired to `templates/`
- Caching

---

##  License

Educational use only.

---

##  Author

**Team Crypt0n1c** – Day 11 Bootcamp Project

---

**Build your own web server. Understand the web.** 🌐
