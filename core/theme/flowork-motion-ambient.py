#!/usr/bin/env python3
# =============================================================================
# 🚀 Flowork Sovereign OS — Living Motion Theme & Ambient Wallpaper Engine 3.0
# Ultra-Soft, Organic Gaseous Silk & Liquid Crystal Motion — Zero Dull Gray
# 6 Distinct Motion Art Styles:
#   1. aurora-silk   — Quantum Silk Aurora (Ethereal Polar Ribbons)
#   2. plasma-drift  — Cyber Liquid Plasma (Molten Neon Mercury Drift)
#   3. nebula-mist   — Cosmic Stardust Nebula (Celestial Breathing Void)
#   4. solar-dusk    — Solar Amber Dusk (Velvety Coronal Flare Dunes)
#   5. matrix-ocean  — Bioluminescent Abyss (Deep Midnight Emerald Swells)
#   6. prism-aether  — Holographic Aether (Iridescent Crystal Silk Veils)
# Hardware Optimized: Dynamic 640x270 Bilinear Scaled Canvas (~2% CPU)
# Co-authored-by: Flowork OS Architecture Board & Dr. Flow <agent@floworkos.com>
# =============================================================================

import os
import sys
import math
import time
import json
import signal
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Rsvg', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Rsvg
import cairo

try:
    import flowork_neural_bridge
except ImportError:
    sys.path.insert(0, "/opt/floworkos/theme")
    import flowork_neural_bridge

THEME_FILE = "/opt/floworkos/theme/current-theme.json"
CONFIG_FILE = "/opt/floworkos/theme/motion-config.json"
WALLPAPER_SHM_FILE = "/dev/shm/flowork-wallpaper.json"
WALLPAPER_PATH_FILE = "/opt/floworkos/theme/current-wallpaper.path"
PID_FILE = f"/run/user/{os.getuid()}/flowork-motion-ambient.pid"

MOTION_STYLES = {
    "oceanic-core": {
        "id": "oceanic-core",
        "name": "Mr. Flow Sovereign Oceanic Core",
        "desc": "Deep marine navy abyss with centered holographic arc reactor & dynamic voice/tool visualizer.",
        "bg_top": (0.006, 0.028, 0.065),
        "bg_bottom": (0.001, 0.006, 0.018),
        "colors": [
            (0.00, 0.85, 1.00),   # Electric oceanic cyan (#00d2ff)
            (0.00, 0.50, 0.90),   # Deep marine azure
            (0.00, 1.00, 0.55),   # Phosphor mint (#00ff88)
            (0.40, 0.95, 1.00)    # Ice core white-cyan
        ],
        "speed": 0.005,
        "style": "oceanic"
    },
    "aurora-silk": {
        "id": "aurora-silk",
        "name": "Quantum Silk Aurora",
        "desc": "Ethereal polar ribbons of electric cyan, emerald green, and cosmic violet glowing in the Arctic midnight sky.",
        "bg_top": (0.010, 0.025, 0.055),
        "bg_bottom": (0.002, 0.008, 0.018),
        "colors": [
            (0.00, 0.95, 1.00),   # Glacial cyan
            (0.00, 1.00, 0.45),   # Emerald green
            (0.65, 0.20, 1.00),   # Cosmic violet
            (0.00, 0.80, 0.90)    # Deep aqua
        ],
        "speed": 0.006,
        "style": "aurora"
    },
    "plasma-drift": {
        "id": "plasma-drift",
        "name": "Cyber Liquid Plasma",
        "desc": "Voluptuous molten fluid blobs of neon fuchsia, electric cyan, and deep ultraviolet drifting and morphing softly.",
        "bg_top": (0.035, 0.008, 0.050),
        "bg_bottom": (0.008, 0.002, 0.018),
        "colors": [
            (1.00, 0.00, 0.50),   # Hot fuchsia (#ff007f)
            (0.00, 0.95, 1.00),   # Electric cyan (#00f2fe)
            (0.72, 0.16, 1.00),   # Deep violet
            (1.00, 0.20, 0.65)    # Neon rose
        ],
        "speed": 0.005,
        "style": "plasma"
    },
    "nebula-mist": {
        "id": "nebula-mist",
        "name": "Cosmic Stardust Nebula",
        "desc": "Deep interstellar stardust clouds breathing in cosmic space with celestial magenta and starlight cyan pockets.",
        "bg_top": (0.020, 0.010, 0.045),
        "bg_bottom": (0.005, 0.002, 0.015),
        "colors": [
            (0.72, 0.16, 1.00),   # Cosmic violet (#b829ff)
            (0.00, 0.90, 1.00),   # Starlight aqua
            (1.00, 0.18, 0.55),   # Stellar rose
            (0.40, 0.10, 0.85)    # Deep void indigo
        ],
        "speed": 0.004,
        "style": "nebula"
    },
    "solar-dusk": {
        "id": "solar-dusk",
        "name": "Solar Amber Dusk",
        "desc": "Warm, velvety sunset flare of liquid amber gold, coral crimson, and molten bronze rolling softly like dunes of sunlight.",
        "bg_top": (0.045, 0.018, 0.008),
        "bg_bottom": (0.012, 0.004, 0.002),
        "colors": [
            (1.00, 0.72, 0.00),   # Amber gold (#ffb800)
            (1.00, 0.18, 0.32),   # Sunset coral (#ff2d55)
            (1.00, 0.45, 0.05),   # Molten copper
            (0.85, 0.12, 0.20)    # Deep ruby dusk
        ],
        "speed": 0.005,
        "style": "solar"
    },
    "matrix-ocean": {
        "id": "matrix-ocean",
        "name": "Bioluminescent Abyss",
        "desc": "Deep oceanic abyss with undulating waves of razor emerald, glowing aquamarine, and mint phosphorescence.",
        "bg_top": (0.005, 0.028, 0.018),
        "bg_bottom": (0.001, 0.008, 0.005),
        "colors": [
            (0.00, 1.00, 0.40),   # Razor emerald (#00ff66)
            (0.00, 0.92, 0.80),   # Cyan bioluminescence
            (0.22, 1.00, 0.55),   # Mint glow
            (0.00, 0.65, 0.50)    # Deep oceanic teal
        ],
        "speed": 0.005,
        "style": "matrix"
    },
    "prism-aether": {
        "id": "prism-aether",
        "name": "Holographic Aether",
        "desc": "Shimmering iridescent silk veils of holographic lavender, prism cyan, and sunset peach flowing gracefully.",
        "bg_top": (0.025, 0.022, 0.045),
        "bg_bottom": (0.008, 0.010, 0.020),
        "colors": [
            (0.75, 0.52, 0.98),   # Holographic lavender (#c084fc)
            (0.22, 0.74, 0.97),   # Prism cyan (#38bdf8)
            (0.98, 0.44, 0.52),   # Sunset peach (#fb7185)
            (0.40, 0.85, 0.95)    # Ice crystal aqua
        ],
        "speed": 0.004,
        "style": "prism"
    }
}

THEME_TO_STYLE = {
    "matrix-razor": "oceanic-core",
    "neon-plasma": "plasma-drift",
    "quantum-aurora": "aurora-silk",
    "solar-flare": "solar-dusk",
    "deep-nebula": "nebula-mist"
}

def load_motion_config():
    cfg = {"enabled": True, "style": "oceanic-core", "speed": 1.0, "glow_intensity": 1.0}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg

def save_motion_config(cfg):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

class FloworkMotionAmbient(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Flowork Living Motion Wallpaper")
        self.set_role("flowork-living-wallpaper")

        # Desktop Invariants (stay strictly in DESKTOP layer below BELOW/HUD windows)
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_app_paintable(True)

        screen = self.get_screen()
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()
        self.resize(self.screen_w, self.screen_h)
        self.move(0, 0)
        screen.connect("size-changed", self.on_screen_resized)
        screen.connect("monitors-changed", self.on_screen_resized)

        # Dynamic low-res buffer preserving screen aspect ratio (~2% CPU)
        self.buf_w = 640
        self.buf_h = max(180, int(640 * self.screen_h / max(1, self.screen_w)))
        self.surface_buf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.buf_w, self.buf_h)

        # Dedicated High-Definition Vector Arc Reactor Surface (1:1 Retina Sharpness, 0% Blur, ~0.2ms Render)
        self.core_size = 440
        self.surface_core = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.core_size, self.core_size)
        self.surface_static_bg = None
        self.last_bg_key = None

        # Style & Theme State
        self.config = load_motion_config()
        self.current_theme_id = "matrix-razor"
        self.active_style_key = "oceanic-core"
        self.style_data = MOTION_STYLES["oceanic-core"]
        self.last_theme_mtime = 0.0
        self.last_config_mtime = 0.0

        # Living Wallpaper State (1:1 retina background canvas)
        self.wallpaper_path = None
        self.wallpaper_surface = None
        self.last_wallpaper_mtime = 0.0
        self.load_active_wallpaper()

        self.t = 0.0
        self.sync_active_style()

        # Neural Reactor State (Living Desktop Canvas for Tools & Voice)
        self.reactor_intensity = 0.0
        self.active_morphology = "morph-idle"
        self.active_amplitude = 0.0
        self.target_amplitude = 0.0
        self.active_tool_name = ""
        self.active_action = ""
        self.radar_angle = 0.0
        self.laser_scan_y = 0.5
        self.laser_scan_dir = 1.0
        self.swarm_phase = 0.0
        self.matrix_offsets = [(i * 37) % 100 for i in range(24)]
        self.raw_state = "idle"
        self.thinking_flux = 0.0
        self.last_tool_payload = None
        self.last_tool_done_time = 0.0

        # Single-slot Reason Subtitle state (below ambient core, theme-integrated)
        self.subtitle_reason = ""
        self.subtitle_tool = ""
        self.subtitle_last_update = 0.0
        self.subtitle_alpha = 0.0
        self.theme_accent_rgb = (0.0, 1.0, 0.40)
        self.theme_secondary_rgb = (0.0, 0.95, 1.0)
        self.theme_text_rgb = (1.0, 1.0, 1.0)

        self.connect("draw", self.on_draw)
        self.connect("realize", self.on_realize)
        GLib.timeout_add(100, self.on_animation_tick)   # Optimized 10 FPS: smooth organic gaseous motion with low CPU
        GLib.timeout_add_seconds(2, self.periodic_check)

    def _hex_to_rgb(self, hex_str, fallback):
        try:
            s = str(hex_str or "").strip().lstrip("#")
            if len(s) == 6:
                return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0, int(s[4:6], 16) / 255.0)
        except Exception:
            pass
        return fallback

    def on_realize(self, widget):
        self.stick()
        self.set_keep_below(True)
        gdk_win = self.get_window()
        if gdk_win:
            gdk_win.lower()

    def sync_active_style(self):
        # 1. Check Theme
        tdata = None
        if os.path.exists(THEME_FILE):
            try:
                mtime = os.path.getmtime(THEME_FILE)
                if mtime != self.last_theme_mtime:
                    self.last_theme_mtime = mtime
                    with open(THEME_FILE, "r", encoding="utf-8") as f:
                        tdata = json.load(f)
                    self.current_theme_id = tdata.get("id", tdata.get("theme_id", "matrix-razor"))
                    self._cached_theme_data = tdata
            except Exception:
                pass

        # 2. Check Config
        if os.path.exists(CONFIG_FILE):
            try:
                mtime = os.path.getmtime(CONFIG_FILE)
                if mtime != self.last_config_mtime:
                    self.last_config_mtime = mtime
                    self.config = load_motion_config()
            except Exception:
                pass

        cfg_style = self.config.get("style", "auto")
        if cfg_style in MOTION_STYLES:
            self.active_style_key = cfg_style
        else:
            self.active_style_key = THEME_TO_STYLE.get(self.current_theme_id, "aurora-silk")

        self.style_data = MOTION_STYLES.get(self.active_style_key, MOTION_STYLES["aurora-silk"])
        style_cols = self.style_data.get("colors", [(0.0, 1.0, 0.40), (0.0, 0.95, 1.0)])
        fallback_acc = style_cols[0] if len(style_cols) > 0 else (0.0, 1.0, 0.40)
        fallback_sec = style_cols[1] if len(style_cols) > 1 else fallback_acc
        cached_t = getattr(self, "_cached_theme_data", None) or {}
        self.theme_accent_rgb = self._hex_to_rgb(cached_t.get("accent_color"), fallback_acc)
        self.theme_secondary_rgb = self._hex_to_rgb(cached_t.get("secondary_color"), fallback_sec)
        self.theme_text_rgb = self._hex_to_rgb(cached_t.get("text_color"), (1.0, 1.0, 1.0))

    def periodic_check(self):
        self.sync_active_style()
        self.check_wallpaper_sync()
        return True

    def check_wallpaper_sync(self):
        """Fast zero-latency check (<1ms) for live wallpaper mutations."""
        if os.path.exists(WALLPAPER_SHM_FILE):
            try:
                mtime = os.path.getmtime(WALLPAPER_SHM_FILE)
                if mtime != self.last_wallpaper_mtime:
                    self.last_wallpaper_mtime = mtime
                    self.load_active_wallpaper()
                    self.queue_draw()
                    return
            except Exception:
                pass
        if os.path.exists(WALLPAPER_PATH_FILE):
            try:
                mtime = os.path.getmtime(WALLPAPER_PATH_FILE)
                if mtime != self.last_wallpaper_mtime:
                    self.last_wallpaper_mtime = mtime
                    self.load_active_wallpaper()
                    self.queue_draw()
            except Exception:
                pass

    def load_active_wallpaper(self):
        """Resolves and renders active wallpaper image into cached 1:1 Cairo ImageSurface."""
        path = None
        if os.path.exists(WALLPAPER_SHM_FILE):
            try:
                with open(WALLPAPER_SHM_FILE, "r") as f:
                    data = json.load(f)
                    p = data.get("path")
                    if p and os.path.isfile(p):
                        path = p
            except Exception:
                pass

        if not path and os.path.exists(WALLPAPER_PATH_FILE):
            try:
                with open(WALLPAPER_PATH_FILE, "r") as f:
                    p = f.read().strip()
                    if p and os.path.isfile(p):
                        path = p
            except Exception:
                pass

        if not path and os.path.exists(THEME_FILE):
            try:
                with open(THEME_FILE, "r") as f:
                    tdata = json.load(f)
                    p = tdata.get("wallpaper")
                    if p and os.path.isfile(p):
                        path = p
            except Exception:
                pass

        if not path:
            default_wp = "/opt/floworkos/theme/flowork-quantum-wallpaper.png"
            if os.path.isfile(default_wp):
                path = default_wp

        if not path or not os.path.isfile(path):
            return

        if self.wallpaper_path == path and self.wallpaper_surface is not None:
            if self.wallpaper_surface.get_width() == self.screen_w and self.wallpaper_surface.get_height() == self.screen_h:
                return

        surf = self._render_wallpaper_surface(path)
        if surf:
            self.wallpaper_surface = surf
            self.wallpaper_path = path

    def _render_wallpaper_surface(self, path):
        target_w = max(1, self.screen_w)
        target_h = max(1, self.screen_h)

        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, target_w, target_h)
        cr = cairo.Context(surf)

        # Handle SVG
        if path.lower().endswith(".svg"):
            try:
                handle = Rsvg.Handle.new_from_file(path)
                dim = handle.get_dimensions()
                dw = max(1.0, float(dim.width))
                dh = max(1.0, float(dim.height))
                scale = max(target_w / dw, target_h / dh)
                sw = dw * scale
                sh = dh * scale
                ox = (target_w - sw) / 2.0
                oy = (target_h - sh) / 2.0

                cr.save()
                cr.translate(ox, oy)
                cr.scale(scale, scale)
                handle.render_cairo(cr)
                cr.restore()
                return surf
            except Exception as e:
                print(f"[Ambient] SVG render fallback for {path}: {e}")

        # Handle Raster (PNG, JPG, JPEG, WebP)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
            pw = max(1, pixbuf.get_width())
            ph = max(1, pixbuf.get_height())
            scale = max(target_w / pw, target_h / ph)
            sw = max(1, int(pw * scale))
            sh = max(1, int(ph * scale))
            scaled_pixbuf = pixbuf.scale_simple(sw, sh, GdkPixbuf.InterpType.BILINEAR)

            ox = (target_w - sw) // 2
            oy = (target_h - sh) // 2
            Gdk.cairo_set_source_pixbuf(cr, scaled_pixbuf, ox, oy)
            cr.paint()
            return surf
        except Exception as e:
            print(f"[Ambient] Raster wallpaper render error for {path}: {e}")
            return None

    def on_animation_tick(self):
        self.check_wallpaper_sync()
        speed_factor = self.config.get("speed", 1.0)
        self.t += self.style_data.get("speed", 0.005) * speed_factor
        if self.t > 100000.0:
            self.t = 0.0

        # Update Neural Reactor state from shared memory (/dev/shm)
        try:
            n_state = flowork_neural_bridge.get_neural_state()
            self.raw_state = n_state.get("state", "idle")
            target_int = 1.0 if self.raw_state in ("tool_use", "speaking", "thinking") else 0.0
            self.active_morphology = n_state.get("morphology", "morph-idle")
            self.target_amplitude = n_state.get("amplitude", 0.7 if self.raw_state in ("tool_use", "thinking") else 0.0)
            self.active_tool_name = n_state.get("tool_name", "")
            self.active_action = n_state.get("action", "")

            # Single-slot Reason Subtitle update (replaces previous reason like a live subtitle)
            now_ts = time.time()
            n_ts = n_state.get("timestamp", 0)
            n_args = n_state.get("args") or {}
            raw_reason = str(
                n_state.get("reason")
                or (n_args.get("reason") if isinstance(n_args, dict) else "")
                or (n_args.get("goal") if isinstance(n_args, dict) else "")
                or ""
            ).strip()
            is_fresh = (now_ts - n_ts) < 60.0
            if raw_reason and is_fresh and self.raw_state in ("tool_use", "deliberation", "thinking"):
                if raw_reason != self.subtitle_reason:
                    self.subtitle_reason = raw_reason
                    self.subtitle_tool = self.active_tool_name
                self.subtitle_last_update = now_ts
                target_sub_alpha = 1.0
            elif self.subtitle_reason and self.raw_state in ("deliberation", "thinking") and (now_ts - self.subtitle_last_update) < 25.0:
                target_sub_alpha = 1.0
            else:
                target_sub_alpha = 0.0

            self.subtitle_alpha += (target_sub_alpha - self.subtitle_alpha) * (0.38 if target_sub_alpha > self.subtitle_alpha else 0.18)
            if self.subtitle_alpha < 0.01 and target_sub_alpha == 0.0:
                self.subtitle_alpha = 0.0
                self.subtitle_reason = ""
        except Exception:
            target_int = 0.0

        # Smooth interpolation (ease in / ease out)
        self.reactor_intensity += (target_int - self.reactor_intensity) * 0.12
        if self.target_amplitude > self.active_amplitude:
            self.active_amplitude += (self.target_amplitude - self.active_amplitude) * 0.65
        else:
            self.active_amplitude += (self.target_amplitude - self.active_amplitude) * 0.30

        # Dynamic cognitive thinking flux (smooth transition 0.0 -> 1.0)
        target_thinking = 1.0 if (self.raw_state in ("thinking", "compacting") or self.active_morphology in ("morph-thinking", "morph-circle", "morph-compacting")) else 0.0
        self.thinking_flux += (target_thinking - self.thinking_flux) * 0.14

        # Update dynamic animation phases
        self.radar_angle = (self.radar_angle + 0.08) % (2 * math.pi)
        self.laser_scan_y += 0.012 * self.laser_scan_dir
        if self.laser_scan_y > 0.85:
            self.laser_scan_dir = -1.0
        elif self.laser_scan_y < 0.25:
            self.laser_scan_dir = 1.0
        self.swarm_phase = (self.swarm_phase + 0.04) % (2 * math.pi)
        for idx in range(len(self.matrix_offsets)):
            self.matrix_offsets[idx] = (self.matrix_offsets[idx] + 1.2 + (idx % 3) * 0.4) % 100.0

        self.render_buffer()

        # Render 1:1 crisp retina arc reactor into dedicated surface
        style_type = self.style_data.get("style", "oceanic")
        if style_type == "oceanic":
            glow = self.config.get("glow_intensity", 1.0)
            cr_core = cairo.Context(self.surface_core)
            cr_core.set_operator(cairo.OPERATOR_CLEAR)
            cr_core.paint()
            cr_core.set_operator(cairo.OPERATOR_OVER)
            self.render_mrflow_holographic_core(cr_core, float(self.core_size), float(self.core_size), glow)

        self.queue_draw()
        return True

    def render_buffer(self):
        cr = cairo.Context(self.surface_buf)
        bw, bh = float(self.buf_w), float(self.buf_h)
        style_type = self.style_data.get("style", "aurora")
        colors = self.style_data.get("colors", [])
        bg_t = self.style_data.get("bg_top", (0.01, 0.02, 0.04))
        bg_b = self.style_data.get("bg_bottom", (0.002, 0.005, 0.015))
        glow = self.config.get("glow_intensity", 1.0)

        if style_type == "oceanic":
            # High-performance static background cache: 66x faster, saves 15-20% continuous CPU
            bg_key = (style_type, self.current_theme_id, self.buf_w, self.buf_h, glow)
            if self.surface_static_bg is None or self.last_bg_key != bg_key:
                self.surface_static_bg = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.buf_w, self.buf_h)
                cr_bg = cairo.Context(self.surface_static_bg)
                cr_bg.set_operator(cairo.OPERATOR_SOURCE)
                base_grad = cairo.LinearGradient(0, 0, bw * 0.4, bh)
                base_grad.add_color_stop_rgb(0.0, bg_t[0], bg_t[1], bg_t[2])
                base_grad.add_color_stop_rgb(1.0, bg_b[0], bg_b[1], bg_b[2])
                cr_bg.set_source(base_grad)
                cr_bg.paint()

                cr_bg.set_operator(cairo.OPERATOR_SCREEN)
                glow_rad = cairo.RadialGradient(bw * 0.5, bh * 0.5, 10.0, bw * 0.5, bh * 0.5, bw * 0.45)
                glow_rad.add_color_stop_rgba(0.0, 0.0, 0.45, 0.85, 0.22 * glow)
                glow_rad.add_color_stop_rgba(0.5, 0.0, 0.20, 0.55, 0.07 * glow)
                glow_rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
                cr_bg.set_source(glow_rad)
                cr_bg.paint()

                cr_bg.set_operator(cairo.OPERATOR_OVER)
                vig = cairo.RadialGradient(bw * 0.5, bh * 0.45, bw * 0.25, bw * 0.5, bh * 0.5, bw * 0.70)
                vig.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, 0.0)
                vig.add_color_stop_rgba(0.65, 0.0, 0.0, 0.0, 0.08)
                vig.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.35)
                cr_bg.set_source(vig)
                cr_bg.paint()
                self.last_bg_key = bg_key

            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.set_source_surface(self.surface_static_bg, 0, 0)
            cr.paint()
        else:
            # Dynamic styles rendered on small buffer
            cr.set_operator(cairo.OPERATOR_SOURCE)
            base_grad = cairo.LinearGradient(0, 0, bw * 0.4, bh)
            base_grad.add_color_stop_rgb(0.0, bg_t[0], bg_t[1], bg_t[2])
            base_grad.add_color_stop_rgb(1.0, bg_b[0], bg_b[1], bg_b[2])
            cr.set_source(base_grad)
            cr.paint()

            cr.set_operator(cairo.OPERATOR_OVER)
            if style_type == "aurora":
                self.render_aurora_silk(cr, bw, bh, colors, glow)
            elif style_type == "plasma":
                self.render_plasma_drift(cr, bw, bh, colors, glow)
            elif style_type == "nebula":
                self.render_nebula_mist(cr, bw, bh, colors, glow)
            elif style_type == "solar":
                self.render_solar_dusk(cr, bw, bh, colors, glow)
            elif style_type == "matrix":
                self.render_matrix_ocean(cr, bw, bh, colors, glow)
            elif style_type == "prism":
                self.render_prism_aether(cr, bw, bh, colors, glow)

            vig = cairo.RadialGradient(bw * 0.5, bh * 0.45, bw * 0.25, bw * 0.5, bh * 0.5, bw * 0.70)
            vig.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, 0.0)
            vig.add_color_stop_rgba(0.65, 0.0, 0.0, 0.0, 0.08)
            vig.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.35)
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.set_source(vig)
            cr.paint()

            if self.reactor_intensity > 0.005:
                self.render_neural_reactor(cr, bw, bh, glow)

    def render_aurora_silk(self, cr, bw, bh, colors, glow):
        """Silky sweeping polar curtains undulating across the upper-mid horizon."""
        # Layer 1: Ambient background glow pools
        for i, c in enumerate(colors[:3]):
            ox = bw * (0.25 + 0.25 * i + 0.10 * math.sin(self.t * 0.6 + i))
            oy = bh * (0.42 + 0.08 * math.cos(self.t * 0.5 + i * 1.5))
            r = bw * (0.35 + 0.08 * math.sin(self.t * 0.4 + i))
            rad = cairo.RadialGradient(ox, oy, 10.0, ox, oy, r)
            rad.add_color_stop_rgba(0.0, c[0], c[1], c[2], 0.28 * glow)
            rad.add_color_stop_rgba(0.4, c[0], c[1], c[2], 0.14 * glow)
            rad.add_color_stop_rgba(0.8, c[0], c[1], c[2], 0.02 * glow)
            rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rad)
            cr.paint()

        # Layer 2: Ethereal flowing silk ribbons
        cr.set_operator(cairo.OPERATOR_SCREEN)
        for idx in range(3):
            phase = self.t * (0.7 + idx * 0.25) + idx * 1.6
            c = colors[idx % len(colors)]
            mid_y = bh * (0.32 + 0.15 * idx)
            wave_amp = 30.0 + 8.0 * idx

            cr.new_sub_path()
            cr.move_to(0, bh)
            cr.line_to(0, mid_y)

            # 4 Organic cubic bezier control nodes
            p1_x = bw * 0.25
            p1_y = mid_y + math.sin(phase) * wave_amp
            p2_x = bw * 0.50
            p2_y = mid_y + math.cos(phase * 0.85) * wave_amp * 1.25
            p3_x = bw * 0.75
            p3_y = mid_y + math.sin(phase * 0.65 + 1.2) * wave_amp
            p4_x = bw
            p4_y = mid_y + math.cos(phase * 0.90) * wave_amp * 0.9

            cr.curve_to(p1_x * 0.6, p1_y, p1_x, p1_y, p2_x, p2_y)
            cr.curve_to(p3_x * 0.9, p3_y, p3_x, p3_y, p4_x, p4_y)
            cr.line_to(bw, bh)
            cr.close_path()

            grad = cairo.LinearGradient(0, mid_y - 35.0, 0, bh)
            alpha = (0.24 + 0.06 * math.sin(phase * 0.7)) * glow
            grad.add_color_stop_rgba(0.0, c[0], c[1], c[2], alpha)
            grad.add_color_stop_rgba(0.35, c[0], c[1], c[2], alpha * 0.65)
            grad.add_color_stop_rgba(0.75, c[0], c[1], c[2], alpha * 0.15)
            grad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(grad)
            cr.fill()

    def render_plasma_drift(self, cr, bw, bh, colors, glow):
        """Voluptuous molten fluid blobs morphing, merging, and floating across the screen."""
        cr.set_operator(cairo.OPERATOR_SCREEN)
        orbs = [
            (bw * (0.32 + 0.22 * math.sin(self.t * 0.6)), bh * (0.45 + 0.18 * math.cos(self.t * 0.5)), bw * 0.38, colors[0]),
            (bw * (0.68 + 0.20 * math.cos(self.t * 0.45)), bh * (0.52 + 0.20 * math.sin(self.t * 0.7)), bw * 0.42, colors[1]),
            (bw * (0.50 + 0.18 * math.sin(self.t * 0.8)), bh * (0.35 + 0.15 * math.sin(self.t * 0.35)), bw * 0.34, colors[2]),
            (bw * (0.18 + 0.14 * math.cos(self.t * 0.55)), bh * (0.65 + 0.16 * math.sin(self.t * 0.65)), bw * 0.30, colors[3 % len(colors)]),
        ]
        for ox, oy, r, c in orbs:
            rad = cairo.RadialGradient(ox, oy, 15.0, ox, oy, r)
            rad.add_color_stop_rgba(0.0, c[0], c[1], c[2], 0.38 * glow)
            rad.add_color_stop_rgba(0.35, c[0], c[1], c[2], 0.22 * glow)
            rad.add_color_stop_rgba(0.70, c[0], c[1], c[2], 0.06 * glow)
            rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rad)
            cr.paint()

    def render_nebula_mist(self, cr, bw, bh, colors, glow):
        """Interstellar stardust clouds breathing in cosmic space with deep luminescence."""
        cr.set_operator(cairo.OPERATOR_SCREEN)
        centers = [
            (bw * (0.28 + 0.08 * math.sin(self.t * 0.35)), bh * (0.48 + 0.08 * math.cos(self.t * 0.3)), bw * 0.46, colors[0]),
            (bw * (0.72 + 0.07 * math.cos(self.t * 0.28)), bh * (0.40 + 0.09 * math.sin(self.t * 0.32)), bw * 0.48, colors[1]),
            (bw * (0.50 + 0.10 * math.sin(self.t * 0.42)), bh * (0.65 + 0.08 * math.cos(self.t * 0.4)), bw * 0.40, colors[2]),
            (bw * (0.85 + 0.06 * math.sin(self.t * 0.3)), bh * (0.70 + 0.08 * math.sin(self.t * 0.25)), bw * 0.32, colors[3 % len(colors)])
        ]
        for cx, cy, r, c in centers:
            breathe = 1.0 + 0.08 * math.sin(self.t * 0.5 + cx)
            rad = cairo.RadialGradient(cx, cy, 25.0, cx, cy, r * breathe)
            rad.add_color_stop_rgba(0.0, c[0], c[1], c[2], 0.32 * glow)
            rad.add_color_stop_rgba(0.40, c[0], c[1], c[2], 0.18 * glow)
            rad.add_color_stop_rgba(0.75, c[0], c[1], c[2], 0.04 * glow)
            rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rad)
            cr.paint()

    def render_solar_dusk(self, cr, bw, bh, colors, glow):
        """Warm molten gold & amber coronal waves rising softly like liquid dusk."""
        # Horizon soft glow
        horizon_y = bh * 0.60
        sun_x = bw * (0.50 + 0.15 * math.sin(self.t * 0.3))
        sun_rad = cairo.RadialGradient(sun_x, horizon_y, 20.0, sun_x, horizon_y, bw * 0.55)
        sun_rad.add_color_stop_rgba(0.0, colors[0][0], colors[0][1], colors[0][2], 0.40 * glow)
        sun_rad.add_color_stop_rgba(0.35, colors[1][0], colors[1][1], colors[1][2], 0.22 * glow)
        sun_rad.add_color_stop_rgba(0.75, colors[2][0], colors[2][1], colors[2][2], 0.05 * glow)
        sun_rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SCREEN)
        cr.set_source(sun_rad)
        cr.paint()

        # Rolling coronal wave dunes
        for idx in range(3):
            phase = self.t * (0.65 + idx * 0.25) + idx * 1.5
            c = colors[idx % len(colors)]
            mid_y = bh * (0.52 + 0.14 * idx)

            cr.new_sub_path()
            cr.move_to(0, bh)
            cr.line_to(0, mid_y)

            steps = 10
            sw = bw / float(steps)
            for s in range(steps + 1):
                cur_x = s * sw
                cur_y = mid_y + math.sin(phase + s * 0.55) * (18.0 + 7.0 * idx)
                cr.line_to(cur_x, cur_y)

            cr.line_to(bw, bh)
            cr.close_path()

            grad = cairo.LinearGradient(0, mid_y - 40.0, 0, bh)
            alpha = (0.26 + 0.05 * math.cos(phase * 0.7)) * glow
            grad.add_color_stop_rgba(0.0, c[0], c[1], c[2], alpha)
            grad.add_color_stop_rgba(0.40, c[0], c[1], c[2], alpha * 0.6)
            grad.add_color_stop_rgba(0.80, c[0], c[1], c[2], alpha * 0.12)
            grad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(grad)
            cr.fill()

    def render_matrix_ocean(self, cr, bw, bh, colors, glow):
        """Deep oceanic abyss with harmonic waves of razor emerald and cyan bioluminescence."""
        # Deep organic luminescent pools
        cr.set_operator(cairo.OPERATOR_SCREEN)
        for i, c in enumerate(colors[:2]):
            ox = bw * (0.35 + 0.30 * i + 0.12 * math.cos(self.t * 0.5 + i))
            oy = bh * (0.55 + 0.12 * math.sin(self.t * 0.4 + i))
            r = bw * (0.42 + 0.06 * math.sin(self.t * 0.35 + i))
            rad = cairo.RadialGradient(ox, oy, 15.0, ox, oy, r)
            rad.add_color_stop_rgba(0.0, c[0], c[1], c[2], 0.34 * glow)
            rad.add_color_stop_rgba(0.40, c[0], c[1], c[2], 0.16 * glow)
            rad.add_color_stop_rgba(0.75, c[0], c[1], c[2], 0.03 * glow)
            rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rad)
            cr.paint()

        # Undulating ocean swells
        for idx in range(3):
            phase = self.t * (0.60 + idx * 0.22) + idx * 1.8
            c = colors[idx % len(colors)]
            mid_y = bh * (0.40 + 0.16 * idx)

            cr.new_sub_path()
            cr.move_to(0, bh)
            cr.line_to(0, mid_y)

            steps = 12
            sw = bw / float(steps)
            for s in range(steps + 1):
                cur_x = s * sw
                cur_y = mid_y + math.sin(phase + s * 0.50) * (20.0 + 8.0 * idx)
                cr.line_to(cur_x, cur_y)

            cr.line_to(bw, bh)
            cr.close_path()

            grad = cairo.LinearGradient(0, mid_y - 35.0, 0, bh)
            alpha = (0.28 + 0.05 * math.sin(phase * 0.6)) * glow
            grad.add_color_stop_rgba(0.0, c[0], c[1], c[2], alpha)
            grad.add_color_stop_rgba(0.45, c[0], c[1], c[2], alpha * 0.55)
            grad.add_color_stop_rgba(0.85, c[0], c[1], c[2], alpha * 0.10)
            grad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(grad)
            cr.fill()

    def render_prism_aether(self, cr, bw, bh, colors, glow):
        """Holographic iridescent crystal silk veils sliding across the screen."""
        cr.set_operator(cairo.OPERATOR_SCREEN)
        for idx in range(4):
            phase = self.t * (0.50 + idx * 0.18) + idx * 1.4
            c = colors[idx % len(colors)]
            cx = bw * (0.20 + 0.22 * idx + 0.10 * math.sin(phase))
            cy = bh * (0.40 + 0.15 * math.cos(phase * 0.8))
            r = bw * (0.36 + 0.08 * math.sin(phase * 0.6))

            rad = cairo.RadialGradient(cx, cy, 20.0, cx, cy, r)
            rad.add_color_stop_rgba(0.0, c[0], c[1], c[2], 0.30 * glow)
            rad.add_color_stop_rgba(0.35, c[0], c[1], c[2], 0.18 * glow)
            rad.add_color_stop_rgba(0.70, c[0], c[1], c[2], 0.04 * glow)
            rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rad)
            cr.paint()

    def render_oceanic_abyss(self, cr, bw, bh, colors, glow):
        """Clean deep ocean navy abyss with tranquil central luminescence pool."""
        cx, cy = bw * 0.5, bh * 0.5
        cr.set_operator(cairo.OPERATOR_SCREEN)
        
        # Central deep-sea luminescence aura
        glow_rad = cairo.RadialGradient(cx, cy, 10.0, cx, cy, bw * 0.45)
        glow_rad.add_color_stop_rgba(0.0, 0.0, 0.45, 0.85, 0.22 * glow)
        glow_rad.add_color_stop_rgba(0.5, 0.0, 0.20, 0.55, 0.07 * glow)
        glow_rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(glow_rad)
        cr.paint()

    def render_mrflow_holographic_core(self, cr, bw, bh, glow):
        """
        Mr. Flow Sovereign Centered Holographic Core Arc Reactor (Oceanic AI OS Engine).
        Rendered with 1:1 retina razor sharpness in dedicated surface or native canvas.
        Dynamically reacts to Voice Cadence, Tool Execution, and Neural Cognitive Thinking.
        """
        cx, cy = bw * 0.5, bh * 0.5
        rint = max(0.88, min(1.0, self.reactor_intensity * glow * 1.5))
        morph = self.active_morphology
        t = self.t
        amp = self.active_amplitude
        tf = self.thinking_flux
        is_thinking = (tf > 0.04)
        is_speech = (morph == "morph-speech") or (self.raw_state == "speaking")
        sc = 2.4 if bw >= 400.0 else 1.0
        is_active = is_speech or is_thinking or (amp > 0.05)

        # Dynamic Rotational Velocity: accelerates up to 2.8x during cognitive thinking
        rot_mult = 1.0 + 1.8 * tf

        # Dynamic Audio Pulse & Thinking Aperture Breathing Factors
        if is_speech:
            vibration = (0.04 * math.sin(t * 32.0) + 0.02 * math.cos(t * 18.0)) * amp
            pulse = 1.0 + 0.18 * amp + vibration
            iris_pulse = 1.0 + 0.32 * amp + vibration * 1.5
            glow_pulse = 1.0 + 0.55 * amp
        elif is_thinking:
            pulse = 1.0 + 0.05 * math.sin(t * 7.0) * tf
            iris_pulse = 1.0 - 0.10 * tf + 0.08 * math.sin(t * 9.0) * tf
            glow_pulse = 1.0 + 0.45 * tf + 0.15 * math.sin(t * 8.0) * tf
        else:
            pulse = 1.0
            iris_pulse = 1.0
            glow_pulse = 1.0

        cr.set_operator(cairo.OPERATOR_OVER)

        # High-contrast deep obsidian glass backing disc so the reactor core always pops against any wallpaper
        r_back = 62.0 * sc * pulse
        grad_back = cairo.RadialGradient(cx, cy, 8.0, cx, cy, r_back)
        grad_back.add_color_stop_rgba(0.0, 0.01, 0.03, 0.07, 0.88)
        grad_back.add_color_stop_rgba(0.70, 0.01, 0.04, 0.08, 0.68)
        grad_back.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(grad_back)
        cr.arc(cx, cy, r_back, 0, 2 * math.pi)
        cr.fill()

        # Dynamic Color Shift: Smooth transition from Ocean Cyan to Electric Indigo
        cr_r = 0.0 * (1.0 - tf) + 0.48 * tf
        cr_g = 0.85 * (1.0 - tf) + 0.28 * tf
        cr_b = 1.0

        # 0. Thinking Luminescence Ripples
        if is_thinking:
            for rip in range(2):
                phase = (t * 1.5 + rip * 0.5) % 1.0
                rip_r = (28.0 * sc * iris_pulse) + phase * (44.0 * sc)
                rip_alpha = (1.0 - phase) * 0.32 * tf * rint
                cr.set_line_width(1.0 if sc <= 1 else 1.4)
                cr.arc(cx, cy, rip_r, 0, 2 * math.pi)
                cr.set_source_rgba(0.55, 0.35, 1.0, rip_alpha)
                cr.stroke()

        # 1. Outer Concentric Precision Arc Ring
        cr.set_line_width((1.8 if sc <= 1 else 2.4) + 0.8 * amp + 0.4 * tf)
        cr.arc(cx, cy, 50.0 * sc * pulse, 0, 2 * math.pi)
        cr.set_source_rgba(cr_r, cr_g * 0.85, cr_b, (0.75 + 0.20 * amp + 0.15 * tf) * rint)
        cr.stroke()

        # 2. Segmented rotating outer brackets (Fast Gyroscopic Counter-Rotation when thinking)
        for s in range(4):
            a_start = t * 0.35 * rot_mult + s * (math.pi / 2.0) + 0.15
            a_end = a_start + 0.75
            cr.set_line_width((2.4 if sc <= 1 else 3.4) + 1.2 * amp + 0.6 * tf)
            cr.arc(cx, cy, 56.0 * sc * pulse, a_start, a_end)
            cr.set_source_rgba(cr_r, cr_g, cr_b, (0.95 if is_active else 0.88) * rint)
            cr.stroke()

        # 3. Precision Ticks on Outer Ring (40 ticks with acoustic flaring)
        num_ticks = 40
        tick_flare = (8.0 * amp) if is_speech else 0.0
        for i in range(num_ticks):
            ang = i * (2 * math.pi / num_ticks) + t * 0.12 * rot_mult
            is_major = (i % 4 == 0)
            r1 = (49.0 * sc * pulse) if is_major else (51.0 * sc * pulse)
            r2 = (56.5 * sc * pulse + tick_flare) if is_major else (55.0 * sc * pulse + tick_flare * 0.5)
            cr.set_line_width(((2.0 if is_major else 1.2) if sc <= 1 else (2.4 if is_major else 1.5)) + 0.4 * amp + 0.2 * tf)
            cr.move_to(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
            cr.line_to(cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))
            cr.set_source_rgba(cr_r, cr_g, cr_b, (0.95 if is_major else 0.78) * rint)
            cr.stroke()

        # 4. Middle counter-rotating ring with satellite nodes
        cr.set_line_width((1.2 if sc <= 1 else 1.6) + 0.4 * amp + 0.3 * tf)
        cr.arc(cx, cy, 40.0 * sc * pulse, 0, 2 * math.pi)
        cr.set_source_rgba(cr_r * 0.85, cr_g * 0.85, cr_b, (0.75 + 0.15 * tf) * rint)
        cr.stroke()

        satellite_coords = []
        for d in range(6):
            ang = -t * 0.50 * rot_mult + d * (math.pi / 3.0)
            dot_x = cx + (40.0 * sc * pulse) * math.cos(ang)
            dot_y = cy + (40.0 * sc * pulse) * math.sin(ang)
            satellite_coords.append((dot_x, dot_y))
            cr.arc(dot_x, dot_y, (2.2 if sc <= 1 else 3.2) + 1.2 * amp + 0.6 * tf, 0, 2 * math.pi)
            cr.set_source_rgba(0.4 + 0.35 * tf, 0.95 - 0.45 * tf, 1.0, (0.95 + 0.05 * amp) * rint)
            cr.fill()

        # 4b. Synaptic inter-node laser web during thinking
        if is_thinking:
            cr.set_line_width(0.7 if sc <= 1 else 1.0)
            for i in range(len(satellite_coords)):
                next_node = satellite_coords[(i + 2) % len(satellite_coords)]
                cr.move_to(satellite_coords[i][0], satellite_coords[i][1])
                cr.line_to(next_node[0], next_node[1])
            cr.set_source_rgba(0.70, 0.40, 1.0, 0.30 * tf * rint)
            cr.stroke()

        # 5. Inner Glowing Iris Ring
        cr.set_line_width((2.2 if sc <= 1 else 3.0) + 1.4 * amp + 0.6 * tf)
        cr.arc(cx, cy, 28.0 * sc * iris_pulse, 0, 2 * math.pi)
        cr.set_source_rgba(cr_r, cr_g, cr_b, (0.92 + 0.08 * amp) * rint)
        cr.stroke()

        # 6. Center Morphology Inside Iris
        if morph == "morph-thinking" or (is_thinking and morph not in ("morph-terminal", "morph-frameless", "morph-chamfer", "morph-swarm")):
            r_iris = 28.0 * sc * iris_pulse
            num_pts = 44
            dx = (r_iris * 1.7) / float(num_pts - 1)
            x_start = cx - (r_iris * 0.85)

            # Wave 1: Primary Synaptic Cognitive Flow
            cr.set_line_width(1.6 if sc <= 1 else 2.2)
            for i in range(num_pts):
                px = x_start + i * dx
                norm_x = (float(i) / (num_pts - 1) - 0.5) * 2.0
                envelope = max(0.0, 1.0 - norm_x * norm_x)
                py = cy + envelope * (7.5 * sc * math.sin(norm_x * 9.0 + t * 14.0) * math.cos(norm_x * 4.0 - t * 8.0))
                if i == 0: cr.move_to(px, py)
                else: cr.line_to(px, py)
            cr.set_source_rgba(0.65, 0.30, 1.0, 0.95 * rint)
            cr.stroke()

            # Wave 2: Fast Harmonic Synaptic Spark
            cr.set_line_width(1.0 if sc <= 1 else 1.4)
            for i in range(num_pts):
                px = x_start + i * dx
                norm_x = (float(i) / (num_pts - 1) - 0.5) * 2.0
                envelope = max(0.0, 1.0 - norm_x * norm_x)
                py = cy + envelope * (4.5 * sc * math.sin(norm_x * 16.0 - t * 20.0))
                if i == 0: cr.move_to(px, py)
                else: cr.line_to(px, py)
            cr.set_source_rgba(0.95, 0.90, 1.0, 0.90 * rint)
            cr.stroke()

            # Wave 3: Sub-Synaptic Resonance Filament
            cr.set_line_width(0.7 if sc <= 1 else 1.0)
            for i in range(num_pts):
                px = x_start + i * dx
                norm_x = (float(i) / (num_pts - 1) - 0.5) * 2.0
                envelope = max(0.0, 1.0 - norm_x * norm_x)
                py = cy - envelope * (5.0 * sc * math.sin(norm_x * 12.0 + t * 10.0))
                if i == 0: cr.move_to(px, py)
                else: cr.line_to(px, py)
            cr.set_source_rgba(0.0, 0.95, 1.0, 0.60 * rint)
            cr.stroke()

            spark_r = (2.4 if sc <= 1 else 3.6) + 1.2 * math.sin(t * 18.0)
            cr.arc(cx, cy, spark_r, 0, 2 * math.pi)
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * rint)
            cr.fill()

        elif morph == "morph-terminal":
            cols = 7
            cdx = (36.0 * sc) / float(cols)
            cr.set_line_width(1.2 if sc <= 1 else 1.6)
            for c in range(cols):
                x = cx - (18.0 * sc) + (c + 0.5) * cdx
                h = 24.0 * sc * (0.35 + 0.65 * math.sin(t * 3.0 + c * 0.8))
                y_top = cy - h / 2.0
                grad = cairo.LinearGradient(x, cy + 12 * sc, x, y_top)
                grad.add_color_stop_rgba(0.0, 0.0, 1.0, 0.4, 0.15)
                grad.add_color_stop_rgba(0.5, 0.0, 1.0, 0.6, 0.80 * rint)
                grad.add_color_stop_rgba(1.0, 0.8, 1.0, 0.9, 0.95 * rint)
                cr.set_source(grad)
                cr.move_to(x, cy + 12 * sc)
                cr.line_to(x, y_top)
                cr.stroke()
                cr.arc(x, y_top, 1.2 if sc <= 1 else 1.8, 0, 2 * math.pi)
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.90 * rint)
                cr.fill()

        elif morph == "morph-circle":
            cr.arc(cx, cy, 24.0 * sc, 0, 2 * math.pi)
            cr.set_source_rgba(0.0, 0.90, 1.0, 0.35 * rint)
            cr.stroke()
            cr.new_sub_path()
            cr.move_to(cx, cy)
            cr.arc(cx, cy, 26.0 * sc, self.radar_angle - 0.5, self.radar_angle)
            cr.close_path()
            rsw = cairo.RadialGradient(cx, cy, 2.0, cx, cy, 26.0 * sc)
            rsw.add_color_stop_rgba(0.0, 0.0, 0.9, 1.0, 0.70 * rint)
            rsw.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rsw)
            cr.fill()

        elif morph == "morph-frameless":
            scan_y = cy - (20.0 * sc) + (abs((t * 24.0 * sc) % (40.0 * sc)) - (20.0 * sc))
            cr.set_line_width(1.5 if sc <= 1 else 2.0)
            cr.move_to(cx - 24.0 * sc, scan_y)
            cr.line_to(cx + 24.0 * sc, scan_y)
            cr.set_source_rgba(0.7, 1.0, 1.0, 0.95 * rint)
            cr.stroke()
            smist = cairo.LinearGradient(0, scan_y - 8.0 * sc, 0, scan_y)
            smist.add_color_stop_rgba(0.0, 0.0, 0.5, 1.0, 0.0)
            smist.add_color_stop_rgba(1.0, 0.0, 0.9, 1.0, 0.35 * rint)
            cr.set_source(smist)
            cr.rectangle(cx - 24.0 * sc, scan_y - 8.0 * sc, 48.0 * sc, 8.0 * sc)
            cr.fill()

        elif morph == "morph-chamfer":
            for ring in (1, 2):
                cr.new_sub_path()
                for corner in range(6):
                    ang = corner * (math.pi / 3.0) + t * (0.8 if ring == 1 else -0.8)
                    px = cx + ring * 10.0 * sc * math.cos(ang)
                    py = cy + ring * 10.0 * sc * math.sin(ang)
                    if corner == 0: cr.move_to(px, py)
                    else: cr.line_to(px, py)
                cr.close_path()
                cr.set_source_rgba(0.0, 1.0, 0.5, (0.85 if ring == 1 else 0.55) * rint)
                cr.set_line_width(1.2 if sc <= 1 else 1.6)
                cr.stroke()

        elif morph == "morph-swarm":
            cr.set_line_width(0.8 if sc <= 1 else 1.2)
            for i in range(len(satellite_coords)):
                for j in range(i + 1, len(satellite_coords)):
                    if (i + j) % 2 == 0:
                        cr.move_to(satellite_coords[i][0], satellite_coords[i][1])
                        cr.line_to(satellite_coords[j][0], satellite_coords[j][1])
                        cr.set_source_rgba(0.0, 1.0, 0.7, 0.35 * rint)
                        cr.stroke()

        else:
            # Speaking & Idle Harmonic Waveform inside core (High-Density Vector Silk Waves)
            r_iris = 28.0 * sc * iris_pulse
            steps = 40
            wave_w = r_iris * 1.85
            x_start = cx - wave_w / 2.0
            dx = wave_w / float(steps)
            cur_amp = (0.24 + 0.75 * amp) if is_speech else 0.18
            speed_mul = 14.0 if is_speech else 6.0

            layers = [
                ((0.0, 0.50, 1.00), 0.70 * rint, 1.0, 0.0, (1.6 if sc <= 1 else 2.2) + 0.6 * amp, r_iris * 0.35),
                ((0.0, 1.00, 0.50), 0.85 * rint, 1.6, 1.2, (2.0 if sc <= 1 else 2.8) + 0.8 * amp, r_iris * 0.55),
                ((0.85, 1.00, 1.00), 1.00 * rint, 2.4, 2.4, (2.6 if sc <= 1 else 3.4) + 1.0 * amp, r_iris * 0.75),
            ]
            for col, alpha, freq_mul, phase_off, line_w, base_h in layers:
                cr.set_line_width(line_w)
                cr.set_source_rgba(col[0], col[1], col[2], alpha)
                cr.new_sub_path()
                for s in range(steps + 1):
                    wx = x_start + s * dx
                    norm = float(s) / float(steps)
                    env = math.sin(norm * math.pi)
                    harmonic = math.sin(t * speed_mul * freq_mul + s * 0.35 + phase_off)
                    if is_speech:
                        harmonic += 0.28 * math.sin(t * 36.0 + s * 0.75) * amp
                    wy = cy + harmonic * (base_h * cur_amp) * env
                    if s == 0: cr.move_to(wx, wy)
                    else: cr.line_to(wx, wy)
                cr.stroke()

        # 7. Central Radiant Core Node Glow
        core_glow = cairo.RadialGradient(cx, cy, 1.0, cx, cy, (28.0 * sc * iris_pulse) * 0.90)
        cg_r = 0.0 * (1.0 - tf) + 0.35 * tf
        cg_g = 0.85 * (1.0 - tf) + 0.20 * tf
        cg_b = 1.0
        core_glow.add_color_stop_rgba(0.0, 0.90, 1.0, 1.0, 0.95 * rint)
        core_glow.add_color_stop_rgba(0.35, cg_r, cg_g, cg_b, (0.75 + 0.20 * amp + 0.15 * tf) * rint)
        core_glow.add_color_stop_rgba(0.70, cg_r * 0.5, cg_g * 0.5, cg_b, 0.35 * rint)
        core_glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(core_glow)
        cr.arc(cx, cy, (28.0 * sc * iris_pulse) * 0.90, 0, 2 * math.pi)
        cr.fill()

    def render_neural_reactor(self, cr, bw, bh, glow):
        """
        Renders the active Sovereign Tool or Voice animation directly into the wallpaper canvas.
        Morphologies:
          1. morph-speech     -> Harmonic Synaptic Audio Waveform
          2. morph-terminal   -> Cybernetic Matrix Phosphor Grid
          3. morph-circle     -> Sonar Radar Scan Wavefronts
          4. morph-frameless  -> Holographic Laser Inspection Sweep
          5. morph-chamfer    -> Crystalline Hexagonal Optical Lattice
          6. morph-swarm      -> Tri-Node Gravitational Swarm Constellation
        """
        style_type = self.style_data.get("style", "oceanic")
        if style_type == "oceanic":
            self.render_mrflow_holographic_core(cr, bw, bh, glow)
            return

        morph = self.active_morphology
        rint = self.reactor_intensity * glow

        cr.set_operator(cairo.OPERATOR_SCREEN)

        if morph == "morph-speech":
            self._render_speech_wave(cr, bw, bh, rint)
        elif morph == "morph-terminal":
            self._render_terminal_grid(cr, bw, bh, rint)
        elif morph == "morph-circle":
            self._render_radar_sonar(cr, bw, bh, rint)
        elif morph == "morph-frameless":
            self._render_laser_sweep(cr, bw, bh, rint)
        elif morph == "morph-chamfer":
            self._render_crystal_lattice(cr, bw, bh, rint)
        elif morph == "morph-swarm":
            self._render_swarm_orbits(cr, bw, bh, rint)
        else:
            self._render_horizon_idle(cr, bw, bh, rint)

    def _render_speech_wave(self, cr, bw, bh, rint):
        """Harmonic Synaptic Audio Waveform undulating across the bottom horizon."""
        horizon_y = bh * 0.78
        base_amp = (8.0 + 28.0 * self.active_amplitude) * rint

        layers = [
            ((0.0, 0.75, 1.0), 0.30 * rint, 1.0, 0.0, 1.5),
            ((0.0, 1.0, 0.4), 0.50 * rint, 1.4, 1.2, 2.0),
            ((0.3, 1.0, 0.7), 0.85 * rint, 1.9, 2.4, 2.5),
        ]
        steps = 32
        dx = bw / float(steps)

        for col, alpha, freq_mul, phase_off, line_w in layers:
            cr.set_line_width(line_w)
            cr.set_source_rgba(col[0], col[1], col[2], alpha)
            cr.new_sub_path()
            for s in range(steps + 1):
                cur_x = s * dx
                norm_x = float(s) / float(steps)
                env = math.sin(norm_x * math.pi)
                cur_y = horizon_y + math.sin(self.t * 8.0 * freq_mul + s * 0.35 + phase_off) * base_amp * env
                if s == 0:
                    cr.move_to(cur_x, cur_y)
                else:
                    cr.line_to(cur_x, cur_y)
            cr.stroke()

        glow_rad = cairo.RadialGradient(bw * 0.5, horizon_y + 10.0, 10.0, bw * 0.5, horizon_y + 10.0, bw * 0.35)
        glow_rad.add_color_stop_rgba(0.0, 0.0, 1.0, 0.4, 0.28 * rint)
        glow_rad.add_color_stop_rgba(0.4, 0.0, 0.8, 1.0, 0.12 * rint)
        glow_rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(glow_rad)
        cr.paint()

    def _render_terminal_grid(self, cr, bw, bh, rint):
        """Cybernetic Phosphor Matrix Grid for terminal and shell execution."""
        cols = 20
        dx = bw / float(cols)
        bottom_y = bh * 0.95
        cr.set_line_width(1.6)

        # Baseline phosphor glow
        bglow = cairo.LinearGradient(0, bottom_y - 25, 0, bh)
        bglow.add_color_stop_rgba(0.0, 0.0, 1.0, 0.4, 0.25 * rint)
        bglow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(bglow)
        cr.rectangle(0, bottom_y - 25, bw, 35)
        cr.fill()

        for c in range(cols):
            x = (c + 0.5) * dx
            offset = self.matrix_offsets[c % len(self.matrix_offsets)]
            h = bh * 0.50 * (0.35 + 0.65 * math.sin(self.t * 2.5 + c * 0.65))
            y_head = bottom_y - (offset / 100.0) * h

            grad = cairo.LinearGradient(x, y_head, x, bottom_y)
            grad.add_color_stop_rgba(0.0, 0.7, 1.0, 0.8, 0.95 * rint)
            grad.add_color_stop_rgba(0.35, 0.0, 1.0, 0.4, 0.50 * rint)
            grad.add_color_stop_rgba(1.0, 0.0, 0.2, 0.1, 0.0)
            cr.set_source(grad)
            cr.move_to(x, bottom_y)
            cr.line_to(x, y_head)
            cr.stroke()

            node_r = 2.2 + 1.2 * math.sin(self.t * 4.0 + c)
            cr.arc(x, y_head, node_r, 0, 2 * math.pi)
            cr.set_source_rgba(0.85, 1.0, 0.9, 0.85 * rint)
            cr.fill()

    def _render_radar_sonar(self, cr, bw, bh, rint):
        """Expanding Sonar Radar wavefronts for Search, Grep, Web & Thinking."""
        cx = bw * 0.5
        cy = bh * 0.74
        max_r = bw * 0.38

        cr.set_line_width(1.6)
        for i in range(4):
            r = ((self.t * 28.0 + i * (max_r / 4.0)) % max_r) + 8.0
            norm_r = r / max_r
            alpha = (1.0 - norm_r) * 0.70 * rint
            cr.arc(cx, cy, r, 0, 2 * math.pi)
            cr.set_source_rgba(0.0, 0.92, 1.0, alpha)
            cr.stroke()

        cr.new_sub_path()
        cr.move_to(cx, cy)
        cr.arc(cx, cy, max_r * 0.75, self.radar_angle - 0.45, self.radar_angle)
        cr.close_path()
        rad = cairo.RadialGradient(cx, cy, 5.0, cx, cy, max_r * 0.75)
        rad.add_color_stop_rgba(0.0, 0.0, 1.0, 0.4, 0.40 * rint)
        rad.add_color_stop_rgba(0.7, 0.0, 0.85, 1.0, 0.15 * rint)
        rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(rad)
        cr.fill()

        cr.arc(cx, cy, 4.0, 0, 2 * math.pi)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.95 * rint)
        cr.fill()

    def _render_laser_sweep(self, cr, bw, bh, rint):
        """Holographic Laser Inspection Sweep for reading and inspecting files."""
        y = bh * self.laser_scan_y
        cr.set_line_width(2.0)

        cr.move_to(0, y)
        cr.line_to(bw, y)
        cr.set_source_rgba(0.7, 1.0, 1.0, 0.90 * rint)
        cr.stroke()

        mist_h = 24.0
        grad = cairo.LinearGradient(0, y - mist_h * self.laser_scan_dir, 0, y)
        grad.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, 0.0)
        grad.add_color_stop_rgba(1.0, 0.0, 0.85, 1.0, 0.25 * rint)
        cr.set_source(grad)
        cr.rectangle(0, min(y, y - mist_h * self.laser_scan_dir), bw, mist_h)
        cr.fill()

        ticks = 24
        tdx = bw / float(ticks)
        cr.set_line_width(1.0)
        for i in range(ticks + 1):
            tx = i * tdx
            th = 4.0 if i % 4 == 0 else 2.0
            cr.move_to(tx, y - th)
            cr.line_to(tx, y + th)
        cr.set_source_rgba(0.0, 1.0, 0.5, 0.65 * rint)
        cr.stroke()

    def _render_crystal_lattice(self, cr, bw, bh, rint):
        """Crystalline Hexagonal Optical Lattice for modifying and writing code."""
        cx = bw * 0.5
        cy = bh * 0.70
        cr.set_line_width(1.4)

        # Central crystalline core glow
        rad = cairo.RadialGradient(cx, cy, 2.0, cx, cy, bw * 0.15)
        rad.add_color_stop_rgba(0.0, 0.0, 1.0, 0.5, 0.40 * rint)
        rad.add_color_stop_rgba(0.5, 0.0, 0.8, 1.0, 0.15 * rint)
        rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(rad)
        cr.paint()

        hex_r = 30.0
        rings = 3
        for ring in range(1, rings + 1):
            cur_r = hex_r * ring * (0.95 + 0.05 * math.sin(self.t * 3.0 + ring))
            alpha = (1.0 - (ring / float(rings + 1))) * 0.75 * rint
            cr.new_sub_path()
            for corner in range(6):
                ang = corner * (math.pi / 3.0) + self.t * 0.5 * (1.0 if ring % 2 == 0 else -1.0)
                px = cx + cur_r * math.cos(ang)
                py = cy + cur_r * math.sin(ang) * 0.65
                if corner == 0:
                    cr.move_to(px, py)
                else:
                    cr.line_to(px, py)
                cr.arc(px, py, 2.2, 0, 2 * math.pi)
            cr.close_path()
            cr.set_source_rgba(0.0, 1.0, 0.45, alpha)
            cr.stroke()

    def _render_swarm_orbits(self, cr, bw, bh, rint):
        """Tri-Node Gravitational Swarm Constellation for subagents and swarm tasks."""
        cx = bw * 0.5
        cy = bh * 0.70
        orbs = [
            (0.0, 1.0, 0.4, bw * 0.16, 1.0, 0.0, 4.0),
            (0.0, 0.9, 1.0, bw * 0.22, -0.8, 1.5, 3.5),
            (0.7, 0.3, 1.0, bw * 0.27, 0.6, 3.0, 3.0),
        ]
        coords = []
        for r, g, b, radius, spd, phase, size in orbs:
            ang = self.swarm_phase * spd + phase
            ox = cx + radius * math.cos(ang)
            oy = cy + radius * math.sin(ang) * 0.55
            coords.append((ox, oy, r, g, b, size))

        # Dynamic inter-node gravitational web
        cr.set_line_width(0.9)
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                cr.move_to(coords[i][0], coords[i][1])
                cr.line_to(coords[j][0], coords[j][1])
                cr.set_source_rgba(0.0, 1.0, 0.7, 0.22 * rint)
                cr.stroke()

        cr.set_line_width(1.2)
        for r, g, b, radius, spd, phase, size in orbs:
            cr.arc(cx, cy, radius, 0, 2 * math.pi)
            cr.set_source_rgba(r, g, b, 0.12 * rint)
            cr.stroke()

        for ox, oy, r, g, b, size in coords:
            rad = cairo.RadialGradient(ox, oy, 1.0, ox, oy, size * 3.2)
            rad.add_color_stop_rgba(0.0, r, g, b, 0.90 * rint)
            rad.add_color_stop_rgba(0.5, r, g, b, 0.40 * rint)
            rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rad)
            cr.arc(ox, oy, size * 3.2, 0, 2 * math.pi)
            cr.fill()

    def _render_horizon_idle(self, cr, bw, bh, rint):
        """Clean resting horizon without line artifacts."""
        pass

    def render_empirical_tool_core(self, cr):
        """
        Flowork Sovereign Option A: Central Living Tool Core.
        Directly embedded in the desktop wallpaper layer (keep_below).
        Zero popups over active applications.
        Displays verbatim command, live stdout/stderr stream, and Exit 0 status.
        """
        try:
            n_state = flowork_neural_bridge.get_neural_state()
        except Exception:
            return

        state = n_state.get("state", "idle")
        tool_name = n_state.get("tool_name", "")
        command = n_state.get("command", "")
        logs = n_state.get("logs", [])
        exit_code = n_state.get("exit_code", 0)
        duration_ms = n_state.get("duration_ms", 0)
        status = n_state.get("status", "idle")
        ts = n_state.get("timestamp", 0)
        now = time.time()

        # Tool HUD is exclusively for empirical tool execution telemetry.
        # When agent is speaking, yield so the pristine 1:1 Arc Reactor vibrates with acoustic voice energy.
        if state == "speaking":
            return

        is_running = (state == "tool_use") or (status in ("running", "deliberating"))
        has_tool = bool(tool_name or command or logs)
        if is_running and has_tool:
            self.last_tool_payload = n_state
            self.last_tool_done_time = now
            cur_payload = n_state
        elif self.last_tool_payload and (now - self.last_tool_done_time < 8.0):
            cur_payload = self.last_tool_payload
        else:
            self.last_tool_payload = None
            return

        tool_name = cur_payload.get("tool_name", "")
        command = cur_payload.get("command", "")
        logs = cur_payload.get("logs", [])
        exit_code = cur_payload.get("exit_code", 0)
        duration_ms = cur_payload.get("duration_ms", 0)
        status = cur_payload.get("status", "idle")

        cx = float(self.screen_w) * 0.5
        cy = float(self.screen_h) * 0.5
        radius = 230.0

        ui_scale = self.get_ui_scale()
        cr.save()
        if abs(ui_scale - 1.0) > 0.001:
            cr.translate(cx, cy)
            cr.scale(ui_scale, ui_scale)
            cr.translate(-cx, -cy)

        # 1. Dark Crystal Glass Disc
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.set_source_rgba(0.005, 0.014, 0.022, 0.82)
        cr.fill_preserve()

        # Ambient radial glow inside the disc
        glow_rad = cairo.RadialGradient(cx, cy, 20.0, cx, cy, radius)
        glow_rad.add_color_stop_rgba(0.0, 0.0, 0.85, 1.0, 0.16)
        glow_rad.add_color_stop_rgba(0.7, 0.0, 1.0, 0.40, 0.06)
        glow_rad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.45)
        cr.set_source(glow_rad)
        cr.fill_preserve()

        # Razor 1.4px Specular Rim
        is_success = (status == "done" and exit_code == 0) or (status != "error" and exit_code == 0 and status not in ("running", "deliberating") and state not in ("thinking", "tool_use", "deliberation"))
        if status == "error" or exit_code != 0:
            rim_col = (1.0, 0.35, 0.35)
        elif state == "thinking":
            rim_col = (0.0, 0.95, 1.0)
        elif state == "deliberation" or status == "deliberating":
            rim_col = (0.0, 1.0, 0.55)
        elif is_success:
            rim_col = (0.0, 1.0, 0.45)
        else:
            rim_col = (0.0, 0.85, 1.0)

        cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.90)
        cr.set_line_width(1.4)
        cr.stroke()

        # 2. Outer Concentric Orbital Track & Gyroscopic Brackets
        cr.arc(cx, cy, radius + 14.0, 0, 2 * math.pi)
        cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.30)
        cr.set_line_width(1.0)
        cr.stroke()

        # 4 rotating brackets on perimeter
        t = getattr(self, "t", 0.0)
        for b in range(4):
            ang_start = t * 0.4 + b * (math.pi / 2.0)
            ang_end = ang_start + 0.65
            cr.arc(cx, cy, radius + 18.0, ang_start, ang_end)
            cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.75)
            cr.set_line_width(2.0)
            cr.stroke()

        # Precision Perimeter Ticks
        for i in range(36):
            ang = i * (2 * math.pi / 36) + t * 0.15
            is_maj = (i % 3 == 0)
            r1 = radius + (10.0 if is_maj else 12.0)
            r2 = radius + 16.0
            cr.move_to(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
            cr.line_to(cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))
            cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.60 if is_maj else 0.25)
            cr.set_line_width(1.2 if is_maj else 0.8)
            cr.stroke()

        # Tool Identification & Structured Arguments
        morph = cur_payload.get("morphology") or flowork_neural_bridge.get_tool_morphology(tool_name)
        args = cur_payload.get("args") or {}

        # ------------------------------------------------------------------
        # MORPHOLOGY BACKGROUND MOTIFS (Unique visual identity per tool)
        # ------------------------------------------------------------------
        if morph == "morph-camera":
            # 6-Blade Camera Aperture Iris
            cr.save()
            blade_r = radius * 0.78
            iris_r = 72.0
            num_blades = 6
            for b_idx in range(num_blades):
                ang = b_idx * (2.0 * math.pi / num_blades) + t * 0.15
                p1_x = cx + blade_r * math.cos(ang)
                p1_y = cy + blade_r * math.sin(ang)
                p2_x = cx + iris_r * math.cos(ang + 0.85)
                p2_y = cy + iris_r * math.sin(ang + 0.85)
                cr.move_to(p1_x, p1_y)
                cr.line_to(p2_x, p2_y)
                cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.16)
                cr.set_line_width(1.2)
                cr.stroke()
            cr.restore()

        elif morph == "morph-diff":
            # Split Diff Chamber: Central vertical hairline & subtle red/green wash
            cr.save()
            cr.set_line_width(1.0)
            cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.20)
            cr.move_to(cx, cy - radius * 0.70)
            cr.line_to(cx, cy + radius * 0.70)
            cr.stroke()
            rw = cairo.RadialGradient(cx - 75.0, cy, 5.0, cx - 75.0, cy, 130.0)
            rw.add_color_stop_rgba(0.0, 1.0, 0.25, 0.25, 0.08)
            rw.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rw)
            cr.arc(cx, cy, radius, 0, 2 * math.pi)
            cr.fill()
            gw = cairo.RadialGradient(cx + 75.0, cy, 5.0, cx + 75.0, cy, 130.0)
            gw.add_color_stop_rgba(0.0, 0.0, 1.0, 0.45, 0.08)
            gw.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(gw)
            cr.arc(cx, cy, radius, 0, 2 * math.pi)
            cr.fill()
            cr.restore()

        elif morph == "morph-blueprint":
            # Hexagonal Blueprint Synthesis Rings
            cr.save()
            for h_r in (radius * 0.52, radius * 0.80):
                cr.new_sub_path()
                for c in range(6):
                    c_ang = c * (math.pi / 3.0) + t * (0.12 if h_r > 150 else -0.12)
                    px = cx + h_r * math.cos(c_ang)
                    py = cy + h_r * math.sin(c_ang)
                    if c == 0: cr.move_to(px, py)
                    else: cr.line_to(px, py)
                cr.close_path()
                cr.set_source_rgba(0.0, 0.85, 1.0, 0.12)
                cr.set_line_width(1.0)
                cr.stroke()
            cr.restore()

        elif morph == "morph-laser":
            # Laser Scanner Sweep Filament
            cr.save()
            laser_y = cy - 40.0 + ((t * 45.0) % 130.0)
            cr.set_line_width(1.4)
            cr.move_to(cx - 150.0, laser_y)
            cr.line_to(cx + 150.0, laser_y)
            cr.set_source_rgba(0.0, 0.95, 1.0, 0.65)
            cr.stroke()
            lmist = cairo.LinearGradient(0, laser_y - 12.0, 0, laser_y)
            lmist.add_color_stop_rgba(0.0, 0.0, 0.8, 1.0, 0.0)
            lmist.add_color_stop_rgba(1.0, 0.0, 0.9, 1.0, 0.18)
            cr.set_source(lmist)
            cr.rectangle(cx - 150.0, laser_y - 12.0, 300.0, 12.0)
            cr.fill()
            cr.restore()

        elif morph == "morph-radar":
            # Sonar Radar Sweep Arc
            cr.save()
            ang_r = getattr(self, "radar_angle", 0.0)
            cr.new_sub_path()
            cr.move_to(cx, cy)
            cr.arc(cx, cy, radius * 0.85, ang_r - 0.65, ang_r)
            cr.close_path()
            rsw = cairo.RadialGradient(cx, cy, 2.0, cx, cy, radius * 0.85)
            rsw.add_color_stop_rgba(0.0, 0.0, 0.9, 1.0, 0.28)
            rsw.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
            cr.set_source(rsw)
            cr.fill()
            for rr in (0.35, 0.60, 0.82):
                cr.arc(cx, cy, radius * rr, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 0.85, 1.0, 0.10)
                cr.set_line_width(0.8)
                cr.stroke()
            cr.restore()

        elif morph == "morph-conduit":
            # Dual-Stream HTTP Inflow Conduits
            cr.save()
            cr.set_line_width(1.0)
            for side in (-160.0, 160.0):
                cr.move_to(cx + side, cy - 80.0)
                cr.line_to(cx + side, cy + 90.0)
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.35)
                cr.stroke()
                for dot in range(3):
                    dy = cy - 70.0 + ((t * 45.0 + dot * 55.0) % 150.0)
                    cr.arc(cx + side, dy, 2.5, 0, 2 * math.pi)
                    cr.set_source_rgba(1.0, 1.0, 1.0, 0.85)
                    cr.fill()
            cr.restore()

        elif morph == "morph-swarm":
            # Tri-Node Gravitational Swarm Constellation Orbits
            cr.save()
            s_phase = getattr(self, "swarm_phase", 0.0)
            s_orbs = [(95.0, 1.0, 0.0), (130.0, -0.7, 2.1), (65.0, 1.4, 4.2)]
            for s_rad, s_spd, s_off in s_orbs:
                s_ang = s_phase * s_spd + s_off
                ox = cx + s_rad * math.cos(s_ang)
                oy = cy + s_rad * math.sin(s_ang) * 0.45
                cr.arc(ox, oy, 4.0, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 1.0, 0.55, 0.80)
                cr.fill()
                cr.move_to(cx, cy)
                cr.line_to(ox, oy)
                cr.set_source_rgba(0.0, 1.0, 0.55, 0.14)
                cr.set_line_width(0.8)
                cr.stroke()
            cr.restore()

        elif morph == "morph-pipeline":
            # Task Signal Pipeline
            cr.save()
            cr.set_line_width(1.2)
            cr.move_to(cx - 150.0, cy)
            cr.line_to(cx + 150.0, cy)
            cr.set_source_rgba(0.0, 0.85, 1.0, 0.20)
            cr.stroke()
            for b in range(4):
                bx = cx - 140.0 + ((t * 50.0 + b * 75.0) % 280.0)
                cr.arc(bx, cy, 3.2, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 1.0, 0.45, 0.80)
                cr.fill()
            cr.restore()

        elif morph == "morph-chronometer":
            # Chronometer Dial
            cr.save()
            cr.move_to(cx, cy)
            cr.line_to(cx + 90.0 * math.cos(t * 1.8), cy + 90.0 * math.sin(t * 1.8))
            cr.set_source_rgba(0.0, 1.0, 0.45, 0.60)
            cr.set_line_width(1.2)
            cr.stroke()
            cr.move_to(cx, cy)
            cr.line_to(cx + 60.0 * math.cos(t * 0.2), cy + 60.0 * math.sin(t * 0.2))
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.75)
            cr.set_line_width(1.8)
            cr.stroke()
            cr.restore()

        elif morph == "morph-signal":
            # Synaptic Audio/Signal Wave along center
            cr.save()
            cr.set_line_width(1.2)
            steps = 24
            dx = 280.0 / float(steps)
            for s in range(steps + 1):
                px = cx - 140.0 + s * dx
                norm_x = (float(s) / steps - 0.5) * 2.0
                envelope = max(0.0, 1.0 - norm_x * norm_x)
                py = cy + envelope * 12.0 * math.sin(t * 10.0 + s * 0.5)
                if s == 0: cr.move_to(px, py)
                else: cr.line_to(px, py)
            cr.set_source_rgba(0.0, 0.95, 1.0, 0.50)
            cr.stroke()
            cr.restore()

        elif morph == "morph-query":
            # Optical Query Diamond Reticle
            cr.save()
            d_sz = 22.0 + 3.0 * math.sin(t * 3.5)
            cr.move_to(cx, cy - d_sz)
            cr.line_to(cx + d_sz, cy)
            cr.line_to(cx, cy + d_sz)
            cr.line_to(cx - d_sz, cy)
            cr.close_path()
            cr.set_source_rgba(0.0, 1.0, 0.7, 0.22)
            cr.fill_preserve()
            cr.set_source_rgba(0.0, 1.0, 0.7, 0.85)
            cr.set_line_width(1.2)
            cr.stroke()
            cr.restore()

        elif morph == "morph-canvas":
            # Aspect-Ratio Canvas Framing Box
            cr.save()
            cw, ch = 240.0, 135.0
            cr.rectangle(cx - cw / 2.0, cy - ch / 2.0, cw, ch)
            cr.set_source_rgba(0.0, 0.85, 1.0, 0.18)
            cr.set_line_width(1.0)
            cr.stroke()
            cr.restore()

        elif morph == "morph-foundry":
            # Crystalline Agent Foundry Mesh
            cr.save()
            for r_mesh in (45.0, 95.0):
                cr.new_sub_path()
                for corn in range(6):
                    c_ang = corn * (math.pi / 3.0) + (t * 0.4 if r_mesh > 60 else -t * 0.4)
                    px = cx + r_mesh * math.cos(c_ang)
                    py = cy + r_mesh * math.sin(c_ang)
                    if corn == 0: cr.move_to(px, py)
                    else: cr.line_to(px, py)
                cr.close_path()
                cr.set_source_rgba(0.0, 1.0, 0.45, 0.18)
                cr.set_line_width(1.0)
                cr.stroke()
            cr.restore()

        elif morph == "morph-thinking":
            # Cognitive Synapse: Pulsing neural core & synaptic flux rings
            cr.save()
            for r_ring in (45.0, 85.0, 130.0):
                pulse = 1.0 + 0.08 * math.sin(t * 3.0 + r_ring * 0.05)
                cr.arc(cx, cy, r_ring * pulse, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 1.0, 0.45, 0.12 if r_ring > 60 else 0.20)
                cr.set_line_width(1.0)
                cr.stroke()
            # 6 Synaptic firing nodes
            for n_idx in range(6):
                ang = n_idx * (math.pi / 3.0) + t * 0.8
                nx = cx + 90.0 * math.cos(ang)
                ny = cy + 90.0 * math.sin(ang) * 0.75
                cr.arc(nx, ny, 3.5, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.85)
                cr.fill()
                cr.move_to(cx, cy)
                cr.line_to(nx, ny)
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.18)
                cr.set_line_width(0.8)
                cr.stroke()
            cr.restore()

        elif morph == "morph-deliberation":
            # Synaptic Deliberation: Inter-tool harmonic wave & orbital focus
            cr.save()
            cr.set_line_width(1.4)
            steps = 30
            dx = 300.0 / float(steps)
            for s in range(steps + 1):
                px = cx - 150.0 + s * dx
                norm_x = (float(s) / steps - 0.5) * 2.0
                envelope = max(0.0, 1.0 - norm_x * norm_x)
                py = cy + envelope * 16.0 * math.sin(t * 8.0 + s * 0.4)
                if s == 0: cr.move_to(px, py)
                else: cr.line_to(px, py)
            cr.set_source_rgba(0.0, 1.0, 0.45, 0.55)
            cr.stroke()
            # Dual orbital focus points
            for f_idx in (-1, 1):
                fx = cx + f_idx * (65.0 + 15.0 * math.sin(t * 2.5))
                cr.arc(fx, cy, 4.0, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.90)
                cr.fill()
            cr.restore()

        elif morph == "morph-compacting":
            # Quantum Memory Vortex: Spiral compression of synaptic nodes into central singularity
            cr.save()
            for r_idx, base_r in enumerate((130.0, 85.0, 48.0)):
                spin = t * (-3.2 + r_idx * 1.1)
                pulse = 1.0 + 0.08 * math.sin(t * 5.0 + r_idx)
                cr.arc(cx, cy, base_r * pulse, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.22 - r_idx * 0.04)
                cr.set_line_width(1.4)
                cr.stroke()

                # Inward compression tick marks
                for k in range(8):
                    tk_ang = k * (math.pi / 4.0) + spin
                    r1 = base_r * pulse
                    r2 = r1 - 8.0
                    cr.move_to(cx + r1 * math.cos(tk_ang), cy + r1 * math.sin(tk_ang) * 0.75)
                    cr.line_to(cx + r2 * math.cos(tk_ang), cy + r2 * math.sin(tk_ang) * 0.75)
                    cr.set_source_rgba(0.0, 1.0, 0.45, 0.65)
                    cr.set_line_width(1.2)
                    cr.stroke()

            # 12 Inward spiraling particle vortex
            for p_idx in range(12):
                phase = (t * 0.85 + p_idx * (1.0 / 12.0)) % 1.0
                spiral_r = (1.0 - phase) * 125.0 + 8.0
                spiral_ang = phase * 4.0 * math.pi + p_idx * (math.pi / 6.0)
                px = cx + spiral_r * math.cos(spiral_ang)
                py = cy + spiral_r * math.sin(spiral_ang) * 0.75
                dot_size = max(1.5, phase * 3.8)
                cr.arc(px, py, dot_size, 0, 2 * math.pi)
                cr.set_source_rgba(0.0, 0.95, 1.0, 0.95)
                cr.fill()

                # Trace line to singularity
                cr.move_to(px, py)
                cr.line_to(cx, cy)
                cr.set_source_rgba(0.0, 1.0, 0.45, 0.15 * phase)
                cr.set_line_width(0.8)
                cr.stroke()
            cr.restore()

        # ------------------------------------------------------------------
        # EMPIRICAL CONTENT DISPLAY (Header, Status, Telemetry & Code)
        # ------------------------------------------------------------------
        box_w = 340.0
        left_x = cx - (box_w / 2.0)
        header_y = cy - 82.0

        # Viewfinder framing corner brackets for camera
        if morph == "morph-camera":
            bf_arm = 14.0
            cr.set_line_width(2.0)
            cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.65)
            # Top-Left
            cr.move_to(left_x - 8.0, header_y - 10.0 + bf_arm)
            cr.line_to(left_x - 8.0, header_y - 10.0)
            cr.line_to(left_x - 8.0 + bf_arm, header_y - 10.0)
            # Top-Right
            cr.move_to(left_x + box_w + 8.0 - bf_arm, header_y - 10.0)
            cr.line_to(left_x + box_w + 8.0, header_y - 10.0)
            cr.line_to(left_x + box_w + 8.0, header_y - 10.0 + bf_arm)
            # Bottom-Left
            cr.move_to(left_x - 8.0, cy + 96.0 - bf_arm)
            cr.line_to(left_x - 8.0, cy + 96.0)
            cr.line_to(left_x - 8.0 + bf_arm, cy + 96.0)
            # Bottom-Right
            cr.move_to(left_x + box_w + 8.0 - bf_arm, cy + 96.0)
            cr.line_to(left_x + box_w + 8.0, cy + 96.0)
            cr.line_to(left_x + box_w + 8.0, cy + 96.0 - bf_arm)
            cr.stroke()

        # 1. Header Title
        title_map = {
            "morph-thinking": "[ COGNITIVE SYNAPSE // THINKING ]",
            "morph-deliberation": "[ SYNAPTIC DELIBERATION ]",
            "morph-compacting": "[ NEURAL COMPACTOR // DEFRAGMENTING ]",
            "morph-camera": "[ CAMERA SNAPSHOT ]",
            "morph-diff": "[ CODE SURGERY ]",
            "morph-blueprint": "[ FILE WRITE ]",
            "morph-laser": "[ FILE INSPECT ]",
            "morph-radar": "[ WEB SEARCH ]",
            "morph-conduit": "[ URL FETCH ]",
            "morph-swarm": "[ SWARM DELEGATE ]" if "invoke" in tool_name.lower() else "[ SWARM AUDIT ]",
            "morph-pipeline": "[ TASK MANAGER ]",
            "morph-chronometer": "[ SCHEDULER ]",
            "morph-signal": "[ AGENT IPC ]",
            "morph-query": "[ USER QUERY ]",
            "morph-canvas": "[ IMAGE SYNTHESIS ]",
            "morph-foundry": "[ AGENT FOUNDRY ]",
            "morph-terminal": "[ RUN_COMMAND ]"
        }
        t_title = title_map.get(morph, f"[ {tool_name.upper()} ]" if tool_name else "[ COGNITIVE REACTOR ]")

        cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.95)
        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(11.0)
        cr.move_to(left_x, header_y)
        cr.show_text(t_title)

        # 2. Status Badge
        stat_x = left_x + box_w - 110.0
        if status in ("running", "deliberating") or state in ("thinking", "deliberation", "tool_use"):
            cr.arc(stat_x, header_y - 3.5, 4.0, 0, 2 * math.pi)
            cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.95)
            cr.fill()
            cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.90)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(9.5)
            cr.move_to(stat_x + 10.0, header_y)
            if state == "thinking":
                run_lbl = "thinking..."
            elif state == "deliberation" or status == "deliberating":
                run_lbl = "deliberating..."
            elif morph == "morph-camera":
                run_lbl = "shutter..."
            else:
                run_lbl = "running..."
            cr.show_text(run_lbl)
        elif is_success:
            cr.arc(stat_x, header_y - 3.5, 4.0, 0, 2 * math.pi)
            cr.set_source_rgba(0.0, 1.0, 0.45, 0.95)
            cr.fill()
            cr.set_source_rgba(0.0, 1.0, 0.45, 0.95)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(9.5)
            cr.move_to(stat_x + 10.0, header_y)
            if morph == "morph-camera": stat_lbl = f"Captured ({duration_ms}ms)"
            elif morph == "morph-diff": stat_lbl = f"Applied ({duration_ms}ms)"
            elif morph == "morph-blueprint": stat_lbl = f"Written ({duration_ms}ms)"
            elif morph == "morph-laser": stat_lbl = f"Read ({duration_ms}ms)"
            elif morph == "morph-radar": stat_lbl = f"Found ({duration_ms}ms)"
            else: stat_lbl = f"Exit 0 ({duration_ms}ms)"
            cr.show_text(stat_lbl)
        else:
            cr.arc(stat_x, header_y - 3.5, 4.0, 0, 2 * math.pi)
            cr.set_source_rgba(1.0, 0.35, 0.35, 0.95)
            cr.fill()
            cr.set_source_rgba(1.0, 0.35, 0.35, 0.95)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(9.5)
            cr.move_to(stat_x + 10.0, header_y)
            cr.show_text(f"Exit {exit_code} ({duration_ms}ms)")

        # Divider Hairline
        cr.move_to(left_x, cy - 64.0)
        cr.line_to(left_x + box_w, cy - 64.0)
        cr.set_source_rgba(rim_col[0], rim_col[1], rim_col[2], 0.25)
        cr.set_line_width(1.0)
        cr.stroke()

        # 3. Sub-Header Line (cy - 42.0) — Concise Target / Goal (reason renders once in subtitle below ambient)
        cmd_y = cy - 42.0
        goal_txt = str(args.get("goal") or "").strip()
        reason_txt = str(n_state.get("reason") or args.get("reason") or "").strip()
        clean_cmd = command.strip()

        if goal_txt and goal_txt != reason_txt:
            disp_cmd = f"» {goal_txt}"
            cr.set_source_rgba(0.0, 1.0, 0.45, 0.98)
        elif clean_cmd:
            disp_cmd = f"$ {clean_cmd}"
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        else:
            disp_cmd = f"$ {tool_name}" if tool_name else "[ COGNITIVE CORE ]"
            cr.set_source_rgba(0.0, 0.85, 1.0, 0.95)

        if len(disp_cmd) > 42:
            disp_cmd = disp_cmd[:39] + "..."
        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(10.5)
        cr.move_to(left_x, cmd_y)
        cr.show_text(disp_cmd)

        # 4. Bespoke Empirical Lines by Tool
        log_start_y = cy - 16.0
        lh = 18.0

        if morph == "morph-camera":
            cam_target = args.get("TargetFile") or args.get("path") or "Screen Area"
            c_items = [
                ("Mode: Electronic Viewfinder (EVF)", (0.0, 0.95, 1.0)),
                ("Optics: [ ISO 100 ] [ 1/500s ] [ F/2.8 ]", (0.75, 0.85, 0.92)),
                (f"Target: {os.path.basename(str(cam_target))[:34]}", (0.85, 0.92, 0.96)),
                ("Shutter: Mechanical Strobe Actuated", (0.0, 1.0, 0.45)),
            ]
            for idx, (txt, col) in enumerate(c_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-diff":
            instr = args.get("Instruction") or args.get("reason") or "Surgical edit"
            target_raw = str(args.get("TargetContent") or "").strip()
            repl_raw = str(args.get("ReplacementContent") or "").strip()
            start_l = args.get("StartLine", 1)
            end_l = args.get("EndLine", 1)

            t_lines = [l.strip() for l in target_raw.splitlines() if l.strip()][:2]
            r_lines = [l.strip() for l in repl_raw.splitlines() if l.strip()][:2]

            diff_items = []
            diff_items.append((f"Instruction: {instr[:36]}", (0.75, 0.85, 0.92)))
            for tl in t_lines:
                diff_items.append((f"[-] {tl[:38]}", (1.0, 0.40, 0.40)))
            for rl in r_lines:
                diff_items.append((f"[+] {rl[:38]}", (0.0, 1.0, 0.45)))
            diff_items.append((f"Lines {start_l}-{end_l} applied atomically", (0.55, 0.75, 0.85)))

            for idx, (txt, col) in enumerate(diff_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-blueprint":
            t_file = args.get("TargetFile") or "file.txt"
            code_c = str(args.get("CodeContent") or "").strip()
            desc = args.get("Description") or "Atomic write"
            c_lines = [l.strip() for l in code_c.splitlines() if l.strip()][:4]

            b_items = [(f"Path: {t_file[:38]}", (0.0, 0.90, 1.0))]
            for i, cl in enumerate(c_lines):
                b_items.append((f"{i+1:02d} │ {cl[:36]}", (0.85, 0.92, 0.96)))
            if not c_lines:
                b_items.append((f"Action: {desc[:38]}", (0.75, 0.85, 0.92)))

            for idx, (txt, col) in enumerate(b_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-laser":
            abs_p = args.get("AbsolutePath") or args.get("path") or ""
            start_l = args.get("StartLine", 1)
            end_l = args.get("EndLine", 25)
            l_items = [
                (f"File: {os.path.basename(abs_p)} [L:{start_l}-{end_l}]", (0.0, 0.90, 1.0)),
                (f"Range: Lines {start_l} to {end_l}", (0.75, 0.85, 0.92)),
            ]
            if logs:
                for log_line in logs[:3]:
                    l_items.append((str(log_line)[:40], (0.85, 0.92, 0.96)))
            else:
                l_items.append((f"Reading AST slice in memory...", (0.55, 0.75, 0.85)))

            for idx, (txt, col) in enumerate(l_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-radar":
            q_txt = args.get("query") or ""
            dom_txt = args.get("domain") or "Global Web Index"
            r_items = [
                (f"Query: \"{q_txt[:34]}\"", (0.0, 0.90, 1.0)),
                (f"Domain: {dom_txt[:34]}", (0.75, 0.85, 0.92)),
            ]
            if logs:
                for l in logs[:3]: r_items.append((str(l)[:40], (0.85, 0.92, 0.96)))
            else:
                r_items.append(("Searching upstream technical docs...", (0.55, 0.75, 0.85)))

            for idx, (txt, col) in enumerate(r_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-conduit":
            u_txt = args.get("Url") or args.get("url") or ""
            c_items = [
                (f"Target: {u_txt[:38]}", (0.0, 0.90, 1.0)),
                (f"Protocol: HTTP/1.1 • Mode: Markdown", (0.75, 0.85, 0.92)),
            ]
            if logs:
                for l in logs[:3]: c_items.append((str(l)[:40], (0.85, 0.92, 0.96)))
            else:
                c_items.append(("Fetching static document payload...", (0.55, 0.75, 0.85)))

            for idx, (txt, col) in enumerate(c_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-swarm":
            sub_arr = args.get("Subagents") or []
            if sub_arr:
                first_sub = sub_arr[0]
                role = first_sub.get("Role") or "Worker"
                t_name = first_sub.get("TypeName") or "research"
                model = first_sub.get("Model") or "inherit"
                p_snippet = first_sub.get("Prompt") or ""
                s_items = [
                    (f"Role: {role[:36]}", (0.0, 1.0, 0.55)),
                    (f"Type: {t_name} • Model: {model}", (0.75, 0.85, 0.92)),
                    (f"Objective: \"{p_snippet[:34]}...\"", (0.85, 0.92, 0.96)),
                    (f"Topology: Swarm Worker Dispatched", (0.55, 0.75, 0.85))
                ]
            else:
                act = args.get("Action") or "list"
                s_items = [
                    (f"Swarm Action: {act.upper()}", (0.0, 1.0, 0.55)),
                    (f"Monitoring active worker lifecycles", (0.75, 0.85, 0.92))
                ]
                if logs:
                    for l in logs[:3]: s_items.append((str(l)[:40], (0.85, 0.92, 0.96)))

            for idx, (txt, col) in enumerate(s_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-pipeline":
            tid = args.get("TaskId") or "active-task"
            act = args.get("Action") or "status"
            pipe_items = [
                (f"Task ID: {str(tid)[:32]}", (0.0, 0.95, 1.0)),
                (f"Pipeline Action: {act.upper()}", (0.75, 0.85, 0.92)),
                ("Status: POSIX Async Subprocess", (0.0, 1.0, 0.45)),
                ("Channel: Non-blocking IPC Pipe", (0.55, 0.75, 0.85)),
            ]
            for idx, (txt, col) in enumerate(pipe_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-chronometer":
            dur = args.get("DurationSeconds")
            cron = args.get("CronExpression")
            prompt_snip = args.get("Prompt") or ""
            max_it = args.get("MaxIterations") or "Unlimited"
            ch_items = [
                (f"Schedule: {dur}s Timer" if dur else f"Cron: {cron}", (0.0, 1.0, 0.45)),
                (f"Prompt: \"{prompt_snip[:36]}...\"", (0.85, 0.92, 0.96)),
                (f"Iterations: {max_it} • Daemon: Active", (0.75, 0.85, 0.92))
            ]
            for idx, (txt, col) in enumerate(ch_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-signal":
            rec = args.get("Recipient") or "Subagent"
            msg = args.get("Message") or ""
            sig_items = [
                (f"Route: Parent ──► {rec[:24]}", (0.0, 0.95, 1.0)),
                (f"Message: \"{msg[:36]}...\"", (0.85, 0.92, 0.96)),
                (f"Bus: UNIX IPC Socket Channel", (0.75, 0.85, 0.92))
            ]
            for idx, (txt, col) in enumerate(sig_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-query":
            q_arr = args.get("questions") or []
            if q_arr:
                q_text = q_arr[0].get("question") or "User decision"
                opts = q_arr[0].get("options") or ["Yes", "No"]
                qu_items = [
                    (f"Question: \"{q_text[:34]}...\"", (0.0, 1.0, 0.70)),
                    (f"[1] {str(opts[0])[:34]}", (0.85, 0.92, 0.96)),
                ]
                if len(opts) > 1:
                    qu_items.append((f"[2] {str(opts[1])[:34]}", (0.85, 0.92, 0.96)))
                qu_items.append(("Status: Awaiting user selection", (0.55, 0.75, 0.85)))
            else:
                qu_items = [("Awaiting user confirmation...", (0.0, 1.0, 0.70))]

            for idx, (txt, col) in enumerate(qu_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-canvas":
            img_n = args.get("ImageName") or "asset"
            ratio = args.get("AspectRatio") or "1:1"
            p_img = args.get("Prompt") or ""
            cv_items = [
                (f"Asset: {img_n[:34]}.png", (0.0, 0.85, 1.0)),
                (f"Aspect Ratio: {ratio}", (0.75, 0.85, 0.92)),
                (f"Prompt: \"{p_img[:34]}...\"", (0.85, 0.92, 0.96)),
                (f"Renderer: Optical Generative Canvas", (0.55, 0.75, 0.85))
            ]
            for idx, (txt, col) in enumerate(cv_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-foundry":
            a_name = args.get("name") or "worker"
            desc_a = args.get("description") or "Specialized worker"
            fd_items = [
                (f"Agent Name: {a_name}", (0.0, 1.0, 0.45)),
                (f"Role: \"{desc_a[:36]}...\"", (0.85, 0.92, 0.96)),
                (f"Capabilities: Read, Write, Subagent Swarm", (0.75, 0.85, 0.92))
            ]
            for idx, (txt, col) in enumerate(fd_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-thinking" or state == "thinking":
            th_dots = int(t * 3.5) % 4
            dot_str = "." * th_dots
            act_label = n_state.get("action") or "Synthesizing strategic execution path"
            th_items = [
                (f"Process: Cognitive Deliberation{dot_str}", (0.0, 1.0, 0.45)),
                (f"Focus: {act_label[:34]}", (0.85, 0.92, 0.96)),
                ("Synapses: Neural Core Active", (0.0, 0.95, 1.0)),
                ("Synthesis: Assembling AST & Invariants", (0.75, 0.85, 0.92)),
                ("State: Formulating execution plan", (0.55, 0.75, 0.85))
            ]
            for idx, (txt, col) in enumerate(th_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-compacting" or state == "compacting":
            cp_dots = int(t * 3.5) % 4
            dot_str = "." * cp_dots
            act_label = n_state.get("action") or "Compacting conversation context into state snapshot"
            cp_items = [
                (f"Process: Neural Defragmentation{dot_str}", (0.0, 1.0, 0.45)),
                (f"Focus: {act_label[:34]}", (0.85, 0.92, 0.96)),
                ("Synapses: Compressing conversation history", (0.0, 0.95, 1.0)),
                ("Archival: Full lossless JSONL ledger committed", (0.75, 0.85, 0.92)),
                ("Reactor: Restoring autonomous execution loop", (0.55, 0.75, 0.85))
            ]
            for idx, (txt, col) in enumerate(cp_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        elif morph == "morph-deliberation" or state == "deliberation" or status == "deliberating":
            delib_phase = int(t * 3.0) % 4
            p_str = "." * delib_phase
            last_t = tool_name or "tool"
            dl_items = [
                (f"Transition: Evaluating tool output{p_str}", (0.0, 1.0, 0.45)),
                (f"Completed: {last_t} (Exit {exit_code})", (0.0, 0.95, 1.0)),
                ("Synapse: Processing stream feedback", (0.85, 0.92, 0.96)),
                ("Next Action: Formulating follow-up step", (0.75, 0.85, 0.92)),
                ("Reactor: Ready for subsequent cycle", (0.55, 0.75, 0.85))
            ]
            for idx, (txt, col) in enumerate(dl_items[:5]):
                cr.set_source_rgba(col[0], col[1], col[2], 0.95)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                cr.move_to(left_x, log_start_y + idx * lh)
                cr.show_text(txt)

        else:
            logs_to_show = logs[-6:] if logs else []
            if not logs_to_show and status in ("running", "deliberating"):
                cr.set_source_rgba(0.55, 0.75, 0.85, 0.80)
                cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(9.0)
                if clean_cmd:
                    cr.move_to(left_x, log_start_y)
                    cr.set_source_rgba(0.0, 0.85, 1.0, 0.95)
                    cr.show_text(f"Exec: {clean_cmd[:36]}")
                    cr.move_to(left_x, log_start_y + lh)
                    cr.set_source_rgba(0.55, 0.75, 0.85, 0.65)
                    cr.show_text("Awaiting process I/O stream...")
                else:
                    cr.move_to(left_x, log_start_y + 12.0)
                    cr.show_text("Awaiting process I/O stream...")
            else:
                for l_idx, line_raw in enumerate(logs_to_show):
                    cur_y = log_start_y + (l_idx * lh)
                    line_str = str(line_raw or "").strip()
                    if not line_str:
                        continue

                    if "exit 0" in line_str.lower() or "exit code: 0" in line_str.lower():
                        cr.set_source_rgba(0.0, 1.0, 0.45, 0.95)
                        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    elif "error" in line_str.lower() or "fail" in line_str.lower():
                        cr.set_source_rgba(1.0, 0.40, 0.40, 0.95)
                        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    else:
                        cr.set_source_rgba(0.85, 0.92, 0.96, 0.85)
                        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

                    cr.set_font_size(9.0)
                    cr.move_to(left_x, cur_y)
                    trunc_txt = line_str if len(line_str) <= 44 else line_str[:41] + "..."
                    cr.show_text(trunc_txt)

        cr.restore()

    def render_reason_subtitle(self, cr):
        """
        Renders Mr. Flow's active tool `reason` once as pure, frameless,
        shadowless, colorful floating text below the Central Living Tool Core
        on the desktop layer (always behind open applications).
        """
        if not self.subtitle_reason or self.subtitle_alpha <= 0.01:
            return

        alpha = max(0.0, min(1.0, self.subtitle_alpha))
        ui_scale = self.get_ui_scale()
        cx = float(self.screen_w) * 0.5
        cy = float(self.screen_h) * 0.50
        # Position subtitle safely in the open visual corridor below Node 05 (cy + 295 + 44 = cy + 339)
        # and above the bottom Conduit command bar (screen_h - 96). Zero overlap guaranteed.
        node05_bottom = cy + 348.0 * ui_scale
        conduit_top = float(self.screen_h) - 96.0 * ui_scale
        if conduit_top > node05_bottom + 36.0:
            sub_center_y = (node05_bottom + conduit_top) * 0.5
        else:
            sub_center_y = max(node05_bottom + 16.0, float(self.screen_h) - 62.0 * ui_scale)

        cr.save()
        cr.select_font_face("JetBrains Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        font_size = max(12.5, 19.5 * ui_scale)
        cr.set_font_size(font_size)

        max_text_w = min(1080.0 * ui_scale, float(self.screen_w) * 0.86)
        words = self.subtitle_reason.split()
        lines = []
        cur_line = ""
        for w in words:
            cand = f"{cur_line} {w}".strip() if cur_line else w
            ext = cr.text_extents(cand)
            if ext.width <= max_text_w or not cur_line:
                cur_line = cand
            else:
                lines.append(cur_line)
                cur_line = w
                if len(lines) >= 2:
                    break
        if cur_line and len(lines) < 2:
            lines.append(cur_line)
        elif cur_line and len(lines) == 2:
            # Truncate second line cleanly if overflowed
            last = lines[1]
            while len(last) > 4 and cr.text_extents(last + "...").width > max_text_w:
                last = last[:-1].rstrip()
            lines[1] = last + "..."

        if not lines:
            cr.restore()
            return

        line_h = max(18.0, 28.0 * ui_scale)
        total_h = len(lines) * line_h
        first_baseline_y = sub_center_y - total_h * 0.5 + font_size * 0.82

        acc = self.theme_accent_rgb
        sec = self.theme_secondary_rgb
        stops = [
            (0.00, (min(1.0, acc[0] * 0.75 + 0.15), min(1.0, acc[1] * 0.75 + 0.25), min(1.0, acc[2] * 0.75 + 0.15))),
            (0.18, (0.00, 0.96, 1.00)),
            (0.36, (0.42, 0.70, 1.00)),
            (0.54, (0.80, 0.46, 1.00)),
            (0.72, (1.00, 0.34, 0.70)),
            (0.88, (1.00, 0.84, 0.34)),
            (1.00, (min(1.0, sec[0] * 0.75 + 0.15), min(1.0, sec[1] * 0.75 + 0.25), min(1.0, sec[2] * 0.75 + 0.15))),
        ]

        for idx, ln in enumerate(lines):
            ext = cr.text_extents(ln)
            tx = cx - ext.width * 0.5 - ext.x_bearing
            ty = first_baseline_y + idx * line_h
            span_w = max(ext.width, 180.0)

            text_grad = cairo.LinearGradient(tx, ty, tx + span_w, ty)
            for pos, col in stops:
                text_grad.add_color_stop_rgba(pos, col[0], col[1], col[2], 0.98 * alpha)

            cr.set_source(text_grad)
            cr.move_to(tx, ty)
            cr.show_text(ln)

        cr.restore()

    def on_draw(self, widget, cr):
        # 1. Base Layer: Custom Wallpaper or Procedural Fluid Background
        if self.wallpaper_surface is not None:
            cr.save()
            cr.set_source_surface(self.wallpaper_surface, 0, 0)
            cr.paint()

            # Delicate ambient atmospheric tint over wallpaper (~18% alpha)
            # Keeps wallpaper crisp while letting soft organic plasma breathe over it
            if self.surface_buf is not None:
                scale_x = float(self.screen_w) / float(self.buf_w)
                scale_y = float(self.screen_h) / float(self.buf_h)
                cr.scale(scale_x, scale_y)
                cr.set_source_surface(self.surface_buf, 0, 0)
                cr.get_source().set_filter(cairo.FILTER_BILINEAR)
                cr.paint_with_alpha(0.18)
            cr.restore()
        else:
            # Fallback procedural fluid background from low-res buffer
            scale_x = float(self.screen_w) / float(self.buf_w)
            scale_y = float(self.screen_h) / float(self.buf_h)

            cr.save()
            cr.scale(scale_x, scale_y)
            cr.set_source_surface(self.surface_buf, 0, 0)
            cr.get_source().set_filter(cairo.FILTER_BILINEAR)
            cr.paint()
            cr.restore()

        # 2. Crisp 1:1 Retina Vector Arc Reactor (Oceanic Core, 0% Blur, ~0.24ms render)
        style_type = self.style_data.get("style", "oceanic")
        if style_type == "oceanic":
            ui_scale = self.get_ui_scale()
            cx = float(self.screen_w) * 0.5
            cy = float(self.screen_h) * 0.5
            half_core = float(self.core_size) * 0.5
            cr.save()
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.translate(cx, cy)
            if abs(ui_scale - 1.0) > 0.001:
                cr.scale(ui_scale, ui_scale)
            cr.set_source_surface(self.surface_core, -half_core, -half_core)
            cr.get_source().set_filter(cairo.FILTER_BILINEAR)
            cr.paint()
            cr.restore()

        # 3. Render Empirical Living Tool Core directly into desktop center
        self.render_empirical_tool_core(cr)

        # 4. Render single-slot Reason Subtitle below ambient core (behind open apps)
        self.render_reason_subtitle(cr)
        return True

    def get_ui_scale(self):
        return max(0.50, min(1.15, min(float(self.screen_w) / 1920.0, float(self.screen_h) / 1080.0)))

    def on_screen_resized(self, *args):
        screen = self.get_screen()
        nw = max(320, screen.get_width())
        nh = max(240, screen.get_height())
        if nw == self.screen_w and nh == self.screen_h:
            return
        self.screen_w = nw
        self.screen_h = nh
        self.resize(self.screen_w, self.screen_h)
        self.move(0, 0)
        self.buf_w = 640
        self.buf_h = max(180, int(640 * self.screen_h / max(1, self.screen_w)))
        self.surface_buf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.buf_w, self.buf_h)
        self.surface_static_bg = None
        self.last_bg_key = None
        self.wallpaper_surface = None
        self.load_active_wallpaper()
        self.queue_draw()

def main():
    if "--stop" in sys.argv or "-k" in sys.argv:
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                os.remove(PID_FILE)
                print("✅ Flowork Living Motion Wallpaper stopped.")
            except Exception as e:
                print(f"Notice: {e}")
        return

    if "--status" in sys.argv:
        cfg = load_motion_config()
        is_running = False
        pid = None
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                is_running = True
            except OSError:
                pass
        print(json.dumps({
            "running": is_running,
            "pid": pid,
            "config": cfg,
            "available_styles": list(MOTION_STYLES.keys())
        }, indent=2))
        return

    for i, a in enumerate(sys.argv):
        if a in ("--style", "-s") and i + 1 < len(sys.argv):
            target_style = sys.argv[i + 1]
            if target_style in MOTION_STYLES or target_style == "auto":
                cfg = load_motion_config()
                cfg["style"] = target_style
                save_motion_config(cfg)
                print(f"✅ Motion style configured to: {target_style}")
                return
            else:
                print(f"❌ Unknown style '{target_style}'. Available: {list(MOTION_STYLES.keys())}")
                return

    if "--toggle" in sys.argv:
        cfg = load_motion_config()
        new_state = not cfg.get("enabled", True)
        cfg["enabled"] = new_state
        save_motion_config(cfg)
        if not new_state:
            if os.path.exists(PID_FILE):
                try:
                    with open(PID_FILE, "r") as f:
                        old_pid = int(f.read().strip())
                    os.kill(old_pid, signal.SIGTERM)
                    os.remove(PID_FILE)
                except OSError:
                    pass
            print("✅ Flowork Living Motion Wallpaper toggled OFF.")
            return
        else:
            print("✅ Flowork Living Motion Wallpaper toggled ON. Launching daemon...")

    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(f"Flowork Motion Wallpaper already running (PID {old_pid}).")
            return
        except OSError:
            pass

    # Save PID
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    print("⚡ Flowork Living Motion Wallpaper running (Ultra-Soft Mode 3.0)...")
    app = FloworkMotionAmbient()
    app.show_all()

    def handle_signal(sig, frame):
        try:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except Exception:
            pass
        Gtk.main_quit()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    Gtk.main()

if __name__ == "__main__":
    main()
