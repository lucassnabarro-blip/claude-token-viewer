#!/usr/bin/env python3
"""Windows system-tray app showing Claude.ai session/weekly usage.

Windows tray icons can't display arbitrary text like the macOS menu bar can,
so the percentage is rendered onto the icon image itself (e.g. "S11/W1"),
and the full "Session 11% · Weekly 1%" string is shown as the hover tooltip.
See usage_core.py for the shared fetch logic (ported from the claude-counter
Chrome extension).
"""

import threading
import time

from PIL import Image, ImageDraw, ImageFont
import pystray

from usage_core import get_session_and_weekly

REFRESH_SECONDS = 60
ICON_SIZE = 64


def _load_font(size):
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_icon_image(session_str, weekly_str, error=False):
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg = (200, 50, 50, 255) if error else (44, 132, 219, 255)
    draw.rounded_rectangle((2, 2, ICON_SIZE - 2, ICON_SIZE - 2), radius=14, fill=bg)

    font = _load_font(18)
    top = "ERR" if error else f"S{session_str}"
    bottom = "" if error else f"W{weekly_str}"

    draw.text((ICON_SIZE / 2, 20), top, font=font, fill="white", anchor="mm")
    if bottom:
        draw.text((ICON_SIZE / 2, 44), bottom, font=font, fill="white", anchor="mm")

    return img


class ClaudeUsageTray:
    def __init__(self):
        self.icon = pystray.Icon(
            "claude-usage",
            icon=make_icon_image("…", ""),
            title="Claude Usage: loading…",
            menu=pystray.Menu(
                pystray.MenuItem("Refresh now", self.refresh_now),
                pystray.MenuItem("Quit", self.quit),
            ),
        )
        self._stop = threading.Event()

    def refresh_now(self, _icon=None, _item=None):
        self.refresh()

    def refresh(self):
        try:
            session_pct, weekly_pct = get_session_and_weekly()
        except Exception as exc:
            self.icon.icon = make_icon_image("", "", error=True)
            self.icon.title = "Claude Usage: error — see console"
            print(f"refresh failed: {exc}")
            return

        session_str = f"{session_pct:.0f}%" if session_pct is not None else "—"
        weekly_str = f"{weekly_pct:.0f}%" if weekly_pct is not None else "—"

        self.icon.icon = make_icon_image(session_str, weekly_str)
        self.icon.title = f"Session {session_str} · Weekly {weekly_str}"

    def _poll_loop(self):
        while not self._stop.is_set():
            self.refresh()
            self._stop.wait(REFRESH_SECONDS)

    def quit(self, _icon=None, _item=None):
        self._stop.set()
        self.icon.stop()

    def run(self):
        threading.Thread(target=self._poll_loop, daemon=True).start()
        self.icon.run()


if __name__ == "__main__":
    ClaudeUsageTray().run()
