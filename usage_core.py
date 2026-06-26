"""Shared logic for fetching Claude.ai usage, ported from the claude-counter
Chrome extension: reads the lastActiveOrg cookie from the user's browser and
polls GET /api/organizations/{orgId}/usage with that browser's session cookies.

Used by both the macOS menubar app (claude_usage_bar.py, via rumps) and the
Windows tray app (claude_usage_tray_win.py, via pystray).
"""

import os
import platform

import browser_cookie3
import requests

USAGE_URL = "https://claude.ai/api/organizations/{org_id}/usage"

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0"
)

OPERA_MAC_COOKIE_FILE = os.path.expanduser(
    "~/Library/Application Support/com.operasoftware.Opera/Default/Cookies"
)


def _candidate_cookiejars():
    """Yield (name, cookiejar-factory) pairs to try, most-likely-first per OS."""
    system = platform.system()

    if system == "Darwin":
        yield "Opera", lambda: browser_cookie3.opera(
            cookie_file=OPERA_MAC_COOKIE_FILE, domain_name="claude.ai"
        )
        yield "Chrome", lambda: browser_cookie3.chrome(domain_name="claude.ai")
        yield "Safari", lambda: browser_cookie3.safari(domain_name="claude.ai")
        yield "Firefox", lambda: browser_cookie3.firefox(domain_name="claude.ai")
    elif system == "Windows":
        yield "Chrome", lambda: browser_cookie3.chrome(domain_name="claude.ai")
        yield "Edge", lambda: browser_cookie3.edge(domain_name="claude.ai")
        yield "Brave", lambda: browser_cookie3.brave(domain_name="claude.ai")
        yield "Firefox", lambda: browser_cookie3.firefox(domain_name="claude.ai")
        yield "Opera", lambda: browser_cookie3.opera(domain_name="claude.ai")
    else:
        yield "Chrome", lambda: browser_cookie3.chrome(domain_name="claude.ai")
        yield "Firefox", lambda: browser_cookie3.firefox(domain_name="claude.ai")


def get_cookiejar():
    """Try each known browser's cookie store until one has a lastActiveOrg cookie."""
    last_error = None
    for name, factory in _candidate_cookiejars():
        try:
            jar = factory()
        except Exception as exc:
            last_error = exc
            continue
        if get_org_id(jar):
            return jar
    if last_error:
        raise RuntimeError(f"Could not read browser cookies: {last_error}")
    raise RuntimeError("No claude.ai cookies found in any supported browser")


def get_org_id(cookiejar):
    for cookie in cookiejar:
        if cookie.name == "lastActiveOrg":
            return cookie.value
    return None


def fetch_usage():
    cookiejar = get_cookiejar()
    org_id = get_org_id(cookiejar)
    if not org_id:
        raise RuntimeError(
            "lastActiveOrg cookie not found — log into claude.ai in your browser first"
        )

    headers = {
        "User-Agent": _USER_AGENT,
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


def get_session_and_weekly():
    data = fetch_usage()
    session_pct = parse_window(data.get("five_hour"))
    weekly_pct = parse_window(data.get("seven_day"))
    return session_pct, weekly_pct
