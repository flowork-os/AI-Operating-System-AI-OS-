#!/usr/bin/env python3
"""
Flowork OS — FXCalc: Sovereign Forex Position Size & Risk Management Engine
Engine Location: /opt/floworkos/engine/fxcalc/fxcalc.py
Based on Tyler Katz's fxcalc architecture with Flowork OS Pure Optical Crystal Glass enhancements.

Features:
- Position sizing in Standard Lots, Mini Lots, Micro Lots & Exact Units
- Pip value calculation across Forex Majors, JPY Crosses, Commodities (XAU/USD) & Crypto
- Real-time Margin Utilization & Maximum Allowable Exposure based on Leverage
- Single-slot Cyber Wing & Standalone Crystal Glass GUI
"""

import sys
import os
import math
import json
import argparse
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo
import cairo

# ── Supported Forex Instruments & Defaults ──
SUPPORTED_PAIRS = [
    {"name": "EUR/USD", "base": "EUR", "quote": "USD", "type": "major", "default_price": 1.0540},
    {"name": "GBP/USD", "base": "GBP", "quote": "USD", "type": "major", "default_price": 1.2610},
    {"name": "USD/JPY", "base": "USD", "quote": "JPY", "type": "major", "default_price": 154.20},
    {"name": "XAU/USD", "base": "XAU", "quote": "USD", "type": "metal", "default_price": 2685.50},
    {"name": "USD/CHF", "base": "USD", "quote": "CHF", "type": "major", "default_price": 0.8840},
    {"name": "AUD/USD", "base": "AUD", "quote": "USD", "type": "major", "default_price": 0.6520},
    {"name": "USD/CAD", "base": "USD", "quote": "CAD", "type": "major", "default_price": 1.4020},
    {"name": "NZD/USD", "base": "NZD", "quote": "USD", "type": "major", "default_price": 0.5890},
    {"name": "EUR/GBP", "base": "EUR", "quote": "GBP", "type": "cross", "default_price": 0.8360},
    {"name": "GBP/JPY", "base": "GBP", "quote": "JPY", "type": "cross", "default_price": 194.50},
    {"name": "EUR/JPY", "base": "EUR", "quote": "JPY", "type": "cross", "default_price": 162.60},
    {"name": "BTC/USD", "base": "BTC", "quote": "USD", "type": "crypto", "default_price": 59300.0},
]

SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF"]
LEVERAGE_OPTIONS = [1, 10, 30, 50, 100, 200, 500, 1000, 2000]

# Flowork Pure Crystal Glass Color Palette
C_BG_DARK = (0.03, 0.05, 0.08)
C_SURFACE = (0.06, 0.10, 0.16)
C_WELL = (0.02, 0.03, 0.05)
C_BORDER = (0.16, 0.24, 0.35)
C_GREEN = (0.0, 1.0, 0.4)        # Matrix Green #00ff66
C_CYAN = (0.0, 0.95, 1.0)        # Cyber Cyan #00f3ff
C_AMBER = (1.0, 0.72, 0.0)       # Warning Amber
C_RED = (1.0, 0.2, 0.35)         # Risk Red
C_TEXT_WHITE = (0.95, 0.98, 1.0)
C_TEXT_MUTED = (0.55, 0.62, 0.72)


# ==============================================================================
# CORE POSITION SIZING ENGINE (Mathematical Heart of FXCalc)
# ==============================================================================
def calculate_position(
    margin: float,
    leverage: float,
    risk_value: float,
    is_risk_pct: bool,
    stop_loss_pips: float,
    pair_name: str,
    account_currency: str = "USD",
    base_price: float = None,
    home_quote_rate: float = 1.0
) -> dict:
    """
    Calculates institutional-grade Forex position sizes and risk telemetry.
    Matches Tyler Katz's fxcalc formula with extensions for lot conversions.
    """
    pair_info = next((p for p in SUPPORTED_PAIRS if p["name"] == pair_name), SUPPORTED_PAIRS[0])
    quote_currency = pair_info["quote"]
    base_currency = pair_info["base"]

    if base_price is None or base_price <= 0:
        base_price = pair_info["default_price"]

    # 1. Determine Pip Size
    if quote_currency == "JPY":
        pip_size = 0.01
    elif base_currency == "XAU" or quote_currency == "XAU":
        pip_size = 0.10
    elif base_currency == "BTC":
        pip_size = 1.00
    else:
        pip_size = 0.0001

    # 2. Risk Amount in Home Currency
    if is_risk_pct:
        risk_amount = margin * (risk_value / 100.0)
    else:
        risk_amount = risk_value

    risk_amount = max(0.01, min(margin, risk_amount))
    stop_loss_pips = max(0.1, stop_loss_pips)
    leverage = max(1.0, leverage)

    # 3. Stop loss distance in price terms
    stop_loss_distance = stop_loss_pips * pip_size

    # 4. Position Size in Units based on Risk
    units_raw = risk_amount / (stop_loss_distance * home_quote_rate) if (stop_loss_distance * home_quote_rate) > 0 else 0
    units = int(units_raw)

    # 5. Margin Limit & Max Units Calculation
    remaining_margin = margin - risk_amount
    margin_rate = 1.0 / leverage
    if quote_currency == account_currency:
        base_to_home = base_price
    else:
        base_to_home = base_price * home_quote_rate

    max_units_raw = (margin * leverage) / base_to_home if base_to_home > 0 else 0
    max_units = int(max_units_raw)

    # 6. Margin Required for Calculated Units
    margin_required = (units * base_to_home) / leverage if leverage > 0 else 0
    margin_utilization = (margin_required / margin * 100.0) if margin > 0 else 0.0
    wcma = margin - margin_required - risk_amount

    # 7. Pip Value for this Position in Home Currency
    pip_value_home = pip_size * units * home_quote_rate

    # 8. Lot Size Conversion
    unit_per_lot = 100.0 if base_currency == "XAU" else (1.0 if base_currency == "BTC" else 100000.0)
    lots = units / unit_per_lot
    max_lots = max_units / unit_per_lot

    # Error or Warning evaluation
    error_msg = ""
    if units <= 0:
        error_msg = "Risk or Stop Loss too small for minimum unit size"
    elif units > max_units:
        error_msg = "Insufficient Margin: Exceeds maximum leverage capacity"

    return {
        "pair": pair_name,
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "account_currency": account_currency,
        "base_price": base_price,
        "margin": margin,
        "leverage": leverage,
        "risk_value": risk_value,
        "is_risk_pct": is_risk_pct,
        "risk_amount": risk_amount,
        "risk_pct": (risk_amount / margin * 100.0) if margin > 0 else 0.0,
        "stop_loss_pips": stop_loss_pips,
        "pip_size": pip_size,
        "units": units,
        "lots": lots,
        "pip_value_home": pip_value_home,
        "margin_required": margin_required,
        "margin_utilization": margin_utilization,
        "max_units": max_units,
        "max_lots": max_lots,
        "wcma": wcma,
        "error": error_msg,
    }


# ==============================================================================
# STANDALONE FLOWORK PURE CRYSTAL GLASS GUI
# ==============================================================================
class FXCalcWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Flowork OS — FX Position & Risk Calculator")
        self.set_wmclass("flowork-fxcalc", "FloworkFXCalc")
        self.set_default_size(480, 720)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # State
        self.pair_idx = 0       # Default: EUR/USD
        self.currency_idx = 0   # Default: USD
        self.margin = 10000.0
        self.leverage = 500.0
        self.risk_pct = 1.0     # 1%
        self.is_risk_pct = True
        self.stop_loss_pips = 20.0
        self.base_price = SUPPORTED_PAIRS[0]["default_price"]

        # Hitbox tracking for interactive Cairo GUI
        self.hitboxes = []
        self.hovered_id = None

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
        self.connect("leave-notify-event", lambda *_: self.queue_draw())
        self.connect("scroll-event", self.on_scroll)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)

    def on_motion(self, widget, event):
        old_hov = self.hovered_id
        self.hovered_id = None
        for (x, y, w, h, hid) in self.hitboxes:
            if x <= event.x <= x + w and y <= event.y <= y + h:
                self.hovered_id = hid
                break
        if old_hov != self.hovered_id:
            self.queue_draw()

    def on_click(self, widget, event):
        if event.button == 1:
            for (x, y, w, h, hid) in self.hitboxes:
                if x <= event.x <= x + w and y <= event.y <= y + h:
                    self._handle_action(hid)
                    self.queue_draw()
                    return True
        return False

    def on_scroll(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            self.stop_loss_pips = min(500.0, self.stop_loss_pips + 1.0)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.stop_loss_pips = max(1.0, self.stop_loss_pips - 1.0)
        self.queue_draw()
        return True

    def on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
        return False

    def _handle_action(self, hid):
        if hid.startswith("pair:"):
            idx = int(hid.split(":")[1])
            self.pair_idx = idx
            self.base_price = SUPPORTED_PAIRS[idx]["default_price"]
        elif hid.startswith("risk:"):
            val = float(hid.split(":")[1])
            self.risk_pct = val
            self.is_risk_pct = True
        elif hid.startswith("sl:"):
            delta = float(hid.split(":")[1])
            self.stop_loss_pips = max(1.0, min(500.0, self.stop_loss_pips + delta))
        elif hid.startswith("lev:"):
            self.leverage = float(hid.split(":")[1])
        elif hid.startswith("margin:"):
            delta = float(hid.split(":")[1])
            self.margin = max(100.0, self.margin + delta)

    def on_draw(self, widget, cr):
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        self.hitboxes = []

        # Background Optical Crystal Glass
        cr.save()
        lin = cairo.LinearGradient(0, 0, 0, h)
        lin.add_color_stop_rgba(0.0, C_BG_DARK[0], C_BG_DARK[1], C_BG_DARK[2], 0.94)
        lin.add_color_stop_rgba(1.0, 0.01, 0.02, 0.04, 0.96)
        cr.set_source(lin)
        cr.paint()

        # Pure Specular Rim Top Highlight
        cr.new_path()
        cr.move_to(0, 1)
        cr.line_to(w, 1)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.22)
        cr.set_line_width(1.5)
        cr.stroke()

        pctx = PangoCairo.create_context(cr)
        layout = Pango.Layout.new(pctx)

        # ── Header ──
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 13"))
        layout.set_text("⚡ FLOWORK OS // FX POSITION & RISK ENGINE", -1)
        cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.95)
        cr.move_to(24, 20)
        PangoCairo.show_layout(cr, layout)

        layout.set_font_description(Pango.FontDescription("Inter 8.5"))
        layout.set_text("Institutional Mathematical Position Sizing & Margin Management", -1)
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.80)
        cr.move_to(24, 42)
        PangoCairo.show_layout(cr, layout)

        # Divider
        cr.move_to(24, 62)
        cr.line_to(w - 24, 62)
        cr.set_source_rgba(C_BORDER[0], C_BORDER[1], C_BORDER[2], 0.40)
        cr.set_line_width(1.0)
        cr.stroke()

        # ── Pair Selection Row ──
        pair_y = 74
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        layout.set_text("SELECT TRADING PAIR", -1)
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.75)
        cr.move_to(24, pair_y)
        PangoCairo.show_layout(cr, layout)

        p_btn_w = 68
        p_btn_h = 28
        p_gap = 6
        p_x = 24
        p_y = pair_y + 16

        top_pairs = SUPPORTED_PAIRS[:6]
        for i, p in enumerate(top_pairs):
            bx = p_x + i * (p_btn_w + p_gap)
            is_sel = (i == self.pair_idx)
            is_hov = (self.hovered_id == f"pair:{i}")

            cr.new_path()
            self._rounded_rect(cr, bx, p_y, p_btn_w, p_btn_h, 6)
            if is_sel:
                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.28)
                cr.fill_preserve()
                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.95)
                cr.set_line_width(1.4)
                cr.stroke()
            elif is_hov:
                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.12)
                cr.fill_preserve()
                cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.50)
                cr.set_line_width(1.0)
                cr.stroke()
            else:
                cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.60)
                cr.fill_preserve()
                cr.set_source_rgba(C_BORDER[0], C_BORDER[1], C_BORDER[2], 0.35)
                cr.set_line_width(0.8)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8"))
            layout.set_text(p["name"], -1)
            tw, th = layout.get_pixel_size()
            cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 1.0 if is_sel else 0.75)
            cr.move_to(bx + (p_btn_w - tw) / 2, p_y + (p_btn_h - th) / 2)
            PangoCairo.show_layout(cr, layout)
            self.hitboxes.append((bx, p_y, p_btn_w, p_btn_h, f"pair:{i}"))

        # ── Compute Real-time Results ──
        cur_pair = SUPPORTED_PAIRS[self.pair_idx]
        res = calculate_position(
            margin=self.margin,
            leverage=self.leverage,
            risk_value=self.risk_pct,
            is_risk_pct=self.is_risk_pct,
            stop_loss_pips=self.stop_loss_pips,
            pair_name=cur_pair["name"],
            account_currency=SUPPORTED_CURRENCIES[self.currency_idx],
            base_price=self.base_price,
        )

        # ── Parameter Control Deck ──
        ctrl_y = p_y + p_btn_h + 16
        # Account Margin Block
        self._draw_param_box(cr, layout, 24, ctrl_y, 206, 76, "ACCOUNT MARGIN", f"${self.margin:,.0f}", [
            ("-$1k", -1000, "margin:-1000"),
            ("+$1k", +1000, "margin:1000"),
            ("+$5k", +5000, "margin:5000"),
        ])

        # Leverage Block
        self._draw_param_box(cr, layout, 246, ctrl_y, 206, 76, "LEVERAGE RATIO", f"1:{int(self.leverage)}", [
            ("1:100", 100, "lev:100"),
            ("1:500", 500, "lev:500"),
            ("1:1000", 1000, "lev:1000"),
        ])

        # Risk & Stop Loss Deck
        ctrl2_y = ctrl_y + 88
        # Risk Selection
        self._draw_param_box(cr, layout, 24, ctrl2_y, 206, 76, "ACCOUNT RISK", f"{self.risk_pct:.1f}% (${res['risk_amount']:,.2f})", [
            ("0.5%", 0.5, "risk:0.5"),
            ("1.0%", 1.0, "risk:1.0"),
            ("2.0%", 2.0, "risk:2.0"),
            ("3.0%", 3.0, "risk:3.0"),
        ])

        # Stop Loss Selection
        self._draw_param_box(cr, layout, 246, ctrl2_y, 206, 76, "STOP LOSS (PIPS)", f"{self.stop_loss_pips:.0f} PIPS", [
            ("-5p", -5, "sl:-5"),
            ("-1p", -1, "sl:-1"),
            ("+1p", +1, "sl:1"),
            ("+5p", +5, "sl:5"),
        ])

        # ── MAIN TELEMETRY WELL: POSITION LOT SIZE ──
        well_y = ctrl2_y + 92
        well_w = w - 48
        well_h = 160

        cr.new_path()
        self._rounded_rect(cr, 24, well_y, well_w, well_h, 12)
        cr.set_source_rgba(C_WELL[0], C_WELL[1], C_WELL[2], 0.88)
        cr.fill_preserve()
        cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.40)
        cr.set_line_width(1.2)
        cr.stroke()

        # Well Header
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8"))
        layout.set_text("CALCULATED POSITION SIZE", -1)
        cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.90)
        cr.move_to(38, well_y + 14)
        PangoCairo.show_layout(cr, layout)

        # Huge Lot Display
        lots_str = f"{res['lots']:.2f} LOTS"
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 28"))
        layout.set_text(lots_str, -1)
        tw, th = layout.get_pixel_size()

        # Ambient Glow
        cr.set_source_rgba(C_GREEN[0], C_GREEN[1], C_GREEN[2], 0.25)
        cr.move_to(24 + (well_w - tw) / 2, well_y + 48)
        PangoCairo.show_layout(cr, layout)

        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.98)
        cr.move_to(24 + (well_w - tw) / 2, well_y + 47)
        PangoCairo.show_layout(cr, layout)

        # Units Subtitle
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.5"))
        layout.set_text(f"EXACT UNITS: {res['units']:,} UNITS  •  BASE PRICE: {res['base_price']}", -1)
        uw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.85)
        cr.move_to(24 + (well_w - uw) / 2, well_y + 92)
        PangoCairo.show_layout(cr, layout)

        # Pip value & Required Margin Bar
        pv_txt = f"PIP VALUE: ${res['pip_value_home']:.2f}  |  MARGIN REQUIRED: ${res['margin_required']:.2f} ({res['margin_utilization']:.1f}%)"
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 8"))
        layout.set_text(pv_txt, -1)
        pw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.80)
        cr.move_to(24 + (well_w - pw) / 2, well_y + 116)
        PangoCairo.show_layout(cr, layout)

        # Utilization Progress Bar
        bar_w = well_w - 40
        bar_h = 6
        bx = 24 + 20
        by = well_y + well_h - 18
        cr.new_path()
        self._rounded_rect(cr, bx, by, bar_w, bar_h, 3)
        cr.set_source_rgba(0.1, 0.15, 0.2, 0.8)
        cr.fill()

        util_frac = min(1.0, max(0.0, res["margin_utilization"] / 100.0))
        if util_frac > 0:
            fill_col = C_RED if util_frac > 0.8 else (C_AMBER if util_frac > 0.5 else C_GREEN)
            cr.new_path()
            self._rounded_rect(cr, bx, by, bar_w * util_frac, bar_h, 3)
            cr.set_source_rgba(fill_col[0], fill_col[1], fill_col[2], 0.9)
            cr.fill()

        # ── Bottom Telemetry Grid ──
        grid_y = well_y + well_h + 16
        self._draw_metric_pill(cr, layout, 24, grid_y, 206, 52, "MAX ALLOWABLE SIZE", f"{res['max_lots']:.2f} Lots ({res['max_units']:,} u)")
        self._draw_metric_pill(cr, layout, 246, grid_y, 206, 52, "WORST-CASE WCMA", f"${res['wcma']:,.2f}")

        # Footer
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text("FLOWORK OS SOVEREIGN ENGINE • /opt/floworkos/engine/fxcalc", -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.40)
        cr.move_to(24 + (well_w - tw) / 2, h - 22)
        PangoCairo.show_layout(cr, layout)

        cr.restore()
        return True

    def _draw_param_box(self, cr, layout, x, y, w, h, title, val_str, buttons):
        cr.new_path()
        self._rounded_rect(cr, x, y, w, h, 8)
        cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.60)
        cr.fill_preserve()
        cr.set_source_rgba(C_BORDER[0], C_BORDER[1], C_BORDER[2], 0.35)
        cr.set_line_width(0.8)
        cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.2"))
        layout.set_text(title, -1)
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.70)
        cr.move_to(x + 10, y + 8)
        PangoCairo.show_layout(cr, layout)

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11"))
        layout.set_text(val_str, -1)
        cr.set_source_rgba(C_TEXT_WHITE[0], C_TEXT_WHITE[1], C_TEXT_WHITE[2], 0.95)
        cr.move_to(x + 10, y + 24)
        PangoCairo.show_layout(cr, layout)

        # Mini Buttons
        bw = (w - 20 - (len(buttons) - 1) * 4) / len(buttons)
        bh = 18
        by = y + h - bh - 6
        for i, (blbl, _val, hid) in enumerate(buttons):
            bx = x + 10 + i * (bw + 4)
            is_hov = (self.hovered_id == hid)

            cr.new_path()
            self._rounded_rect(cr, bx, by, bw, bh, 4)
            cr.set_source_rgba(C_GREEN[0] if is_hov else 0.15, C_GREEN[1] if is_hov else 0.20, C_GREEN[2] if is_hov else 0.28, 0.30 if is_hov else 0.40)
            cr.fill_preserve()
            cr.set_source_rgba(C_GREEN[0] if is_hov else C_BORDER[0], C_GREEN[1] if is_hov else C_BORDER[1], C_GREEN[2] if is_hov else C_BORDER[2], 0.8 if is_hov else 0.3)
            cr.set_line_width(0.8)
            cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
            layout.set_text(blbl, -1)
            tw, th = layout.get_pixel_size()
            cr.set_source_rgba(C_GREEN[0] if is_hov else C_TEXT_WHITE[0], C_GREEN[1] if is_hov else C_TEXT_WHITE[1], C_GREEN[2] if is_hov else C_TEXT_WHITE[2], 0.9)
            cr.move_to(bx + (bw - tw) / 2, by + (bh - th) / 2)
            PangoCairo.show_layout(cr, layout)
            self.hitboxes.append((bx, by, bw, bh, hid))

    def _draw_metric_pill(self, cr, layout, x, y, w, h, title, val):
        cr.new_path()
        self._rounded_rect(cr, x, y, w, h, 8)
        cr.set_source_rgba(C_SURFACE[0], C_SURFACE[1], C_SURFACE[2], 0.50)
        cr.fill_preserve()
        cr.set_source_rgba(C_BORDER[0], C_BORDER[1], C_BORDER[2], 0.30)
        cr.set_line_width(0.8)
        cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.0"))
        layout.set_text(title, -1)
        cr.set_source_rgba(C_TEXT_MUTED[0], C_TEXT_MUTED[1], C_TEXT_MUTED[2], 0.65)
        cr.move_to(x + 10, y + 8)
        PangoCairo.show_layout(cr, layout)

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.2"))
        layout.set_text(val, -1)
        cr.set_source_rgba(C_CYAN[0], C_CYAN[1], C_CYAN[2], 0.90)
        cr.move_to(x + 10, y + 26)
        PangoCairo.show_layout(cr, layout)

    def _rounded_rect(self, cr, x, y, w, h, r):
        cr.move_to(x + r, y)
        cr.line_to(x + w - r, y)
        cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        cr.line_to(x + w, y + h - r)
        cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        cr.line_to(x + r, y + h)
        cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        cr.line_to(x, y + r)
        cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        cr.close_path()


# ==============================================================================
# CLI DISPATCHER
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Flowork OS FX Position Size & Risk Calculator")
    parser.add_argument("--calc", action="store_true", help="Calculate position in headless CLI mode and output JSON")
    parser.add_argument("--margin", type=float, default=10000.0, help="Available margin (default: 10000)")
    parser.add_argument("--leverage", type=float, default=500.0, help="Account leverage (default: 500)")
    parser.add_argument("--risk", type=float, default=1.0, help="Risk value in pct or home currency (default: 1.0)")
    parser.add_argument("--risk-amt", action="store_true", help="Treat risk value as absolute amount rather than percentage")
    parser.add_argument("--sl", type=float, default=20.0, help="Stop loss in pips (default: 20)")
    parser.add_argument("--pair", type=str, default="EUR/USD", help="Trading pair (default: EUR/USD)")
    parser.add_argument("--account", type=str, default="USD", help="Account currency (default: USD)")
    parser.add_argument("--price", type=float, default=None, help="Base price (optional, uses live/default)")

    args = parser.parse_args()

    if args.calc:
        res = calculate_position(
            margin=args.margin,
            leverage=args.leverage,
            risk_value=args.risk,
            is_risk_pct=not args.risk_amt,
            stop_loss_pips=args.sl,
            pair_name=args.pair,
            account_currency=args.account,
            base_price=args.price,
        )
        print(json.dumps(res, indent=2))
        return 0

    # GUI Mode
    win = FXCalcWindow()
    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
