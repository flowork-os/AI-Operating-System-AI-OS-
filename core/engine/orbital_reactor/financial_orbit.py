#!/usr/bin/env python3
# ==============================================================================
# 👑 FLOWORK OS — ORBITAL REACTOR FINANCIAL RADAR (SOVEREIGN PURE TEXT)
# 
# Design Mandate:
# - NO BUTTONS. NO BOXES. NO FRAMES.
# - Pure, high-precision sovereign floating telemetry text with dark shadow aura.
# - 100% ultra-legible on any background (light or dark wallpaper).
# - TOP: Exactly 8 Upcoming High & Medium Impact Forex Events (4 left, 4 right).
# - BOTTOM: Exactly 8 Largest Cryptocurrencies by Market Cap (4 left, 4 right).
# ==============================================================================

import json
import math
import os
import sys
import threading
import time
import urllib.request
from typing import List, Dict, Any

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

# Import Forex Feed
ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOREX_FEED_PATH = os.path.join(ENGINE_DIR, "forex_calendar")
if FOREX_FEED_PATH not in sys.path:
    sys.path.insert(0, FOREX_FEED_PATH)

try:
    import forex_feed
except ImportError:
    forex_feed = None

class FinancialOrbitRadar:
    """Singleton engine managing live Forex & Crypto telemetry with shadow-backed crisp text."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FinancialOrbitRadar()
        return cls._instance

    def __init__(self):
        self.lock = threading.Lock()
        self.crypto_items: List[Dict[str, Any]] = []
        self.forex_events: List[Dict[str, Any]] = []
        self.last_crypto_fetch = 0.0
        self.last_forex_fetch = 0.0

        # High-contrast corporate tactical palette
        self.c_gold = (1.00, 0.78, 0.22, 1.0)
        self.c_green = (0.24, 0.92, 0.52, 1.0)
        self.c_red = (0.98, 0.32, 0.36, 1.0)
        self.c_cyan = (0.25, 0.85, 1.00, 1.0)
        self.c_white = (1.00, 1.00, 1.00, 0.98)
        self.c_muted = (0.75, 0.80, 0.88, 0.85)
        self.c_dim = (0.55, 0.60, 0.70, 0.65)

        # Baseline crypto values
        self.crypto_items = [
            {"symbol": "BTC", "price_str": "$59,220", "change": -3.9, "change_str": "-3.9%"},
            {"symbol": "ETH", "price_str": "$1,648", "change": -4.6, "change_str": "-4.6%"},
            {"symbol": "SOL", "price_str": "$70.80", "change": -3.4, "change_str": "-3.4%"},
            {"symbol": "BNB", "price_str": "$549.7", "change": -2.5, "change_str": "-2.5%"},
            {"symbol": "XRP", "price_str": "$0.940", "change": -4.5, "change_str": "-4.5%"},
            {"symbol": "DOGE", "price_str": "$0.057", "change": -3.6, "change_str": "-3.6%"},
            {"symbol": "ADA", "price_str": "$0.146", "change": -4.7, "change_str": "-4.7%"},
            {"symbol": "AVAX", "price_str": "$6.50", "change": -4.4, "change_str": "-4.4%"},
        ]

        # Immediate synchronous load
        self._fetch_forex_data()
        self.last_forex_fetch = time.time()

        # Background polling thread
        t = threading.Thread(target=self._worker_loop, daemon=True)
        t.start()

    def _worker_loop(self):
        """Refreshes Forex and Crypto telemetry periodically."""
        while True:
            now = time.time()
            if now - self.last_crypto_fetch >= 60.0:
                self._fetch_crypto_data()
                self.last_crypto_fetch = now

            if now - self.last_forex_fetch >= 180.0:
                self._fetch_forex_data()
                self.last_forex_fetch = now

            time.sleep(10.0)

    def _fetch_crypto_data(self):
        """Fetches top 8 crypto telemetry from CoinGecko, falling back to Indodax."""
        items = []
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,ripple,dogecoin,cardano,avalanche-2&vs_currencies=usd&include_24hr_change=true"
            req = urllib.request.Request(url, headers={"User-Agent": "FloworkOS-FinancialOrbit/2.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                mapping = [
                    ("BTC", "bitcoin"),
                    ("ETH", "ethereum"),
                    ("SOL", "solana"),
                    ("BNB", "binancecoin"),
                    ("XRP", "ripple"),
                    ("DOGE", "dogecoin"),
                    ("ADA", "cardano"),
                    ("AVAX", "avalanche-2"),
                ]
                for sym, gid in mapping:
                    info = data.get(gid, {})
                    p = float(info.get("usd", 0))
                    ch = float(info.get("usd_24h_change", 0))
                    if p >= 1000:
                        p_str = f"${p:,.0f}"
                    elif p >= 1:
                        p_str = f"${p:.2f}"
                    else:
                        p_str = f"${p:.3f}"
                    items.append({
                        "symbol": sym,
                        "price": p,
                        "price_str": p_str,
                        "change": ch,
                        "change_str": f"{ch:+.1f}%"
                    })
        except Exception:
            pass

        # Fallback to Indodax
        if not items:
            try:
                url = "https://indodax.com/api/tickers"
                req = urllib.request.Request(url, headers={"User-Agent": "FloworkOS-FinancialOrbit/2.0"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    tickers = data.get("tickers", {})
                    usdt_idr = float(tickers.get("usdt_idr", {}).get("last", 16000))
                    syms = ["btc", "eth", "sol", "bnb", "xrp", "doge", "ada", "avax"]
                    for s in syms:
                        t = tickers.get(f"{s}_idr", {})
                        last_idr = float(t.get("last", 0))
                        p = last_idr / usdt_idr if usdt_idr > 0 else 0
                        if p >= 1000:
                            p_str = f"${p:,.0f}"
                        elif p >= 1:
                            p_str = f"${p:.2f}"
                        else:
                            p_str = f"${p:.3f}"
                        items.append({
                            "symbol": s.upper(),
                            "price": p,
                            "price_str": p_str,
                            "change": 0.0,
                            "change_str": "LIVE"
                        })
            except Exception:
                pass

        if items:
            with self.lock:
                self.crypto_items = items

    def _fetch_forex_data(self):
        """Fetches Forex calendar and retrieves exactly 8 upcoming high/med events."""
        if forex_feed is None:
            return
        try:
            events = forex_feed.get_calendar_events()
            filtered = [e for e in events if e.get("impact") in ("High", "Medium")][:8]
            with self.lock:
                self.forex_events = filtered
        except Exception:
            pass

    def draw_financial_wings(self, cr: cairo.Context, cx: float, cy: float, scale: float, alpha: float):
        """
        Renders Pure Floating Text Telemetry:
        - TOP (y ≈ 92): Exactly 8 Upcoming Forex Calendar Events (4 left, 4 right of center)
        - BOTTOM (y ≈ 705): Exactly 8 Crypto Prices (4 left, 4 right of center)
        """
        with self.lock:
            events = list(self.forex_events)
            cryptos = list(self.crypto_items)

        # Spacing geometry: 4 left columns, 4 right columns
        gap_center = 142.0 * scale   # 284px clear corridor in center around 12 & 6 o'clock nodes
        col_pitch = 158.0 * scale    # 158px width per column

        # Calculate 8 X centers
        x_centers = []
        for i in range(4):
            x_centers.append(cx - gap_center - (3 - i) * col_pitch)
        for i in range(4):
            x_centers.append(cx + gap_center + i * col_pitch)

        # ----------------------------------------------------------------------
        # 1. TOP: 8 UPCOMING FOREX CALENDAR EVENTS (PURE TEXT WITH SHADOW AURA)
        # ----------------------------------------------------------------------
        y_top = 92.0 * scale
        for i in range(min(8, len(events))):
            ev = events[i]
            col_x = x_centers[i]
            self._draw_single_forex_item(cr, col_x, y_top, ev, scale, alpha)

        # ----------------------------------------------------------------------
        # 2. BOTTOM: 8 CRYPTO PRICES (PURE TEXT WITH SHADOW AURA)
        # ----------------------------------------------------------------------
        y_bot = 705.0 * scale
        for i in range(min(8, len(cryptos))):
            cp = cryptos[i]
            col_x = x_centers[i]
            self._draw_single_crypto_item(cr, col_x, y_bot, cp, scale, alpha)

    def _draw_shadowed_text(self, cr: cairo.Context, layout, x: float, y: float, r: float, g: float, b: float, a: float):
        """Renders text with a subtle drop shadow to guarantee 100% legibility on any background."""
        # Shadow
        cr.save()
        cr.set_source_rgba(0.01, 0.02, 0.04, 0.85 * a)
        cr.move_to(x + 1.2, y + 1.2)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

        # Foreground
        cr.save()
        cr.set_source_rgba(r, g, b, a)
        cr.move_to(x, y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

    def _draw_single_forex_item(self, cr: cairo.Context, col_x: float, col_y: float, ev: dict, scale: float, alpha: float):
        """Draws one column of pure floating Forex telemetry with shadow backing."""
        curr = ev.get("country", "USD")
        impact = ev.get("impact", "High")
        is_high = impact == "High"
        imp_col = self.c_red if is_high else self.c_gold
        time_status = ev.get("time_status", "")
        title = ev.get("title", "")
        
        # Clean title shortening
        title = title.replace("Manufacturing", "Mfg").replace("Estimate", "Est")
        if len(title) > 18:
            title = title[:16] + ".."
            
        time_str = f"{ev.get('date_str', '')[:3]} {ev.get('time_str', '')}"

        # Line 1: Impact Dot + Country + Countdown
        l1 = PangoCairo.create_layout(cr)
        l1.set_text(f"● {curr}  {time_status}", -1)
        d1 = Pango.FontDescription("Inter, monospace Bold")
        d1.set_size(int(6.8 * Pango.SCALE * scale))
        l1.set_font_description(d1)
        w1, _ = l1.get_pixel_size()
        self._draw_shadowed_text(cr, l1, col_x - w1 / 2.0, col_y, imp_col[0], imp_col[1], imp_col[2], 0.98 * alpha)

        # Line 2: Event Title
        l2 = PangoCairo.create_layout(cr)
        l2.set_text(title, -1)
        d2 = Pango.FontDescription("Inter, sans-serif Bold")
        d2.set_size(int(7.0 * Pango.SCALE * scale))
        l2.set_font_description(d2)
        w2, _ = l2.get_pixel_size()
        self._draw_shadowed_text(cr, l2, col_x - w2 / 2.0, col_y + 16.0 * scale, self.c_white[0], self.c_white[1], self.c_white[2], 0.98 * alpha)

        # Line 3: Day & Time WIB
        l3 = PangoCairo.create_layout(cr)
        l3.set_text(time_str, -1)
        d3 = Pango.FontDescription("Inter, monospace Medium")
        d3.set_size(int(6.0 * Pango.SCALE * scale))
        l3.set_font_description(d3)
        w3, _ = l3.get_pixel_size()
        self._draw_shadowed_text(cr, l3, col_x - w3 / 2.0, col_y + 30.0 * scale, self.c_muted[0], self.c_muted[1], self.c_muted[2], 0.90 * alpha)

    def _draw_single_crypto_item(self, cr: cairo.Context, col_x: float, col_y: float, cp: dict, scale: float, alpha: float):
        """Draws one column of pure floating Crypto telemetry with shadow backing."""
        sym = cp.get("symbol", "")
        price_str = cp.get("price_str", "")
        ch_val = cp.get("change", 0.0)
        ch_str = cp.get("change_str", "")
        is_up = ch_val >= 0.0
        ch_col = self.c_green if is_up else self.c_red

        # Line 1: Symbol + 24h Change %
        l1 = PangoCairo.create_layout(cr)
        l1.set_text(f"{sym}  {ch_str}", -1)
        d1 = Pango.FontDescription("Inter, monospace Bold")
        d1.set_size(int(6.8 * Pango.SCALE * scale))
        l1.set_font_description(d1)
        w1, _ = l1.get_pixel_size()
        self._draw_shadowed_text(cr, l1, col_x - w1 / 2.0, col_y, ch_col[0], ch_col[1], ch_col[2], 0.98 * alpha)

        # Line 2: Large Price
        l2 = PangoCairo.create_layout(cr)
        l2.set_text(price_str, -1)
        d2 = Pango.FontDescription("Inter, sans-serif Heavy")
        d2.set_size(int(8.5 * Pango.SCALE * scale))
        l2.set_font_description(d2)
        w2, _ = l2.get_pixel_size()
        self._draw_shadowed_text(cr, l2, col_x - w2 / 2.0, col_y + 15.0 * scale, self.c_white[0], self.c_white[1], self.c_white[2], 0.98 * alpha)

        # Line 3: Micro Tag
        l3 = PangoCairo.create_layout(cr)
        l3.set_text("CRYPTO 24H", -1)
        d3 = Pango.FontDescription("Inter, monospace")
        d3.set_size(int(5.5 * Pango.SCALE * scale))
        l3.set_font_description(d3)
        w3, _ = l3.get_pixel_size()
        self._draw_shadowed_text(cr, l3, col_x - w3 / 2.0, col_y + 31.0 * scale, self.c_dim[0], self.c_dim[1], self.c_dim[2], 0.80 * alpha)

# Global Singleton Hook
radar = FinancialOrbitRadar.get_instance()
