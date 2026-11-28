#!/usr/bin/env python3
"""
Flowork Live Stage - Ghost Cursor & Target Highlight Overlay (Phase 2)
Runs on the isolated Virtual Stage display (e.g. :99) as a 60fps click-through
RGBA Cairo overlay rendering smooth cursor glides, bounding-box highlights,
click ripples, and live AI/User Takeover status badges.
"""

import json
import math
import os
import socket
import sys
import threading
import time

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

SOCK_PATH = os.environ.get("FLOWORK_GHOST_SOCK", "/tmp/flowork-ghost.sock")


class GhostOverlay(Gtk.Window):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.stage_w = width
        self.stage_h = height

        self.set_title("Flowork Ghost Overlay")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_default_size(width, height)
        self.move(0, 0)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)

        self.connect("draw", self.on_draw)
        self.connect("realize", self.on_realize)

        # Animation & visual state
        self.lock = threading.Lock()
        self.cursor_x = width / 2.0
        self.cursor_y = height / 2.0
        self.start_x = self.cursor_x
        self.start_y = self.cursor_y
        self.target_x = self.cursor_x
        self.target_y = self.cursor_y
        self.move_start_t = 0.0
        self.move_duration = 0.22

        self.highlight_box = None  # (x, y, w, h, timestamp)
        self.action_label = ""
        self.label_time = 0.0
        self.ripples = []  # list of (x, y, start_t)
        self.mode = "AI_ACTIVE"  # AI_ACTIVE | PAUSED_USER_TAKEOVER
        self.status_text = "AI CO-PILOT READY"

        # 60fps animation tick
        GLib.timeout_add(16, self.on_tick)

    def on_realize(self, widget):
        # Make window 100% click-through
        gdk_win = self.get_window()
        if gdk_win:
            gdk_win.input_shape_combine_region(cairo.Region(), 0, 0)
            gdk_win.set_override_redirect(True)

    def handle_command(self, cmd: dict):
        now = time.monotonic()
        action = cmd.get("cmd", "")
        with self.lock:
            if action == "move":
                self.start_x = self.cursor_x
                self.start_y = self.cursor_y
                self.target_x = float(cmd.get("x", self.cursor_x))
                self.target_y = float(cmd.get("y", self.cursor_y))
                self.move_start_t = now
                self.move_duration = max(0.08, float(cmd.get("duration", 0.22)))
                if "label" in cmd and cmd["label"]:
                    self.action_label = str(cmd["label"])[:48]
                    self.label_time = now
            elif action == "highlight":
                x = float(cmd.get("x", 0))
                y = float(cmd.get("y", 0))
                w = float(cmd.get("w", 40))
                h = float(cmd.get("h", 24))
                self.highlight_box = (x, y, w, h, now)
                if "label" in cmd and cmd["label"]:
                    self.action_label = str(cmd["label"])[:48]
                    self.label_time = now
            elif action == "click":
                cx = float(cmd.get("x", self.cursor_x))
                cy = float(cmd.get("y", self.cursor_y))
                self.cursor_x = cx
                self.cursor_y = cy
                self.target_x = cx
                self.target_y = cy
                self.ripples.append((cx, cy, now))
                if "label" in cmd and cmd["label"]:
                    self.action_label = str(cmd["label"])[:48]
                    self.label_time = now
            elif action == "type":
                if "x" in cmd and "y" in cmd:
                    self.cursor_x = float(cmd["x"])
                    self.cursor_y = float(cmd["y"])
                    self.target_x = self.cursor_x
                    self.target_y = self.cursor_y
                txt = str(cmd.get("text", ""))
                preview = txt if len(txt) <= 28 else txt[:25] + "..."
                self.action_label = f"Typing: {preview}"
                self.label_time = now
            elif action == "mode":
                self.mode = cmd.get("mode", "AI_ACTIVE")
                self.status_text = str(cmd.get("status", self.mode))[:48]
            elif action == "clear":
                self.highlight_box = None
                self.action_label = ""

    def on_tick(self):
        now = time.monotonic()
        with self.lock:
            # Smooth cubic ease-out cursor interpolation
            if self.move_start_t > 0:
                t = (now - self.move_start_t) / self.move_duration
                if t >= 1.0:
                    self.cursor_x = self.target_x
                    self.cursor_y = self.target_y
                    self.move_start_t = 0.0
                else:
                    ease = 1.0 - pow(1.0 - t, 3)
                    self.cursor_x = self.start_x + (self.target_x - self.start_x) * ease
                    self.cursor_y = self.start_y + (self.target_y - self.start_y) * ease

            # Prune expired ripples (> 0.55s)
            self.ripples = [(rx, ry, rt) for (rx, ry, rt) in self.ripples if now - rt < 0.55]

            # Auto-fade highlight after 2.5s
            if self.highlight_box and (now - self.highlight_box[4] > 2.5):
                self.highlight_box = None

            # Auto-fade action label after 2.5s
            if self.action_label and (now - self.label_time > 2.5):
                self.action_label = ""

        self.queue_draw()
        return True

    def _rounded_rect(self, cr, x, y, w, h, r):
        r = min(r, w / 2.0, h / 2.0)
        cr.new_sub_path()
        cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        cr.close_path()

    def on_draw(self, widget, cr):
        now = time.monotonic()
        # Clear to full transparency
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        with self.lock:
            cx, cy = self.cursor_x, self.cursor_y
            hbox = self.highlight_box
            label = self.action_label
            ripples = list(self.ripples)
            mode = self.mode
            status_text = self.status_text

        # 1. Draw Target Bounding Box Highlight
        if hbox is not None:
            hx, hy, hw, hh, ht = hbox
            age = now - ht
            alpha = max(0.0, min(1.0, 1.0 - max(0.0, age - 1.8) / 0.7))
            pad = 4.0
            # Outer glow
            self._rounded_rect(cr, hx - pad, hy - pad, hw + pad * 2, hh + pad * 2, 6.0)
            cr.set_source_rgba(0.0, 0.88, 1.0, 0.14 * alpha)
            cr.fill_preserve()
            cr.set_line_width(2.0)
            cr.set_source_rgba(0.0, 0.92, 1.0, 0.90 * alpha)
            cr.stroke()

        # 2. Draw Click Ripples
        for rx, ry, rt in ripples:
            p = (now - rt) / 0.55
            radius = 6.0 + p * 34.0
            alpha = (1.0 - p) * 0.85
            cr.arc(rx, ry, radius, 0, 2 * math.pi)
            cr.set_line_width(2.5 * (1.0 - p * 0.5))
            cr.set_source_rgba(0.0, 0.95, 0.85, alpha)
            cr.stroke()

        # 3. Draw Ghost Cursor (only prominent in AI_ACTIVE mode)
        if mode == "AI_ACTIVE":
            # Soft cyan halo
            cr.arc(cx, cy, 14, 0, 2 * math.pi)
            cr.set_source_rgba(0.0, 0.88, 1.0, 0.18)
            cr.fill()

            # Crisp vector pointer
            cr.save()
            cr.translate(cx, cy)
            cr.move_to(0, 0)
            cr.line_to(0, 20)
            cr.line_to(5.5, 15.5)
            cr.line_to(10.5, 23)
            cr.line_to(13.5, 21.5)
            cr.line_to(8.5, 14)
            cr.line_to(15, 13.5)
            cr.close_path()
            cr.set_source_rgba(0.0, 0.92, 1.0, 0.95)
            cr.fill_preserve()
            cr.set_line_width(1.5)
            cr.set_source_rgba(0.04, 0.08, 0.14, 0.95)
            cr.stroke()
            cr.restore()

            # Action label pill next to cursor
            if label:
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.set_font_size(12.0)
                ext = cr.text_extents(label)
                pw = ext.width + 18
                ph = 24
                px = min(self.stage_w - pw - 10, cx + 18)
                py = min(self.stage_h - ph - 10, cy + 18)
                self._rounded_rect(cr, px, py, pw, ph, 6.0)
                cr.set_source_rgba(0.05, 0.09, 0.15, 0.88)
                cr.fill_preserve()
                cr.set_line_width(1.2)
                cr.set_source_rgba(0.0, 0.88, 1.0, 0.75)
                cr.stroke()
                cr.set_source_rgba(0.92, 0.98, 1.0, 0.98)
                cr.move_to(px + 9, py + 16)
                cr.show_text(label)

        # 4. Top-Right Stage Mode Badge
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(11.5)
        badge_text = f"  {status_text}  "
        ext = cr.text_extents(badge_text)
        bw = ext.width + 22
        bh = 26
        bx = self.stage_w - bw - 14
        by = 12
        self._rounded_rect(cr, bx, by, bw, bh, 13.0)
        if mode == "PAUSED_USER_TAKEOVER":
            cr.set_source_rgba(0.18, 0.10, 0.02, 0.90)
            cr.fill_preserve()
            cr.set_line_width(1.5)
            cr.set_source_rgba(1.0, 0.68, 0.0, 0.95)
            cr.stroke()
            # Amber dot
            cr.arc(bx + 13, by + bh / 2.0, 4.5, 0, 2 * math.pi)
            cr.set_source_rgba(1.0, 0.72, 0.0, 1.0)
            cr.fill()
        else:
            cr.set_source_rgba(0.03, 0.09, 0.14, 0.86)
            cr.fill_preserve()
            cr.set_line_width(1.5)
            cr.set_source_rgba(0.0, 0.88, 1.0, 0.85)
            cr.stroke()
            # Cyan dot
            cr.arc(bx + 13, by + bh / 2.0, 4.5, 0, 2 * math.pi)
            cr.set_source_rgba(0.0, 0.95, 0.85, 1.0)
            cr.fill()

        cr.set_source_rgba(0.95, 0.98, 1.0, 0.98)
        cr.move_to(bx + 20, by + 17)
        cr.show_text(badge_text.strip())


def socket_server(overlay: GhostOverlay):
    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCK_PATH)
    os.chmod(SOCK_PATH, 0o666)
    srv.listen(16)
    while True:
        conn, _ = srv.accept()
        try:
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            for line in data.decode("utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    cmd = json.loads(line)
                    overlay.handle_command(cmd)
                except json.JSONDecodeError:
                    pass
        finally:
            conn.close()


def main():
    w = int(os.environ.get("FLOWORK_STAGE_W", "1280"))
    h = int(os.environ.get("FLOWORK_STAGE_H", "720"))
    overlay = GhostOverlay(w, h)
    t = threading.Thread(target=socket_server, args=(overlay,), daemon=True)
    t.start()
    overlay.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
