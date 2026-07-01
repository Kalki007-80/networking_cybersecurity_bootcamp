# Day 11 Notes – Shadow Web Server 

## Professional Project Structure

A real web server project separates concerns into directories:

```
shadow_web_server/
├── config/                # Configuration files
├── www/                   # Static website (document root)
├── logs/                  # Access logs
├── reports/                # Generated reports
├── templates/              # HTML templates (future use)
└── shadow_web_server.py   # Main server code
```

### Why This Structure?

- **Config** – Allows customization without touching code.
- **www/** – Mimics an Apache/Nginx document root; now a full static site
  with a homepage, about page, shared CSS/JS, and an image asset.
- **Logs** – Separates logs from source.
- **Reports** – Holds output from future monitoring features.
- **Templates** – Prepares for dynamic HTML generation.

---

## Configuration Management

The server reads `config/config.json` on startup. If missing, it creates a default:

```json
{
    "host": "0.0.0.0",
    "port": 8080,
    "www_dir": "www",
    "log_file": "logs/server.log"
}
```

---

## Static File Serving

All files under `www/` are served via the `/files/` route:

- `/files/index.html` → `www/index.html`
- `/files/about.html` → `www/about.html`
- `/files/css/main.css` → `www/css/main.css`
- `/files/js/app.js` → `www/js/app.js`
- `/files/images/logo.png` → `www/images/logo.png`

This mirrors how professional web servers operate. `serve_static_file()`
strips leading slashes and rejects `..` segments to prevent directory
traversal outside `www/`.

---

## Logging

Each request is logged to `logs/server.log` with:

- Timestamp
- Client IP
- Method and path
- Status code
- Response time in milliseconds

---

## Future Extensibility

With this structure, you can easily add:

- Authentication (`auth.py`)
- Database integration (`database.py`)
- WebSocket support
- SSL/TLS encryption
- Caching middleware
- A real `{{ variable }}` substitution engine for `templates/`

---

## Commands

```bash
# Run with default config (port 8080)
python3 shadow_web_server.py

# Override port via command line
python3 shadow_web_server.py 9000
```

---

## Key Takeaways

- Separation of code, config, and data is professional.
- Configuration files make deployment easier.
- Logs are essential for monitoring.
- A clean structure scales with the project.
