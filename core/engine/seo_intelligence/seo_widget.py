#!/usr/bin/env python3
# ==============================================================================
# 👑 FLOWORK OS — SOVEREIGN OMNI-SEARCH SEO RADAR & MULTI-INTELLIGENCE HUD
# 100% Native Python Engine, Zero Paid APIs, Zero Cloud Worker Dependencies
# Seamless Optical Crystal Glass Docked in Top Panel (Y=3, H=34 -> H=315)
# Supported Modes:
#   1. KEYWORD RESEARCH (Search Volume, Difficulty, CPC, Google & YouTube Ideas)
#   2. DOMAIN & BACKLINK AUDIT (Link Graph, DoFollow Ratio, On-Page, RDAP, Subdomains)
#   3. YOUTUBE SEO DEEPSCAN (Title, Views, Monetization, Secret Tags, Ad Breaks)
# ==============================================================================

import os
import sys
import math
import json
import subprocess
import threading
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import cairo

OMNI_ENGINE = "/opt/floworkos/engine/seo_intelligence/seo_intel.py"

SCREEN_W = 2560
SCREEN_H = 1080

COLLAPSED_W = 580
COLLAPSED_H = 34
COLLAPSED_X = (SCREEN_W - COLLAPSED_W) // 2   # 990
COLLAPSED_Y = 3

EXPANDED_W  = 1260
EXPANDED_H  = 315
EXPANDED_X  = (SCREEN_W - EXPANDED_W) // 2    # 650
EXPANDED_Y  = 3

# High-Voltage Cyber & Razor Matrix Palette
C_GREEN  = (0.00, 1.00, 0.40)     # Neon Matrix Green (#00ff66)
C_CYAN   = (0.00, 0.95, 1.00)     # Electric Cyan (#00f2fe)
C_AMBER  = (1.00, 0.75, 0.20)     # Amber (#ffbf33)
C_PURPLE = (0.75, 0.50, 1.00)     # Purple (#c084fc)
C_RED    = (1.00, 0.35, 0.35)     # Red (#ff5959)
C_WHITE  = (1.00, 1.00, 1.00)
C_MUTED  = (0.65, 0.78, 0.88)
C_DARK   = (0.01, 0.03, 0.06)

def draw_rounded_rect(cr, x, y, w, h, r):
    cr.new_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()

try:
    import ctypes
    x11 = ctypes.cdll.LoadLibrary("libX11.so.6")
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    x11.XRaiseWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XFlush.argtypes = [ctypes.c_void_p]
    _X11_DISPLAY = x11.XOpenDisplay(None)
except Exception:
    x11 = None
    _X11_DISPLAY = None


class OmniSeoWidgetWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        self.set_title("Flowork Omni SEO Radar")
        self.set_wmclass("flowork-seo-widget", "Flowork-Seo-Widget")
        self.set_role("seo_widget")
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.stick()

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Intelligence State
        self.is_expanded = False
        self.is_loading = False
        self.current_query = ""
        self.status_msg = ""
        self.results = None
        self.copied_feedback = ""
        self.copied_timer_id = 0
        self.rot_angle = 0.0

        # Mode Selection: "auto", "keyword", "domain", "youtube"
        self.selected_mode = "auto"
        self.detected_mode = "keyword"

        # Hover & Focus States
        self.pill_hovered = False
        self.entry_focused = False

        self.clickable_chips = []  # list of (x, y, w, h, text, action_type)
        self.hovered_chip_idx = None
        self.hovered_btn = None

        # Fixed Container for Gtk.Entry
        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        # Input Search Entry
        self.entry = Gtk.Entry()
        self.entry.set_has_frame(False)
        self.entry.set_placeholder_text("Search keywords, domain (e.g. apple.com), or YouTube URL... [Enter]")
        self.fixed.put(self.entry, 36, 4)

        # Responsive Dimensions Engine
        self.recalculate_metrics()
        screen.connect("size-changed", lambda s: self.recalculate_metrics())
        screen.connect("monitors-changed", lambda s: self.recalculate_metrics())

        self.entry.connect("activate", self.on_search_activate)
        self.entry.connect("focus-in-event", self.on_entry_focus_in)
        self.entry.connect("focus-out-event", self.on_entry_focus_out)
        self.entry.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.entry.connect("button-press-event", self.on_entry_button_press)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            entry, entry:focus, entry:disabled, entry text {
                background: transparent;
                background-color: transparent;
                background-image: none;
                border-color: transparent;
                border-style: none;
                border-width: 0px;
                border-radius: 0px;
                box-shadow: none;
                outline-style: none;
                outline-width: 0px;
                color: #ffffff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                padding: 0px 4px;
                margin: 0px;
            }
            entry selection {
                background-color: rgba(0, 242, 254, 0.4);
                color: #ffffff;
            }
            entry placeholder {
                color: rgba(255, 255, 255, 0.35);
            }
        """)
        self.entry.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.ENTER_NOTIFY_MASK |
            Gdk.EventMask.LEAVE_NOTIFY_MASK |
            Gdk.EventMask.KEY_PRESS_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("realize", self.on_realize)
        self.connect("enter-notify-event", self.on_enter_notify)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-press-event", self.on_button_press)
        self.connect("leave-notify-event", self.on_leave)
        self.connect("key-press-event", self.on_key_press)

        GLib.timeout_add(33, self.on_tick)

    def on_realize(self, widget):
        self._update_input_shape()
        self.raise_to_top()

    def on_enter_notify(self, widget, event):
        self.raise_to_top()
        return False

    def on_entry_button_press(self, entry, event):
        self.grab_focus_and_input()
        return False

    def grab_focus_and_input(self):
        self.raise_to_top()
        try:
            win = self.get_window()
            if win and _X11_DISPLAY and x11:
                xid = win.get_xid()
                x11.XSetInputFocus(_X11_DISPLAY, xid, 2, 0)
                x11.XFlush(_X11_DISPLAY)
        except Exception:
            pass
        self.entry.grab_focus()

    def raise_to_top(self):
        try:
            win = self.get_window()
            if win:
                win.raise_()
                if _X11_DISPLAY and x11:
                    x11.XRaiseWindow(_X11_DISPLAY, win.get_xid())
                    x11.XFlush(_X11_DISPLAY)
        except Exception:
            pass

    def on_entry_focus_in(self, entry, event):
        self.entry_focused = True
        GLib.idle_add(entry.select_region, 0, -1)
        self.queue_draw()
        return False

    def on_entry_focus_out(self, entry, event):
        self.entry_focused = False
        self.queue_draw()
        return False

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.collapse()
            return True
        return False

    def recalculate_metrics(self):
        screen = self.get_screen()
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()

        if self.screen_w >= 2000:
            self.collapsed_w = 580
            self.collapsed_h = 34
            self.expanded_w = 1260
            self.expanded_h = 320
        elif self.screen_w >= 1400:
            self.collapsed_w = 500
            self.collapsed_h = 34
            self.expanded_w = min(1120, int(self.screen_w * 0.75))
            self.expanded_h = 320
        else:
            # Mini laptop (1366x768, 1280x720, etc.)
            self.collapsed_w = min(440, max(360, int(self.screen_w * 0.44)))
            self.collapsed_h = 34
            self.expanded_w = min(960, max(680, int(self.screen_w * 0.88)))
            self.expanded_h = min(320, int(self.screen_h * 0.50))

        self.collapsed_x = (self.screen_w - self.collapsed_w) // 2
        self.collapsed_y = 3
        self.expanded_x = (self.screen_w - self.expanded_w) // 2
        self.expanded_y = 3

        if hasattr(self, "entry"):
            self.entry.set_size_request(self.collapsed_w - 120, 26)

        if not getattr(self, "is_expanded", False):
            self.set_size_request(self.collapsed_w, self.collapsed_h)
            self.resize(self.collapsed_w, self.collapsed_h)
            self.move(self.collapsed_x, self.collapsed_y)
            if hasattr(self, "fixed"):
                self.fixed.move(self.entry, 36, 4)
        else:
            self.set_size_request(self.expanded_w, self.expanded_h)
            self.resize(self.expanded_w, self.expanded_h)
            self.move(self.expanded_x, self.expanded_y)
            trough_x = (self.expanded_w - self.collapsed_w) // 2
            if hasattr(self, "fixed"):
                self.fixed.move(self.entry, trough_x + 36, 4)

        if hasattr(self, "get_window") and self.get_window():
            self._update_input_shape()
        self.queue_draw()

    def _update_input_shape(self):
        win = self.get_window()
        if not win:
            return

        reg = cairo.Region()
        if not self.is_expanded:
            reg.union(cairo.RectangleInt(0, 0, self.collapsed_w, self.collapsed_h))
        else:
            reg.union(cairo.RectangleInt(10, 0, self.expanded_w - 20, self.expanded_h - 4))

        win.input_shape_combine_region(reg, 0, 0)

    def on_search_activate(self, entry):
        text = entry.get_text().strip()
        if not text:
            return
        self.trigger_search(text)

    def trigger_search(self, query):
        if self.is_loading:
            return

        self.current_query = query
        self.is_loading = True
        self.status_msg = "Executing Sovereign Omni-Search..."
        self.results = None
        self.is_expanded = True

        self.set_size_request(self.expanded_w, self.expanded_h)
        self.resize(self.expanded_w, self.expanded_h)
        self.move(self.expanded_x, self.expanded_y)
        self.raise_to_top()

        trough_x = (self.expanded_w - self.collapsed_w) // 2
        self.fixed.move(self.entry, trough_x + 36, 4)

        self._update_input_shape()
        self.queue_draw()

        threading.Thread(target=self._worker_search, args=(query, self.selected_mode), daemon=True).start()

    def _worker_search(self, query, mode):
        try:
            cmd = [sys.executable, OMNI_ENGINE, query, "--mode", mode, "--json"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=18)
            if proc.returncode == 0:
                raw_out = proc.stdout.strip()
                data = json.loads(raw_out)
                GLib.idle_add(self._on_search_success, data)
            else:
                err_msg = proc.stderr.strip() or "Omni engine query error"
                GLib.idle_add(self._on_search_error, err_msg)
        except Exception as e:
            GLib.idle_add(self._on_search_error, str(e))

    def _on_search_success(self, data):
        self.is_loading = False
        self.results = data
        self.detected_mode = data.get("mode", "keyword")
        self.status_msg = "Research Complete"
        self._update_input_shape()
        self.queue_draw()

    def _on_search_error(self, err_msg):
        self.is_loading = False
        self.status_msg = f"Failed: {err_msg[:60]}"
        self._update_input_shape()
        self.queue_draw()

    def collapse(self):
        self.is_expanded = False
        self.results = None
        self.is_loading = False

        self.set_size_request(self.collapsed_w, self.collapsed_h)
        self.resize(self.collapsed_w, self.collapsed_h)
        self.move(self.collapsed_x, self.collapsed_y)
        self.raise_to_top()

        self.fixed.move(self.entry, 36, 4)
        self.entry.set_text("")
        self._update_input_shape()
        self.queue_draw()

    def copy_to_clipboard(self, text, feedback="✓ Copied to clipboard!"):
        cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        cb.set_text(text, -1)
        self.copied_feedback = feedback
        if self.copied_timer_id:
            GLib.source_remove(self.copied_timer_id)
        self.copied_timer_id = GLib.timeout_add(2500, self._clear_feedback)
        self.queue_draw()

    def _clear_feedback(self):
        self.copied_feedback = ""
        self.copied_timer_id = 0
        self.queue_draw()
        return False

    def on_tick(self):
        if self.is_loading:
            self.rot_angle = (self.rot_angle + 0.12) % (2 * math.pi)
            self.queue_draw()
        return True

    def on_motion(self, widget, event):
        x, y = event.x, event.y
        prev_chip = self.hovered_chip_idx
        prev_btn = self.hovered_btn
        prev_pill_hov = self.pill_hovered

        self.hovered_chip_idx = None
        self.hovered_btn = None

        if not self.is_expanded:
            self.pill_hovered = (0 <= x <= self.collapsed_w and 0 <= y <= self.collapsed_h)
            sb_x, sb_y, sb_w, sb_h = self.collapsed_w - 68, 4, 62, 26
            if sb_x <= x <= sb_x + sb_w and sb_y <= y <= sb_y + sb_h:
                self.hovered_btn = "search"
        else:
            trough_x = (self.expanded_w - self.collapsed_w) // 2
            self.pill_hovered = (trough_x <= x <= trough_x + self.collapsed_w and 0 <= y <= self.collapsed_h)

            # Search button in trough
            sb_x, sb_y, sb_w, sb_h = trough_x + self.collapsed_w - 68, 4, 62, 26
            if sb_x <= x <= sb_x + sb_w and sb_y <= y <= sb_y + sb_h:
                self.hovered_btn = "search"

            # Header buttons
            if (self.expanded_w - 105) <= x <= (self.expanded_w - 20) and 4 <= y <= 32:
                self.hovered_btn = "close"
            elif (self.expanded_w - 225) <= x <= (self.expanded_w - 115) and 4 <= y <= 32:
                self.hovered_btn = "copy_all"

            # Clickable Chips
            for i, c in enumerate(self.clickable_chips):
                cx, cy, cw, ch, _, _ = c
                if cx <= x <= cx + cw and cy <= y <= cy + ch:
                    self.hovered_chip_idx = i
                    break

        if (prev_chip != self.hovered_chip_idx or
            prev_btn != self.hovered_btn or
            prev_pill_hov != self.pill_hovered):
            win = self.get_window()
            if win:
                if self.hovered_chip_idx is not None or self.hovered_btn is not None:
                    win.set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "pointer"))
                else:
                    win.set_cursor(None)
            self.queue_draw()

    def on_leave(self, widget, event):
        self.pill_hovered = False
        self.hovered_chip_idx = None
        self.hovered_btn = None
        win = self.get_window()
        if win:
            win.set_cursor(None)
        self.queue_draw()

    def on_button_press(self, widget, event):
        if event.button != 1:
            return

        x, y = event.x, event.y

        if not self.is_expanded:
            sb_x, sb_y, sb_w, sb_h = self.collapsed_w - 68, 4, 62, 26
            if sb_x <= x <= sb_x + sb_w and sb_y <= y <= sb_y + sb_h:
                self.on_search_activate(self.entry)
                return
            self.grab_focus_and_input()
            return
        else:
            trough_x = (self.expanded_w - self.collapsed_w) // 2
            sb_x, sb_y, sb_w, sb_h = trough_x + self.collapsed_w - 68, 4, 62, 26
            if sb_x <= x <= sb_x + sb_w and sb_y <= y <= sb_y + sb_h:
                self.on_search_activate(self.entry)
                return

            if trough_x <= x <= trough_x + self.collapsed_w and 0 <= y <= self.collapsed_h:
                self.grab_focus_and_input()
                return

            if (self.expanded_w - 105) <= x <= (self.expanded_w - 20) and 4 <= y <= 32:
                self.collapse()
                return

            if (self.expanded_w - 225) <= x <= (self.expanded_w - 115) and 4 <= y <= 32:
                self._copy_all_content()
                return

            # Chip clicks
            if self.hovered_chip_idx is not None and self.hovered_chip_idx < len(self.clickable_chips):
                _, _, _, _, text, action_type = self.clickable_chips[self.hovered_chip_idx]
                if action_type == "copy":
                    self.copy_to_clipboard(text, f"✓ Copied: '{text[:30]}'")
                elif action_type == "set_mode":
                    self.selected_mode = text
                    self.queue_draw()
                    if self.entry.get_text().strip():
                        self.trigger_search(self.entry.get_text().strip())
                return

            # Outside click dismiss
            rx = 10
            ry = 0
            rw = self.expanded_w - 20
            rh = self.expanded_h - 4
            if not (rx <= x <= rx + rw and ry <= y <= ry + rh):
                self.collapse()
                return

    def _copy_all_content(self):
        if not self.results:
            return
        mode = self.results.get("mode", "keyword")
        if mode == "keyword":
            items = []
            for kw in self.results.get("google_autocomplete", []): items.append(kw)
            for kw in self.results.get("youtube_suggestions", []):
                if kw not in items: items.append(kw)
            self.copy_to_clipboard("\n".join(items), "✓ All keywords copied to clipboard!")
        elif mode == "youtube":
            tags = self.results.get("secret_keywords", [])
            self.copy_to_clipboard(", ".join(tags), "✓ All YouTube tags copied to clipboard!")
        elif mode == "domain":
            subs = self.results.get("subdomains", [])
            lines = [f"Domain: {self.results.get('domain')}"]
            lines.append(f"Title: {self.results.get('title')}")
            lines.append("Subdomains:\n" + "\n".join(subs))
            self.copy_to_clipboard("\n".join(lines), "✓ Domain recon copied to clipboard!")

    def on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        layout = self.create_pango_layout()

        # ======================================================================
        # SCENARIO A: COLLAPSED COMPACT PILL DOCKED IN TOP PANEL
        # ======================================================================
        if not self.is_expanded:
            pw, ph = self.collapsed_w, self.collapsed_h
            is_active = (self.pill_hovered or self.entry_focused)

            draw_rounded_rect(cr, 0, 0, pw, ph, 16)
            cr.set_source_rgba(0.01, 0.03, 0.07, 0.88 if is_active else 0.55)
            cr.fill_preserve()
            border_alpha = 0.85 if is_active else 0.22
            cr.set_source_rgba(*C_CYAN, border_alpha)
            cr.set_line_width(1.0 if is_active else 0.7)
            cr.stroke()

            # Magnifier Icon
            cr.save()
            cr.arc(18, ph / 2, 5.5, 0, 2 * math.pi)
            cr.set_source_rgba(*C_CYAN, 0.90 if is_active else 0.40)
            cr.set_line_width(1.4)
            cr.stroke()
            cr.move_to(22, ph / 2 + 4)
            cr.line_to(26, ph / 2 + 8)
            cr.set_line_width(1.6)
            cr.stroke()
            cr.restore()

            # Search Button inside Pill
            sb_x, sb_y, sb_w, sb_h = pw - 68, 4, 62, 26
            draw_rounded_rect(cr, sb_x, sb_y, sb_w, sb_h, 12)
            is_btn_hov = (self.hovered_btn == "search")
            if is_active:
                cr.set_source_rgba(0.00, 0.24, 0.20, 0.95 if is_btn_hov else 0.85)
                cr.fill_preserve()
                cr.set_source_rgba(*C_GREEN, 0.90 if is_btn_hov else 0.50)
                cr.set_line_width(1.0)
                cr.stroke()
                cr.set_source_rgba(*C_WHITE, 0.95)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.04)
                cr.fill_preserve()
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.12)
                cr.set_line_width(0.8)
                cr.stroke()
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.40)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
            layout.set_text("SEARCH", -1)
            tw, th = layout.get_pixel_size()
            cr.move_to(sb_x + (sb_w - tw) / 2, sb_y + (sb_h - th) / 2)
            PangoCairo.show_layout(cr, layout)
            return

        # ======================================================================
        # SCENARIO B: EXPANDED UNIFIED PANORAMIC HUD ISLAND
        # ======================================================================
        rx = 10
        ry = 0
        rw = self.expanded_w - 20
        rh = self.expanded_h - 4

        draw_rounded_rect(cr, rx, ry, rw, rh, 18)
        cr.set_source_rgba(0.01, 0.03, 0.07, 0.96)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 0.45)
        cr.set_line_width(1.2)
        cr.stroke()

        # Top Highlight Specular Rim
        cr.save()
        cr.move_to(rx + 18, ry + 1)
        cr.line_to(rx + rw - 18, ry + 1)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.25)
        cr.set_line_width(1.0)
        cr.stroke()
        cr.restore()

        # Header: Pulse Dot & Mode Title
        mode = self.detected_mode if self.results else "keyword"
        mode_titles = {
            "keyword": f"KEYWORD RADAR: \"{self.current_query.upper()[:28]}\"",
            "domain": f"DOMAIN & BACKLINK RECON: {self.current_query.upper()[:28]}",
            "youtube": f"YOUTUBE SEO DEEPSCAN: {self.current_query[:28]}"
        }
        head_title = mode_titles.get(mode, "SOVEREIGN OMNI-SEARCH") if not self.is_loading else "EXECUTING SOVEREIGN RECON ENGINE..."

        cr.arc(rx + 22, ry + 17, 4.0, 0, 2 * math.pi)
        cr.set_source_rgba(*C_GREEN, 0.95)
        cr.fill()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.8"))
        layout.set_text(head_title, -1)
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(rx + 32, ry + 10)
        PangoCairo.show_layout(cr, layout)

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 6.8"))
        sub_text = self.copied_feedback if self.copied_feedback else "Autonomous Multi-Engine Intelligence (Keyword • Domain • YouTube)"
        layout.set_text(sub_text, -1)
        sub_col = C_GREEN if self.copied_feedback else C_MUTED
        cr.set_source_rgba(*sub_col, 0.95 if self.copied_feedback else 0.65)
        cr.move_to(rx + 32, ry + 24)
        PangoCairo.show_layout(cr, layout)

        # Header Search Trough
        trough_x = (self.expanded_w - self.collapsed_w) // 2
        draw_rounded_rect(cr, trough_x, 0, self.collapsed_w, self.collapsed_h, 16)
        cr.set_source_rgba(0.00, 0.04, 0.08, 0.70)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.35)
        cr.set_line_width(0.8)
        cr.stroke()

        # Magnifier Icon
        cr.save()
        icon_cx = trough_x + 18
        icon_cy = self.collapsed_h / 2
        cr.arc(icon_cx, icon_cy, 5.5, 0, 2 * math.pi)
        cr.set_source_rgba(*C_CYAN, 0.85)
        cr.set_line_width(1.4)
        cr.stroke()
        cr.move_to(icon_cx + 4.0, icon_cy + 4.0)
        cr.line_to(icon_cx + 8.0, icon_cy + 8.0)
        cr.set_line_width(1.6)
        cr.stroke()
        cr.restore()

        # Search Button in Trough
        sb_x, sb_y, sb_w, sb_h = trough_x + self.collapsed_w - 68, 4, 62, 26
        draw_rounded_rect(cr, sb_x, sb_y, sb_w, sb_h, 12)
        is_btn_hov = (self.hovered_btn == "search")
        cr.set_source_rgba(0.00, 0.24, 0.20, 0.95 if is_btn_hov else 0.85)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 0.90 if is_btn_hov else 0.50)
        cr.set_line_width(1.0)
        cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        layout.set_text("SEARCH" if not self.is_loading else "...", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(sb_x + (sb_w - tw) / 2, sb_y + (sb_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Action Buttons: [ COPY ALL ] + [ ESC ]
        kx, ky, kw, kh = self.expanded_w - 225, 4, 110, 28
        draw_rounded_rect(cr, kx, ky, kw, kh, 8)
        k_hov = (self.hovered_btn == "copy_all")
        cr.set_source_rgba(0.00, 0.18, 0.12, 0.85 if k_hov else 0.35)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 0.85 if k_hov else 0.35)
        cr.set_line_width(0.9)
        cr.stroke()
        layout.set_text("📋 COPY ALL", -1)
        ktw, kth = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.90)
        cr.move_to(kx + (kw - ktw) / 2, ky + (kh - kth) / 2)
        PangoCairo.show_layout(cr, layout)

        cx, cy, cw, ch = self.expanded_w - 105, 4, 85, 28
        draw_rounded_rect(cr, cx, cy, cw, ch, 8)
        c_hov = (self.hovered_btn == "close")
        cr.set_source_rgba(0.20, 0.05, 0.08, 0.85 if c_hov else 0.35)
        cr.fill_preserve()
        cr.set_source_rgba(*C_RED, 0.85 if c_hov else 0.35)
        cr.set_line_width(0.9)
        cr.stroke()
        layout.set_text("✕ ESC", -1)
        ctw, cth = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.90)
        cr.move_to(cx + (cw - ctw) / 2, cy + (ch - cth) / 2)
        PangoCairo.show_layout(cr, layout)

        # Hairline
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.07)
        cr.set_line_width(0.8)
        cr.move_to(rx + 16, 40)
        cr.line_to(rx + rw - 16, 40)
        cr.stroke()

        if self.is_loading:
            cr.save()
            cr.translate(rx + rw / 2, ry + rh / 2 + 15)
            cr.rotate(self.rot_angle)
            cr.set_source_rgba(*C_CYAN, 0.85)
            cr.set_line_width(2.5)
            cr.arc(0, 0, 18, 0, 1.5 * math.pi)
            cr.stroke()
            cr.restore()
            return

        if not self.results:
            return

        self.clickable_chips = []

        # ======================================================================
        # RENDER MODE 1: KEYWORD RESEARCH
        # ======================================================================
        if mode == "keyword":
            self._render_keyword_mode(cr, layout, rx, ry, rw, rh)

        # ======================================================================
        # RENDER MODE 2: DOMAIN & BACKLINK RECON
        # ======================================================================
        elif mode == "domain":
            self._render_domain_mode(cr, layout, rx, ry, rw, rh)

        # ======================================================================
        # RENDER MODE 3: YOUTUBE SEO DEEPSCAN
        # ======================================================================
        elif mode == "youtube":
            self._render_youtube_mode(cr, layout, rx, ry, rw, rh)

    def _render_keyword_mode(self, cr, layout, rx, ry, rw, rh):
        vol = self.results.get("search_volume", "N/A")
        kd = self.results.get("seo_difficulty", 0)
        kd_lvl = self.results.get("seo_difficulty_level", "MEDIUM")
        cpc = self.results.get("estimated_cpc", "$0.00")
        intent = self.results.get("search_intent", "GENERAL")

        # Ribbon
        tel_x = rx + 16
        tel_y = 48
        tel_w = rw - 32
        tel_h = 44

        draw_rounded_rect(cr, tel_x, tel_y, tel_w, tel_h, 9)
        cr.set_source_rgba(0.00, 0.04, 0.08, 0.70)
        cr.fill_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.07)
        cr.set_line_width(0.8)
        cr.stroke()

        col_w_m = tel_w / 4
        m_stations = [
            ("SEARCH VOLUME", vol, "ORGANIC DEMAND", C_GREEN),
            ("SEO DIFFICULTY", f"{kd} / 100", kd_lvl, C_GREEN if kd < 35 else (C_AMBER if kd < 60 else C_RED)),
            ("ESTIMATED CPC", cpc, "VALUE", C_CYAN),
            ("SEARCH INTENT", intent, "AUDIENCE", C_PURPLE)
        ]

        for i, (m_lbl, m_val, m_tag, m_col) in enumerate(m_stations):
            sx = tel_x + i * col_w_m
            if i > 0:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.06)
                cr.set_line_width(0.8)
                cr.move_to(sx, tel_y + 6)
                cr.line_to(sx, tel_y + tel_h - 6)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
            layout.set_text(m_lbl, -1)
            cr.set_source_rgba(*m_col, 0.85)
            cr.move_to(sx + 14, tel_y + 6)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11.0"))
            layout.set_text(m_val, -1)
            cr.set_source_rgba(*C_WHITE, 0.95)
            cr.move_to(sx + 14, tel_y + 21)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.0"))
            layout.set_text(m_tag, -1)
            tw_tag, th_tag = layout.get_pixel_size()
            tag_x = sx + col_w_m - tw_tag - 18
            tag_y = tel_y + 15
            draw_rounded_rect(cr, tag_x - 5, tag_y - 2, tw_tag + 10, th_tag + 4, 4)
            cr.set_source_rgba(*m_col, 0.12)
            cr.fill_preserve()
            cr.set_source_rgba(*m_col, 0.40)
            cr.set_line_width(0.6)
            cr.stroke()
            cr.set_source_rgba(*m_col, 0.90)
            cr.move_to(tag_x, tag_y)
            PangoCairo.show_layout(cr, layout)

        # Two Columns of Keywords
        kw_col_w = (rw - 44) / 2
        kw_col_y = tel_y + tel_h + 8

        # Left: Google
        col1_x = rx + 16
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.8"))
        layout.set_text("🌐 GOOGLE AUTOCOMPLETE (Organic Search Intent)", -1)
        cr.set_source_rgba(*C_CYAN, 0.90)
        cr.move_to(col1_x, kw_col_y)
        PangoCairo.show_layout(cr, layout)

        google_ideas = self.results.get("google_autocomplete", [])[:5]
        y_cursor1 = kw_col_y + 16
        for idx, kw in enumerate(google_ideas):
            self._render_keyword_row(cr, layout, col1_x, y_cursor1, kw_col_w, 24, idx + 1, kw, C_CYAN)
            y_cursor1 += 28

        # Right: YouTube
        col2_x = rx + 20 + kw_col_w + 8
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.8"))
        layout.set_text("📺 YOUTUBE TOP QUERIES (Video Search Demand)", -1)
        cr.set_source_rgba(*C_AMBER, 0.90)
        cr.move_to(col2_x, kw_col_y)
        PangoCairo.show_layout(cr, layout)

        yt_ideas = self.results.get("youtube_suggestions", [])[:5]
        y_cursor2 = kw_col_y + 16
        for idx, kw in enumerate(yt_ideas):
            self._render_keyword_row(cr, layout, col2_x, y_cursor2, kw_col_w, 24, idx + 1, kw, C_AMBER)
            y_cursor2 += 28

        # Bottom Tip
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 6.8"))
        layout.set_text("💡 TIP: Click any keyword row to copy  //  Press ESC or click outside to collapse", -1)
        cr.set_source_rgba(*C_AMBER, 0.70)
        cr.move_to(rx + 22, rh - 12)
        PangoCairo.show_layout(cr, layout)

    def _render_domain_mode(self, cr, layout, rx, ry, rw, rh):
        score = self.results.get("seo_health_score", 75)
        lg = self.results.get("link_graph", {})
        total_links = lg.get("total_links", 0)
        dofollow_ratio = lg.get("dofollow_ratio", "100%")
        rdap = self.results.get("whois_rdap", {})
        created = rdap.get("created", "N/A")[:10]
        expires = rdap.get("expires", "N/A")[:10]
        sub_count = self.results.get("subdomains_count", 0)

        # Ribbon
        tel_x = rx + 16
        tel_y = 48
        tel_w = rw - 32
        tel_h = 44

        draw_rounded_rect(cr, tel_x, tel_y, tel_w, tel_h, 9)
        cr.set_source_rgba(0.00, 0.04, 0.08, 0.70)
        cr.fill_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.07)
        cr.set_line_width(0.8)
        cr.stroke()

        col_w_m = tel_w / 4
        m_stations = [
            ("ON-PAGE SEO HEALTH", f"{score} / 100", "EXCELLENT" if score >= 80 else "NEEDS WORK", C_GREEN if score >= 80 else C_AMBER),
            ("TOTAL LINK GRAPH", f"{total_links} Links", f"{dofollow_ratio} DOFOLLOW", C_CYAN),
            ("DOMAIN AGE (WHOIS)", created, "REGISTERED", C_PURPLE),
            ("SUBDOMAINS (CRT.SH)", f"{sub_count} Discovered", "RECON", C_GREEN)
        ]

        for i, (m_lbl, m_val, m_tag, m_col) in enumerate(m_stations):
            sx = tel_x + i * col_w_m
            if i > 0:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.06)
                cr.set_line_width(0.8)
                cr.move_to(sx, tel_y + 6)
                cr.line_to(sx, tel_y + tel_h - 6)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
            layout.set_text(m_lbl, -1)
            cr.set_source_rgba(*m_col, 0.85)
            cr.move_to(sx + 14, tel_y + 6)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11.0"))
            layout.set_text(m_val, -1)
            cr.set_source_rgba(*C_WHITE, 0.95)
            cr.move_to(sx + 14, tel_y + 21)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.0"))
            layout.set_text(m_tag, -1)
            tw_tag, th_tag = layout.get_pixel_size()
            tag_x = sx + col_w_m - tw_tag - 18
            tag_y = tel_y + 15
            draw_rounded_rect(cr, tag_x - 5, tag_y - 2, tw_tag + 10, th_tag + 4, 4)
            cr.set_source_rgba(*m_col, 0.12)
            cr.fill_preserve()
            cr.set_source_rgba(*m_col, 0.40)
            cr.set_line_width(0.6)
            cr.stroke()
            cr.set_source_rgba(*m_col, 0.90)
            cr.move_to(tag_x, tag_y)
            PangoCairo.show_layout(cr, layout)

        # Dual Deck
        kw_col_w = (rw - 44) / 2
        kw_col_y = tel_y + tel_h + 8

        # Left Deck: Link Graph & On-Page Audit
        col1_x = rx + 16
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.8"))
        layout.set_text("🔗 LINK GRAPH & ON-PAGE ARCHITECTURE", -1)
        cr.set_source_rgba(*C_CYAN, 0.90)
        cr.move_to(col1_x, kw_col_y)
        PangoCairo.show_layout(cr, layout)

        y_c1 = kw_col_y + 16
        items_left = [
            f"Internal Links: {lg.get('internal_links', 0)}  //  External Outbound: {lg.get('external_links', 0)}",
            f"DoFollow Links: {lg.get('dofollow_links', 0)}  //  NoFollow Links: {lg.get('nofollow_links', 0)}",
            f"Page Title: {self.results.get('title', 'N/A')[:48]}",
            f"H1 Heading: {', '.join(self.results.get('h1_tags', ['None']))[:48]}",
            f"Sample Outbound: {', '.join(lg.get('sample_outbound', ['None']))[:48]}"
        ]
        for idx, line in enumerate(items_left):
            self._render_keyword_row(cr, layout, col1_x, y_c1, kw_col_w, 24, idx + 1, line, C_CYAN)
            y_c1 += 28

        # Right Deck: Subdomains & Infrastructure
        col2_x = rx + 20 + kw_col_w + 8
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.8"))
        layout.set_text("🌐 SUBDOMAIN RECON & INFRASTRUCTURE (CRT.SH)", -1)
        cr.set_source_rgba(*C_GREEN, 0.90)
        cr.move_to(col2_x, kw_col_y)
        PangoCairo.show_layout(cr, layout)

        sub_list = self.results.get("subdomains", [])[:5]
        if not sub_list:
            sub_list = [f"Expires: {expires}", f"Nameservers: {', '.join(rdap.get('nameservers', []))[:35]}", "No subdomains found in CT logs"]
        y_c2 = kw_col_y + 16
        for idx, sub in enumerate(sub_list):
            self._render_keyword_row(cr, layout, col2_x, y_c2, kw_col_w, 24, idx + 1, sub, C_GREEN)
            y_c2 += 28

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 6.8"))
        layout.set_text("💡 TIP: Click any item to copy  //  COPY ALL saves full domain recon snapshot", -1)
        cr.set_source_rgba(*C_GREEN, 0.70)
        cr.move_to(rx + 22, rh - 12)
        PangoCairo.show_layout(cr, layout)

    def _render_youtube_mode(self, cr, layout, rx, ry, rw, rh):
        views = self.results.get("views", "0")
        dur = self.results.get("duration", "N/A")
        monetized = "ACTIVE" if self.results.get("is_monetized") else "INACTIVE"
        ad_breaks = self.results.get("ad_breaks_count", 0)
        channel = self.results.get("channel_name", "Unknown Channel")
        title = self.results.get("title", "")
        tags = self.results.get("secret_keywords", [])

        # Ribbon
        tel_x = rx + 16
        tel_y = 48
        tel_w = rw - 32
        tel_h = 44

        draw_rounded_rect(cr, tel_x, tel_y, tel_w, tel_h, 9)
        cr.set_source_rgba(0.00, 0.04, 0.08, 0.70)
        cr.fill_preserve()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.07)
        cr.set_line_width(0.8)
        cr.stroke()

        col_w_m = tel_w / 4
        m_stations = [
            ("TOTAL VIEWS", views, "ENGAGEMENT", C_GREEN),
            ("DURATION", dur, "LENGTH", C_CYAN),
            ("MONETIZATION", monetized, "STATUS", C_GREEN if monetized == "ACTIVE" else C_AMBER),
            ("AD BREAKS", f"{ad_breaks} Breaks", "COMMERCIAL", C_PURPLE)
        ]

        for i, (m_lbl, m_val, m_tag, m_col) in enumerate(m_stations):
            sx = tel_x + i * col_w_m
            if i > 0:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.06)
                cr.set_line_width(0.8)
                cr.move_to(sx, tel_y + 6)
                cr.line_to(sx, tel_y + tel_h - 6)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
            layout.set_text(m_lbl, -1)
            cr.set_source_rgba(*m_col, 0.85)
            cr.move_to(sx + 14, tel_y + 6)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11.0"))
            layout.set_text(m_val, -1)
            cr.set_source_rgba(*C_WHITE, 0.95)
            cr.move_to(sx + 14, tel_y + 21)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.0"))
            layout.set_text(m_tag, -1)
            tw_tag, th_tag = layout.get_pixel_size()
            tag_x = sx + col_w_m - tw_tag - 18
            tag_y = tel_y + 15
            draw_rounded_rect(cr, tag_x - 5, tag_y - 2, tw_tag + 10, th_tag + 4, 4)
            cr.set_source_rgba(*m_col, 0.12)
            cr.fill_preserve()
            cr.set_source_rgba(*m_col, 0.40)
            cr.set_line_width(0.6)
            cr.stroke()
            cr.set_source_rgba(*m_col, 0.90)
            cr.move_to(tag_x, tag_y)
            PangoCairo.show_layout(cr, layout)

        # Video Header
        yt_area_y = tel_y + tel_h + 8
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.8"))
        layout.set_text(f"🎥 CHANNEL: {channel.upper()}  //  SECRET ALGORITHM TAGS ({len(tags)})", -1)
        cr.set_source_rgba(*C_CYAN, 0.90)
        cr.move_to(rx + 16, yt_area_y)
        PangoCairo.show_layout(cr, layout)

        # Interactive Tag Matrix (Flow Layout)
        chip_x = rx + 16
        chip_y = yt_area_y + 16
        max_w = rw - 32
        row_max_h = 24

        if not tags:
            layout.set_text("No secret tags embedded in this video metadata.", -1)
            cr.set_source_rgba(*C_MUTED, 0.60)
            cr.move_to(chip_x, chip_y + 6)
            PangoCairo.show_layout(cr, layout)
        else:
            for tag in tags[:24]:
                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.2"))
                layout.set_text(tag, -1)
                tw_chip, th_chip = layout.get_pixel_size()
                chip_w = tw_chip + 16

                if chip_x + chip_w > rx + 16 + max_w:
                    chip_x = rx + 16
                    chip_y += 28
                    if chip_y + row_max_h > rh - 20:
                        break

                c_idx = len(self.clickable_chips)
                is_hov = (self.hovered_chip_idx == c_idx)
                self.clickable_chips.append((chip_x, chip_y, chip_w, row_max_h, tag, "copy"))

                draw_rounded_rect(cr, chip_x, chip_y, chip_w, row_max_h, 6)
                cr.set_source_rgba(0.00, 0.18, 0.15, 0.85 if is_hov else 0.40)
                cr.fill_preserve()
                cr.set_source_rgba(*C_CYAN, 0.85 if is_hov else 0.30)
                cr.set_line_width(0.8)
                cr.stroke()

                cr.set_source_rgba(*C_WHITE, 0.95 if is_hov else 0.85)
                cr.move_to(chip_x + 8, chip_y + (row_max_h - th_chip) / 2)
                PangoCairo.show_layout(cr, layout)

                chip_x += chip_w + 6

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 6.8"))
        layout.set_text("💡 TIP: Click any tag chip to copy individually  //  Click COPY ALL for comma-separated YouTube Studio format", -1)
        cr.set_source_rgba(*C_CYAN, 0.70)
        cr.move_to(rx + 22, rh - 12)
        PangoCairo.show_layout(cr, layout)

    def _render_keyword_row(self, cr, layout, x, y, w, h, index, text, theme_color):
        c_idx = len(self.clickable_chips)
        is_hov = (self.hovered_chip_idx == c_idx)
        self.clickable_chips.append((x, y, w, h, text, "copy"))

        draw_rounded_rect(cr, x, y, w, h, 6)
        if is_hov:
            cr.set_source_rgba(0.00, 0.15, 0.18, 0.85)
            cr.fill_preserve()
            cr.set_source_rgba(*theme_color, 0.65)
            cr.set_line_width(1.0)
            cr.stroke()
        else:
            cr.set_source_rgba(0.00, 0.04, 0.08, 0.50)
            cr.fill_preserve()
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.06)
            cr.set_line_width(0.7)
            cr.stroke()

        # Index Badge
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
        layout.set_text(f"{index:02d}", -1)
        cr.set_source_rgba(*theme_color, 0.85 if is_hov else 0.55)
        cr.move_to(x + 10, y + 5)
        PangoCairo.show_layout(cr, layout)

        # Keyword / Content Text
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        disp_txt = text if len(text) <= 52 else text[:51] + "…"
        layout.set_text(disp_txt, -1)
        cr.set_source_rgba(*C_WHITE, 0.95 if is_hov else 0.82)
        cr.move_to(x + 36, y + 5)
        PangoCairo.show_layout(cr, layout)

        # Mini Copy Action Badge
        if is_hov:
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.2"))
            layout.set_text("COPY", -1)
            tw_c, _ = layout.get_pixel_size()
            cr.set_source_rgba(*theme_color, 0.90)
            cr.move_to(x + w - tw_c - 12, y + 6)
            PangoCairo.show_layout(cr, layout)


def main():
    win = OmniSeoWidgetWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
