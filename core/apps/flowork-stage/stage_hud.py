#!/usr/bin/env python3
"""
Flowork Live Stage - Floating Control Pill (Phase 4)
Runs on host display (:0) as a compact always-on-top glass pill allowing
1-click Pause / Take Over, Resume AI (with auto re-sync), and Stop Stage.
"""

import json
import os
import socket
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

STAGE_SOCK = "/tmp/flowork-stage.sock"


def ipc_call(req: dict) -> dict:
    if not os.path.exists(STAGE_SOCK):
        return {"ok": False, "error": "Stage not running"}
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(STAGE_SOCK)
        s.sendall((json.dumps(req) + "\n").encode("utf-8"))
        data = s.recv(4096).decode("utf-8", errors="ignore").strip()
        s.close()
        return json.loads(data) if data else {"ok": False}
    except Exception as e:
        return {"ok": False, "error": str(e)}


class StageHudPill(Gtk.Window):
    def __init__(self):
        super().__init__(title="Flowork Stage Control")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_resizable(False)

        css = Gtk.CssProvider()
        css.load_from_data(
            b"""
            window {
                background-color: rgba(12, 18, 28, 0.94);
                border: 1px solid rgba(0, 225, 255, 0.55);
                border-radius: 12px;
            }
            label.status-ai {
                color: #00e5ff;
                font-weight: bold;
                font-size: 12px;
            }
            label.status-user {
                color: #ffb300;
                font-weight: bold;
                font-size: 12px;
            }
            button.toggle-ai {
                background: #00b8d4;
                color: #081018;
                font-weight: bold;
                border-radius: 8px;
                padding: 4px 12px;
                border: none;
            }
            button.toggle-user {
                background: #ffb300;
                color: #181004;
                font-weight: bold;
                border-radius: 8px;
                padding: 4px 12px;
                border: none;
            }
            button.stop-btn {
                background: rgba(255, 70, 90, 0.22);
                color: #ff6b7a;
                font-weight: bold;
                border-radius: 8px;
                padding: 4px 9px;
                border: 1px solid rgba(255, 70, 90, 0.45);
            }
            """
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(7)
        box.set_margin_bottom(7)
        box.set_margin_start(12)
        box.set_margin_end(10)

        self.status_lbl = Gtk.Label(label="AI CO-PILOT ACTIVE")
        self.status_lbl.get_style_context().add_class("status-ai")

        self.toggle_btn = Gtk.Button(label="Pause / Take Over")
        self.toggle_btn.get_style_context().add_class("toggle-ai")
        self.toggle_btn.connect("clicked", self.on_toggle)

        self.stop_btn = Gtk.Button(label="Stop")
        self.stop_btn.get_style_context().add_class("stop-btn")
        self.stop_btn.connect("clicked", self.on_stop)

        box.pack_start(self.status_lbl, False, False, 0)
        box.pack_start(self.toggle_btn, False, False, 0)
        box.pack_start(self.stop_btn, False, False, 0)
        self.add(box)

        # Allow dragging the pill anywhere
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_drag)

        # Position top-center of primary screen
        display = Gdk.Display.get_default()
        mon = display.get_primary_monitor() or display.get_monitor(0)
        geo = mon.get_geometry()
        self.move(geo.x + (geo.width // 2) - 170, geo.y + 14)

        GLib.timeout_add(400, self.poll_status)

    def on_drag(self, widget, event):
        if event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def on_toggle(self, btn):
        ipc_call({"action": "toggle"})
        self.poll_status()

    def on_stop(self, btn):
        ipc_call({"action": "stop"})
        Gtk.main_quit()

    def poll_status(self):
        res = ipc_call({"action": "status"})
        if not res.get("ok"):
            Gtk.main_quit()
            return False
        mode = res.get("mode", "AI_ACTIVE")
        ctx_lbl = self.status_lbl.get_style_context()
        ctx_btn = self.toggle_btn.get_style_context()
        if mode == "PAUSED_USER_TAKEOVER":
            self.status_lbl.set_text("USER TAKEOVER")
            ctx_lbl.remove_class("status-ai")
            ctx_lbl.add_class("status-user")
            self.toggle_btn.set_label("Resume AI")
            ctx_btn.remove_class("toggle-ai")
            ctx_btn.add_class("toggle-user")
        else:
            self.status_lbl.set_text("AI CO-PILOT ACTIVE")
            ctx_lbl.remove_class("status-user")
            ctx_lbl.add_class("status-ai")
            self.toggle_btn.set_label("Pause / Take Over")
            ctx_btn.remove_class("toggle-user")
            ctx_btn.add_class("toggle-ai")
        return True


def main():
    win = StageHudPill()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
