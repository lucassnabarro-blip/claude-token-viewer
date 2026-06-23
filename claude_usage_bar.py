#!/usr/bin/env python3
"""Menubar app showing Claude.ai session/weekly usage, ported from claude-counter
(Chrome extension) logic: reads the lastActiveOrg cookie and polls
GET /api/organizations/{orgId}/usage with the browser's session cookies."""

import os

import rumps
import browser_cookie3
import requests

USAGE_URL = "https://claude.ai/api/organizations/{org_id}/usage"
REFRESH_SECONDS = 60


OPERA_COOKIE_FILE = os.path.expanduser(
    "~/Library/Application Support/com.operasoftware.Opera/Default/Cookies"
)


def get_cookiejar():
    return browser_cookie3.opera(cookie_file=OPERA_COOKIE_FILE, domain_name="claude.ai")


def get_org_id(cookiejar):
    for cookie in cookiejar:
        if cookie.name == "lastActiveOrg":
            return cookie.value
    return None


def fetch_usage():
    cookiejar = get_cookiejar()
    org_id = get_org_id(cookiejar)
    if not org_id:
        raise RuntimeError("lastActiveOrg cookie not found — log into claude.ai in Opera first")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://claude.ai/",
        "Origin": "https://claude.ai",
    }
    resp = requests.get(
        USAGE_URL.format(org_id=org_id),
        cookies=cookiejar,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def parse_window(window):
    if not window or "utilization" not in window:
        return None
    utilization = window["utilization"]
    if not isinstance(utilization, (int, float)):
        return None
    return max(0, min(100, utilization))


class ClaudeUsageApp(rumps.App):
    def __init__(self):
        super().__init__("Claude Usage", title="Claude: …")
        self.session_item = rumps.MenuItem("Session: —")
        self.weekly_item = rumps.MenuItem("Weekly: —")
        self.error_item = rumps.MenuItem("")
        self.menu = [
            self.session_item,
            self.weekly_item,
            None,
            rumps.MenuItem("Refresh now", callback=self.refresh_now),
        ]
        self.timer = rumps.Timer(self.refresh, REFRESH_SECONDS)
        self.timer.start()
        self.refresh(None)

    def refresh_now(self, _):
        self.refresh(None)

    def refresh(self, _):
        try:
            data = fetch_usage()
        except Exception as exc:
            self.title = "Claude: ⚠️"
            self.session_item.title = "Session: error"
            self.weekly_item.title = "Weekly: error"
            print(f"refresh failed: {exc}")
            return

        session_pct = parse_window(data.get("five_hour"))
        weekly_pct = parse_window(data.get("seven_day"))

        session_str = f"{session_pct:.0f}%" if session_pct is not None else "—"
        weekly_str = f"{weekly_pct:.0f}%" if weekly_pct is not None else "—"

        self.title = f"Session {session_str} · Weekly {weekly_str}"
        self.session_item.title = f"Session: {session_str}"
        self.weekly_item.title = f"Weekly: {weekly_str}"


if __name__ == "__main__":
    ClaudeUsageApp().run()
