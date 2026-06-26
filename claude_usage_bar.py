#!/usr/bin/env python3
"""macOS menubar app showing Claude.ai session/weekly usage. See usage_core.py
for the shared fetch logic (ported from the claude-counter Chrome extension)."""

import rumps

from usage_core import get_session_and_weekly

REFRESH_SECONDS = 60


class ClaudeUsageApp(rumps.App):
    def __init__(self):
        super().__init__("Claude Usage", title="Claude: …")
        self.session_item = rumps.MenuItem("Session: —")
        self.weekly_item = rumps.MenuItem("Weekly: —")
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
            session_pct, weekly_pct = get_session_and_weekly()
        except Exception as exc:
            self.title = "Claude: ⚠️"
            self.session_item.title = "Session: error"
            self.weekly_item.title = "Weekly: error"
            print(f"refresh failed: {exc}")
            return

        session_str = f"{session_pct:.0f}%" if session_pct is not None else "—"
        weekly_str = f"{weekly_pct:.0f}%" if weekly_pct is not None else "—"

        self.title = f"Session {session_str} · Weekly {weekly_str}"
        self.session_item.title = f"Session: {session_str}"
        self.weekly_item.title = f"Weekly: {weekly_str}"


if __name__ == "__main__":
    ClaudeUsageApp().run()
