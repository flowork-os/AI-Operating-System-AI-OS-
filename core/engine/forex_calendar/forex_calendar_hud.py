#!/usr/bin/env python3
# ==============================================================================
# 👑 FLOWORK OS — SOVEREIGN QUANTUM FOREX CALENDAR DESKTOP HUD
# Ambient Holographic Watermark with Session Radar & Real-Time Economic Radar
# ==============================================================================

import math
import os
import sys
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo

# Engine import
ENGINE_PATH = os.path.dirname(os.path.abspath(__file__))
if ENGINE_PATH not in sys.path:
    sys.path.insert(0, ENGINE_PATH)

import forex_feed

def round_rect(cr, x, y, w, h, r):
    """Draws an ultra-smooth rounded rectangle in Cairo."""
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()

class QuantumForexHUD(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Flowork Quantum Forex HUD")
        self.set_wmclass("flowork-forex-calendar-hud", "FloworkForexCalendarHUD")
        self.set_role("forex-calendar-hud")

        # Desktop Invariant: Floating stealth desktop overlay
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_below(True)
        self.set_accept_focus(False)
        self.set_app_paintable(True)

        # True RGBA Hardware Translucency
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)

        # Positioning & Layout Dynamics
        self.base_width = 400
        self.base_height = 630
        self.set_default_size(self.base_width, self.base_height)
        self.reposition_to_top_right()

        # State Variables
        self.is_hovered = False
        self.alpha_anim = 0.28  # Starts as stealth ambient watermark
        self.target_alpha = 0.28
        self.anim_timer_id = None

        # Filter & Data State
        self.active_currency = "ALL" # ALL, USD, EUR, GBP, JPY, GOLD
        self.impact_mode = "HIGH+MED" # HIGH+MED, HIGH ONLY, ALL
        self.scroll_offset = 0
        self.events_data: List[Dict[str, Any]] = []
        self.sessions_data: Dict[str, Any] = {}
        self.last_fetch_time = 0.0
        self.tick_counter = 0

        # Colors (Flowork Sovereign Palette)
        self.gold_color = (0.96, 0.77, 0.19, 1.0)       # Amber Gold (#F5C518)
        self.high_impact_color = (0.94, 0.27, 0.32, 1.0) # Crimson (#EF4444)
        self.med_impact_color = (0.96, 0.62, 0.15, 1.0)  # Amber (#F59E0B)
        self.low_impact_color = (0.20, 0.80, 0.75, 1.0)  # Cyan Teal (#14B8A6)

        # Interactive Hit-Testing
        self.click_regions = {}

        # Event Listeners
        self.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.SCROLL_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        self.connect("draw", self._on_draw)
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
        self.connect("button-press-event", self._on_button_press)
        self.connect("scroll-event", self._on_scroll)
        self.connect("screen-changed", self._on_screen_changed)

        # Initial Data Population
        self._refresh_data(force=False)

        # Periodic Refresh Timers
        GLib.timeout_add(1000, self._on_second_tick)
        GLib.timeout_add_seconds(600, self._on_periodic_data_fetch)

    def reposition_to_top_right(self):
        screen = self.get_screen()
        w = screen.get_width()
        scale = max(0.9, min(1.3, w / 2560.0))
        target_w = int(self.base_width * scale)
        target_h = int(self.base_height * scale)
        margin_x = int(24 * scale)
        margin_y = int(48 * scale)
        target_x = w - target_w - margin_x
        target_y = margin_y
        self.resize(target_w, target_h)
        self.move(target_x, target_y)

    def _on_screen_changed(self, widget, previous_screen):
        self.reposition_to_top_right()

    def _refresh_data(self, force: bool = False):
        try:
            self.events_data = forex_feed.get_calendar_events(force_refresh=force)
            self.sessions_data = forex_feed.get_market_sessions()
            self.last_fetch_time = time.time()
        except Exception as e:
            pass

    def _on_periodic_data_fetch(self):
        self._refresh_data(force=True)
        self.queue_draw()
        return True

    def _on_second_tick(self):
        self.tick_counter += 1
        # Smooth hover bloom animation interpolation
        if abs(self.alpha_anim - self.target_alpha) > 0.01:
            step = 0.08 if self.is_hovered else 0.04
            self.alpha_anim += (self.target_alpha - self.alpha_anim) * step
            self.queue_draw()

        # Update market sessions in memory every 15s
        if self.tick_counter % 15 == 0:
            self.sessions_data = forex_feed.get_market_sessions()
            self.queue_draw()

        return True

    def _on_enter(self, widget, event):
        self.is_hovered = True
        self.target_alpha = 0.96
        self.queue_draw()
        return False

    def _on_leave(self, widget, event):
        self.is_hovered = False
        self.target_alpha = 0.28
        self.queue_draw()
        return False

    def _on_button_press(self, widget, event):
        if event.button == 1:
            x, y = event.x, event.y
            for name, rect in self.click_regions.items():
                rx, ry, rw, rh = rect
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    if name.startswith("cur_"):
                        self.active_currency = name.replace("cur_", "")
                        self.scroll_offset = 0
                        self.queue_draw()
                        return True
                    elif name == "toggle_impact":
                        # Cycle modes: HIGH+MED -> HIGH ONLY -> ALL -> HIGH+MED
                        if self.impact_mode == "HIGH+MED":
                            self.impact_mode = "HIGH ONLY"
                        elif self.impact_mode == "HIGH ONLY":
                            self.impact_mode = "ALL"
                        else:
                            self.impact_mode = "HIGH+MED"
                        self.scroll_offset = 0
                        self.queue_draw()
                        return True
                    elif name == "btn_refresh":
                        self._refresh_data(force=True)
                        self.scroll_offset = 0
                        self.queue_draw()
                        return True
                    elif name == "scroll_up":
                        self.scroll_offset = max(0, self.scroll_offset - 5)
                        self.queue_draw()
                        return True
                    elif name == "scroll_down":
                        filtered = self._get_filtered_events()
                        if self.scroll_offset + 5 < len(filtered):
                            self.scroll_offset += 5
                        else:
                            self.scroll_offset = max(0, len(filtered) - 5)
                        self.queue_draw()
                        return True
        return False

    def _on_scroll(self, widget, event):
        filtered = self._get_filtered_events()
        if event.direction == Gdk.ScrollDirection.UP:
            self.scroll_offset = max(0, self.scroll_offset - 1)
            self.queue_draw()
            return True
        elif event.direction == Gdk.ScrollDirection.DOWN:
            if self.scroll_offset + 1 < len(filtered):
                self.scroll_offset += 1
                self.queue_draw()
                return True
        return False

    def _get_filtered_events(self) -> List[Dict[str, Any]]:
        items = self.events_data
        # Currency filter
        if self.active_currency == "GOLD":
            items = [e for e in items if e.get("is_gold")]
        elif self.active_currency != "ALL":
            items = [e for e in items if e.get("country") == self.active_currency]

        # Impact filter
        if self.impact_mode == "HIGH ONLY":
            items = [e for e in items if e.get("impact") == "High"]
        elif self.impact_mode == "HIGH+MED":
            items = [e for e in items if e.get("impact") in ("High", "Medium")]

        return items

    def _on_draw(self, widget, cr: cairo.Context):
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        scale = w / float(self.base_width)

        # Clear background to transparent
        cr.save()
        cr.set_operator(cairo.Operator.CLEAR)
        cr.paint()
        cr.restore()

        self.click_regions = {}
        alpha_mult = self.alpha_anim

        # Outer Holographic Canvas
        pad = 6.0 * scale
        cw = w - 2 * pad
        ch = h - 2 * pad
        cx = pad
        cy = pad
        radius = 12.0 * scale

        # Draw Backdrop Card
        round_rect(cr, cx, cy, cw, ch, radius)
        if self.is_hovered:
            cr.set_source_rgba(0.04, 0.06, 0.10, 0.88 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(1.0 * scale)
            cr.set_source_rgba(0.20, 0.45, 0.75, 0.60 * alpha_mult)
            cr.stroke()
        else:
            cr.set_source_rgba(0.02, 0.04, 0.07, 0.45 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.75 * scale)
            cr.set_source_rgba(0.15, 0.30, 0.50, 0.30 * alpha_mult)
            cr.stroke()

        # Render Header Section
        self._draw_header(cr, cx, cy, cw, scale, alpha_mult)

        # Render Market Session Radar (SYD, TYO, LDN, NYC)
        self._draw_session_radar(cr, cx, cy, cw, scale, alpha_mult)

        # Render Currency Filter Bar & Impact Toggle
        self._draw_currency_filters(cr, cx, cy, cw, scale, alpha_mult)

        # Render Event List
        self._draw_event_list(cr, cx, cy, cw, ch, scale, alpha_mult)

        return False

    def _draw_header(self, cr, cx, cy, cw, scale, alpha_mult):
        top_y = cy + 10 * scale

        # Title: FOREX QUANTUM CALENDAR
        cr.save()
        layout = self.create_pango_layout("FOREX RADAR")
        desc = Pango.FontDescription("Inter, sans-serif Heavy")
        desc.set_size(int(9.0 * Pango.SCALE * scale))
        layout.set_font_description(desc)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * alpha_mult)
        cr.move_to(cx + 14 * scale, top_y + 1 * scale)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

        # Subtitle / UTC Clock
        utc_str = self.sessions_data.get("utc_time_str", "UTC")
        cr.save()
        sub_layout = self.create_pango_layout(f"REAL-TIME HUD  •  {utc_str}")
        sub_desc = Pango.FontDescription("Inter, monospace Bold")
        sub_desc.set_size(int(6.5 * Pango.SCALE * scale))
        sub_layout.set_font_description(sub_desc)
        cr.set_source_rgba(self.gold_color[0], self.gold_color[1], self.gold_color[2], 0.85 * alpha_mult)
        cr.move_to(cx + 14 * scale, top_y + 16 * scale)
        PangoCairo.show_layout(cr, sub_layout)
        cr.restore()

        # Refresh Icon / Button at Right
        rf_w = 22 * scale
        rf_h = 22 * scale
        rf_x = cx + cw - 14 * scale - rf_w
        rf_y = top_y + 2 * scale
        self.click_regions["btn_refresh"] = (rf_x, rf_y, rf_w, rf_h)

        round_rect(cr, rf_x, rf_y, rf_w, rf_h, 4.0 * scale)
        cr.set_line_width(0.6 * scale)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.15 * alpha_mult)
        cr.stroke()

        cr.save()
        rf_layout = self.create_pango_layout("↻")
        rf_desc = Pango.FontDescription("sans-serif Bold")
        rf_desc.set_size(int(10.0 * Pango.SCALE * scale))
        rf_layout.set_font_description(rf_desc)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.70 * alpha_mult)
        cr.move_to(rf_x + 5.5 * scale, rf_y + 1.5 * scale)
        PangoCairo.show_layout(cr, rf_layout)
        cr.restore()

        # Header Separator
        div_y1 = top_y + 34 * scale
        cr.set_line_width(0.5 * scale)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.08 * alpha_mult)
        cr.move_to(cx + 10 * scale, div_y1)
        cr.line_to(cx + cw - 10 * scale, div_y1)
        cr.stroke()

    def _draw_session_radar(self, cr, cx, cy, cw, scale, alpha_mult):
        top_y = cy + 10 * scale
        div_y1 = top_y + 34 * scale
        sess_y = div_y1 + 8 * scale

        sessions = self.sessions_data.get("sessions", [])
        if not sessions:
            return

        pill_w = (cw - 20 * scale - (len(sessions) - 1) * 6 * scale) / float(len(sessions))
        pill_h = 32 * scale

        for idx, s in enumerate(sessions):
            px = cx + 10 * scale + idx * (pill_w + 6 * scale)
            py = sess_y
            is_open = s.get("is_open", False)

            round_rect(cr, px, py, pill_w, pill_h, 5.0 * scale)

            if is_open:
                # Glowing Emerald Green
                cr.set_source_rgba(0.08, 0.35, 0.22, 0.50 * alpha_mult)
                cr.fill_preserve()
                cr.set_line_width(1.0 * scale)
                cr.set_source_rgba(0.20, 0.90, 0.45, 0.90 * alpha_mult)
                cr.stroke()
            else:
                # Dim Closed
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.03 * alpha_mult)
                cr.fill_preserve()
                cr.set_line_width(0.5 * scale)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.12 * alpha_mult)
                cr.stroke()

            # Session Code + Status
            cr.save()
            txt_code = f"{s.get('code')}"
            sc_layout = self.create_pango_layout(txt_code)
            sc_desc = Pango.FontDescription("Inter, monospace Bold")
            sc_desc.set_size(int(7.0 * Pango.SCALE * scale))
            sc_layout.set_font_description(sc_desc)
            if is_open:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * alpha_mult)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.45 * alpha_mult)
            cr.move_to(px + 7 * scale, py + 4 * scale)
            PangoCairo.show_layout(cr, sc_layout)
            cr.restore()

            # Status Badge: OPEN (Green Dot) or CLOSED
            cr.save()
            st_text = "● OPEN" if is_open else "CLOSED"
            st_layout = self.create_pango_layout(st_text)
            st_desc = Pango.FontDescription("Inter, sans-serif Bold")
            st_desc.set_size(int(5.5 * Pango.SCALE * scale))
            st_layout.set_font_description(st_desc)
            if is_open:
                cr.set_source_rgba(0.20, 0.90, 0.45, 0.95 * alpha_mult)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.30 * alpha_mult)
            cr.move_to(px + 7 * scale, py + 18 * scale)
            PangoCairo.show_layout(cr, st_layout)
            cr.restore()

        # Session Overlap or Weekend banner
        banner_y = sess_y + pill_h + 6 * scale
        banner_h = 22 * scale

        round_rect(cr, cx + 10 * scale, banner_y, cw - 20 * scale, banner_h, 4.0 * scale)
        if self.sessions_data.get("is_overlap"):
            cr.set_source_rgba(0.96, 0.62, 0.15, 0.20 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.75 * scale)
            cr.set_source_rgba(0.96, 0.62, 0.15, 0.80 * alpha_mult)
            cr.stroke()
            b_text = "🔥 HIGH VOLATILITY OVERLAP: LONDON & NEW YORK ACTIVE"
            b_color = (1.0, 0.85, 0.4, 1.0)
        elif self.sessions_data.get("is_weekend"):
            cr.set_source_rgba(0.2, 0.3, 0.4, 0.20 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.6 * scale)
            cr.set_source_rgba(0.5, 0.7, 0.9, 0.50 * alpha_mult)
            cr.stroke()
            cd = self.sessions_data.get("countdown_open", "")
            b_text = f"MARKET CLOSED (WEEKEND) • SYDNEY OPENS IN {cd}" if cd else "MARKET CLOSED (WEEKEND)"
            b_color = (0.7, 0.85, 1.0, 0.85)
        else:
            cr.set_source_rgba(0.1, 0.4, 0.25, 0.15 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.6 * scale)
            cr.set_source_rgba(0.2, 0.8, 0.4, 0.50 * alpha_mult)
            cr.stroke()
            b_text = f"ACTIVE SESSIONS: {self.sessions_data.get('active_count', 0)} / 4 SESSIONS TRADING"
            b_color = (0.6, 0.9, 0.7, 0.85)

        cr.save()
        bn_layout = self.create_pango_layout(b_text)
        bn_desc = Pango.FontDescription("Inter, monospace Bold")
        bn_desc.set_size(int(6.5 * Pango.SCALE * scale))
        bn_layout.set_font_description(bn_desc)
        cr.set_source_rgba(b_color[0], b_color[1], b_color[2], b_color[3] * alpha_mult)
        cr.move_to(cx + 18 * scale, banner_y + 5 * scale)
        PangoCairo.show_layout(cr, bn_layout)
        cr.restore()

    def _draw_currency_filters(self, cr, cx, cy, cw, scale, alpha_mult):
        top_y = cy + 10 * scale
        div_y1 = top_y + 34 * scale
        sess_y = div_y1 + 8 * scale
        pill_h = 32 * scale
        banner_y = sess_y + pill_h + 6 * scale
        banner_h = 22 * scale
        chips_y = banner_y + banner_h + 8 * scale

        currencies = ["ALL", "USD", "EUR", "GBP", "JPY", "GOLD"]
        chip_x = cx + 10 * scale

        for c_code in currencies:
            is_active = (self.active_currency == c_code)
            chip_w = 34.0 * scale if c_code != "GOLD" else 48.0 * scale
            chip_h = 20.0 * scale

            self.click_regions[f"cur_{c_code}"] = (chip_x, chips_y, chip_w, chip_h)

            round_rect(cr, chip_x, chips_y, chip_w, chip_h, 3.5 * scale)
            if is_active:
                if c_code == "GOLD":
                    cr.set_source_rgba(self.gold_color[0], self.gold_color[1], self.gold_color[2], 0.35 * alpha_mult)
                    cr.fill_preserve()
                    cr.set_line_width(0.9 * scale)
                    cr.set_source_rgba(self.gold_color[0], self.gold_color[1], self.gold_color[2], 0.95 * alpha_mult)
                    cr.stroke()
                else:
                    cr.set_source_rgba(0.25, 0.55, 0.95, 0.35 * alpha_mult)
                    cr.fill_preserve()
                    cr.set_line_width(0.9 * scale)
                    cr.set_source_rgba(0.40, 0.70, 1.0, 0.95 * alpha_mult)
                    cr.stroke()
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.04 * alpha_mult)
                cr.fill_preserve()
                cr.set_line_width(0.5 * scale)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.15 * alpha_mult)
                cr.stroke()

            # Text Label
            cr.save()
            cp_layout = self.create_pango_layout(c_code)
            cp_desc = Pango.FontDescription("Inter, monospace Bold")
            cp_desc.set_size(int(6.5 * Pango.SCALE * scale))
            cp_layout.set_font_description(cp_desc)
            if is_active:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * alpha_mult)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.40 * alpha_mult)
            cr.move_to(chip_x + 5.5 * scale, chips_y + 3.5 * scale)
            PangoCairo.show_layout(cr, cp_layout)
            cr.restore()

            chip_x += chip_w + 5.0 * scale

        # Impact Mode Toggle Chip (HIGH+MED / HIGH ONLY / ALL)
        impact_w = 78.0 * scale
        impact_h = 20.0 * scale
        impact_x = cx + cw - 10 * scale - impact_w
        self.click_regions["toggle_impact"] = (impact_x, chips_y, impact_w, impact_h)

        round_rect(cr, impact_x, chips_y, impact_w, impact_h, 3.5 * scale)
        if self.impact_mode == "HIGH ONLY":
            cr.set_source_rgba(self.high_impact_color[0], self.high_impact_color[1], self.high_impact_color[2], 0.22 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.9 * scale)
            cr.set_source_rgba(self.high_impact_color[0], self.high_impact_color[1], self.high_impact_color[2], 0.90 * alpha_mult)
            cr.stroke()
            imp_label = "HIGH ONLY"
            txt_color = self.high_impact_color
        elif self.impact_mode == "HIGH+MED":
            cr.set_source_rgba(0.95, 0.65, 0.15, 0.18 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.85 * scale)
            cr.set_source_rgba(0.95, 0.70, 0.20, 0.85 * alpha_mult)
            cr.stroke()
            imp_label = "HIGH + MED"
            txt_color = (0.95, 0.75, 0.25, 1.0)
        else: # ALL
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.05 * alpha_mult)
            cr.fill_preserve()
            cr.set_line_width(0.6 * scale)
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.35 * alpha_mult)
            cr.stroke()
            imp_label = "ALL IMPACT"
            txt_color = (1.0, 1.0, 1.0, 0.80)

        cr.save()
        imp_layout = self.create_pango_layout(imp_label)
        imp_desc = Pango.FontDescription("Inter, monospace Bold")
        imp_desc.set_size(int(6.5 * Pango.SCALE * scale))
        imp_layout.set_font_description(imp_desc)
        cr.set_source_rgba(txt_color[0], txt_color[1], txt_color[2], 0.90 * alpha_mult)
        cr.move_to(impact_x + 6 * scale, chips_y + 3.5 * scale)
        PangoCairo.show_layout(cr, imp_layout)
        cr.restore()

    def _draw_event_list(self, cr, cx, cy, cw, ch, scale, alpha_mult):
        top_y = cy + 10 * scale
        div_y1 = top_y + 34 * scale
        sess_y = div_y1 + 8 * scale
        pill_h = 32 * scale
        banner_y = sess_y + pill_h + 6 * scale
        banner_h = 22 * scale
        chips_y = banner_y + banner_h + 8 * scale
        chips_h = 20 * scale

        list_y = chips_y + chips_h + 8 * scale
        card_h = 70.0 * scale
        card_gap = 6.0 * scale
        visible_count = 5  # Show 5 economic events simultaneously!

        filtered_events = self._get_filtered_events()

        if not filtered_events:
            cr.save()
            empty_layout = self.create_pango_layout("NO ECONOMIC EVENTS MATCH CURRENT FILTER")
            empty_desc = Pango.FontDescription("Inter, monospace Bold")
            empty_desc.set_size(int(7.5 * Pango.SCALE * scale))
            empty_layout.set_font_description(empty_desc)
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.35 * alpha_mult)
            cr.move_to(cx + 25 * scale, list_y + 60 * scale)
            PangoCairo.show_layout(cr, empty_layout)
            cr.restore()
        else:
            start_idx = self.scroll_offset
            end_idx = min(len(filtered_events), start_idx + visible_count)

            for i in range(start_idx, end_idx):
                ev = filtered_events[i]
                cy_card = list_y + (i - start_idx) * (card_h + card_gap)
                cx_card = cx + 10 * scale
                cw_card = cw - 20 * scale

                # Card Background
                round_rect(cr, cx_card, cy_card, cw_card, card_h, 6.0 * scale)
                cr.set_source_rgba(0.06, 0.09, 0.14, 0.50 * alpha_mult)
                cr.fill_preserve()

                # Impact Accent Line on Left Edge
                imp = ev.get("impact", "Low")
                if imp == "High":
                    imp_col = self.high_impact_color
                elif imp == "Medium":
                    imp_col = self.med_impact_color
                else:
                    imp_col = self.low_impact_color

                cr.set_line_width(0.6 * scale)
                cr.set_source_rgba(imp_col[0], imp_col[1], imp_col[2], 0.35 * alpha_mult)
                cr.stroke()

                # Left Impact Indicator Strip
                round_rect(cr, cx_card + 1 * scale, cy_card + 5 * scale, 3.5 * scale, card_h - 10 * scale, 2.0 * scale)
                cr.set_source_rgba(imp_col[0], imp_col[1], imp_col[2], 0.90 * alpha_mult)
                cr.fill()

                # Country Pill Badge
                cr_badge_w = 34 * scale
                cr_badge_h = 16 * scale
                bx = cx_card + 10 * scale
                by = cy_card + 7 * scale
                round_rect(cr, bx, by, cr_badge_w, cr_badge_h, 3.0 * scale)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.08 * alpha_mult)
                cr.fill_preserve()
                cr.set_line_width(0.5 * scale)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.20 * alpha_mult)
                cr.stroke()

                cr.save()
                c_layout = self.create_pango_layout(ev.get("country", "USD"))
                c_desc = Pango.FontDescription("Inter, monospace Bold")
                c_desc.set_size(int(6.5 * Pango.SCALE * scale))
                c_layout.set_font_description(c_desc)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * alpha_mult)
                cr.move_to(bx + 4.5 * scale, by + 2 * scale)
                PangoCairo.show_layout(cr, c_layout)
                cr.restore()

                # Impact Badge Pill
                ix = bx + cr_badge_w + 5 * scale
                iy = by
                i_badge_w = 42 * scale
                i_badge_h = 16 * scale
                round_rect(cr, ix, iy, i_badge_w, i_badge_h, 3.0 * scale)
                cr.set_source_rgba(imp_col[0], imp_col[1], imp_col[2], 0.18 * alpha_mult)
                cr.fill_preserve()
                cr.set_line_width(0.5 * scale)
                cr.set_source_rgba(imp_col[0], imp_col[1], imp_col[2], 0.65 * alpha_mult)
                cr.stroke()

                cr.save()
                imp_t_layout = self.create_pango_layout(imp.upper())
                imp_t_desc = Pango.FontDescription("Inter, sans-serif Bold")
                imp_t_desc.set_size(int(6.0 * Pango.SCALE * scale))
                imp_t_layout.set_font_description(imp_t_desc)
                cr.set_source_rgba(imp_col[0], imp_col[1], imp_col[2], 0.95 * alpha_mult)
                cr.move_to(ix + 5 * scale, iy + 2.5 * scale)
                PangoCairo.show_layout(cr, imp_t_layout)
                cr.restore()

                # Gold Radar Tag
                if ev.get("is_gold"):
                    gx = ix + i_badge_w + 5 * scale
                    gy = by
                    gw = 54 * scale
                    gh = 16 * scale
                    round_rect(cr, gx, gy, gw, gh, 3.0 * scale)
                    cr.set_source_rgba(self.gold_color[0], self.gold_color[1], self.gold_color[2], 0.20 * alpha_mult)
                    cr.fill_preserve()
                    cr.set_line_width(0.5 * scale)
                    cr.set_source_rgba(self.gold_color[0], self.gold_color[1], self.gold_color[2], 0.70 * alpha_mult)
                    cr.stroke()

                    cr.save()
                    g_layout = self.create_pango_layout("⚡ XAU/GOLD")
                    g_desc = Pango.FontDescription("Inter, sans-serif Bold")
                    g_desc.set_size(int(5.5 * Pango.SCALE * scale))
                    g_layout.set_font_description(g_desc)
                    cr.set_source_rgba(self.gold_color[0], self.gold_color[1], self.gold_color[2], 0.95 * alpha_mult)
                    cr.move_to(gx + 4.5 * scale, gy + 2.5 * scale)
                    PangoCairo.show_layout(cr, g_layout)
                    cr.restore()

                # Date & Countdown (Right aligned on top row)
                cr.save()
                status_txt = ev.get("time_status", "")
                date_txt = f"{ev.get('date_str', '')} • {ev.get('time_str', '')}"
                full_time_txt = f"{date_txt}  [{status_txt}]"
                dt_layout = self.create_pango_layout(full_time_txt)
                dt_desc = Pango.FontDescription("Inter, monospace Bold")
                dt_desc.set_size(int(6.5 * Pango.SCALE * scale))
                dt_layout.set_font_description(dt_desc)
                if "LIVE" in status_txt:
                    cr.set_source_rgba(0.95, 0.25, 0.25, 0.95 * alpha_mult)
                elif "in" in status_txt:
                    cr.set_source_rgba(0.35, 0.85, 0.55, 0.95 * alpha_mult)
                else:
                    cr.set_source_rgba(1.0, 1.0, 1.0, 0.40 * alpha_mult)

                dt_w, _ = dt_layout.get_pixel_size()
                cr.move_to(cx_card + cw_card - 8 * scale - dt_w, by + 1.5 * scale)
                PangoCairo.show_layout(cr, dt_layout)
                cr.restore()

                # Event Title (Middle row)
                cr.save()
                title_text = ev.get("title", "Economic Event")
                if len(title_text) > 42:
                    title_text = title_text[:39] + "..."
                ev_layout = self.create_pango_layout(title_text)
                ev_desc = Pango.FontDescription("Inter, sans-serif Bold")
                ev_desc.set_size(int(7.8 * Pango.SCALE * scale))
                ev_layout.set_font_description(ev_desc)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.90 * alpha_mult)
                cr.move_to(cx_card + 10 * scale, cy_card + 28 * scale)
                PangoCairo.show_layout(cr, ev_layout)
                cr.restore()

                # Forecast vs Previous (Bottom row)
                nums_text = f"FORECAST: {ev.get('forecast')}   |   PREVIOUS: {ev.get('previous')}"
                cr.save()
                num_layout = self.create_pango_layout(nums_text)
                num_desc = Pango.FontDescription("Inter, monospace Medium")
                num_desc.set_size(int(6.2 * Pango.SCALE * scale))
                num_layout.set_font_description(num_desc)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.45 * alpha_mult)
                cr.move_to(cx_card + 10 * scale, cy_card + 48 * scale)
                PangoCairo.show_layout(cr, num_layout)
                cr.restore()

        # Footer Pagination & Counter
        foot_y = cy + ch - 34 * scale
        cr.save()
        total_evs = len(filtered_events)
        showing_str = f"SHOWING {min(total_evs, self.scroll_offset + 1)}-{min(total_evs, self.scroll_offset + visible_count)} OF {total_evs} EVENTS" if total_evs > 0 else "0 EVENTS"
        ft_layout = self.create_pango_layout(showing_str)
        ft_desc = Pango.FontDescription("Inter, monospace Bold")
        ft_desc.set_size(int(6.5 * Pango.SCALE * scale))
        ft_layout.set_font_description(ft_desc)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.45 * alpha_mult)
        cr.move_to(cx + 12 * scale, foot_y + 6 * scale)
        PangoCairo.show_layout(cr, ft_layout)
        cr.restore()

        # Scroll Up / Down Buttons
        btn_up_x = cx + cw - 58 * scale
        btn_down_x = cx + cw - 28 * scale
        nav_y = foot_y + 3 * scale
        nav_w = 22 * scale
        nav_h = 20 * scale

        self.click_regions["scroll_up"] = (btn_up_x, nav_y, nav_w, nav_h)
        self.click_regions["scroll_down"] = (btn_down_x, nav_y, nav_w, nav_h)

        for bx, sym in [(btn_up_x, "▲"), (btn_down_x, "▼")]:
            round_rect(cr, bx, nav_y, nav_w, nav_h, 4.0 * scale)
            cr.set_line_width(0.6 * scale)
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.15 * alpha_mult)
            cr.stroke()

            cr.save()
            sy_layout = self.create_pango_layout(sym)
            sy_desc = Pango.FontDescription("sans-serif Bold")
            sy_desc.set_size(int(7.0 * Pango.SCALE * scale))
            sy_layout.set_font_description(sy_desc)
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.65 * alpha_mult)
            cr.move_to(bx + 6.5 * scale, nav_y + 3 * scale)
            PangoCairo.show_layout(cr, sy_layout)
            cr.restore()

def main():
    win = QuantumForexHUD()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
