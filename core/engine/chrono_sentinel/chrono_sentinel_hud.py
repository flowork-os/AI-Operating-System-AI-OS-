#!/usr/bin/env python3
"""
Flowork OS Sovereign Chrono Sentinel - Quantum Power & Sleep HUD
Native Pure Optical Crystal Glass Desktop Widget replacing legacy webview shutflow.
Anchored symmetrically at the Left Wing (X=38, Y=776) pairing with Quantum Tarot (X=2322, Y=776).
Rendered with 100% transparent zero-background ethereal design (samar-samar matching tarot).
"""

import sys
import math
import time
import subprocess
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import cairo

class ChronoSentinelHUD(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        self.set_title("Flowork Chrono Sentinel")
        self.set_wmclass("flowork-chrono-sentinel", "Flowork-Chrono-Sentinel")
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_below(True)
        self.stick()

        # Transparent RGBA visual
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        # Geometry: 240x230, baseline matched with Quantum Tarot at Y=776
        self.width = 240
        self.height = 230
        self.pos_x = 38
        self.pos_y = 776

        self.set_default_size(self.width, self.height)
        self.move(self.pos_x, self.pos_y)

        # State
        self.mode = "SHUTDOWN"  # "SHUTDOWN", "SLEEP", "RESTART"
        self.target_time = None
        self.total_duration = 0.0
        self.timer_active = False
        self.hover_btn = None
        self.is_hovered = False
        self.hover_blend = 0.0
        self.anim_phase = 0.0
        self.warned_60s = False

        # Hit testing button rects (x, y, w, h, id, text)
        self.buttons = []
        self._setup_buttons()

        # Events
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.connect("draw", self._on_draw)
        self.connect("motion-notify-event", self._on_motion)
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
        self.connect("button-press-event", self._on_click)

        # Screen size tracking
        screen.connect("size-changed", self._on_screen_changed)
        self._update_geometry()

        # Tick timer (every 50ms for smooth hover fade)
        GLib.timeout_add(50, self._on_tick)

    def _setup_buttons(self):
        # Mode selector chips: [ SHUTDOWN ] [ SLEEP ] [ RESTART ]
        mw = 66
        mh = 20
        my = 142
        start_mx = 14
        self.buttons = [
            {"id": "mode_shutdown", "type": "mode", "val": "SHUTDOWN", "rect": (start_mx, my, mw, mh), "label": "SHUTDOWN"},
            {"id": "mode_sleep", "type": "mode", "val": "SLEEP", "rect": (start_mx + mw + 6, my, mw - 6, mh), "label": "SLEEP"},
            {"id": "mode_restart", "type": "mode", "val": "RESTART", "rect": (start_mx + 2*mw + 6, my, mw + 2, mh), "label": "RESTART"},
        ]

        # Preset pills: [ +15m ] [ +30m ] [ +1h ] [ ABORT ]
        pw = 48
        ph = 20
        py = 170
        start_px = 14
        gap_p = 7
        self.buttons.extend([
            {"id": "preset_15", "type": "preset", "val": 15 * 60, "rect": (start_px, py, pw, ph), "label": "+15m"},
            {"id": "preset_30", "type": "preset", "val": 30 * 60, "rect": (start_px + pw + gap_p, py, pw, ph), "label": "+30m"},
            {"id": "preset_60", "type": "preset", "val": 60 * 60, "rect": (start_px + 2*(pw + gap_p), py, pw, ph), "label": "+1h"},
            {"id": "preset_abort", "type": "abort", "val": 0, "rect": (start_px + 3*(pw + gap_p), py, pw, ph), "label": "ABORT"},
        ])

    def _update_geometry(self):
        screen = self.get_screen()
        sw = screen.get_width()
        sh = screen.get_height()
        self.pos_x = 38
        self.pos_y = max(120, sh - self.height - 74)
        self.move(self.pos_x, self.pos_y)
        self._ensure_above_wallpaper()

    def _ensure_above_wallpaper(self):
        """Keep HUD strictly above DESKTOP wallpaper while staying below normal app windows."""
        try:
            screen = Gdk.Screen.get_default()
            my_win = self.get_window()
            if not screen or not my_win:
                return
            stack = screen.get_window_stack()
            if not stack:
                return
            my_xid = my_win.get_xid()
            my_idx = -1
            ambient_win = None
            ambient_idx = -1
            for i, w in enumerate(stack):
                xid = w.get_xid()
                if xid == my_xid:
                    my_idx = i
                elif w.get_type_hint() == Gdk.WindowTypeHint.DESKTOP:
                    ambient_win = w
                    ambient_idx = i
            if ambient_win is not None and my_idx != -1 and my_idx < ambient_idx:
                my_win.restack(ambient_win, True)
        except Exception:
            pass

    def _on_screen_changed(self, screen):
        self._update_geometry()
        self.queue_draw()

    def _on_enter(self, widget, event):
        self.is_hovered = True
        self.queue_draw()
        return True

    def _on_leave(self, widget, event):
        self.is_hovered = False
        self.hover_btn = None
        self.queue_draw()
        return True

    def _on_motion(self, widget, event):
        x, y = event.x, event.y
        self.is_hovered = True
        old_hover = self.hover_btn
        self.hover_btn = None
        for b in self.buttons:
            bx, by, bw, bh = b["rect"]
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.hover_btn = b["id"]
                break
        if self.hover_btn != old_hover:
            self.queue_draw()
        return True

    def _on_click(self, widget, event):
        if event.button != 1:
            return False
        x, y = event.x, event.y

        # Check button clicks
        for b in self.buttons:
            bx, by, bw, bh = b["rect"]
            if bx <= x <= bx + bw and by <= y <= by + bh:
                btype = b["type"]
                if btype == "mode":
                    self.mode = b["val"]
                    self.queue_draw()
                elif btype == "preset":
                    self._add_duration(b["val"])
                elif btype == "abort":
                    self._abort_timer()
                return True

        # Check dial center click (toggle / abort / quick +15m)
        cx_dial = self.width / 2.0
        cy_dial = 78.0
        dist = math.hypot(x - cx_dial, y - cy_dial)
        if dist <= 46.0:
            if not self.timer_active:
                self._add_duration(30 * 60)
            else:
                self._abort_timer()
            return True

        return True

    def _add_duration(self, seconds: int):
        now = time.time()
        if not self.timer_active or self.target_time is None or self.target_time <= now:
            self.total_duration = float(seconds)
            self.target_time = now + self.total_duration
            self.timer_active = True
        else:
            remaining = self.target_time - now
            self.total_duration = remaining + float(seconds)
            self.target_time = now + self.total_duration

        self.warned_60s = False
        m = int(self.total_duration // 60)
        self._notify("Chrono Sentinel", f"Timer {self.mode} disetel ke {m} menit.", "system-shutdown")
        self.queue_draw()

    def _abort_timer(self):
        if self.timer_active:
            self.timer_active = False
            self.target_time = None
            self.total_duration = 0.0
            self._notify("Chrono Sentinel", f"Timer {self.mode} dibatalkan.", "dialog-information")
            self.queue_draw()

    def _notify(self, title: str, msg: str, icon: str):
        try:
            subprocess.Popen(["notify-send", title, msg, "-i", icon, "-a", "Chrono Sentinel", "-t", "4000"])
        except Exception:
            pass

    def _on_tick(self):
        self.anim_phase += 0.08
        self.tick_count = getattr(self, "tick_count", 0) + 1
        if self.tick_count % 20 == 0:
            self._ensure_above_wallpaper()
        target_blend = 1.0 if (self.is_hovered or self.timer_active) else 0.0
        self.hover_blend += (target_blend - self.hover_blend) * 0.20

        if self.timer_active and self.target_time:
            now = time.time()
            rem = self.target_time - now
            if rem <= 60 and not self.warned_60s and rem > 0:
                self.warned_60s = True
                self._notify("Chrono Sentinel", f"Peringatan: Sistem akan {self.mode} dalam 60 detik!", "dialog-warning")
            elif rem <= 0:
                self.timer_active = False
                self._trigger_power_action()
        self.queue_draw()
        return True

    def _trigger_power_action(self):
        self._notify("Chrono Sentinel", f"Waktu habis! Menjalankan {self.mode}...", "system-shutdown")
        try:
            if self.mode == "SHUTDOWN":
                subprocess.Popen(["systemctl", "poweroff"])
            elif self.mode == "SLEEP":
                subprocess.Popen(["systemctl", "suspend"])
            elif self.mode == "RESTART":
                subprocess.Popen(["systemctl", "reboot"])
        except Exception as e:
            self._notify("Chrono Sentinel Error", f"Gagal mengeksekusi {self.mode}: {e}", "dialog-error")

    def _on_draw(self, widget, cr: cairo.Context):
        w, h = self.width, self.height

        # 100% PURE TRANSPARENT ZERO-BACKGROUND (NO CARD BOX, NO OBSIDIAN FILL)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # Stealth ambient alpha matching Tarot (0.42 idle -> 0.98 hover)
        alpha = 0.42 + 0.56 * self.hover_blend

        # 1. Floating Ethereal Header
        cr.select_font_face("JetBrains Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(10.5)
        cr.set_source_rgba(0.0, 0.95, 1.0, 0.90 * alpha)
        cr.move_to(20, 24)
        cr.show_text("CHRONO SENTINEL")

        # Status pulse dot
        dot_r = 3.6 + 0.6 * math.sin(self.anim_phase * 2)
        cr.arc(w - 24, 20, dot_r, 0, 2*math.pi)
        if self.timer_active:
            cr.set_source_rgba(1.0, 0.45, 0.15, 0.95 * alpha)
        else:
            cr.set_source_rgba(0.0, 1.0, 0.45, 0.85 * alpha)
        cr.fill()

        # 2. Circular Progress Arc Dial
        cx_dial = w / 2.0
        cy_dial = 78.0
        r_dial = 38.0

        # Dial subtle background track
        start_angle = -math.pi * 1.25
        end_angle = math.pi * 0.25
        total_sweep = 1.5 * math.pi

        cr.arc(cx_dial, cy_dial, r_dial, start_angle, end_angle)
        cr.set_source_rgba(0.0, 0.95, 1.0, 0.18 * alpha)
        cr.set_line_width(3.2)
        cr.stroke()

        # Progress Arc
        ratio = 0.0
        display_str = "STANDBY"
        if self.timer_active and self.target_time and self.total_duration > 0:
            rem = max(0.0, self.target_time - time.time())
            ratio = max(0.0, min(1.0, rem / self.total_duration))
            hrs = int(rem // 3600)
            mins = int((rem % 3600) // 60)
            secs = int(rem % 60)
            display_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        if ratio > 0.0:
            arc_cur = start_angle + ratio * total_sweep
            cr.arc(cx_dial, cy_dial, r_dial, start_angle, arc_cur)
            prog_pat = cairo.LinearGradient(cx_dial - r_dial, cy_dial, cx_dial + r_dial, cy_dial)
            prog_pat.add_color_stop_rgba(0.0, 0.0, 0.95, 1.0, 0.95 * alpha)
            prog_pat.add_color_stop_rgba(1.0, 1.0, 0.45, 0.15, 0.95 * alpha)
            cr.set_source(prog_pat)
            cr.set_line_width(3.8)
            cr.stroke()

        # Countdown / Status Text Inside Dial
        cr.select_font_face("JetBrains Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(13.0)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * alpha)
        ext = cr.text_extents(display_str)
        cr.move_to(cx_dial - ext.width/2.0, cy_dial + 3.0)
        cr.show_text(display_str)

        # Mode Subtitle inside Dial
        sub_str = f"{self.mode} ARMED" if self.timer_active else f"{self.mode} READY"
        cr.set_font_size(7.5)
        if self.timer_active:
            cr.set_source_rgba(1.0, 0.6, 0.2, 0.95 * alpha)
        else:
            cr.set_source_rgba(0.0, 0.95, 1.0, 0.75 * alpha)
        sub_ext = cr.text_extents(sub_str)
        cr.move_to(cx_dial - sub_ext.width/2.0, cy_dial + 16.0)
        cr.show_text(sub_str)

        # 3. Mode Selector Buttons (Ethereal Glass Outline Pills)
        r_btn = 6.0
        for b in self.buttons:
            if b["type"] != "mode":
                continue
            bx, by, bw, bh = b["rect"]
            is_active = (self.mode == b["val"])
            is_hover = (self.hover_btn == b["id"])

            # Rounded pill path
            cr.new_sub_path()
            cr.arc(bx + bw - r_btn, by + r_btn, r_btn, -math.pi/2, 0)
            cr.arc(bx + bw - r_btn, by + bh - r_btn, r_btn, 0, math.pi/2)
            cr.arc(bx + r_btn, by + bh - r_btn, r_btn, math.pi/2, math.pi)
            cr.arc(bx + r_btn, by + r_btn, r_btn, math.pi, 3*math.pi/2)
            cr.close_path()

            if is_active:
                cr.set_source_rgba(1.0, 0.45, 0.15, 0.22 * alpha if not is_hover else 0.35 * alpha)
                cr.fill_preserve()
                cr.set_source_rgba(1.0, 0.60, 0.25, 0.85 * alpha)
                cr.set_line_width(1.0)
                cr.stroke()
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.98 * alpha)
            else:
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.05 * alpha if not is_hover else 0.15 * alpha)
                cr.fill_preserve()
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.25 * alpha if not is_hover else 0.65 * alpha)
                cr.set_line_width(0.8)
                cr.stroke()
                cr.set_source_rgba(0.7, 0.85, 0.95, 0.70 * alpha if not is_hover else 0.98 * alpha)

            cr.set_font_size(7.0)
            lext = cr.text_extents(b["label"])
            cr.move_to(bx + (bw - lext.width)/2.0, by + (bh + lext.height)/2.0 - 1.0)
            cr.show_text(b["label"])

        # 4. Preset Pills & Abort (Ethereal Glass Outline Pills)
        for b in self.buttons:
            if b["type"] not in ("preset", "abort"):
                continue
            bx, by, bw, bh = b["rect"]
            is_abort = (b["type"] == "abort")
            is_hover = (self.hover_btn == b["id"])

            cr.new_sub_path()
            cr.arc(bx + bw - r_btn, by + r_btn, r_btn, -math.pi/2, 0)
            cr.arc(bx + bw - r_btn, by + bh - r_btn, r_btn, 0, math.pi/2)
            cr.arc(bx + r_btn, by + bh - r_btn, r_btn, math.pi/2, math.pi)
            cr.arc(bx + r_btn, by + r_btn, r_btn, math.pi, 3*math.pi/2)
            cr.close_path()

            if is_abort:
                cr.set_source_rgba(1.0, 0.15, 0.2, 0.18 * alpha if not is_hover else 0.35 * alpha)
                cr.fill_preserve()
                cr.set_source_rgba(1.0, 0.3, 0.3, 0.55 * alpha if not is_hover else 0.90 * alpha)
                cr.set_line_width(1.0)
                cr.stroke()
                cr.set_source_rgba(1.0, 0.55, 0.55, 0.85 * alpha if not is_hover else 1.0)
            else:
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.05 * alpha if not is_hover else 0.15 * alpha)
                cr.fill_preserve()
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.25 * alpha if not is_hover else 0.65 * alpha)
                cr.set_line_width(0.8)
                cr.stroke()
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.80 * alpha if not is_hover else 1.0)

            cr.set_font_size(7.5)
            lext = cr.text_extents(b["label"])
            cr.move_to(bx + (bw - lext.width)/2.0, by + (bh + lext.height)/2.0 - 1.0)
            cr.show_text(b["label"])

        # 5. Bottom Footnote Indicator
        cr.set_font_size(7.2)
        cr.set_source_rgba(0.45, 0.7, 0.85, 0.60 * alpha)
        foot_str = "● ACTIVE TIMER" if self.timer_active else "IDLE SENSING: ACTIVE"
        fext = cr.text_extents(foot_str)
        cr.move_to(w/2.0 - fext.width/2.0, h - 14)
        cr.show_text(foot_str)

        return True

def main():
    app = ChronoSentinelHUD()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
