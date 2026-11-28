#!/usr/bin/env python3
# ==============================================================================
# 🔮 FLOWORK OS — JARVIS HOLOGRAPHIC TAROT DECK HUD (BOTTOM-RIGHT DESKTOP)
# Stealth Ambient Watermark + 3D Holographic 5-Card Stack Launcher
# ==============================================================================

import math
import os
import random
import subprocess
import time
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import cairo

TAROT_ORACLE_BIN = "/opt/floworkos/bin/flowork-tarot-oracle"

C_CYAN = (0.0, 0.95, 1.0)
C_GOLD = (1.0, 0.82, 0.18)
C_MINT = (0.0, 0.96, 0.63)
C_VIOLET = (0.68, 0.38, 1.0)


def draw_rounded_rect(cr, x, y, w, h, r):
    r = min(r, w / 2.0, h / 2.0)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


class JarvisTarotDeckHUD(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Flowork Quantum Tarot Deck")
        self.set_wmclass("flowork-tarot-deck-hud", "flowork-tarot-deck-hud")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_resizable(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_keep_below(True)
        self.stick()

        self.base_w = 210.0
        self.base_h = 230.0
        self.ui_scale = 1.0
        self.win_w = int(self.base_w)
        self.win_h = int(self.base_h)
        self.set_default_size(self.win_w, self.win_h)
        self.set_size_request(self.win_w, self.win_h)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Responsive positioning & hotplugging
        screen.connect("size-changed", self._reposition)
        screen.connect("monitors-changed", self._reposition)
        self.connect("realize", self._reposition)
        self._reposition()

        # Animation & interaction state
        self.t = 0.0
        self.hovered = False
        self.hover_blend = 0.0
        self.burst_t = 0.0
        self.burst_active = False
        self.last_launch_ts = 0.0

        # Floating quantum motes
        self.motes = [
            {
                "x": random.uniform(-55, 55),
                "y": random.uniform(-55, 55),
                "vy": random.uniform(-0.35, -0.12),
                "r": random.uniform(1.0, 2.2),
                "phase": random.uniform(0, math.tau),
                "color": random.choice([C_CYAN, C_GOLD, C_MINT]),
            }
            for _ in range(14)
        ]

        self.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
        )
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
        self.connect("button-press-event", self._on_click)
        self.connect("draw", self._on_draw)

        GLib.timeout_add(16, self._on_tick)

    def _reposition(self, *args):
        screen = self.get_screen()
        geo_x, geo_y = 0, 0
        geo_w, geo_h = screen.get_width(), screen.get_height()
        try:
            disp = Gdk.Display.get_default()
            mon_obj = disp.get_primary_monitor() if disp else None
            if mon_obj is None and disp and disp.get_n_monitors() > 0:
                mon_obj = disp.get_monitor(0)
            if mon_obj is not None:
                geo = mon_obj.get_geometry()
                if geo.width > 0 and geo.height > 0:
                    geo_x, geo_y, geo_w, geo_h = geo.x, geo.y, geo.width, geo.height
            else:
                mon = screen.get_primary_monitor()
                if mon >= 0:
                    geo = screen.get_monitor_geometry(mon)
                    if geo.width > 0 and geo.height > 0:
                        geo_x, geo_y, geo_w, geo_h = geo.x, geo.y, geo.width, geo.height
        except Exception:
            pass

        scale = max(0.50, min(1.20, min(float(geo_w) / 1920.0, float(geo_h) / 1080.0)))
        self.ui_scale = scale
        self.win_w = max(105, int(round(self.base_w * scale)))
        self.win_h = max(115, int(round(self.base_h * scale)))
        self.set_size_request(self.win_w, self.win_h)
        self.resize(self.win_w, self.win_h)

        margin_x = max(10, int(round(28 * scale)))
        margin_y = max(48, int(round(74 * scale)))  # Clearance above bottom dock/panel
        x = geo_x + geo_w - self.win_w - margin_x
        y = geo_y + geo_h - self.win_h - margin_y
        x = max(geo_x + 4, min(x, geo_x + geo_w - self.win_w - 4))
        y = max(geo_y + 4, min(y, geo_y + geo_h - self.win_h - 4))
        self.move(x, y)
        self._ensure_above_wallpaper()
        self.queue_draw()

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

    def _on_enter(self, widget, event):
        self.hovered = True
        return False

    def _on_leave(self, widget, event):
        self.hovered = False
        return False

    def _on_click(self, widget, event):
        if event.button != 1:
            return False
        now = time.monotonic()
        if now - self.last_launch_ts < 1.5:
            return True
        self.last_launch_ts = now
        self.burst_active = True
        self.burst_t = 0.0

        # Launch 5-card auto-summon Tarot Oracle detached
        if os.path.exists(TAROT_ORACLE_BIN):
            subprocess.Popen(
                [TAROT_ORACLE_BIN, "--spread", "five", "--auto-summon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        return True

    def _on_tick(self):
        self.t += 0.016
        self.tick_count = getattr(self, "tick_count", 0) + 1
        if self.tick_count % 30 == 0:
            self._ensure_above_wallpaper()
        target_hover = 1.0 if self.hovered else 0.0
        self.hover_blend += (target_hover - self.hover_blend) * 0.14

        if self.burst_active:
            self.burst_t += 0.035
            if self.burst_t >= 1.0:
                self.burst_active = False
                self.burst_t = 0.0

        for m in self.motes:
            m["y"] += m["vy"] * (1.0 + self.hover_blend * 0.8)
            if m["y"] < -68:
                m["y"] = 58
                m["x"] = random.uniform(-52, 52)

        self.queue_draw()
        return True

    def _draw_card_sigil(self, cr, cw, ch, alpha, is_top=False):
        # Card body (pure transparent holographic frame - zero dark background to blend seamlessly with wallpaper)
        draw_rounded_rect(cr, -cw / 2, -ch / 2, cw, ch, 7)

        # Specular rim
        rim_col = C_GOLD if is_top and self.hover_blend > 0.4 else C_CYAN
        cr.set_source_rgba(*rim_col, (0.60 + 0.40 * self.hover_blend) * alpha)
        cr.set_line_width(1.4 if is_top else 0.9)
        cr.stroke()

        if is_top:
            # Inner sacred geometry & Jarvis circuit sigil
            cr.set_source_rgba(*C_CYAN, 0.35 * alpha)
            cr.set_line_width(0.8)
            draw_rounded_rect(cr, -cw / 2 + 5, -ch / 2 + 5, cw - 10, ch - 10, 4)
            cr.stroke()

            # Central quantum diamond + eye
            cr.save()
            cr.rotate(self.t * 0.35)
            cr.set_source_rgba(*C_GOLD, (0.45 + 0.4 * self.hover_blend) * alpha)
            cr.set_line_width(1.0)
            cr.arc(0, 0, 14, 0, math.tau)
            cr.stroke()
            cr.restore()

            cr.set_source_rgba(*C_CYAN, (0.55 + 0.4 * self.hover_blend) * alpha)
            cr.set_line_width(1.0)
            cr.move_to(0, -18)
            cr.line_to(12, 0)
            cr.line_to(0, 18)
            cr.line_to(-12, 0)
            cr.close_path()
            cr.stroke()

            # Core dot
            cr.set_source_rgba(*C_GOLD, 0.9 * alpha)
            cr.arc(0, 0, 2.6, 0, math.tau)
            cr.fill()

    def _on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        cr.save()
        cr.scale(self.ui_scale, self.ui_scale)

        cx = self.base_w / 2.0
        cy = self.base_h / 2.0 - 10.0

        # Stealth ambient alpha (0.48 idle -> 0.98 hover)
        alpha = 0.48 + 0.50 * self.hover_blend
        levitate = math.sin(self.t * 2.1) * 3.5

        # 1. Ambient Quantum Glow Halo
        glow_r = 78 + 14 * self.hover_blend
        glow = cairo.RadialGradient(cx, cy + levitate, 8, cx, cy + levitate, glow_r)
        glow.add_color_stop_rgba(0.0, *C_CYAN, 0.22 * alpha)
        glow.add_color_stop_rgba(0.55, *C_VIOLET, 0.10 * alpha)
        glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(glow)
        cr.arc(cx, cy + levitate, glow_r, 0, math.tau)
        cr.fill()

        # 2. Jarvis Counter-Rotating Orbital Telemetry Rings
        cr.save()
        cr.translate(cx, cy + levitate)

        # Outer dashed ring
        cr.save()
        cr.rotate(self.t * 0.45)
        cr.set_source_rgba(*C_CYAN, (0.28 + 0.45 * self.hover_blend) * alpha)
        cr.set_line_width(1.1)
        cr.set_dash([10, 6, 3, 6])
        cr.arc(0, 0, 68 + 6 * self.hover_blend, 0, math.tau)
        cr.stroke()
        cr.restore()

        # Inner gold arc segments
        cr.save()
        cr.rotate(-self.t * 0.75)
        cr.set_source_rgba(*C_GOLD, (0.25 + 0.55 * self.hover_blend) * alpha)
        cr.set_line_width(1.4)
        for k in range(3):
            a0 = k * (math.tau / 3.0)
            cr.arc(0, 0, 56 + 4 * self.hover_blend, a0, a0 + 0.85)
            cr.stroke()
        cr.restore()

        # Degree ticks
        cr.set_source_rgba(*C_CYAN, 0.30 * alpha)
        cr.set_line_width(0.8)
        for deg in range(0, 360, 15):
            rad = math.radians(deg)
            r1 = 73 + 6 * self.hover_blend
            r2 = r1 + (5 if deg % 45 == 0 else 2.5)
            cr.move_to(math.cos(rad) * r1, math.sin(rad) * r1)
            cr.line_to(math.cos(rad) * r2, math.sin(rad) * r2)
            cr.stroke()

        # 3. Floating Quantum Motes
        for m in self.motes:
            pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self.t * 3.0 + m["phase"]))
            cr.set_source_rgba(*m["color"], pulse * 0.75 * alpha)
            cr.arc(m["x"], m["y"], m["r"], 0, math.tau)
            cr.fill()

        # 4. 5-Card Holographic Stack (fans out smoothly on hover!)
        cw, ch = 54.0, 84.0
        for i in range(5):
            # i=0 is bottom card, i=4 is top card
            idx_from_top = 4 - i
            fan_spread = self.hover_blend
            burst_spread = math.sin(self.burst_t * math.pi) * 1.4 if self.burst_active else 0.0
            spread = fan_spread + burst_spread

            # Idle stack offset vs Hover fan offset
            ox = (-idx_from_top * 3.2) + (i - 2) * 11.5 * spread
            oy = (idx_from_top * 2.6) - abs(i - 2) * 2.5 * spread
            angle = (-0.04 * idx_from_top) + (i - 2) * 0.14 * spread

            cr.save()
            cr.translate(ox, oy)
            cr.rotate(angle)
            self._draw_card_sigil(cr, cw, ch, alpha * (0.65 + 0.08 * i), is_top=(i == 4))
            cr.restore()

        # 5. Click Shockwave Burst
        if self.burst_active:
            br = 20 + self.burst_t * 75
            ba = (1.0 - self.burst_t) * 0.9
            cr.set_source_rgba(*C_CYAN, ba)
            cr.set_line_width(2.2 * (1.0 - self.burst_t))
            cr.arc(0, 0, br, 0, math.tau)
            cr.stroke()

        cr.restore()

        # 6. Jarvis Micro-HUD Label below stack
        label_y = self.base_h - 24
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(9.5)
        txt = "CLICK: 5-CARD ORACLE" if self.hovered else "QUANTUM TAROT"
        ext = cr.text_extents(txt)

        pill_w = ext.width + 18
        pill_h = 18
        pill_x = cx - pill_w / 2
        pill_y = label_y - 13

        draw_rounded_rect(cr, pill_x, pill_y, pill_w, pill_h, 9)
        cr.set_source_rgba(*(C_GOLD if self.hovered else C_CYAN), (0.45 + 0.55 * self.hover_blend) * alpha)
        cr.set_line_width(0.9)
        cr.stroke()

        cr.set_source_rgba(*(C_GOLD if self.hovered else C_CYAN), 0.95 * alpha)
        cr.move_to(cx - ext.width / 2, label_y - 1)
        cr.show_text(txt)
        cr.restore()


def main():
    win = JarvisTarotDeckHUD()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
