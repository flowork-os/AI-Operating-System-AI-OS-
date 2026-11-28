#!/usr/bin/env python3
# ==============================================================================
# FLOWORK OS — SOVEREIGN SHUTDOWN TIMER
# Pure Optical Crystal Glass Popup for scheduling system shutdown/restart/sleep
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

# ── Colors ──
C_BG = (0.02, 0.04, 0.08)
C_BORDER = (0.20, 0.85, 1.00)
C_CYAN = (0.00, 0.90, 1.00)
C_GREEN = (0.00, 1.00, 0.45)
C_RED = (1.00, 0.30, 0.30)
C_AMBER = (1.00, 0.72, 0.10)
C_WHITE = (0.92, 0.94, 0.96)
C_DIM = (0.45, 0.50, 0.55)
C_PURPLE = (0.65, 0.40, 1.00)

PRESETS = [
    {"label": "15 MIN", "minutes": 15},
    {"label": "30 MIN", "minutes": 30},
    {"label": "1 HOUR", "minutes": 60},
    {"label": "2 HOUR", "minutes": 120},
    {"label": "3 HOUR", "minutes": 180},
    {"label": "CUSTOM", "minutes": 0},
]

ACTIONS = [
    {"label": "SHUTDOWN", "cmd": "systemctl poweroff", "color": C_RED},
    {"label": "RESTART", "cmd": "systemctl reboot", "color": C_AMBER},
    {"label": "SLEEP", "cmd": "systemctl suspend", "color": C_PURPLE},
]


class ShutdownTimerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Flowork Shutdown Timer")
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

        self.win_w, self.win_h = 480, 420
        self.set_size_request(self.win_w, self.win_h)

        # State
        self.selected_preset = 0  # index into PRESETS
        self.selected_action = 0  # index into ACTIONS
        self.custom_minutes = 45
        self.is_counting = False
        self.remaining_seconds = 0
        self.timer_id = None
        self.scheduled_pid = None

        # Hover
        self.hover_x = -1
        self.hover_y = -1
        self.hovered_preset = -1
        self.hovered_action = -1
        self.hovered_start = False
        self.hovered_cancel = False
        self.hovered_close = False
        self.hovered_plus = False
        self.hovered_minus = False

        # Animation
        self.anim_progress = 0.0
        self.anim_id = None

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.SCROLL_MASK
            | Gdk.EventMask.FOCUS_CHANGE_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
        )
        self.set_can_focus(True)
        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-press-event", self.on_click)
        self.connect("leave-notify-event", self.on_leave)
        self.connect("scroll-event", self.on_scroll)
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)

        self._start_entrance_anim()

    def _start_entrance_anim(self):
        def tick():
            self.anim_progress = min(1.0, self.anim_progress + 0.06)
            self.queue_draw()
            if self.anim_progress >= 1.0:
                self.anim_id = None
                return False
            return True
        self.anim_id = GLib.timeout_add(16, tick)

    def _ease_out(self, t):
        return 1.0 - (1.0 - t) ** 3

    # ── Drawing ──
    def on_draw(self, _widget, cr):
        w, h = self.win_w, self.win_h
        p = self._ease_out(self.anim_progress)
        pad = 3.0

        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # Background glass panel
        bx, by, bw, bh = pad, pad, w - 2 * pad, h - 2 * pad
        radius = 18.0
        self._rounded_rect(cr, bx, by, bw, bh, radius)
        cr.set_source_rgba(C_BG[0], C_BG[1], C_BG[2], 0.92 * p)
        cr.fill_preserve()

        # Border glow
        cr.set_line_width(1.5)
        cr.set_source_rgba(C_BORDER[0], C_BORDER[1], C_BORDER[2], 0.35 * p)
        cr.stroke()

        if p < 0.1:
            return True

        pctx = PangoCairo.create_context(cr)
        layout = Pango.Layout.new(pctx)

        # ── Header ──
        # Close button (top right)
        close_x, close_y, close_r = w - 28, 22, 10
        cr.new_path()
        cr.arc(close_x, close_y, close_r, 0, 2 * math.pi)
        if self.hovered_close:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.8)
        else:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.4)
        cr.fill()
        # X mark
        cr.set_source_rgba(1, 1, 1, 0.9)
        cr.set_line_width(1.5)
        cr.move_to(close_x - 4, close_y - 4)
        cr.line_to(close_x + 4, close_y + 4)
        cr.move_to(close_x + 4, close_y - 4)
        cr.line_to(close_x - 4, close_y + 4)
        cr.stroke()
        self._close_hitbox = (close_x - close_r, close_y - close_r, close_r * 2, close_r * 2)

        # Title
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 13"))
        layout.set_text("SHUTDOWN TIMER", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.95 * p)
        cr.move_to((w - tw) / 2, 14)
        PangoCairo.show_layout(cr, layout)

        # Thin separator
        cr.new_path()
        cr.set_source_rgba(C_BORDER[0], C_BORDER[1], C_BORDER[2], 0.15 * p)
        cr.move_to(20, 42)
        cr.line_to(w - 20, 42)
        cr.set_line_width(0.8)
        cr.stroke()

        if self.is_counting:
            self._draw_countdown(cr, layout, w, h, p)
        else:
            self._draw_config(cr, layout, w, h, p)

        return True

    def _draw_config(self, cr, layout, w, h, p):
        # ── Action Type (SHUTDOWN / RESTART / SLEEP) ──
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 8"))
        layout.set_text("ACTION", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_DIM[0], C_DIM[1], C_DIM[2], 0.7 * p)
        cr.move_to(24, 52)
        PangoCairo.show_layout(cr, layout)

        action_y = 70
        action_w = 136
        action_h = 36
        action_gap = 10
        total_aw = len(ACTIONS) * action_w + (len(ACTIONS) - 1) * action_gap
        ax_start = (w - total_aw) / 2
        self._action_hitboxes = []

        for i, act in enumerate(ACTIONS):
            ax = ax_start + i * (action_w + action_gap)
            col = act["color"]
            is_sel = (i == self.selected_action)
            is_hov = (i == self.hovered_action)

            cr.new_path()
            self._rounded_rect(cr, ax, action_y, action_w, action_h, 8)
            if is_sel:
                cr.set_source_rgba(col[0], col[1], col[2], 0.25 * p)
                cr.fill_preserve()
                cr.set_line_width(1.5)
                cr.set_source_rgba(col[0], col[1], col[2], 0.85 * p)
                cr.stroke()
            elif is_hov:
                cr.set_source_rgba(col[0], col[1], col[2], 0.12 * p)
                cr.fill_preserve()
                cr.set_line_width(1.0)
                cr.set_source_rgba(col[0], col[1], col[2], 0.5 * p)
                cr.stroke()
            else:
                cr.set_source_rgba(0.1, 0.12, 0.15, 0.6 * p)
                cr.fill_preserve()
                cr.set_line_width(0.8)
                cr.set_source_rgba(col[0], col[1], col[2], 0.25 * p)
                cr.stroke()

            cr.new_path()
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9"))
            layout.set_text(act["label"], -1)
            tw, th = layout.get_pixel_size()
            if is_sel:
                cr.set_source_rgba(col[0], col[1], col[2], 0.95 * p)
            else:
                cr.set_source_rgba(C_WHITE[0], C_WHITE[1], C_WHITE[2], 0.6 * p)
            cr.move_to(ax + (action_w - tw) / 2, action_y + (action_h - th) / 2)
            PangoCairo.show_layout(cr, layout)
            self._action_hitboxes.append((ax, action_y, action_w, action_h))

        # ── Time Presets ──
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 8"))
        layout.set_text("DURATION", -1)
        cr.set_source_rgba(C_DIM[0], C_DIM[1], C_DIM[2], 0.7 * p)
        cr.move_to(24, 120)
        PangoCairo.show_layout(cr, layout)

        preset_y = 140
        preset_w = 68
        preset_h = 42
        preset_gap = 6
        cols_per_row = 6
        total_pw = cols_per_row * preset_w + (cols_per_row - 1) * preset_gap
        px_start = (w - total_pw) / 2
        self._preset_hitboxes = []

        for i, pre in enumerate(PRESETS):
            col_i = i % cols_per_row
            px = px_start + col_i * (preset_w + preset_gap)
            py = preset_y
            is_sel = (i == self.selected_preset)
            is_hov = (i == self.hovered_preset)

            cr.new_path()
            self._rounded_rect(cr, px, py, preset_w, preset_h, 8)
            if is_sel:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.2 * p)
                cr.fill_preserve()
                cr.set_line_width(1.5)
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.85 * p)
                cr.stroke()
            elif is_hov:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.1 * p)
                cr.fill_preserve()
                cr.set_line_width(1.0)
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.4 * p)
                cr.stroke()
            else:
                cr.set_source_rgba(0.08, 0.10, 0.14, 0.6 * p)
                cr.fill_preserve()
                cr.set_line_width(0.6)
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.15 * p)
                cr.stroke()

            cr.new_path()
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.5"))
            layout.set_text(pre["label"], -1)
            tw, th = layout.get_pixel_size()
            if is_sel:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.95 * p)
            else:
                cr.set_source_rgba(C_WHITE[0], C_WHITE[1], C_WHITE[2], 0.55 * p)
            cr.move_to(px + (preset_w - tw) / 2, py + (preset_h - th) / 2)
            PangoCairo.show_layout(cr, layout)
            self._preset_hitboxes.append((px, py, preset_w, preset_h))

        # ── Custom Minutes Spinner (shown when CUSTOM selected) ──
        if self.selected_preset == 5:  # CUSTOM
            spin_y = 200
            spin_cx = w / 2

            # Minus button
            m_x, m_y, m_w, m_h = spin_cx - 90, spin_y, 40, 40
            cr.new_path()
            self._rounded_rect(cr, m_x, m_y, m_w, m_h, 8)
            if self.hovered_minus:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.25 * p)
            else:
                cr.set_source_rgba(0.1, 0.12, 0.15, 0.6 * p)
            cr.fill_preserve()
            cr.set_line_width(1.0)
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.5 * p)
            cr.stroke()
            cr.new_path()
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 16"))
            layout.set_text("-", -1)
            tw, th = layout.get_pixel_size()
            cr.set_source_rgba(C_WHITE[0], C_WHITE[1], C_WHITE[2], 0.9 * p)
            cr.move_to(m_x + (m_w - tw) / 2, m_y + (m_h - th) / 2)
            PangoCairo.show_layout(cr, layout)
            self._minus_hitbox = (m_x, m_y, m_w, m_h)

            # Number display
            cr.new_path()
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 22"))
            txt = f"{self.custom_minutes} MIN"
            layout.set_text(txt, -1)
            tw, th = layout.get_pixel_size()
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.95 * p)
            cr.move_to(spin_cx - tw / 2, spin_y + (40 - th) / 2)
            PangoCairo.show_layout(cr, layout)

            # Plus button
            p_x, p_y, p_w, p_h = spin_cx + 50, spin_y, 40, 40
            cr.new_path()
            self._rounded_rect(cr, p_x, p_y, p_w, p_h, 8)
            if self.hovered_plus:
                cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.25 * p)
            else:
                cr.set_source_rgba(0.1, 0.12, 0.15, 0.6 * p)
            cr.fill_preserve()
            cr.set_line_width(1.0)
            cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.5 * p)
            cr.stroke()
            cr.new_path()
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 16"))
            layout.set_text("+", -1)
            tw, th = layout.get_pixel_size()
            cr.set_source_rgba(C_WHITE[0], C_WHITE[1], C_WHITE[2], 0.9 * p)
            cr.move_to(p_x + (p_w - tw) / 2, p_y + (p_h - th) / 2)
            PangoCairo.show_layout(cr, layout)
            self._plus_hitbox = (p_x, p_y, p_w, p_h)

        # ── Summary line ──
        summary_y = 260 if self.selected_preset == 5 else 210
        mins = self.custom_minutes if self.selected_preset == 5 else PRESETS[self.selected_preset]["minutes"]
        act_label = ACTIONS[self.selected_action]["label"]
        act_col = ACTIONS[self.selected_action]["color"]

        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 9"))
        summary = f"System will {act_label.lower()} in {mins} minutes"
        layout.set_text(summary, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_DIM[0], C_DIM[1], C_DIM[2], 0.8 * p)
        cr.move_to((w - tw) / 2, summary_y)
        PangoCairo.show_layout(cr, layout)

        # ── START Button ──
        btn_w, btn_h = 200, 48
        btn_x = (w - btn_w) / 2
        btn_y = summary_y + 36

        cr.new_path()
        self._rounded_rect(cr, btn_x, btn_y, btn_w, btn_h, 12)
        if self.hovered_start:
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.35 * p)
        else:
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.18 * p)
        cr.fill_preserve()
        cr.set_line_width(1.8)
        if self.hovered_start:
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.95 * p)
        else:
            cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.6 * p)
        cr.stroke()

        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 12"))
        layout.set_text(f"START {act_label}", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.95 * p)
        cr.move_to(btn_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)
        self._start_hitbox = (btn_x, btn_y, btn_w, btn_h)

        # ── Footer ──
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("FLOWORK OS SOVEREIGN POWER CONTROL", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_DIM[0], C_DIM[1], C_DIM[2], 0.3 * p)
        cr.move_to((w - tw) / 2, h - 24)
        PangoCairo.show_layout(cr, layout)

    def _draw_countdown(self, cr, layout, w, h, p):
        act_col = ACTIONS[self.selected_action]["color"]
        act_label = ACTIONS[self.selected_action]["label"]

        # ── Big circular countdown ──
        ring_cx, ring_cy = w / 2, 180
        ring_r = 80

        mins = self.custom_minutes if self.selected_preset == 5 else PRESETS[self.selected_preset]["minutes"]
        total_secs = mins * 60
        frac = self.remaining_seconds / max(total_secs, 1)

        # Background ring
        cr.new_path()
        cr.set_line_width(6)
        cr.set_source_rgba(0.15, 0.17, 0.20, 0.5 * p)
        cr.arc(ring_cx, ring_cy, ring_r, 0, 2 * math.pi)
        cr.stroke()

        # Progress ring
        cr.new_path()
        start_a = -math.pi / 2
        end_a = start_a + 2 * math.pi * frac
        cr.set_line_width(6)
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.85 * p)
        cr.arc(ring_cx, ring_cy, ring_r, start_a, end_a)
        cr.stroke()

        # Time text
        rm = self.remaining_seconds // 60
        rs = self.remaining_seconds % 60
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 28"))
        layout.set_text(f"{rm:02d}:{rs:02d}", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_WHITE[0], C_WHITE[1], C_WHITE[2], 0.95 * p)
        cr.move_to(ring_cx - tw / 2, ring_cy - th / 2)
        PangoCairo.show_layout(cr, layout)

        # Action label
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 9"))
        layout.set_text(f"{act_label} SCHEDULED", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(act_col[0], act_col[1], act_col[2], 0.8 * p)
        cr.move_to(ring_cx - tw / 2, ring_cy + ring_r + 20)
        PangoCairo.show_layout(cr, layout)

        # ── Cancel Button ──
        btn_w, btn_h = 200, 48
        btn_x = (w - btn_w) / 2
        btn_y = h - 100

        cr.new_path()
        self._rounded_rect(cr, btn_x, btn_y, btn_w, btn_h, 12)
        if self.hovered_cancel:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.35 * p)
        else:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.15 * p)
        cr.fill_preserve()
        cr.set_line_width(1.8)
        if self.hovered_cancel:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.95 * p)
        else:
            cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.5 * p)
        cr.stroke()

        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 12"))
        layout.set_text("CANCEL TIMER", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(C_RED[0], C_RED[1], C_RED[2], 0.95 * p)
        cr.move_to(btn_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)
        self._cancel_hitbox = (btn_x, btn_y, btn_w, btn_h)

        # Footer
        cr.new_path()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7"))
        layout.set_text("FLOWORK OS SOVEREIGN POWER CONTROL", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_DIM[0], C_DIM[1], C_DIM[2], 0.3 * p)
        cr.move_to((w - tw) / 2, h - 24)
        PangoCairo.show_layout(cr, layout)

    # ── Events ──
    def on_motion(self, _w, event):
        self.hover_x, self.hover_y = event.x, event.y
        self._update_hover()
        self.queue_draw()

    def on_leave(self, *_):
        self.hover_x, self.hover_y = -1, -1
        self.hovered_preset = -1
        self.hovered_action = -1
        self.hovered_start = False
        self.hovered_cancel = False
        self.hovered_close = False
        self.hovered_plus = False
        self.hovered_minus = False
        self.queue_draw()

    def _update_hover(self):
        x, y = self.hover_x, self.hover_y
        self.hovered_preset = -1
        self.hovered_action = -1
        self.hovered_start = False
        self.hovered_cancel = False
        self.hovered_close = False
        self.hovered_plus = False
        self.hovered_minus = False

        # Close button
        if hasattr(self, '_close_hitbox'):
            bx, by, bw, bh = self._close_hitbox
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.hovered_close = True
                return

        if not self.is_counting:
            # Action buttons
            for i, hb in enumerate(getattr(self, '_action_hitboxes', [])):
                bx, by, bw, bh = hb
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_action = i
                    return

            # Preset buttons
            for i, hb in enumerate(getattr(self, '_preset_hitboxes', [])):
                bx, by, bw, bh = hb
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_preset = i
                    return

            # Custom +/- buttons
            if self.selected_preset == 5:
                if hasattr(self, '_minus_hitbox'):
                    bx, by, bw, bh = self._minus_hitbox
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_minus = True
                        return
                if hasattr(self, '_plus_hitbox'):
                    bx, by, bw, bh = self._plus_hitbox
                    if bx <= x <= bx + bw and by <= y <= by + bh:
                        self.hovered_plus = True
                        return

            # Start button
            if hasattr(self, '_start_hitbox'):
                bx, by, bw, bh = self._start_hitbox
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_start = True
                    return
        else:
            # Cancel button
            if hasattr(self, '_cancel_hitbox'):
                bx, by, bw, bh = self._cancel_hitbox
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.hovered_cancel = True
                    return

    def on_click(self, _w, event):
        if event.button != 1:
            return

        # Click outside window bounds -> minimize
        win_x, win_y = self.get_position()
        rx, ry = event.x_root, event.y_root
        if (rx < win_x or ry < win_y
                or rx > win_x + self.win_w
                or ry > win_y + self.win_h):
            self.iconify()
            return

        if self.hovered_close:
            self._cancel_scheduled()
            self.destroy()
            return

        if not self.is_counting:
            if self.hovered_action >= 0:
                self.selected_action = self.hovered_action
                self.queue_draw()
                return

            if self.hovered_preset >= 0:
                self.selected_preset = self.hovered_preset
                self.queue_draw()
                return

            if self.hovered_minus and self.selected_preset == 5:
                self.custom_minutes = max(5, self.custom_minutes - 5)
                self.queue_draw()
                return

            if self.hovered_plus and self.selected_preset == 5:
                self.custom_minutes = min(480, self.custom_minutes + 5)
                self.queue_draw()
                return

            if self.hovered_start:
                self._start_timer()
                return
        else:
            if self.hovered_cancel:
                self._cancel_timer()
                return

    def on_scroll(self, _w, event):
        if self.selected_preset == 5 and not self.is_counting:
            if event.direction == Gdk.ScrollDirection.UP:
                self.custom_minutes = min(480, self.custom_minutes + 5)
            elif event.direction == Gdk.ScrollDirection.DOWN:
                self.custom_minutes = max(5, self.custom_minutes - 5)
            self.queue_draw()

    # ── Timer Logic ──
    def _start_timer(self):
        mins = self.custom_minutes if self.selected_preset == 5 else PRESETS[self.selected_preset]["minutes"]
        self.remaining_seconds = mins * 60
        self.is_counting = True

        # Schedule actual shutdown via `shutdown` command
        act = ACTIONS[self.selected_action]
        cmd = act["cmd"]
        try:
            if "poweroff" in cmd:
                subprocess.Popen(["shutdown", "-h", f"+{mins}"], start_new_session=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif "reboot" in cmd:
                subprocess.Popen(["shutdown", "-r", f"+{mins}"], start_new_session=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Sleep doesn't use shutdown command — handled via at/timer
        except Exception:
            pass

        # Visual countdown
        def tick():
            if self.remaining_seconds <= 0:
                # For sleep action, execute now
                if "suspend" in ACTIONS[self.selected_action]["cmd"]:
                    try:
                        subprocess.Popen(["systemctl", "suspend"], start_new_session=True)
                    except Exception:
                        pass
                self.is_counting = False
                self.timer_id = None
                self.queue_draw()
                return False
            self.remaining_seconds -= 1
            self.queue_draw()
            return True

        self.timer_id = GLib.timeout_add(1000, tick)
        self.queue_draw()

    def _cancel_timer(self):
        self._cancel_scheduled()
        self.is_counting = False
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        self.queue_draw()

    def _cancel_scheduled(self):
        try:
            subprocess.Popen(["shutdown", "-c"], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def on_destroy(self, *_):
        if self.anim_id:
            GLib.source_remove(self.anim_id)
        try:
            seat = Gdk.Display.get_default().get_default_seat()
            seat.ungrab()
        except Exception:
            pass
        Gtk.main_quit()

    def on_focus_out(self, _widget, _event):
        """Minimize when focus is lost."""
        GLib.idle_add(self.iconify)
        return False

    def on_key_press(self, _widget, event):
        """Escape key minimizes the popup."""
        if event.keyval == Gdk.KEY_Escape:
            self.iconify()
            return True
        return False

    # ── Helpers ──
    def _rounded_rect(self, cr, x, y, w, h, r):
        cr.new_path()
        cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        cr.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
        cr.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
        cr.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
        cr.close_path()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    win = ShutdownTimerWindow()

    def _grab_seat(_win):
        gdk_win = _win.get_window()
        if gdk_win:
            seat = Gdk.Display.get_default().get_default_seat()
            seat.grab(gdk_win, Gdk.SeatCapabilities.ALL, True, None, None, None)

    def _ungrab_seat():
        try:
            seat = Gdk.Display.get_default().get_default_seat()
            seat.ungrab()
        except Exception:
            pass

    def on_map(_win, *_a):
        GLib.timeout_add(100, lambda: _grab_seat(_win) or False)

    def on_unmap(_win, *_a):
        _ungrab_seat()

    win.connect("realize", _grab_seat)
    win.connect("map-event", on_map)
    win.connect("unmap-event", on_unmap)
    win.show_all()
    win.present()
    Gtk.main()


if __name__ == "__main__":
    main()
