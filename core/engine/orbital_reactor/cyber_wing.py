#!/usr/bin/env python3
# ==============================================================================
# 👑 FLOWORK OS — ORBITAL CYBER WINGS HUD ENGINE
# Architecture: Pure Optical Crystal Glass Sci-Fi Cockpit Wings
# Left Wing & Right Wing Manager with 1-App Single-Slot Invariant
# Co-authored-by: Flowork Architecture Board & Dr. Flow
# ==============================================================================

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import cairo
import math
import subprocess
import os
import sys
import signal
import time
import json
import socket
from datetime import datetime

# ── Dynamic Runtime Paths ──
RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
SOCK_PATH = os.path.join(RUNTIME_DIR, "flowork_cyber_wing.sock")
STATE_FILE = os.path.join(RUNTIME_DIR, "flowork_power_timer.json")

# ── Colors ──
C_VOID        = (0.035, 0.051, 0.086)      # Deep obsidian glass
C_SURFACE     = (0.055, 0.078, 0.125)      # Card surface
C_WELL        = (0.020, 0.030, 0.050)      # Recessed well
C_SPECULAR    = (1.000, 1.000, 1.000)      # White rim highlight
C_BORDER_BASE = (0.200, 0.350, 0.500)      # Base border

C_GREEN       = (0.000, 1.000, 0.400)      # Matrix Razor #00ff66
C_CYAN        = (0.000, 0.950, 1.000)      # Electric Cyan #00f2fe
C_AMBER       = (1.000, 0.700, 0.000)      # Solar Amber #ffb300 (Restart)
C_RED         = (1.000, 0.200, 0.350)      # Neon Crimson #ff3359 (Shutdown)
C_PURPLE      = (0.650, 0.350, 1.000)      # Quantum Purple (Suspend)
C_TEXT_WHITE  = (0.940, 0.960, 0.980)      # Crisp white
C_TEXT_MUTED  = (0.500, 0.580, 0.680)      # Muted slate

ACTIONS = [
    {
        "id": "reboot",
        "label": "RESTART",
        "icon": "⚡",
        "cmd": ["systemctl", "reboot"],
        "color": C_AMBER,
    },
    {
        "id": "poweroff",
        "label": "SHUTDOWN",
        "icon": "🛑",
        "cmd": ["systemctl", "poweroff"],
        "color": C_RED,
    },
    {
        "id": "suspend",
        "label": "SLEEP",
        "icon": "🌙",
        "cmd": ["systemctl", "suspend"],
        "color": C_CYAN,
    },
]

PRESETS = [
    {"label": "5m",  "seconds": 5 * 60},
    {"label": "15m", "seconds": 15 * 60},
    {"label": "30m", "seconds": 30 * 60},
    {"label": "45m", "seconds": 45 * 60},
    {"label": "1h",  "seconds": 60 * 60},
    {"label": "2h",  "seconds": 120 * 60},
]


def abort_timer():
    """Cancel active countdown and terminate daemon."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                st = json.load(f)
            dpid = st.get("daemon_pid")
            if dpid and dpid > 0:
                try:
                    os.kill(dpid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        except Exception:
            pass
        try:
            os.remove(STATE_FILE)
        except Exception:
            pass

    try:
        subprocess.run(["shutdown", "-c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    try:
        subprocess.run([
            "notify-send",
            "-u", "normal",
            "-a", "Flowork Power Engine",
            "-i", "system-shutdown-symbolic",
            "⏱️ Power Timer Aborted",
            "Scheduled countdown safely cancelled."
        ], check=False)
    except Exception:
        pass


def get_active_state():
    """Returns active state dict if valid timer is running."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            st = json.load(f)
        target = st.get("target_timestamp", 0)
        remaining = target - time.time()
        if remaining > 0:
            return st
        else:
            try:
                os.remove(STATE_FILE)
            except Exception:
                pass
            return None
    except Exception:
        return None


# ==============================================================================
# CYBER WING WINDOW COMPONENT
# ==============================================================================
class CyberWingWindow(Gtk.Window):
    def __init__(self, side: str = "left"):
        super().__init__(title=f"Flowork Cyber Wing ({side.upper()})")
        self.side = side.lower()  # "left" or "right"

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_accept_focus(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Dynamically calculate responsive geometry matching Forex, Crypto & Orbital Reactor
        self.update_geometry()
        screen.connect("size-changed", lambda *_: self.update_geometry())
        screen.connect("monitors-changed", lambda *_: self.update_geometry())

        # Active App in this Wing (Single-Slot Invariant!)
        self.active_app = None  # e.g. "timer", "system", etc.

        # Animation states (Slide & Bloom)
        self.is_open = False
        self.anim_progress = 0.0
        self.anim_id = None
        self.pulse_phase = 0.0

        # Timer App State
        self.timer_action = 0  # 0: reboot, 1: poweroff, 2: suspend
        self.timer_seconds = 15 * 60
        self.timer_counting = False
        self.timer_target = 0.0
        self.timer_active_total = 0
        self.timer_source_id = None

        # Hover & Hitbox Registry
        self.hover_x = -1
        self.hover_y = -1
        self._close_hitbox = None
        self._action_hitboxes = []
        self._preset_hitboxes = []
        self._step_hitboxes = []
        self._initiate_hitbox = None
        self._bg_hitbox = None
        self._cancel_hitbox = None
        self._time_well_hitbox = None

        self.hovered_close = False
        self.hovered_action = -1
        self.hovered_preset = -1
        self.hovered_step = None
        self.hovered_initiate = False
        self.hovered_bg = False
        self.hovered_cancel = False

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.SCROLL_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-press-event", self.on_click)
        self.connect("leave-notify-event", self.on_leave)
        self.connect("scroll-event", self.on_scroll)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)

        # Sync existing timer state if present
        self._sync_timer_state()
        self._start_pulse_ticker()

    def update_geometry(self):
        """
        Dynamically calculates responsive wing geometry:
        - TOP: Stops strictly below Forex Calendar line 3 (with safe gap)
        - BOTTOM: Stops strictly above Crypto Ticker line 1 (with safe gap)
        - WIDTH: Left wing matches Forex/Crypto left 4 columns; Right wing matches right 4 columns
        - NOTCH: Inward chevron apex stops precisely in front of central satellite nodes (4K RENDER / SUNO 59S)
        - RESPONSIVE: Fully recalculates on any monitor resolution (Ultrawide, FHD, Laptop, QHD, etc.)
        """
        screen = self.get_screen()
        sw = max(640, screen.get_width())
        sh = max(480, screen.get_height())

        # Exact scale formula matching reactor_hud.py & financial_orbit.py
        self.ui_scale = max(0.52, min(1.0, min(float(sw) / 1920.0, float(sh) / 1080.0)))
        scale = self.ui_scale

        cx = sw / 2.0
        cy = sh / 2.0

        gap_center = 142.0 * scale
        col_pitch = 158.0 * scale
        col_half_w = col_pitch / 2.0

        # Reactor HUD window geometry matching reactor_hud.py
        hud_h = min(816, max(400, sh - 140))
        hud_pos_y = max(132, int((sh - hud_h) // 2))

        # Vertical Safe Corridor: strictly between Forex bottom and Crypto top
        # Forex in reactor_hud: y_top = 92 * scale, line 3 is at y_top + 30 * scale, text height ~14 * scale
        forex_bottom_screen = hud_pos_y + (92.0 + 44.0) * scale
        crypto_top_screen = hud_pos_y + 705.0 * scale

        gap_v = 18.0 * scale
        self.dock_y = int(forex_bottom_screen + gap_v)
        bottom_y = int(crypto_top_screen - gap_v)
        self.win_h = max(300, bottom_y - self.dock_y)

        # Horizontal Safe Span: matching Forex & Crypto columns
        col_0_x = cx - gap_center - 3.0 * col_pitch
        col_3_x = cx - gap_center - 0.0 * col_pitch
        col_4_x = cx + gap_center + 0.0 * col_pitch
        col_7_x = cx + gap_center + 3.0 * col_pitch

        r_orbit = 222.0 * scale
        r_node = 44.0 * scale
        horn_clearance = 54.0 * scale
        notch_flange = 36.0 * scale

        # Outermost edges of Forex news columns
        col_0_outer = col_0_x - 44.0 * scale
        col_7_outer = col_7_x + 44.0 * scale

        if self.side == "left":
            # 4K RENDER equator node (180 deg) - Horns stay clear of circle
            left_node_outer = (cx - r_orbit) - r_node
            horn_screen_x = int(left_node_outer - horn_clearance)
            notch_apex_screen = horn_screen_x - notch_flange

            # Left boundary aligns flush with the outer edge ("akhir") of Forex news (Col 0)
            self.dock_x = int(col_0_outer)
            self.win_w = max(240, horn_screen_x - self.dock_x)

            # Inward notch apex indents smoothly
            self.notch_apex_x = notch_apex_screen - self.dock_x
            self.notch_depth = self.win_w - self.notch_apex_x

            self.content_x = 16.0 * scale
            self.content_w = max(200.0 * scale, self.notch_apex_x - self.content_x - 14.0 * scale)
        else:
            # SUNO 59S equator node (0 deg) - Horns stay clear of circle
            right_node_outer = (cx + r_orbit) + r_node
            horn_screen_x = int(right_node_outer + horn_clearance)
            notch_apex_screen = horn_screen_x + notch_flange

            # Right boundary aligns flush with outer edge ("akhir") of Forex news (Col 7)
            self.dock_x = horn_screen_x
            self.win_w = max(240, int(col_7_outer) - self.dock_x)

            # Inward notch apex indents smoothly
            self.notch_apex_x = notch_apex_screen - self.dock_x
            self.notch_depth = self.notch_apex_x

            self.content_x = self.notch_apex_x + 14.0 * scale
            self.content_w = max(200.0 * scale, (self.win_w - 16.0 * scale) - self.content_x)

        self.notch_half_h = 76.0 * scale
        self.reactor_local_y = cy - self.dock_y

        self.set_size_request(self.win_w, self.win_h)
        self.resize(self.win_w, self.win_h)
        self.move(self.dock_x, self.dock_y)
        self.queue_draw()

    def _sync_timer_state(self):
        st = get_active_state()
        if st:
            self.timer_counting = True
            self.timer_target = st.get("target_timestamp", 0)
            self.timer_active_total = st.get("total_seconds", 900)
            act_id = st.get("action", "reboot")
            for i, a in enumerate(ACTIONS):
                if a["id"] == act_id:
                    self.timer_action = i
                    break
            self._start_timer_ticker()

    def _start_pulse_ticker(self):
        def pulse_tick():
            self.pulse_phase = (self.pulse_phase + 0.05) % (2 * math.pi)
            if self.is_open and self.timer_counting:
                self.queue_draw()
            return True
        GLib.timeout_add(33, pulse_tick)

    def _start_timer_ticker(self):
        if self.timer_source_id:
            GLib.source_remove(self.timer_source_id)

        def tick():
            if not self.timer_counting:
                return False
            now = time.time()
            rem = self.timer_target - now
            if rem <= 0:
                self.timer_counting = False
                self.timer_source_id = None
                self.queue_draw()
                # Fire action immediately
                act = ACTIONS[self.timer_action]
                try:
                    subprocess.Popen(act["cmd"], start_new_session=True)
                except Exception:
                    subprocess.Popen(["sudo", "-n"] + act["cmd"], start_new_session=True)
                return False
            self.queue_draw()
            return True

        self.timer_source_id = GLib.timeout_add(100, tick)

    # ── Single-Slot App Switcher / Wing Control ──
    def open_app(self, app_name: str):
        """Open or swap app in this wing. Enforces 1-App Invariant."""
        app_name = app_name.lower().strip()
        self.active_app = app_name
        self.is_open = True
        self.show_all()
        self.present()
        self._animate_wing(target=1.0)

    def close_wing(self):
        """Retract and hide this wing."""
        self._animate_wing(target=0.0, on_done=lambda: self.hide())

    def toggle_app(self, app_name: str):
        """Toggle app: If already open with same app -> close. If different -> swap."""
        app_name = app_name.lower().strip()
        if self.is_open and self.active_app == app_name:
            self.close_wing()
        else:
            self.open_app(app_name)

    def _animate_wing(self, target: float, on_done=None):
        if self.anim_id:
            GLib.source_remove(self.anim_id)

        step = 0.12 if target > self.anim_progress else -0.15

        def tick():
            self.anim_progress += step
            if (step > 0 and self.anim_progress >= target) or (step < 0 and self.anim_progress <= target):
                self.anim_progress = target
                self.anim_id = None
                if target == 0.0:
                    self.is_open = False
                    self.active_app = None
                if on_done:
                    on_done()
                self.queue_draw()
                return False
            self.queue_draw()
            return True

        self.anim_id = GLib.timeout_add(16, tick)

    def _ease_out(self, t):
        return 1.0 - (1.0 - t) ** 3

    # ==========================================================================
    # CAIRO RENDERING: CHEVRON / NOTCHED WING CHASSIS
    # ==========================================================================
    def on_draw(self, _widget, cr):
        if self.anim_progress <= 0.001:
            return True

        p = self._ease_out(self.anim_progress)
        w, h = self.win_w, self.win_h

        # Clear canvas
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # Slide offset during animation (slides outward from center)
        slide_offset = (1.0 - p) * 60.0
        draw_x = -slide_offset if self.side == "left" else slide_offset

        cr.save()
        cr.translate(draw_x, 0)

        # ── 1. Create Notched / Chevron Wing Path ──
        self._build_wing_path(cr, w, h)

        # Fill with Cosmic Obsidian Optical Ice Glass
        cr.set_source_rgba(C_VOID[0], C_VOID[1], C_VOID[2], 0.88 * p)
        cr.fill_preserve()

        # Specular Rim Gradient on Edge
        lin = cairo.LinearGradient(0, 0, 0, h)
        act_col = ACTIONS[self.timer_action]["color"] if self.active_app == "timer" else C_CYAN
        lin.add_color_stop_rgba(0.00, 1.0, 1.0, 1.0, 0.50 * p)
        lin.add_color_stop_rgba(0.15, act_col[0], act_col[1], act_col[2], 0.40 * p)
        lin.add_color_stop_rgba(0.85, act_col[0], act_col[1], act_col[2], 0.15 * p)
        lin.add_color_stop_rgba(1.00, 1.0, 1.0, 1.0, 0.30 * p)
        cr.set_source(lin)
        cr.set_line_width(1.8)
        cr.stroke()

        pctx = PangoCairo.create_context(cr)
        layout = Pango.Layout.new(pctx)

        # ── 2. Horn Tactical Telemetry & Cyber Circuitry ──
        self._draw_horn_telemetry(cr, layout, w, h, p)

        # ── 3. Wing Header Bar ──
        self._draw_wing_header(cr, layout, w, h, p)

        # ── 4. Render Active App Content inside Wing ──
        if self.active_app == "timer":
            self._draw_timer_content(cr, layout, w, h, p)
        else:
            self._draw_placeholder_content(cr, layout, w, h, p)

        cr.restore()
        return True

    def _build_wing_path(self, cr, w, h):
        """Constructs the angular cyberpunk wing with inward chevron notch matching user sketch."""
        scale = getattr(self, "ui_scale", 1.0)
        pad = 8.0 * scale
        r = 16.0 * scale

        x0, y0 = pad, pad
        x1, y1 = w - pad, h - pad
        mid_y = getattr(self, "reactor_local_y", (y0 + y1) / 2.0)
        notch_apex = getattr(self, "notch_apex_x", (w - 60.0 if self.side == "left" else 60.0))
        notch_half_h = getattr(self, "notch_half_h", 76.0 * scale)

        cr.new_path()
        if self.side == "left":
            # Left wing: Notch is on the RIGHT side (facing the center reactor node)
            cr.move_to(x0 + r, y0)
            cr.line_to(x1 - r, y0)
            cr.arc(x1 - r, y0 + r, r, -math.pi / 2, 0)
            # Upper right horn edge down to notch
            cr.line_to(x1, mid_y - notch_half_h)
            # Inward notch (indentation towards left towards apex)
            cr.line_to(notch_apex, mid_y)
            # Notch recovery outward towards lower horn
            cr.line_to(x1, mid_y + notch_half_h)
            # Lower right horn edge down
            cr.line_to(x1, y1 - r)
            cr.arc(x1 - r, y1 - r, r, 0, math.pi / 2)
            # Bottom edge to left
            cr.line_to(x0 + r, y1)
            cr.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi)
            # Straight left outer edge
            cr.line_to(x0, y0 + r)
            cr.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2)
        else:
            # Right wing: Notch is on the LEFT side (facing center reactor node)
            cr.move_to(x0 + r, y0)
            cr.line_to(x1 - r, y0)
            cr.arc(x1 - r, y0 + r, r, -math.pi / 2, 0)
            # Right outer edge straight down
            cr.line_to(x1, y1 - r)
            cr.arc(x1 - r, y1 - r, r, 0, math.pi / 2)
            # Bottom edge to left
            cr.line_to(x0 + r, y1)
            cr.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi)
            # Lower left horn edge up to notch
            cr.line_to(x0, mid_y + notch_half_h)
            # Inward notch (indentation towards right towards apex)
            cr.line_to(notch_apex, mid_y)
            # Notch recovery outward towards upper horn
            cr.line_to(x0, mid_y - notch_half_h)
            # Upper left horn edge up
            cr.line_to(x0, y0 + r)
            cr.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2)

        cr.close_path()

    def _draw_horn_telemetry(self, cr, layout, w, h, p):
        pad = 8.0
        cr.save()
        if self.side == "left":
            horn_x0 = getattr(self, "notch_apex_x", w - 180.0) + 14.0
            horn_x1 = w - pad - 12.0
            if horn_x1 > horn_x0 + 20:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.22 * p)
                cr.set_line_width(1.0)
                for lx in range(int(horn_x0), int(horn_x1), 16):
                    cr.move_to(lx, 16)
                    cr.line_to(lx + 8, 30)
                cr.stroke()

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
                layout.set_text("ORBITAL FLANK // L-01", -1)
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.60 * p)
                cr.move_to(horn_x0 + 4, 38)
                PangoCairo.show_layout(cr, layout)

                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.22 * p)
                cr.set_line_width(1.0)
                for lx in range(int(horn_x0), int(horn_x1), 16):
                    cr.move_to(lx, h - 30)
                    cr.line_to(lx + 8, h - 16)
                cr.stroke()

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
                layout.set_text("SYS SYNC // LOCKED", -1)
                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.60 * p)
                cr.move_to(horn_x0 + 4, h - 46)
                PangoCairo.show_layout(cr, layout)
        else:
            horn_x0 = pad + 12.0
            horn_x1 = getattr(self, "notch_apex_x", 180.0) - 14.0
            if horn_x1 > horn_x0 + 20:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.22 * p)
                cr.set_line_width(1.0)
                for lx in range(int(horn_x0), int(horn_x1), 16):
                    cr.move_to(lx, 16)
                    cr.line_to(lx - 8, 30)
                cr.stroke()

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
                layout.set_text("ORBITAL FLANK // R-02", -1)
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.60 * p)
                cr.move_to(horn_x0 + 4, 38)
                PangoCairo.show_layout(cr, layout)

                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.22 * p)
                cr.set_line_width(1.0)
                for lx in range(int(horn_x0), int(horn_x1), 16):
                    cr.move_to(lx, h - 30)
                    cr.line_to(lx - 8, h - 16)
                cr.stroke()

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
                layout.set_text("SYS SYNC // LOCKED", -1)
                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.60 * p)
                cr.move_to(horn_x0 + 4, h - 46)
                PangoCairo.show_layout(cr, layout)
        cr.restore()

    def _draw_wing_header(self, cr, layout, w, h, p):
        pad = 8.0
        sep_y = 52.0
        cx = getattr(self, "content_x", 24.0)
        cw = getattr(self, "content_w", w - 48.0)

        # Separator line
        cr.new_path()
        cr.set_source_rgba(0.2, 0.4, 0.6, 0.22 * p)
        cr.move_to(cx, sep_y)
        cr.line_to(cx + cw, sep_y)
        cr.set_line_width(1.0)
        cr.stroke()

        # Title indicator pill
        cr.new_path()
        act_col = ACTIONS[self.timer_action]["color"] if self.active_app == "timer" else C_CYAN
        dot_x, dot_y, dot_r = cx + 8, 28, 4.5
        cr.arc(dot_x, dot_y, dot_r, 0, 2 * math.pi)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.95 * p)
        cr.fill()

        # Dot ambient glow
        cr.arc(dot_x, dot_y, dot_r + 3.0, 0, 2 * math.pi)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.25 * p)
        cr.fill()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10.5"))
        app_title = "POWER CONTROL" if self.active_app == "timer" else (self.active_app or "HUD WING").upper()
        layout.set_text(f"{self.side.upper()} WING // {app_title}", -1)
        tw, th = layout.get_pixel_size()

        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.95 * p)
        cr.move_to(cx + 22, 28 - th / 2)
        PangoCairo.show_layout(cr, layout)

        # Retract / Close arrow button
        cb_x, cb_y, cb_r = cx + cw - 14, 28, 12
        cr.new_path()
        cr.arc(cb_x, cb_y, cb_r, 0, 2 * math.pi)
        if self.hovered_close:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.35 * p)
            cr.fill_preserve()
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.85 * p)
        else:
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.08 * p)
            cr.fill_preserve()
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.25 * p)
        cr.set_line_width(1.0)
        cr.stroke()

        # Close X icon
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.85 * p)
        cr.set_line_width(1.5)
        cr.move_to(cb_x - 4, cb_y - 4)
        cr.line_to(cb_x + 4, cb_y + 4)
        cr.move_to(cb_x + 4, cb_y - 4)
        cr.line_to(cb_x - 4, cb_y + 4)
        cr.stroke()
        self._close_hitbox = (cb_x - cb_r, cb_y - cb_r, cb_r * 2, cb_r * 2)

    # ==========================================================================
    # TIMER CONTENT INSIDE WING
    # ==========================================================================
    def _draw_timer_content(self, cr, layout, w, h, p):
        # Header tabs: [ RESTART ] [ SHUTDOWN ] [ SLEEP ]
        tab_y = 66
        tab_h = 36
        gap = 6
        cx = getattr(self, "content_x", 24.0)
        cw = getattr(self, "content_w", w - 48.0)
        avail_w = cw
        tab_w = (avail_w - (len(ACTIONS) - 1) * gap) / len(ACTIONS)
        self._action_hitboxes = []

        for i, act in enumerate(ACTIONS):
            tx = cx + i * (tab_w + gap)
            is_sel = (i == self.timer_action)
            is_hov = (i == self.hovered_action)
            col = act["color"]

            cr.new_path()
            self._rounded_rect(cr, tx, tab_y, tab_w, tab_h, 8)
            if is_sel:
                lin = cairo.LinearGradient(tx, tab_y, tx, tab_y + tab_h)
                lin.add_color_stop_rgba(0.0, col[0], col[1], col[2], 0.35 * p)
                lin.add_color_stop_rgba(1.0, col[0], col[1], col[2], 0.12 * p)
                cr.set_source(lin)
                cr.fill_preserve()
                cr.set_source_rgba(col[0], col[1], col[2], 0.90 * p)
                cr.set_line_width(1.5)
                cr.stroke()
            elif is_hov:
                cr.set_source_rgba(col[0], col[1], col[2], 0.15 * p)
                cr.fill_preserve()
                cr.set_source_rgba(col[0], col[1], col[2], 0.45 * p)
                cr.set_line_width(1.0)
                cr.stroke()
            else:
                cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.50 * p)
                cr.fill_preserve()
                cr.set_source_rgba(C_BORDER_BASE[0], C_BORDER_BASE[1], C_BORDER_BASE[2], 0.20 * p)
                cr.set_line_width(0.8)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9"))
            layout.set_text(f"{act['icon']} {act['label']}", -1)
            tw, th = layout.get_pixel_size()
            if is_sel:
                cr.set_source_rgba(col[0], col[1], col[2], 1.0 * p)
            else:
                cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.70 * p)
            cr.move_to(tx + (tab_w - tw) / 2, tab_y + (tab_h - th) / 2)
            PangoCairo.show_layout(cr, layout)

            self._action_hitboxes.append((tx, tab_y, tab_w, tab_h))

        if self.timer_counting:
            self._draw_timer_countdown(cr, layout, w, h, p)
        else:
            self._draw_timer_setup(cr, layout, w, h, p)

    def _draw_timer_setup(self, cr, layout, w, h, p):
        cx = getattr(self, "content_x", 24.0)
        cw = getattr(self, "content_w", w - 48.0)
        avail_w = cw
        act_col = ACTIONS[self.timer_action]["color"]

        # Presets row
        pre_label_y = 114
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8"))
        layout.set_text("DURATION PRESET", -1)
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.75 * p)
        cr.move_to(cx + 2, pre_label_y)
        PangoCairo.show_layout(cr, layout)

        pre_y = 130
        pre_h = 30
        pre_gap = 6
        cols = len(PRESETS)
        pre_w = (avail_w - (cols - 1) * pre_gap) / cols
        self._preset_hitboxes = []

        for i, pre in enumerate(PRESETS):
            px = cx + i * (pre_w + pre_gap)
            is_sel = (self.timer_seconds == pre["seconds"])
            is_hov = (i == self.hovered_preset)

            cr.new_path()
            self._rounded_rect(cr, px, pre_y, pre_w, pre_h, 7)
            if is_sel:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.24 * p)
                cr.fill_preserve()
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.90 * p)
                cr.set_line_width(1.4)
                cr.stroke()
            elif is_hov:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.10 * p)
                cr.fill_preserve()
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.40 * p)
                cr.set_line_width(0.9)
                cr.stroke()
            else:
                cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.40 * p)
                cr.fill_preserve()
                cr.set_source_rgba(0.2, 0.3, 0.4, 0.25 * p)
                cr.set_line_width(0.7)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.5"))
            layout.set_text(pre["label"], -1)
            tw, th = layout.get_pixel_size()
            if is_sel:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 1.0 * p)
            else:
                cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.65 * p)
            cr.move_to(px + (pre_w - tw) / 2, pre_y + (pre_h - th) / 2)
            PangoCairo.show_layout(cr, layout)

            self._preset_hitboxes.append((px, pre_y, pre_w, pre_h))

        # Recessed Digital Well
        well_y = 172
        well_h = 136
        well_w = avail_w
        well_x = cx
        self._time_well_hitbox = (well_x, well_y, well_w, well_h)

        cr.new_path()
        self._rounded_rect(cr, well_x, well_y, well_w, well_h, 14)
        cr.set_source_rgba(C_WELL[0], C_WELL[1], C_WELL[2], 0.85 * p)
        cr.fill_preserve()
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.28 * p)
        cr.set_line_width(1.0)
        cr.stroke()

        # Step Adjustment Buttons Layout
        self._step_hitboxes = []
        step_btn_w = 34
        step_btn_h = 28
        step_y_top = well_y + 24
        step_y_bot = well_y + 70

        left_steps = [
            ("-10m", -600, well_x + 10, step_y_top),
            ("-1m",  -60,  well_x + 10, step_y_bot),
        ]
        right_steps = [
            ("+1m",  +60,  well_x + well_w - 10 - step_btn_w, step_y_top),
            ("+5m",  +300, well_x + well_w - 10 - step_btn_w, step_y_bot),
        ]

        for s in left_steps:
            lbl, delta, sx, sy = s
            self._draw_step_btn(cr, layout, lbl, delta, sx, sy, step_btn_w, step_btn_h, p)

        for s in right_steps:
            lbl, delta, sx, sy = s
            self._draw_step_btn(cr, layout, lbl, delta, sx, sy, step_btn_w, step_btn_h, p)

        # Center Digital Clock
        hours = self.timer_seconds // 3600
        mins = (self.timer_seconds % 3600) // 60
        secs = self.timer_seconds % 60

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 24"))
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        layout.set_text(time_str, -1)
        tw, th = layout.get_pixel_size()

        clock_cx = well_x + well_w / 2

        # Ambient glow shadow
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.25 * p)
        cr.move_to(clock_cx - tw / 2, well_y + 42 - th / 2 + 1)
        PangoCairo.show_layout(cr, layout)

        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.98 * p)
        cr.move_to(clock_cx - tw / 2, well_y + 42 - th / 2)
        PangoCairo.show_layout(cr, layout)

        # Sub-labels
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text("HRS       MINS       SECS", -1)
        sw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.70 * p)
        cr.move_to(clock_cx - sw / 2, well_y + 72)
        PangoCairo.show_layout(cr, layout)

        # Scroll hint
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("▲ SCROLL MOUSE WHEEL ▲", -1)
        hw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.50 * p)
        cr.move_to(clock_cx - hw / 2, well_y + well_h - 18)
        PangoCairo.show_layout(cr, layout)

        # Target Timestamp info
        target_dt = datetime.fromtimestamp(time.time() + self.timer_seconds)
        time_fmt = target_dt.strftime("%H:%M:%S")

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 9"))
        act_info = ACTIONS[self.timer_action]
        txt = f"⚡ {act_info['label']} armed for {time_fmt} ({self.timer_seconds // 60}m)"
        layout.set_text(txt, -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.85 * p)
        cr.move_to(clock_cx - tw / 2, well_y + well_h + 16)
        PangoCairo.show_layout(cr, layout)

        # Initiate Button
        btn_y = well_y + well_h + 46
        btn_w = min(260.0 * getattr(self, "ui_scale", 1.0), avail_w - 20)
        btn_h = 46
        btn_x = well_x + (well_w - btn_w) / 2
        self._initiate_hitbox = (btn_x, btn_y, btn_w, btn_h)

        cr.new_path()
        self._rounded_rect(cr, btn_x, btn_y, btn_w, btn_h, 12)
        if self.hovered_initiate:
            lin = cairo.LinearGradient(btn_x, btn_y, btn_x, btn_y + btn_h)
            lin.add_color_stop_rgba(0.0, act_col[0], act_col[1], act_col[2], 0.45 * p)
            lin.add_color_stop_rgba(1.0, act_col[0], act_col[1], act_col[2], 0.18 * p)
            cr.set_source(lin)
            cr.fill_preserve()
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.95 * p)
            cr.set_line_width(1.8)
            cr.stroke()
        else:
            lin = cairo.LinearGradient(btn_x, btn_y, btn_x, btn_y + btn_h)
            lin.add_color_stop_rgba(0.0, act_col[0], act_col[1], act_col[2], 0.30 * p)
            lin.add_color_stop_rgba(1.0, act_col[0], act_col[1], act_col[2], 0.10 * p)
            cr.set_source(lin)
            cr.fill_preserve()
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.65 * p)
            cr.set_line_width(1.4)
            cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10.5"))
        btn_txt = f"INITIATE {act_info['label']} TIMER"
        layout.set_text(btn_txt, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 1.0 * p)
        cr.move_to(btn_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Footer
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("FLOWORK OS SOVEREIGN WING HUD • PERSISTENT DAEMON BACKED", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.40 * p)
        cr.move_to(clock_cx - tw / 2, h - 22)
        PangoCairo.show_layout(cr, layout)

    def _draw_step_btn(self, cr, layout, label, delta, x, y, w, h, p):
        is_hov = (self.hovered_step == label)
        cr.new_path()
        self._rounded_rect(cr, x, y, w, h, 7)
        if is_hov:
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.25 * p)
            cr.fill_preserve()
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.80 * p)
            cr.set_line_width(1.2)
            cr.stroke()
        else:
            cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.70 * p)
            cr.fill_preserve()
            cr.set_source_rgba(0.3, 0.4, 0.5, 0.35 * p)
            cr.set_line_width(0.8)
            cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.5"))
        layout.set_text(label, -1)
        tw, th = layout.get_pixel_size()
        if is_hov:
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 1.0 * p)
        else:
            cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.75 * p)
        cr.move_to(x + (w - tw) / 2, y + (h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        self._step_hitboxes.append((label, delta, x, y, w, h))

    def _draw_timer_countdown(self, cr, layout, w, h, p):
        act_info = ACTIONS[self.timer_action]
        act_col = act_info["color"]

        now = time.time()
        remaining = max(0.0, self.timer_target - now)
        total = max(1.0, float(self.timer_active_total))
        frac = min(1.0, max(0.0, remaining / total))
        is_imminent = (remaining <= 60.0)

        cx = getattr(self, "content_x", 24.0)
        cw = getattr(self, "content_w", w - 48.0)

        # Circular Reactor Gauge
        rcx, rcy = cx + cw / 2, 220
        rr = 70.0 * getattr(self, "ui_scale", 1.0)
        ring_w = 7.0

        cr.new_path()
        cr.set_line_width(ring_w)
        cr.set_source_rgba(0.12, 0.16, 0.22, 0.60 * p)
        cr.arc(rcx, rcy, rr, 0, 2 * math.pi)
        cr.stroke()

        pulse_alpha = 0.70 + 0.25 * math.sin(self.pulse_phase * (3.0 if is_imminent else 1.0))
        cr.new_path()
        start_angle = -math.pi / 2
        end_angle = start_angle + (2 * math.pi * frac)
        cr.set_line_width(ring_w)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], pulse_alpha * p)
        cr.arc(rcx, rcy, rr, start_angle, end_angle)
        cr.stroke()

        # Digital Countdown Text inside Ring
        rem_int = int(remaining)
        chrs = rem_int // 3600
        cmins = (rem_int % 3600) // 60
        csecs = rem_int % 60

        if chrs > 0:
            c_str = f"{chrs:02d}:{cmins:02d}:{csecs:02d}"
            font_size = "24"
        else:
            c_str = f"{cmins:02d}:{csecs:02d}"
            font_size = "32"

        layout.set_font_description(Pango.FontDescription(f"JetBrains Mono Bold {font_size}"))
        layout.set_text(c_str, -1)
        tw, th = layout.get_pixel_size()

        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.98 * p)
        cr.move_to(rcx - tw / 2, rcy - th / 2 - 4)
        PangoCairo.show_layout(cr, layout)

        # Status badge below time
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8"))
        if is_imminent:
            layout.set_text("CRITICAL: IMMINENT", -1)
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.95 * p)
        else:
            layout.set_text(f"{act_info['label']} ARMED", -1)
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.90 * p)
        stw, _ = layout.get_pixel_size()
        cr.move_to(rcx - stw / 2, rcy + th / 2 - 2)
        PangoCairo.show_layout(cr, layout)

        # Target info line
        target_dt = datetime.fromtimestamp(self.timer_target)
        t_fmt = target_dt.strftime("%H:%M:%S WIB")
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 9"))
        status_line = f"Target Execution: {t_fmt} ({rem_int}s left)"
        layout.set_text(status_line, -1)
        itw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.80 * p)
        cr.move_to(rcx - itw / 2, 335)
        PangoCairo.show_layout(cr, layout)

        # Dual Buttons: [ RETRACT TO BACKGROUND ] & [ ABORT TIMER ]
        btn_y = 380
        gap = 12
        avail_w = cw
        btn_w = (avail_w - gap) / 2
        btn_h = 44

        # 1. RETRACT WING Button
        bg_x = cx
        self._bg_hitbox = (bg_x, btn_y, btn_w, btn_h)

        cr.new_path()
        self._rounded_rect(cr, bg_x, btn_y, btn_w, btn_h, 12)
        if self.hovered_bg:
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.25 * p)
            cr.fill_preserve()
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.85 * p)
            cr.set_line_width(1.5)
            cr.stroke()
        else:
            cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.70 * p)
            cr.fill_preserve()
            cr.set_source_rgba(C_BORDER_BASE[0], C_BORDER_BASE[1], C_BORDER_BASE[2], 0.40 * p)
            cr.set_line_width(1.0)
            cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9"))
        layout.set_text("RETRACT WING", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.90 * p)
        cr.move_to(bg_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 2. ABORT TIMER Button
        abort_x = cx + btn_w + gap
        self._cancel_hitbox = (abort_x, btn_y, btn_w, btn_h)

        cr.new_path()
        self._rounded_rect(cr, abort_x, btn_y, btn_w, btn_h, 12)
        if self.hovered_cancel:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.35 * p)
            cr.fill_preserve()
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.95 * p)
            cr.set_line_width(1.8)
            cr.stroke()
        else:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.16 * p)
            cr.fill_preserve()
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.60 * p)
            cr.set_line_width(1.2)
            cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9"))
        layout.set_text("ABORT TIMER", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 1.0 * p)
        cr.move_to(abort_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

    def _draw_placeholder_content(self, cr, layout, w, h, p):
        cx = getattr(self, "content_x", 24.0)
        cw = getattr(self, "content_w", w - 48.0)
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 12"))
        layout.set_text(f"{self.active_app.upper()} MODULE LOADED", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.85 * p)
        cr.move_to(cx + (cw - tw) / 2, 200)
        PangoCairo.show_layout(cr, layout)

    # ==========================================================================
    # INTERACTION & EVENTS
    # ==========================================================================
    def on_motion(self, _w, event):
        self.hover_x, self.hover_y = event.x, event.y
        self._update_hover()
        self.queue_draw()

    def on_leave(self, *_):
        self.hover_x, self.hover_y = -1, -1
        self.hovered_close = False
        self.hovered_action = -1
        self.hovered_preset = -1
        self.hovered_step = None
        self.hovered_initiate = False
        self.hovered_bg = False
        self.hovered_cancel = False
        self.queue_draw()

    def _update_hover(self):
        x, y = self.hover_x, self.hover_y
        self.hovered_close = False
        self.hovered_action = -1
        self.hovered_preset = -1
        self.hovered_step = None
        self.hovered_initiate = False
        self.hovered_bg = False
        self.hovered_cancel = False

        if self._close_hitbox:
            bx, by, bw, bh = self._close_hitbox
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.hovered_close = True
                return

        if self.active_app == "timer":
            if self.timer_counting:
                if self._bg_hitbox:
                    bx, by, bw, bh = self._bg_hitbox
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_bg = True
                        return
                if self._cancel_hitbox:
                    bx, by, bw, bh = self._cancel_hitbox
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_cancel = True
                        return
            else:
                for i, hb in enumerate(self._action_hitboxes):
                    bx, by, bw, bh = hb
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_action = i
                        return
                for i, hb in enumerate(self._preset_hitboxes):
                    bx, by, bw, bh = hb
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_preset = i
                        return
                for item in self._step_hitboxes:
                    lbl, _, bx, by, bw, bh = item
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_step = lbl
                        return
                if self._initiate_hitbox:
                    bx, by, bw, bh = self._initiate_hitbox
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_initiate = True
                        return

    def on_click(self, _w, event):
        if event.button != 1:
            return

        if self.hovered_close:
            self.close_wing()
            return

        if self.active_app == "timer":
            if self.timer_counting:
                if self.hovered_bg:
                    self.close_wing()
                    return
                if self.hovered_cancel:
                    abort_timer()
                    self.timer_counting = False
                    if self.timer_source_id:
                        GLib.source_remove(self.timer_source_id)
                        self.timer_source_id = None
                    self.queue_draw()
                    return
            else:
                if self.hovered_action >= 0:
                    self.timer_action = self.hovered_action
                    self.queue_draw()
                    return
                if self.hovered_preset >= 0:
                    self.timer_seconds = PRESETS[self.hovered_preset]["seconds"]
                    self.queue_draw()
                    return
                if self.hovered_step:
                    for item in self._step_hitboxes:
                        lbl, delta, _, _, _, _ = item
                        if lbl == self.hovered_step:
                            self.timer_seconds = max(60, min(86400, self.timer_seconds + delta))
                            self.queue_draw()
                            return
                if self.hovered_initiate:
                    self._arm_timer()
                    return

    def on_scroll(self, _w, event):
        if self.active_app == "timer" and not self.timer_counting:
            if self._time_well_hitbox:
                bx, by, bw, bh = self._time_well_hitbox
                if bx <= event.x <= bx + bw and by <= event.y <= by + bh:
                    delta = 60 if event.direction == Gdk.ScrollDirection.UP else -60
                    self.timer_seconds = max(60, min(86400, self.timer_seconds + delta))
                    self.queue_draw()

    def on_key_press(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close_wing()
            return True
        return False

    def _arm_timer(self):
        """Initiates daemon and arms timer."""
        now = time.time()
        self.timer_target = now + self.timer_seconds
        self.timer_active_total = self.timer_seconds
        self.timer_counting = True

        act = ACTIONS[self.timer_action]

        st = {
            "target_timestamp": self.timer_target,
            "total_seconds": self.timer_active_total,
            "action": act["id"],
            "action_label": act["label"],
            "command": " ".join(act["cmd"]),
            "daemon_pid": 0,
            "created_at": now
        }
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(st, f, indent=2)
        except Exception:
            pass

        cmd_daemon = [
            sys.executable,
            "/opt/floworkos/engine/shutdown_timer/shutdown_timer.py",
            "--daemon",
            str(self.timer_target),
            act["id"]
        ]
        proc = subprocess.Popen(
            cmd_daemon,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        st["daemon_pid"] = proc.pid
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(st, f, indent=2)
        except Exception:
            pass

        mins_left = max(1, self.timer_seconds // 60)
        try:
            subprocess.Popen([
                "notify-send",
                "-u", "normal",
                "-a", "Flowork Power Engine",
                "-i", "system-shutdown-symbolic",
                f"⏱️ {act['label']} Timer Armed (Left Wing)",
                f"System will {act['label'].lower()} in {mins_left} min. Backed by persistent daemon."
            ])
        except Exception:
            pass

        self._start_timer_ticker()
        self.queue_draw()

    def on_destroy(self, *_):
        if self.timer_source_id:
            GLib.source_remove(self.timer_source_id)
        if self.anim_id:
            GLib.source_remove(self.anim_id)

    def _rounded_rect(self, cr, x, y, w, h, r):
        cr.new_path()
        cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        cr.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
        cr.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
        cr.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
        cr.close_path()


# ==============================================================================
# CYBER WING SERVICE & DAEMON IPC LISTENER
# ==============================================================================
class CyberWingService:
    def __init__(self):
        self.left_wing = CyberWingWindow("left")
        self.right_wing = CyberWingWindow("right")
        self._setup_ipc()

    def _setup_ipc(self):
        if os.path.exists(SOCK_PATH):
            try:
                os.remove(SOCK_PATH)
            except Exception:
                pass

        self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_sock.bind(SOCK_PATH)
        self.server_sock.listen(5)
        self.server_sock.setblocking(False)

        GLib.io_add_watch(self.server_sock.fileno(), GLib.IO_IN, self._on_client_connect)

    def _on_client_connect(self, source, condition):
        try:
            conn, _ = self.server_sock.accept()
            conn.setblocking(True)
            data = conn.recv(1024).decode("utf-8").strip()
            conn.close()
            if data:
                self._handle_command(data)
        except Exception:
            pass
        return True

    def _handle_command(self, cmd_line: str):
        # e.g., "toggle left timer", "open left timer", "close left", etc.
        parts = cmd_line.split()
        if not parts:
            return

        action = parts[0].lower()
        side = parts[1].lower() if len(parts) > 1 else "left"
        app = parts[2].lower() if len(parts) > 2 else "timer"

        target_wing = self.left_wing if side == "left" else self.right_wing

        if action == "toggle":
            target_wing.toggle_app(app)
        elif action == "open":
            target_wing.open_app(app)
        elif action == "close":
            target_wing.close_wing()
        elif action == "abort":
            abort_timer()


# ==============================================================================
# CLI IPC CLIENT OR SERVER ENTRYPOINT
# ==============================================================================
def send_ipc(command: str) -> bool:
    """Attempts to send command to existing Cyber Wing daemon."""
    if not os.path.exists(SOCK_PATH):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCK_PATH)
        s.sendall(command.encode("utf-8"))
        s.close()
        return True
    except Exception:
        return False


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    args = sys.argv[1:]
    cmd_str = " ".join(args) if args else "toggle left timer"

    # If already running as daemon service, send IPC command and return
    if send_ipc(cmd_str):
        print(f"Dispatched command to Cyber Wing service: {cmd_str}")
        return

    # Otherwise, start service and execute initial command
    service = CyberWingService()
    service._handle_command(cmd_str)
    Gtk.main()


if __name__ == "__main__":
    main()
