# Claude Token Viewer

macOS menubar app showing real-time Claude.ai usage: `Session X% · Weekly X%`.

Ported from the [claude-counter](https://github.com) Chrome extension's usage logic:
reads the `lastActiveOrg` cookie from your browser and polls
`GET /api/organizations/{orgId}/usage` on claude.ai using your existing browser session
(no API key, no login flow in the app itself).

## Requirements

- macOS
- Python 3.9+
- Logged into claude.ai in **Opera** (cookie source is hardcoded to Opera's cookie store —
  edit `get_cookiejar()` in `claude_usage_bar.py` to point at a different Chromium browser,
  e.g. `browser_cookie3.chrome(...)`, if needed)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 claude_usage_bar.py
```

The menubar title updates every 60 seconds with the current session (5h window) and
weekly (7d window) usage percentages reported by claude.ai.

## Notes

- macOS may prompt for Keychain access the first time it decrypts Opera's cookie store —
  this is required to read the session cookie.
- If you see "Session: error", make sure you're logged into claude.ai in Opera and have
  visited the site recently so the `lastActiveOrg` cookie is set.
