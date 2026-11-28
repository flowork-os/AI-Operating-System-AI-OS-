#!/usr/bin/env python3
# ==============================================================================
# 👑 FLOWORK OS — SOVEREIGN DIGITAL CLOCK & CALENDAR HUD (BELOW SEARCH BAR)
# 100% Native Python + GTK3 + Cairo + Pango, Zero Overhead, 100% Click-Through
# ==============================================================================

import os
import sys
import time
import math
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import cairo

# Cyber & Holographic Palette
C_CYAN   = (0.00, 0.95, 1.00)     # Electric Cyan (#00f2fe)
C_WHITE  = (0.97, 0.99, 1.00)     # Razor Crisp White
C_GOLD   = (1.00, 0.82, 0.24)     # Radiant Gold
C_MUTED  = (0.50, 0.70, 0.85)     # Atmospheric Muted Cyan

DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

class SovereignDigitalClockHUD(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        self.set_title("Flowork Digital Clock HUD")
        self.set_wmclass("flowork-digital-clock-hud", "flowork-digital-clock-hud")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_resizable(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_keep_below(True)
        self.stick()

        # Scaling and baseline geometry
        self.ui_scale = 1.0
        self.base_w = 600
        self.base_h = 84
        self.win_w = self.base_w
        self.win_h = self.base_h

        self.set_default_size(self.base_w, self.base_h)
        self.set_size_request(self.base_w, self.base_h)

        # RGBA Visual
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        screen.connect("size-changed", self._reposition)
        screen.connect("monitors-changed", self._reposition)

        self.connect("realize", self._on_realize)
        self.connect("draw", self._on_draw)

        # Pulse animation state
        self.t = 0.0

        # Fast tick for ultra-smooth colon pulse and second accuracy
        GLib.timeout_add(100, self._on_tick)

    def _on_realize(self, widget):
        self._reposition()
        self._ensure_click_through()
        self._ensure_above_wallpaper()

    def _ensure_click_through(self):
        """Pass all mouse events 100% through to desktop / wallpaper."""
        win = self.get_window()
        if win:
            empty_region = cairo.Region()
            win.input_shape_combine_region(empty_region, 0, 0)

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

    def _reposition(self, *args):
        screen = self.get_screen()
        display = screen.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        if not monitor:
            return

        geo = monitor.get_geometry()
        scale = monitor.get_scale_factor() if hasattr(monitor, "get_scale_factor") else 1
        self.ui_scale = max(1.0, float(scale))

        self.win_w = int(round(self.base_w * self.ui_scale))
        self.win_h = int(round(self.base_h * self.ui_scale))
        self.set_size_request(self.win_w, self.win_h)
        self.resize(self.win_w, self.win_h)

        # Center horizontally, place directly beneath search bar (search bar y=3, h=34 -> ends at y=37)
        x = geo.x + (geo.width - self.win_w) // 2
        y = geo.y + int(round(44 * self.ui_scale))

        self.move(x, y)
        self._ensure_click_through()
        self._ensure_above_wallpaper()
        self.queue_draw()

    def _on_tick(self):
        self.t += 0.1
        self.tick_count = getattr(self, "tick_count", 0) + 1
        if self.tick_count % 4 == 0:
            self._ensure_above_wallpaper()
        self.queue_draw()
        return True

    def _on_draw(self, widget, cr: cairo.Context):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        cr.save()
        cr.scale(self.ui_scale, self.ui_scale)

        cx = self.base_w / 2.0

        # Read exact system time and PC settings
        now = time.localtime()
        hour_str = f"{now.tm_hour:02d}"
        min_str = f"{now.tm_min:02d}"
        sec_str = f"{now.tm_sec:02d}"

        day_name = DAYS_ID[now.tm_wday]
        month_name = MONTHS_ID[now.tm_mon - 1]
        date_str = f"{day_name}, {now.tm_mday} {month_name} {now.tm_year}"

        # -------------------------------------------------------------
        # 1. Main Digital Clock Typography
        # -------------------------------------------------------------
        layout = self.create_pango_layout()

        # Large Time Numerals: HH:MM
        time_text = f"{hour_str}:{min_str}"
        layout.set_font_description(Pango.FontDescription("JetBrains Mono SemiBold 30"))
        layout.set_text(time_text, -1)
        tw, th = layout.get_pixel_size()

        # Seconds Tag: :SS
        sec_layout = self.create_pango_layout()
        sec_layout.set_font_description(Pango.FontDescription("JetBrains Mono Medium 14"))
        sec_layout.set_text(f":{sec_str}", -1)
        sw, sh = sec_layout.get_pixel_size()

        total_time_w = tw + sw + 4
        time_x = cx - total_time_w / 2.0
        time_y = 2
        sec_x = time_x + tw + 4
        sec_y = time_y + (th - sh) - 4

        # Multi-Color Prismatic Subtitle Gradient for Time (Cyan -> Azure -> Violet -> Magenta -> Amber)
        time_grad = cairo.LinearGradient(time_x, time_y, time_x + total_time_w, time_y)
        time_grad.add_color_stop_rgba(0.00, 0.00, 0.96, 1.00, 0.98)   # Electric Cyan
        time_grad.add_color_stop_rgba(0.24, 0.38, 0.72, 1.00, 0.98)   # Azure Blue
        time_grad.add_color_stop_rgba(0.48, 0.82, 0.46, 1.00, 0.98)   # Royal Purple / Lavender
        time_grad.add_color_stop_rgba(0.72, 1.00, 0.30, 0.70, 0.98)   # Hot Magenta / Pink
        time_grad.add_color_stop_rgba(1.00, 1.00, 0.82, 0.28, 0.98)   # Cyber Gold / Amber

        # Subtle dark silhouette behind time for razor-sharp legibility on any wallpaper
        cr.save()
        cr.set_source_rgba(0.01, 0.02, 0.05, 0.65)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (0, 2)):
            cr.move_to(time_x + dx, time_y + dy)
            PangoCairo.show_layout(cr, layout)
            cr.move_to(sec_x + dx, sec_y + dy)
            PangoCairo.show_layout(cr, sec_layout)
        cr.restore()

        # Foreground Multicolored Crisp Time
        cr.set_source(time_grad)
        cr.move_to(time_x, time_y)
        PangoCairo.show_layout(cr, layout)

        # Seconds Numerals (radiant amber-gold gradient)
        sec_grad = cairo.LinearGradient(sec_x, sec_y, sec_x + sw, sec_y)
        sec_grad.add_color_stop_rgba(0.0, 1.00, 0.58, 0.22, 0.98)   # Solar Amber
        sec_grad.add_color_stop_rgba(1.0, 1.00, 0.88, 0.28, 0.98)   # Radiant Gold
        cr.set_source(sec_grad)
        cr.move_to(sec_x, sec_y)
        PangoCairo.show_layout(cr, sec_layout)

        # -------------------------------------------------------------
        # 2. Formatted Date & Telemetry
        # -------------------------------------------------------------
        date_layout = self.create_pango_layout()
        date_layout.set_font_description(Pango.FontDescription("Inter Medium 11.5"))
        date_layout.set_text(date_str, -1)
        dw, dh = date_layout.get_pixel_size()

        date_x = cx - dw / 2.0
        date_y = time_y + th + 2

        # Flanking hairline brackets around date with complementary gradient
        accent_w = 42
        y_hairline = date_y + dh / 2.0

        # Left bracket (Cyan-Violet)
        brk_left = cairo.LinearGradient(date_x - 10 - accent_w, y_hairline, date_x - 10, y_hairline)
        brk_left.add_color_stop_rgba(0.0, 0.00, 0.95, 1.00, 0.15)
        brk_left.add_color_stop_rgba(1.0, 0.40, 0.70, 1.00, 0.60)
        cr.set_source(brk_left)
        cr.set_line_width(0.9)
        cr.move_to(date_x - 10 - accent_w, y_hairline)
        cr.line_to(date_x - 10, y_hairline)
        cr.stroke()
        cr.arc(date_x - 10, y_hairline, 1.5, 0, math.tau)
        cr.set_source_rgba(0.00, 0.95, 1.00, 0.85)
        cr.fill()

        # Right bracket (Magenta-Gold)
        brk_right = cairo.LinearGradient(date_x + dw + 10, y_hairline, date_x + dw + 10 + accent_w, y_hairline)
        brk_right.add_color_stop_rgba(0.0, 1.00, 0.35, 0.70, 0.60)
        brk_right.add_color_stop_rgba(1.0, 1.00, 0.82, 0.28, 0.15)
        cr.set_source(brk_right)
        cr.set_line_width(0.9)
        cr.move_to(date_x + dw + 10, y_hairline)
        cr.line_to(date_x + dw + 10 + accent_w, y_hairline)
        cr.stroke()
        cr.arc(date_x + dw + 10, y_hairline, 1.5, 0, math.tau)
        cr.set_source_rgba(1.00, 0.82, 0.28, 0.85)
        cr.fill()

        # Soft backdrop shadow for date
        cr.set_source_rgba(0.01, 0.02, 0.06, 0.65)
        cr.move_to(date_x + 1, date_y + 1)
        PangoCairo.show_layout(cr, date_layout)

        # Multicolored Radiant Date Gradient (Cyan -> Lavender -> Gold)
        date_grad = cairo.LinearGradient(date_x, date_y, date_x + dw, date_y)
        date_grad.add_color_stop_rgba(0.00, 0.00, 0.95, 1.00, 0.94)  # Cyan
        date_grad.add_color_stop_rgba(0.35, 0.55, 0.68, 1.00, 0.94)  # Azure Lavender
        date_grad.add_color_stop_rgba(0.70, 0.88, 0.42, 0.95, 0.94)  # Orchid Magenta
        date_grad.add_color_stop_rgba(1.00, 1.00, 0.80, 0.30, 0.94)  # Amber
        cr.set_source(date_grad)
        cr.move_to(date_x, date_y)
        PangoCairo.show_layout(cr, date_layout)

        cr.restore()
        return False


def main():
    win = SovereignDigitalClockHUD()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
