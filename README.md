# Claude Token Viewer

macOS menubar / Windows tray app showing real-time Claude.ai usage:
`Session X% · Weekly X%`.

Ported from the [claude-counter](https://github.com) Chrome extension's usage logic:
reads the `lastActiveOrg` cookie from your browser and polls
`GET /api/organizations/{orgId}/usage` on claude.ai using your existing browser session
(no API key, no login flow in the app itself — each user reads their own local cookies).

## Requirements

- macOS or Windows
- Python 3.9+
- Logged into claude.ai in a supported browser:
  - macOS: tries Opera, Chrome, Safari, Firefox (in that order)
  - Windows: tries Chrome, Edge, Brave, Firefox, Opera (in that order)
  - `usage_core.py` picks the first browser whose cookie store has a `lastActiveOrg`
    cookie for claude.ai — no manual config needed unless you use an unlisted browser.

## Setup

```bash
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Run the app for your platform:

```bash
# macOS — menu bar app (rumps)
python3 claude_usage_bar.py

# Windows — system tray app (pystray)
python3 claude_usage_tray_win.py
```

Both update every 60 seconds with the current session (5h window) and weekly
(7d window) usage percentages reported by claude.ai.

- macOS: the menu bar title shows `Session X% · Weekly X%` directly.
- Windows: tray icons can't show arbitrary text, so the icon itself is drawn
  with an abbreviated `S11/W1`-style label, and hovering shows the full
  `Session 11% · Weekly 1%` text as a tooltip.

## Notes

- macOS may prompt for Keychain access the first time it decrypts a browser's cookie
  store — this is required to read the session cookie.
- Windows may show a DPAPI/Keychain-equivalent prompt depending on the browser.
- If you see an error state, make sure you're logged into claude.ai in one of the
  supported browsers and have visited the site recently so the `lastActiveOrg`
  cookie is set.
