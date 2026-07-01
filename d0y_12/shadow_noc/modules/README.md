# modules/

Reserved for a future refactor that splits `shadow_noc.py` into
per-phase files, e.g.:

- `dns.py` — Phase 1 (DNS intelligence)
- `ping.py` — Phase 2 (reachability)
- `traceroute.py` — Phase 3 (route intelligence)
- `scanner.py` — Phase 4 (port scanning)
- `banner.py` — Phase 5 (banner grabbing)
- `ssl_info.py` — Phase 6 (TLS inspection)
- `http.py` — Phase 7 (HTTP exploration)
- `security.py` — Phase 8 (security headers)
- `cookies.py` — Phase 9 (cookie analysis)
- `technologies.py` — Phase 10 (technology detection)
- `report.py` — report generation (JSON/TXT/HTML)

Currently everything lives in `shadow_noc.py` for simplicity, as noted
in the project README — this directory is a placeholder for that split.
