#!/usr/bin/env python3
# ==============================================================================
# 👑 FLOWORK OS — SOVEREIGN POWER CONTROL & COUNTDOWN TIMER ENGINE
# Architecture: Pure Optical Crystal Glass HUD (Cairo + GTK3 + Detached Daemon)
# Fully Decoupled & Resilient — Executes systemctl reboot/poweroff/suspend reliably
# ==============================================================================

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
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
from datetime import datetime

# ── Dynamic User & Runtime Paths ──
RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
STATE_FILE = os.path.join(RUNTIME_DIR, "flowork_power_timer.json")

# ── Pure Optical Crystal Glass Palette ──
C_VOID        = (0.035, 0.051, 0.086)      # #090d16
C_SURFACE     = (0.055, 0.078, 0.125)      # #0e1420
C_WELL        = (0.020, 0.030, 0.050)      # Recessed well
C_SPECULAR    = (1.000, 1.000, 1.000)      # White rim highlight
C_BORDER_BASE = (0.200, 0.350, 0.500)      # Subtle border

C_GREEN       = (0.000, 1.000, 0.400)      # Matrix Razor #00ff66
C_CYAN        = (0.000, 0.950, 1.000)      # Electric Cyan #00f2fe
C_AMBER       = (1.000, 0.700, 0.000)      # Solar Amber #ffb300 (Restart)
C_RED         = (1.000, 0.200, 0.350)      # Neon Crimson #ff3359 (Shutdown)
C_PURPLE      = (0.650, 0.350, 1.000)      # Quantum Purple (Suspend)
C_TEXT_WHITE  = (0.940, 0.960, 0.980)      # Crisp white text
C_TEXT_MUTED  = (0.500, 0.580, 0.680)      # Muted slate

ACTIONS = [
    {
        "id": "reboot",
        "label": "RESTART",
        "icon": "⚡",
        "cmd": ["systemctl", "reboot"],
        "color": C_AMBER,
        "desc": "Full system reboot & restart"
    },
    {
        "id": "poweroff",
        "label": "SHUTDOWN",
        "icon": "🛑",
        "cmd": ["systemctl", "poweroff"],
        "color": C_RED,
        "desc": "Complete hardware power down"
    },
    {
        "id": "suspend",
        "label": "SLEEP",
        "icon": "🌙",
        "cmd": ["systemctl", "suspend"],
        "color": C_CYAN,
        "desc": "Low-power standby state"
    },
]

PRESETS = [
    {"label": "5 MIN",  "seconds": 5 * 60},
    {"label": "15 MIN", "seconds": 15 * 60},
    {"label": "30 MIN", "seconds": 30 * 60},
    {"label": "45 MIN", "seconds": 45 * 60},
    {"label": "1 HOUR", "seconds": 60 * 60},
    {"label": "2 HOUR", "seconds": 120 * 60},
]


# ==============================================================================
# DAEMON LOGIC (DETACHED SURVIVAL WORKER)
# ==============================================================================
def daemon_worker(target_timestamp: float, action_id: str):
    """Detached background worker that guarantees action execution at target time."""
    action = next((a for a in ACTIONS if a["id"] == action_id), ACTIONS[0])
    cmd = action["cmd"]

    # Write PID into state file
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                st = json.load(f)
            st["daemon_pid"] = os.getpid()
            with open(STATE_FILE, "w") as f:
                json.dump(st, f, indent=2)
    except Exception:
        pass

    # Track whether state file was verified
    seen_state = os.path.exists(STATE_FILE)

    # Loop until target timestamp
    while True:
        now = time.time()
        remaining = target_timestamp - now
        if remaining <= 0:
            break

        # Check if state file was created in the meantime
        if not seen_state and os.path.exists(STATE_FILE):
            seen_state = True

        # Check if state file was removed after being seen (user explicitly aborted)
        if seen_state and not os.path.exists(STATE_FILE):
            sys.exit(0)

        # Sleep up to 1 second
        sleep_dur = min(1.0, max(0.05, remaining))
        time.sleep(sleep_dur)

    # Clean up state file before firing command
    try:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    except Exception:
        pass

    # Send final desktop notification
    try:
        subprocess.run([
            "notify-send",
            "-u", "critical",
            "-a", "Flowork Power Engine",
            "-i", "system-shutdown-symbolic",
            "⚡ System Power Action Executing",
            f"Countdown reached zero. Initiating {action['label']} now!"
        ], check=False)
    except Exception:
        pass

    # Execute system power command with fallback to sudo
    try:
        subprocess.run(cmd, check=True)
    except Exception:
        try:
            subprocess.run(["sudo", "-n"] + cmd, check=True)
        except Exception:
            pass
    sys.exit(0)


def abort_timer():
    """Cancel any active countdown and terminate daemon."""
    killed = False
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                st = json.load(f)
            dpid = st.get("daemon_pid")
            if dpid and dpid > 0:
                try:
                    os.kill(dpid, signal.SIGTERM)
                    killed = True
                except ProcessLookupError:
                    pass
        except Exception:
            pass
        try:
            os.remove(STATE_FILE)
        except Exception:
            pass

    # Cancel legacy systemd shutdown scheduler if running
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
            "Scheduled system countdown has been safely cancelled."
        ], check=False)
    except Exception:
        pass
    return killed


def get_active_state():
    """Returns active state dict if valid timer is running, else None."""
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
            # Stale state file
            os.remove(STATE_FILE)
            return None
    except Exception:
        return None


# ==============================================================================
# GTK 3.0 PURE OPTICAL CRYSTAL GLASS HUD POPUP
# ==============================================================================
class ShutdownTimerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Flowork Sovereign Power Control")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_accept_focus(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.win_w, self.win_h = 510, 470
        self.set_size_request(self.win_w, self.win_h)

        # State initialization
        self.selected_action = 0  # 0: reboot, 1: poweroff, 2: suspend
        self.total_seconds = 15 * 60
        self.selected_preset_idx = 1

        self.is_counting = False
        self.target_timestamp = 0.0
        self.active_total_seconds = 0
        self.timer_source_id = None
        self.pulse_phase = 0.0

        # Animation
        self.anim_progress = 0.0
        self.anim_id = None

        # Hitboxes & Hover states
        self.hover_x = -1
        self.hover_y = -1
        self._action_hitboxes = []
        self._preset_hitboxes = []
        self._step_hitboxes = []
        self._initiate_hitbox = None
        self._close_hitbox = None
        self._cancel_hitbox = None
        self._bg_hitbox = None
        self._time_well_hitbox = None

        self.hovered_action = -1
        self.hovered_preset = -1
        self.hovered_step = None
        self.hovered_initiate = False
        self.hovered_close = False
        self.hovered_cancel = False
        self.hovered_bg = False

        # Load active state if daemon is running
        self._sync_with_active_state()

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

        self._start_entrance_anim()
        self._start_pulse_anim()

    def _sync_with_active_state(self):
        st = get_active_state()
        if st:
            self.is_counting = True
            self.target_timestamp = st.get("target_timestamp", 0)
            self.active_total_seconds = st.get("total_seconds", 900)
            act_id = st.get("action", "reboot")
            for i, a in enumerate(ACTIONS):
                if a["id"] == act_id:
                    self.selected_action = i
                    break
            self._start_live_ticker()

    def _start_entrance_anim(self):
        def tick():
            self.anim_progress = min(1.0, self.anim_progress + 0.08)
            self.queue_draw()
            if self.anim_progress >= 1.0:
                self.anim_id = None
                return False
            return True
        self.anim_id = GLib.timeout_add(16, tick)

    def _start_pulse_anim(self):
        def pulse_tick():
            self.pulse_phase = (self.pulse_phase + 0.05) % (2 * math.pi)
            if self.is_counting:
                self.queue_draw()
            return True
        GLib.timeout_add(33, pulse_tick)

    def _start_live_ticker(self):
        if self.timer_source_id:
            GLib.source_remove(self.timer_source_id)

        def tick():
            if not self.is_counting:
                return False
            now = time.time()
            rem = self.target_timestamp - now
            if rem <= 0:
                self.is_counting = False
                self.timer_source_id = None
                self.queue_draw()
                # Trigger action immediately
                act = ACTIONS[self.selected_action]
                try:
                    subprocess.Popen(act["cmd"], start_new_session=True)
                except Exception:
                    subprocess.Popen(["sudo", "-n"] + act["cmd"], start_new_session=True)
                self.destroy()
                return False
            self.queue_draw()
            return True

        self.timer_source_id = GLib.timeout_add(100, tick)

    def _ease_out(self, t):
        return 1.0 - (1.0 - t) ** 3

    # ==========================================================================
    # CAIRO RENDERING ENGINE (PURE OPTICAL CRYSTAL GLASS)
    # ==========================================================================
    def on_draw(self, _widget, cr):
        w, h = self.win_w, self.win_h
        p = self._ease_out(self.anim_progress)
        pad = 6.0

        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # ── 1. Glass Card Chassis ──
        bx, by, bw, bh = pad, pad, w - 2 * pad, h - 2 * pad
        radius = 26.0

        # Base obsidian body
        self._rounded_rect(cr, bx, by, bw, bh, radius)
        cr.set_source_rgba(C_VOID[0], C_VOID[1], C_VOID[2], 0.90 * p)
        cr.fill_preserve()

        # Specular Rim Gradient
        lin = cairo.LinearGradient(bx, by, bx, by + bh)
        lin.add_color_stop_rgba(0.00, 1.0, 1.0, 1.0, 0.45 * p)
        lin.add_color_stop_rgba(0.12, 0.5, 0.7, 0.9, 0.20 * p)
        lin.add_color_stop_rgba(0.85, 0.2, 0.3, 0.5, 0.10 * p)
        lin.add_color_stop_rgba(1.00, 1.0, 1.0, 1.0, 0.25 * p)
        cr.set_source(lin)
        cr.set_line_width(1.6)
        cr.stroke()

        if p < 0.15:
            return True

        pctx = PangoCairo.create_context(cr)
        layout = Pango.Layout.new(pctx)

        # ── 2. Top Glass Header Bar ──
        self._draw_header(cr, layout, w, h, p)

        # ── 3. Mode Content ──
        if self.is_counting:
            self._draw_countdown_screen(cr, layout, w, h, p)
        else:
            self._draw_setup_screen(cr, layout, w, h, p)

        return True

    def _draw_header(self, cr, layout, w, h, p):
        # Header separator line
        cr.new_path()
        cr.set_source_rgba(0.3, 0.5, 0.7, 0.18 * p)
        cr.move_to(22, 54)
        cr.line_to(w - 22, 54)
        cr.set_line_width(1.0)
        cr.stroke()

        # Title Emblem & Pill
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11"))
        layout.set_text("FLOWORK POWER CONTROL", -1)
        tw, th = layout.get_pixel_size()

        # Small status beacon dot
        act_col = ACTIONS[self.selected_action]["color"]
        dot_x, dot_y, dot_r = 30, 31, 4.5
        cr.arc(dot_x, dot_y, dot_r, 0, 2 * math.pi)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.95 * p)
        cr.fill()

        # Dot ambient glow
        cr.arc(dot_x, dot_y, dot_r + 3.0, 0, 2 * math.pi)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.25 * p)
        cr.fill()

        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.95 * p)
        cr.move_to(44, 31 - th / 2)
        PangoCairo.show_layout(cr, layout)

        # Subtitle badge
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text("SOVEREIGN ENGINE", -1)
        st_w, st_h = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.65 * p)
        cr.move_to(48 + tw, 31 - st_h / 2)
        PangoCairo.show_layout(cr, layout)

        # Close button (Glass pill with red hover)
        cb_x, cb_y, cb_r = w - 34, 31, 12
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

        # Cross mark in close button
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.85 * p)
        cr.set_line_width(1.5)
        cr.move_to(cb_x - 4, cb_y - 4)
        cr.line_to(cb_x + 4, cb_y + 4)
        cr.move_to(cb_x + 4, cb_y - 4)
        cr.line_to(cb_x - 4, cb_y + 4)
        cr.stroke()
        self._close_hitbox = (cb_x - cb_r, cb_y - cb_r, cb_r * 2, cb_r * 2)

    def _draw_setup_screen(self, cr, layout, w, h, p):
        # ── 1. Action Tabs (Segmented Glass Pills) ──
        tab_y = 68
        tab_h = 38
        gap = 8
        avail_w = w - 44
        tab_w = (avail_w - (len(ACTIONS) - 1) * gap) / len(ACTIONS)
        self._action_hitboxes = []

        for i, act in enumerate(ACTIONS):
            tx = 22 + i * (tab_w + gap)
            is_sel = (i == self.selected_action)
            is_hov = (i == self.hovered_action)
            col = act["color"]

            cr.new_path()
            self._rounded_rect(cr, tx, tab_y, tab_w, tab_h, 10)
            if is_sel:
                # Active convex glass gradient
                lin = cairo.LinearGradient(tx, tab_y, tx, tab_y + tab_h)
                lin.add_color_stop_rgba(0.0, col[0], col[1], col[2], 0.32 * p)
                lin.add_color_stop_rgba(1.0, col[0], col[1], col[2], 0.12 * p)
                cr.set_source(lin)
                cr.fill_preserve()
                # Specular upper lip
                cr.set_source_rgba(col[0], col[1], col[2], 0.90 * p)
                cr.set_line_width(1.6)
                cr.stroke()
            elif is_hov:
                cr.set_source_rgba(col[0], col[1], col[2], 0.14 * p)
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

            # Text inside tab
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.5"))
            layout.set_text(f"{act['icon']} {act['label']}", -1)
            tw, th = layout.get_pixel_size()
            if is_sel:
                cr.set_source_rgba(col[0], col[1], col[2], 1.0 * p)
            else:
                cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.70 * p)
            cr.move_to(tx + (tab_w - tw) / 2, tab_y + (tab_h - th) / 2)
            PangoCairo.show_layout(cr, layout)

            self._action_hitboxes.append((tx, tab_y, tab_w, tab_h))

        # ── 2. Time Presets (Quick Badges) ──
        pre_label_y = 120
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8"))
        layout.set_text("SELECT DURATION PRESET", -1)
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.75 * p)
        cr.move_to(24, pre_label_y)
        PangoCairo.show_layout(cr, layout)

        pre_y = 138
        pre_h = 32
        pre_gap = 6
        cols = len(PRESETS)
        pre_w = (avail_w - (cols - 1) * pre_gap) / cols
        self._preset_hitboxes = []

        for i, pre in enumerate(PRESETS):
            px = 22 + i * (pre_w + pre_gap)
            is_sel = (self.total_seconds == pre["seconds"])
            is_hov = (i == self.hovered_preset)
            act_col = ACTIONS[self.selected_action]["color"]

            cr.new_path()
            self._rounded_rect(cr, px, pre_y, pre_w, pre_h, 8)
            if is_sel:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.22 * p)
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

        # ── 3. Recessed Concave Glass Well (Digital Timer Readout & Quick Tweak) ──
        well_y = 186
        well_h = 130
        well_w = avail_w
        well_x = 22
        self._time_well_hitbox = (well_x, well_y, well_w, well_h)

        # Concave trough fill
        cr.new_path()
        self._rounded_rect(cr, well_x, well_y, well_w, well_h, 16)
        cr.set_source_rgba(C_WELL[0], C_WELL[1], C_WELL[2], 0.85 * p)
        cr.fill_preserve()

        # Inner subtle glow border
        act_col = ACTIONS[self.selected_action]["color"]
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.30 * p)
        cr.set_line_width(1.0)
        cr.stroke()

        # Step Adjustment Buttons Layout
        # Left buttons: [-10m], [-1m] | Center: Digital Readout | Right: [+1m], [+5m], [+15m]
        self._step_hitboxes = []

        step_btn_w = 48
        step_btn_h = 32
        step_y_top = well_y + 24
        step_y_bot = well_y + 68

        left_steps = [
            ("-10m", -600, well_x + 16, step_y_top),
            ("-1m",  -60,  well_x + 16, step_y_bot),
        ]
        right_steps = [
            ("+1m",  +60,  well_x + well_w - 16 - step_btn_w * 2 - 8, step_y_top),
            ("+5m",  +300, well_x + well_w - 16 - step_btn_w, step_y_top),
            ("+15m", +900, well_x + well_w - 16 - step_btn_w * 2 - 8, step_y_bot, step_btn_w * 2 + 8),
        ]

        for s in left_steps:
            lbl, delta, sx, sy = s
            sw = step_btn_w
            self._draw_step_button(cr, layout, lbl, delta, sx, sy, sw, step_btn_h, p)

        for s in right_steps:
            if len(s) == 5:
                lbl, delta, sx, sy, sw = s
            else:
                lbl, delta, sx, sy = s
                sw = step_btn_w
            self._draw_step_button(cr, layout, lbl, delta, sx, sy, sw, step_btn_h, p)

        # Center Digital Readout (Hours : Minutes : Seconds)
        hours = self.total_seconds // 3600
        mins = (self.total_seconds % 3600) // 60
        secs = self.total_seconds % 60

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 32"))
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        layout.set_text(time_str, -1)
        tw, th = layout.get_pixel_size()

        # Soft text shadow
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.25 * p)
        cr.move_to(w / 2 - tw / 2, well_y + 40 - th / 2 + 1)
        PangoCairo.show_layout(cr, layout)

        # Crisp primary readout
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.98 * p)
        cr.move_to(w / 2 - tw / 2, well_y + 40 - th / 2)
        PangoCairo.show_layout(cr, layout)

        # Digital Sub-labels (HRS  MINS  SECS)
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text("HRS         MINS         SECS", -1)
        sw, sh = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.70 * p)
        cr.move_to(w / 2 - sw / 2, well_y + 68)
        PangoCairo.show_layout(cr, layout)

        # Scroll hint at bottom of well
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("▲ MOUSE WHEEL TO TWEAK ▲", -1)
        hw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.50 * p)
        cr.move_to(w / 2 - hw / 2, well_y + well_h - 20)
        PangoCairo.show_layout(cr, layout)

        # ── 4. Dynamic Summary Status Line ──
        summary_y = 330
        target_time_dt = datetime.fromtimestamp(time.time() + self.total_seconds)
        time_fmt = target_time_dt.strftime("%H:%M:%S")

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 9"))
        act_info = ACTIONS[self.selected_action]
        txt = f"⚡ Action: {act_info['label']} scheduled at {time_fmt} ({self.total_seconds // 60}m)"
        layout.set_text(txt, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.85 * p)
        cr.move_to(w / 2 - tw / 2, summary_y)
        PangoCairo.show_layout(cr, layout)

        # ── 5. Main Initiation Convex Glass Button ──
        btn_y = 362
        btn_w = 260
        btn_h = 48
        btn_x = (w - btn_w) / 2
        self._initiate_hitbox = (btn_x, btn_y, btn_w, btn_h)

        cr.new_path()
        self._rounded_rect(cr, btn_x, btn_y, btn_w, btn_h, 14)
        if self.hovered_initiate:
            lin = cairo.LinearGradient(btn_x, btn_y, btn_x, btn_y + btn_h)
            lin.add_color_stop_rgba(0.0, act_col[0], act_col[1], act_col[2], 0.45 * p)
            lin.add_color_stop_rgba(1.0, act_col[0], act_col[1], act_col[2], 0.20 * p)
            cr.set_source(lin)
            cr.fill_preserve()
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.95 * p)
            cr.set_line_width(2.0)
            cr.stroke()
        else:
            lin = cairo.LinearGradient(btn_x, btn_y, btn_x, btn_y + btn_h)
            lin.add_color_stop_rgba(0.0, act_col[0], act_col[1], act_col[2], 0.30 * p)
            lin.add_color_stop_rgba(1.0, act_col[0], act_col[1], act_col[2], 0.12 * p)
            cr.set_source(lin)
            cr.fill_preserve()
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.70 * p)
            cr.set_line_width(1.5)
            cr.stroke()

        # Button specular reflection (top 45%)
        cr.new_path()
        self._rounded_rect(cr, btn_x + 2, btn_y + 2, btn_w - 4, btn_h * 0.45, 12)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.12 * p)
        cr.fill()

        # Button text
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11"))
        btn_txt = f"INITIATE {act_info['label']} TIMER"
        layout.set_text(btn_txt, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 1.0 * p)
        cr.move_to(btn_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # ── 6. Bottom System Footer ──
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("FLOWORK OS SOVEREIGN POWER MANAGEMENT • PERSISTENT DAEMON BACKED", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.40 * p)
        cr.move_to(w / 2 - tw / 2, h - 22)
        PangoCairo.show_layout(cr, layout)

    def _draw_step_button(self, cr, layout, label, delta, x, y, w, h, p):
        is_hov = (self.hovered_step == label)
        cr.new_path()
        self._rounded_rect(cr, x, y, w, h, 8)
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

    # ==========================================================================
    # COUNTDOWN SCREEN (HIGH-TECH REACTOR RING & SAFE DISMISS/ABORT)
    # ==========================================================================
    def _draw_countdown_screen(self, cr, layout, w, h, p):
        act_info = ACTIONS[self.selected_action]
        act_col = act_info["color"]

        now = time.time()
        remaining = max(0.0, self.target_timestamp - now)
        total = max(1.0, float(self.active_total_seconds))
        frac = min(1.0, max(0.0, remaining / total))

        # Warning threshold (less than 60s)
        is_imminent = (remaining <= 60.0)

        # ── Circular Quantum Gauge ──
        rcx, rcy = w / 2, 195
        rr = 88.0
        ring_width = 8.0

        # Background track
        cr.new_path()
        cr.set_line_width(ring_width)
        cr.set_source_rgba(0.12, 0.16, 0.22, 0.60 * p)
        cr.arc(rcx, rcy, rr, 0, 2 * math.pi)
        cr.stroke()

        # Dynamic Neon Glow Pulse on Track
        pulse_alpha = 0.70 + 0.25 * math.sin(self.pulse_phase * (3.0 if is_imminent else 1.0))
        cr.new_path()
        start_angle = -math.pi / 2
        end_angle = start_angle + (2 * math.pi * frac)
        cr.set_line_width(ring_width)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], pulse_alpha * p)
        cr.arc(rcx, rcy, rr, start_angle, end_angle)
        cr.stroke()

        # Outer faint specular boundary
        cr.new_path()
        cr.set_line_width(1.0)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.15 * p)
        cr.arc(rcx, rcy, rr + ring_width + 4.0, 0, 2 * math.pi)
        cr.stroke()

        # Digital Countdown Text inside Ring
        rem_int = int(remaining)
        chrs = rem_int // 3600
        cmins = (rem_int % 3600) // 60
        csecs = rem_int % 60

        if chrs > 0:
            c_str = f"{chrs:02d}:{cmins:02d}:{csecs:02d}"
            font_size = "26"
        else:
            c_str = f"{cmins:02d}:{csecs:02d}"
            font_size = "34"

        layout.set_font_description(Pango.FontDescription(f"JetBrains Mono Bold {font_size}"))
        layout.set_text(c_str, -1)
        tw, th = layout.get_pixel_size()

        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.98 * p)
        cr.move_to(rcx - tw / 2, rcy - th / 2 - 4)
        PangoCairo.show_layout(cr, layout)

        # Status badge below time inside ring
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8"))
        if is_imminent:
            layout.set_text("CRITICAL: IMMINENT", -1)
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.95 * p)
        else:
            layout.set_text(f"{act_info['label']} ARMED", -1)
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.90 * p)
        stw, sth = layout.get_pixel_size()
        cr.move_to(rcx - stw / 2, rcy + th / 2 - 2)
        PangoCairo.show_layout(cr, layout)

        # ── Target Execution Info ──
        info_y = 312
        target_dt = datetime.fromtimestamp(self.target_timestamp)
        t_fmt = target_dt.strftime("%H:%M:%S WIB")

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 9"))
        status_line = f"Target Execution: {t_fmt} ({rem_int}s remaining)"
        layout.set_text(status_line, -1)
        itw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.80 * p)
        cr.move_to(w / 2 - itw / 2, info_y)
        PangoCairo.show_layout(cr, layout)

        # ── Dual Buttons: [ RUN IN BACKGROUND ] & [ ABORT / CANCEL ] ──
        btn_y = 352
        btn_w = 190
        btn_h = 44
        gap = 14
        total_w = btn_w * 2 + gap
        start_x = (w - total_w) / 2

        # 1. RUN IN BACKGROUND Button
        bg_x = start_x
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

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.5"))
        layout.set_text("RUN IN BACKGROUND", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.90 * p)
        cr.move_to(bg_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 2. ABORT / CANCEL Button
        abort_x = start_x + btn_w + gap
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

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.5"))
        layout.set_text("ABORT TIMER", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 1.0 * p)
        cr.move_to(abort_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Footer hint
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("COUNTDOWN IS PERSISTED VIA BACKGROUND DAEMON WORKER", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.40 * p)
        cr.move_to(w / 2 - tw / 2, h - 22)
        PangoCairo.show_layout(cr, layout)

    # ==========================================================================
    # INTERACTION & EVENT HANDLERS
    # ==========================================================================
    def on_motion(self, _w, event):
        self.hover_x, self.hover_y = event.x, event.y
        self._update_hover()
        self.queue_draw()

    def on_leave(self, *_):
        self.hover_x, self.hover_y = -1, -1
        self.hovered_action = -1
        self.hovered_preset = -1
        self.hovered_step = None
        self.hovered_initiate = False
        self.hovered_close = False
        self.hovered_cancel = False
        self.hovered_bg = False
        self.queue_draw()

    def _update_hover(self):
        x, y = self.hover_x, self.hover_y
        self.hovered_action = -1
        self.hovered_preset = -1
        self.hovered_step = None
        self.hovered_initiate = False
        self.hovered_close = False
        self.hovered_cancel = False
        self.hovered_bg = False

        # Close button
        if self._close_hitbox:
            bx, by, bw, bh = self._close_hitbox
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.hovered_close = True
                return

        if self.is_counting:
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
            # Action tabs
            for i, hb in enumerate(self._action_hitboxes):
                bx, by, bw, bh = hb
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_action = i
                    return

            # Presets
            for i, hb in enumerate(self._preset_hitboxes):
                bx, by, bw, bh = hb
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_preset = i
                    return

            # Steps
            for item in self._step_hitboxes:
                lbl, _delta, bx, by, bw, bh = item
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_step = lbl
                    return

            # Initiate button
            if self._initiate_hitbox:
                bx, by, bw, bh = self._initiate_hitbox
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_initiate = True
                    return

    def on_click(self, _w, event):
        if event.button != 1:
            return

        # Close / Dismiss
        if self.hovered_close:
            self.destroy()
            return

        if self.is_counting:
            if self.hovered_bg:
                # User chose run in background -> send notification and close GUI
                st = get_active_state()
                act_lbl = ACTIONS[self.selected_action]["label"]
                mins_left = max(1, int((self.target_timestamp - time.time()) // 60))
                subprocess.Popen([
                    "notify-send",
                    "-u", "normal",
                    "-a", "Flowork Power Engine",
                    "-i", "system-shutdown-symbolic",
                    "⏱️ Power Timer Running in Background",
                    f"System will {act_lbl.lower()} in ~{mins_left} min. Re-open timer to view or abort."
                ])
                self.destroy()
                return
            if self.hovered_cancel:
                abort_timer()
                self.is_counting = False
                if self.timer_source_id:
                    GLib.source_remove(self.timer_source_id)
                    self.timer_source_id = None
                self.queue_draw()
                return
        else:
            # Action tab change
            if self.hovered_action >= 0:
                self.selected_action = self.hovered_action
                self.queue_draw()
                return

            # Preset selection
            if self.hovered_preset >= 0:
                self.total_seconds = PRESETS[self.hovered_preset]["seconds"]
                self.queue_draw()
                return

            # Step buttons
            if self.hovered_step:
                for item in self._step_hitboxes:
                    lbl, delta, _, _, _, _ = item
                    if lbl == self.hovered_step:
                        self.total_seconds = max(60, min(86400, self.total_seconds + delta))
                        self.queue_draw()
                        return

            # Initiate countdown
            if self.hovered_initiate:
                self._arm_timer()
                return

    def on_scroll(self, _w, event):
        if self.is_counting:
            return
        # Scroll over well adjusts time
        if self._time_well_hitbox:
            bx, by, bw, bh = self._time_well_hitbox
            if bx <= event.x <= bx + bw and by <= event.y <= by + bh:
                delta = 60 if event.direction == Gdk.ScrollDirection.UP else -60
                self.total_seconds = max(60, min(86400, self.total_seconds + delta))
                self.queue_draw()

    def on_key_press(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False

    def _arm_timer(self):
        """Saves persistent state, spawns background daemon, and switches GUI to countdown."""
        now = time.time()
        self.target_timestamp = now + self.total_seconds
        self.active_total_seconds = self.total_seconds
        self.is_counting = True

        act = ACTIONS[self.selected_action]

        # 1. Write state file first to guarantee presence for daemon
        st = {
            "target_timestamp": self.target_timestamp,
            "total_seconds": self.active_total_seconds,
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

        # 2. Spawn detached background daemon worker
        cmd_daemon = [
            sys.executable,
            os.path.abspath(__file__),
            "--daemon",
            str(self.target_timestamp),
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

        # 3. Desktop notification
        mins_left = max(1, self.total_seconds // 60)
        try:
            subprocess.Popen([
                "notify-send",
                "-u", "normal",
                "-a", "Flowork Power Engine",
                "-i", "system-shutdown-symbolic",
                f"⏱️ {act['label']} Timer Armed",
                f"System will {act['label'].lower()} in {mins_left} min. Persisted in background."
            ])
        except Exception:
            pass

        # 4. Start live ticker
        self._start_live_ticker()
        self.queue_draw()

    def on_destroy(self, *_):
        if self.timer_source_id:
            GLib.source_remove(self.timer_source_id)
        if self.anim_id:
            GLib.source_remove(self.anim_id)
        Gtk.main_quit()

    def _rounded_rect(self, cr, x, y, w, h, r):
        cr.new_path()
        cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        cr.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
        cr.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
        cr.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
        cr.close_path()


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # CLI modes
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        if flag == "--daemon" and len(sys.argv) >= 4:
            target_time = float(sys.argv[2])
            action = sys.argv[3]
            daemon_worker(target_time, action)
            return
        elif flag in ("--abort", "-a"):
            abort_timer()
            print("Shutdown timer aborted successfully.")
            return
        elif flag in ("--status", "-s"):
            st = get_active_state()
            if st:
                print(json.dumps(st, indent=2))
            else:
                print("No active shutdown timer.")
            return

    win = ShutdownTimerWindow()
    win.show_all()
    win.present()
    Gtk.main()


if __name__ == "__main__":
    main()
