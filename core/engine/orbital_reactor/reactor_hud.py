#!/usr/bin/env python3
# ==============================================================================
# 🔮 FLOWORK OS — UNIFIED SOVEREIGN REACTOR HUD
# Concentric Architecture centered pixel-perfectly on the Living Core:
#   1. Center Core (0..78px): F-CLEANER (Headless RAM/Cache/Trash/Journal Purge)
#   2. Radial Irisan Ring (84..180px): 6 Modular Sectors + Targeted Bloom Cards
#   3. Living Core Ring (~210..220px): flowork-motion-ambient.py
#   4. Outer Orbital Ring (295px, nodes 251..339px): 8 Orbital Tool Nodes
#      - Node 01 (12 o'clock): VOCAL (Headless Vocal Focus Mastering)
#      - Node 02 (1:30 o'clock): STEM SPLIT (Native Vocal & Music Split)
#      - Nodes 03-08: Reserved orbital slots
# ==============================================================================

import json
import math
import os
import queue
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
from pathlib import Path

# Disable Ubuntu Apport crash interception to prevent file descriptor leaks
sys.excepthook = sys.__excepthook__

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango, PangoCairo  # noqa: E402

sys.path.insert(0, "/opt/floworkos/engine/vocal_master")
sys.path.insert(0, "/opt/floworkos/engine/stem_split")
sys.path.insert(0, "/opt/floworkos/engine/suno_59s")
sys.path.insert(0, "/opt/floworkos/engine/auto_lyric")
sys.path.insert(0, "/opt/floworkos/engine/title_generator")
sys.path.insert(0, "/opt/floworkos/engine/bg_remove")
sys.path.insert(0, "/opt/floworkos/engine/suno_cover")
from title_generator import generate_title_bundle, export_bundle_to_file, clean_song_name  # noqa: E402
sys.path.insert(0, "/opt/floworkos/engine/renderer_4k")
from renderer_4k import (  # noqa: E402
    render_4k_bundle,
    probe_audio_info,
    probe_image_info,
    format_duration,
    detect_best_encoder,
)
from bg_remove import (  # noqa: E402
    SUPPORTED_IMAGE_EXTS,
    get_pictures_dir,
    open_pictures_dir,
    remove_background_image,
)
from suno_cover import generate_suno_cover  # noqa: E402
from stem_split import separate_vocal_and_music  # noqa: E402
from suno_59s import render_suno_59s  # noqa: E402
from vocal_focus import (  # noqa: E402
    SUPPORTED_AUDIO_EXTS,
    get_music_dir,
    master_vocal_focus,
    open_music_dir,
)
import financial_orbit  # noqa: E402

CACHE_TECH_TOPICS = "/opt/floworkos/cache/last30days_widget.json"
CACHE_TREND_REPOS = "/opt/floworkos/cache/trending_repos.json"

# Palette Murni & Fungsional
C_CYAN = (0.00, 0.95, 1.00)
C_GREEN = (0.00, 1.00, 0.40)
C_AMBER = (1.00, 0.72, 0.10)
C_RED = (1.00, 0.35, 0.35)
C_MINT = (0.00, 0.96, 0.63)
C_GOLD = (1.00, 0.82, 0.10)
C_WHITE = (1.00, 1.00, 1.00)
C_MUTED = (0.65, 0.78, 0.88)
C_DARK = (0.01, 0.03, 0.07)


def draw_rounded_rect(cr, x, y, w, h, r):
    cr.new_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


class UnifiedReactorHudWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Flowork Orbital Reactor HUD")

        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_keep_below(True)
        self.stick()
        self.set_wmclass("flowork-center-reactor-hud", "flowork-center-reactor-hud")

        # Concentric geometry (dynamically scaled & pixel-centered on screen)
        self.ui_scale = 1.0
        self.width = 1660
        self.height = 816
        self.pos_x = 450
        self.pos_y = 132
        self.cx = 830.0
        self.cy = 408.0
        self.r_core = 78.0
        self.r_in = 84.0
        self.r_out = 180.0
        self.r_node = 44.0
        self.r_orbit_idle = self.r_out + self.r_node - 2.0
        self.r_orbit_expanded = 315.0
        self.r_orbit = self.r_orbit_idle
        self.target_r_orbit = self.r_orbit_idle
        self.is_chat_mode = False
        self.was_floating = False
        self.spin_angle = 0.0
        self.spin_velocity = 0.0

        # Inner Irisan & F-Cleaner animation state
        self.progress = 0.0
        self.target_progress = 0.0
        self.rot_angle = 0.0
        self.phase = 0.0

        self.active_sector = None
        self.cluster_progress = 0.0
        self.hovered_sector = None
        self.hovered_card = None
        self.hovered_core = False
        self.hovered_cleaner = False
        self.cleaner_running = False
        self.cleaner_status_text = ""
        self.cleaner_status_until = 0.0
        self.card_hitboxes = []
        self.last_click_time = 0.0

        # Outer 8 Orbital Nodes state
        self.hovered_node = None
        self.drag_hover_node = None
        self.nodes = [
            {
                "id": "vocal_master",
                "slot": "01",
                "angle_deg": -90.0,
                "title": "VOCAL",
                "sub": "DROP WAV",
                "drop_pill": "DROP TO MASTER",
                "picker_title": "Select Audio File for Vocal Focus Mastering",
                "active": True,
                "accent_rgb": (0.00, 0.95, 1.00),    # Electric Cyan
                "bg_inner_rgb": (0.01, 0.16, 0.24),
                "bg_outer_rgb": (0.01, 0.04, 0.09),
            },
            {
                "id": "stem_split",
                "slot": "02",
                "angle_deg": -45.0,
                "title": "STEM SPLIT",
                "sub": "DROP WAV",
                "drop_pill": "DROP TO SPLIT",
                "picker_title": "Select Audio File for Vocal & Music Split",
                "active": True,
                "accent_rgb": (0.78, 0.38, 1.00),    # Radiant Ultra Violet
                "bg_inner_rgb": (0.18, 0.05, 0.26),
                "bg_outer_rgb": (0.06, 0.01, 0.11),
            },
            {
                "id": "suno_59s",
                "slot": "03",
                "angle_deg": 0.0,
                "title": "SUNO 59S",
                "sub": "DROP AUDIO",
                "drop_pill": "DROP TO 59S",
                "done_pill": "SAVED 59S MP3",
                "picker_title": "Select Audio File(s) for 59s Suno Speed-Up",
                "active": True,
                "accent_rgb": (1.00, 0.25, 0.65),    # Neon Hot Pink / Magenta
                "bg_inner_rgb": (0.24, 0.03, 0.14),
                "bg_outer_rgb": (0.08, 0.01, 0.05),
            },
            {
                "id": "title_generator",
                "slot": "04",
                "angle_deg": 45.0,
                "title": "TITLE GEN",
                "sub": "VIRAL DRACHIN",
                "drop_pill": "CLICK / DROP",
                "done_pill": "TITLES READY",
                "picker_title": "Pilih Audio atau File untuk Generate Judul Viral",
                "media_type": "all",
                "active": True,
                "accent_rgb": (1.00, 0.60, 0.10),    # Solar Amber / Orange
                "bg_inner_rgb": (0.24, 0.10, 0.01),
                "bg_outer_rgb": (0.08, 0.04, 0.01),
            },
            {
                "id": "bg_remove",
                "slot": "05",
                "angle_deg": 90.0,
                "title": "BG REMOVE",
                "sub": "DROP IMG",
                "drop_pill": "DROP TO CUTOUT",
                "done_pill": "SAVED TO PICS",
                "picker_title": "Select Image(s) for Background Removal",
                "media_type": "image",
                "active": True,
                "accent_rgb": (0.10, 0.96, 0.46),    # Matrix Emerald Lime
                "bg_inner_rgb": (0.02, 0.20, 0.10),
                "bg_outer_rgb": (0.01, 0.07, 0.03),
            },
            {
                "id": "suno_cover",
                "slot": "06",
                "angle_deg": 135.0,
                "title": "SUNO COVER",
                "sub": "DROP 2 IMG",
                "drop_pill": "DROP 2 IMAGES",
                "done_pill": "SAVED TO PICS",
                "picker_title": "Suno Cover Studio",
                "media_type": "image",
                "active": True,
                "accent_rgb": (0.20, 0.58, 1.00),    # Royal Azure Blue
                "bg_inner_rgb": (0.03, 0.10, 0.26),
                "bg_outer_rgb": (0.01, 0.03, 0.11),
            },
            {
                "id": "renderer_4k",
                "slot": "07",
                "angle_deg": 180.0,
                "title": "4K RENDER",
                "sub": "AUDIO + IMG",
                "drop_pill": "DROP AUDIO/IMG",
                "done_pill": "4K READY",
                "picker_title": "4K UHD Audio-Visual Studio",
                "media_type": "all",
                "active": True,
                "accent_rgb": (1.00, 0.32, 0.32),    # Crimson Coral Ruby
                "bg_inner_rgb": (0.25, 0.04, 0.05),
                "bg_outer_rgb": (0.09, 0.01, 0.02),
            },
            {
                "id": "file_manager",
                "slot": "08",
                "angle_deg": -135.0,
                "title": "FILES",
                "sub": "FILE MANAGER",
                "drop_pill": "OPEN IN NEMO",
                "done_pill": "FILES OPEN",
                "picker_title": "Buka File Manager",
                "media_type": "all",
                "active": True,
                "accent_rgb": (1.00, 0.86, 0.16),    # Golden Topaz Gold
                "bg_inner_rgb": (0.22, 0.16, 0.02),
                "bg_outer_rgb": (0.08, 0.06, 0.01),
            },
        ]
        self.suno_cover_pending_left = None

        self.node_states = {}
        for node in self.nodes:
            if node["active"]:
                self.node_states[node["id"]] = {
                    "state": "idle",
                    "progress": 0.0,
                    "display_progress": 0.0,
                    "stage": node.get("sub", "DROP WAV"),
                    "batch_label": "",
                    "reset_timer_id": None,
                    "job_queue": queue.Queue(),
                    "worker_lock": threading.Lock(),
                    "worker_running": False,
                }

        # App catalogs & trending feeds for 6-sector Irisan Menu
        self.fxcalc_apps = []
        self.internet_apps = []
        self.media_apps = []
        self.sistem_apps = []
        self.oracle_apps = []
        self.trending_items = []
        self._load_app_catalogs()
        self._load_cached_data()

        # RGBA visual
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.SCROLL_MASK
        )

        targets = [
            Gtk.TargetEntry.new("text/uri-list", 0, 0),
            Gtk.TargetEntry.new("text/plain", 0, 1),
        ]
        self.drag_dest_set(Gtk.DestDefaults.DROP, targets, Gdk.DragAction.COPY)

        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("leave-notify-event", self.on_leave)
        self.connect("button-press-event", self.on_button_press)
        self.connect("scroll-event", self.on_scroll_event)
        self.connect("drag-motion", self.on_drag_motion)
        self.connect("drag-leave", self.on_drag_leave)
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("realize", self.on_realize)
        screen.connect("size-changed", lambda *_: self.update_geometry())
        screen.connect("monitors-changed", lambda *_: self.update_geometry())

        self.update_geometry()
        threading.Thread(target=self._bg_refresh_loop, daemon=True).start()
        GLib.timeout_add(33, self._tick)

    def on_realize(self, *_args):
        self.update_geometry()
        self._update_input_shape()

    def update_geometry(self):
        screen = self.get_screen()
        sw = max(640, screen.get_width())
        sh = max(480, screen.get_height())

        # Match flowork-motion-ambient.py scale & exact screen center (sw/2, sh/2)
        self.ui_scale = max(0.52, min(1.0, min(float(sw) / 1920.0, float(sh) / 1080.0)))
        self.r_core = 78.0 * self.ui_scale
        self.r_in = 84.0 * self.ui_scale
        self.r_out = 180.0 * self.ui_scale
        self.r_node = 44.0 * self.ui_scale
        self.r_orbit_idle = (self.r_out + self.r_node - 2.0 * self.ui_scale)
        self.r_orbit_expanded = 315.0 * self.ui_scale
        if getattr(self, "is_chat_mode", False):
            self.target_r_orbit = self.r_orbit_expanded
        else:
            self.target_r_orbit = self.r_orbit_idle
        self.r_orbit = self.target_r_orbit

        # Keep pos_y >= 132 so it never collides with the top sub-search digital clock (y=44..128)
        # Cap width to avoid overlapping edge desktop widgets (Tarot at x=2322)
        self.width = min(1660, max(640, sw - 120))
        self.height = min(816, max(400, sh - 140))
        self.pos_x = max(0, (sw - self.width) // 2)
        self.pos_y = max(132, int((sh - self.height) // 2))

        # Exact screen center mapped into window-local coordinates
        self.cx = (sw / 2.0) - self.pos_x
        self.cy = (sh / 2.0) - self.pos_y

        self.set_size_request(self.width, self.height)
        self.resize(self.width, self.height)
        self.move(self.pos_x, self.pos_y)
        self._update_input_shape()
        self.queue_draw()

    def _load_app_catalogs(self):
        self.fxcalc_apps = [
            {"name": "FX Position Calculator", "cmd": "/opt/floworkos/bin/flowork-fxcalc", "meta": "Forex Risk & Lot Size Engine", "badge": "CALC"},
            {"name": "Visual Studio Code", "cmd": "/usr/share/code/code", "meta": "Code Editor & Workspace", "badge": "CODE"},
            {"name": "Alacritty Terminal", "cmd": "alacritty", "meta": "GPU Accelerated Terminal", "badge": "SHELL"},
        ]
        self.internet_apps = [
            {"name": "Google Chrome", "cmd": "/usr/local/bin/google-chrome", "meta": "Web Browser & DevTools", "badge": "CHROME"},
            {"name": "Flowork Stealth", "cmd": "/usr/local/bin/flowork-stealth gui", "meta": "Tor Privacy Browser", "badge": "TOR"},
            {"name": "Downflow Manager", "cmd": "/opt/floworkos/bin/downflow", "meta": "Multi-Thread Downloader", "badge": "DOWN"},
            {"name": "Flowork Profile", "cmd": "/opt/floworkos/bin/flowork-profile", "meta": "Browser Profile Manager", "badge": "PROF"},
        ]
        self.media_apps = [
            {"name": "Blender 3D", "cmd": "blender", "meta": "3D Modeling & CGI Suite", "badge": "3D"},
            {"name": "Vocal Focus Master", "cmd": "/opt/floworkos/bin/flowork-vocal-master", "meta": "Headless -14 LUFS Vocal DSP", "badge": "VOCAL"},
            {"name": "Stem Split Separator", "cmd": "/opt/floworkos/bin/flowork-stem-split", "meta": "Vocal & Music Stem DSP", "badge": "STEM"},
        ]
        self.sistem_apps = [
            {"name": "File Manager (Nemo)", "cmd": "nemo", "meta": "File & NVMe Storage Access", "badge": "FILE"},
            {"name": "Flowork Settings", "cmd": "/usr/local/bin/flowork-settings", "meta": "OS Control & Preferences", "badge": "CONF"},
            {"name": "Flowork App Manager", "cmd": "/opt/floworkos/bin/flowork-app-manager", "meta": "External App Uninstaller", "badge": "APPS"},
            {"name": "Rollback RILIS V1.0", "cmd": "/opt/floworkos/bin/flowork-rollback --gui", "meta": "One-Click Git Reset & Force Push", "badge": "ROLL"},
        ]
        self.oracle_apps = [
            {"name": "Flowork Tarot Oracle", "cmd": "/opt/floworkos/bin/flowork-tarot-oracle", "meta": "Sovereign Oracle Engine", "badge": "ORACLE"},
        ]

    def _load_cached_data(self):
        items = []
        if os.path.exists(CACHE_TREND_REPOS):
            try:
                with open(CACHE_TREND_REPOS, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r in data.get("repos", [])[:2]:
                        stars = r.get("stars_today") or f"{r.get('stars', 0):,} ★"
                        items.append({
                            "name": r.get("name", ""),
                            "url": r.get("url", "https://github.com/trending"),
                            "meta": f"{r.get('language', 'Code')} • {stars}",
                            "badge": "REPO",
                        })
            except Exception:
                pass

        if os.path.exists(CACHE_TECH_TOPICS):
            try:
                with open(CACHE_TECH_TOPICS, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for t in data.get("topics", [])[:2]:
                        items.append({
                            "name": t.get("title", ""),
                            "url": t.get("url", "https://news.ycombinator.com"),
                            "meta": f"{t.get('source', 'Tech')} • {t.get('score', '')}",
                            "badge": "TECH",
                        })
            except Exception:
                pass

        if not items:
            items = [
                {"name": "GitHub Trending", "url": "https://github.com/trending", "meta": "Open Source Repositories", "badge": "REPO"},
                {"name": "Hacker News", "url": "https://news.ycombinator.com", "meta": "Tech & AI Discussions", "badge": "TECH"},
            ]
        self.trending_items = items

    def _bg_refresh_loop(self):
        while True:
            try:
                self._load_cached_data()
            except Exception:
                pass
            time.sleep(30.0)

    def _node_center(self, idx: int) -> tuple[float, float]:
        rad = math.radians(self.nodes[idx]["angle_deg"] + self.spin_angle)
        return (
            self.cx + self.r_orbit * math.cos(rad),
            self.cy + self.r_orbit * math.sin(rad),
        )

    def _update_input_shape(self):
        """Capture events ONLY on the 8 orbital nodes, center core/irisan, and active bloom cards."""
        win = self.get_window()
        if not win:
            return

        sw = max(640, self.get_allocated_width())
        sh = max(480, self.get_allocated_height())
        surface = cairo.ImageSurface(cairo.FORMAT_A1, sw, sh)
        cr = cairo.Context(surface)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(1, 1, 1, 1)

        # 1. Always capture the 8 orbital nodes
        hit_r = self.r_node + 10.0 * self.ui_scale
        for idx in range(len(self.nodes)):
            nx, ny = self._node_center(idx)
            cr.arc(nx, ny, hit_r, 0, 2.0 * math.pi)
            cr.fill()

        # 2. Center core and Irisan radial ring capture zone (only if center not occluded)
        if not self.is_center_covered():
            center_r = self.r_out + 12.0 * self.ui_scale
            cr.arc(self.cx, self.cy, center_r, 0, 2.0 * math.pi)
            cr.fill()

        # 3. Active Targeted Bloom Card cluster
        if self.active_sector is not None and self.cluster_progress > 0.05:
            for (x, y, w, h, _cid, _idx, _atype, _target) in self.card_hitboxes:
                cr.rectangle(int(x - 12), int(y - 36), int(w + 24), int(h + 48))
                cr.fill()

        region = Gdk.cairo_region_create_from_surface(surface)
        win.input_shape_combine_region(region, 0, 0)

    def _hit_test_node(self, x: float, y: float):
        hit_r2 = (self.r_node + 8.0 * self.ui_scale) ** 2
        for idx in range(len(self.nodes)):
            nx, ny = self._node_center(idx)
            dx = x - nx
            dy = y - ny
            if dx * dx + dy * dy <= hit_r2:
                return idx
        return None

    def is_center_covered(self):
        """Check if a normal application window covers the screen center."""
        try:
            screen = Gdk.Screen.get_default()
            if not screen:
                return False
            stack = screen.get_window_stack()
            if not stack:
                return False
            my_win = self.get_window()
            my_xid = my_win.get_xid() if my_win else 0
            cx_abs = int(self.pos_x + self.cx)
            cy_abs = int(self.pos_y + self.cy)

            for w in reversed(stack):
                xid = w.get_xid()
                if my_xid is not None and xid == my_xid:
                    break
                if not w.is_visible():
                    continue
                hint = w.get_type_hint()
                if hint in (Gdk.WindowTypeHint.DESKTOP, Gdk.WindowTypeHint.DOCK):
                    continue
                state = w.get_state()
                if state & (Gdk.WindowState.ICONIFIED | Gdk.WindowState.WITHDRAWN):
                    continue
                geom = w.get_geometry()
                # Skip maximized/fullscreen windows (allowing panel margin)
                if geom.width >= screen.get_width() - 80 and geom.height >= screen.get_height() - 80:
                    continue
                if geom.x <= cx_abs <= geom.x + geom.width and geom.y <= cy_abs <= geom.y + geom.height:
                    return True
            return False
        except Exception:
            return False

    def is_chat_active(self) -> bool:
        """Detect if Flowork Matrix Quantum Console or Mr Flow chat is active."""
        # 1. Check /dev/shm/flowork-neural-state.json (0ms RAM state)
        try:
            state_file = "/dev/shm/flowork-neural-state.json"
            if os.path.exists(state_file):
                mtime = os.path.getmtime(state_file)
                if time.time() - mtime < 3.5:
                    with open(state_file, "r") as f:
                        data = json.load(f)
                    status = data.get("status", "")
                    state = data.get("state", "")
                    if status in ("running", "busy", "active") or state in ("tool_use", "generating", "speaking", "thinking"):
                        return True
        except Exception:
            pass

        # 2. Check X11 window stack for Matrix Console
        try:
            screen = Gdk.Screen.get_default()
            if screen:
                stack = screen.get_window_stack()
                if stack:
                    for w in stack:
                        if not w.is_visible():
                            continue
                        state = w.get_state()
                        if state & (Gdk.WindowState.ICONIFIED | Gdk.WindowState.WITHDRAWN):
                            continue
                        geom = w.get_geometry()
                        if 900 <= geom.width <= 1600 and 400 <= geom.height <= 850:
                            cx_abs = int(self.pos_x + self.cx)
                            cy_abs = int(self.pos_y + self.cy)
                            if (geom.x <= cx_abs <= geom.x + geom.width and
                                geom.y <= cy_abs <= geom.y + geom.height):
                                return True
        except Exception:
            pass

        return False

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

    def _tick(self):
        self.phase = (self.phase + 0.035) % (2.0 * math.pi)
        self.rot_angle = (self.rot_angle + 0.008) % (2 * math.pi)
        needs_redraw = False
        if int(self.phase * 10) % 5 == 0:
            self._ensure_above_wallpaper()

        # 1. Check pointer position for center Irisan + F-Cleaner bloom
        try:
            display = Gdk.Display.get_default()
            seat = display.get_default_seat()
            pointer = seat.get_pointer()
            _scr, px, py = pointer.get_position()
            lx = px - self.pos_x
            ly = py - self.pos_y
            dx = lx - self.cx
            dy = ly - self.cy
            dist = math.sqrt(dx * dx + dy * dy)

            hit_node = self._hit_test_node(lx, ly)
            if self.is_center_covered():
                self.target_progress = 0.0
                self.active_sector = None
            else:
                if self.progress < 0.05 and self.active_sector is None:
                    if dist <= self.r_out + 6.0 * self.ui_scale and hit_node is None:
                        self.target_progress = 1.0
                    else:
                        self.target_progress = 0.0
                else:
                    in_ring = dist <= self.r_out + 20.0 * self.ui_scale and hit_node is None
                    in_card = False
                    if self.active_sector is not None:
                        for (x, y, w, h, _cid, _idx, _atype, _target) in self.card_hitboxes:
                            if x - 24 <= lx <= x + w + 24 and y - 40 <= ly <= y + h + 24:
                                in_card = True
                                break
                    if in_ring or in_card:
                        self.target_progress = 1.0
                    else:
                        self.target_progress = 0.0
                        self.active_sector = None
        except Exception:
            pass

        # Dynamic orbital radius animation (expands during chat/center occlusion, compact at idle)
        is_chatting = self.is_chat_active() or self.is_center_covered()
        is_floating = is_chatting or (self.r_orbit > (self.r_orbit_idle + 8.0))
        if is_floating and not self.was_floating:
            # Trigger high-speed initial spinner spin when nodes begin floating!
            self.spin_velocity = 28.0
        self.was_floating = is_floating
        self.is_chat_mode = is_chatting
        self.target_r_orbit = self.r_orbit_expanded if is_chatting else self.r_orbit_idle

        orbit_diff = self.target_r_orbit - self.r_orbit
        if abs(orbit_diff) > 0.4:
            self.r_orbit += orbit_diff * 0.14
            self._update_input_shape()
            needs_redraw = True
        elif abs(orbit_diff) > 0.01:
            self.r_orbit = self.target_r_orbit
            self._update_input_shape()
            needs_redraw = True

        # High-precision fidget spinner physics: fast initial spin, smooth progressive deceleration
        if abs(self.spin_velocity) > 0.05:
            self.spin_angle = (self.spin_angle + self.spin_velocity) % 360.0
            self.spin_velocity *= 0.94  # Progressive smooth friction damping
            self._update_input_shape()
            needs_redraw = True
        elif abs(self.spin_velocity) > 0.0:
            self.spin_velocity = 0.0
            needs_redraw = True

        # Settle gracefully back to 0 alignment when stopped
        if self.spin_velocity == 0.0 and self.spin_angle != 0.0:
            diff_ang = (self.spin_angle + 180.0) % 360.0 - 180.0
            if abs(diff_ang) > 0.4:
                self.spin_angle = (self.spin_angle - diff_ang * 0.14) % 360.0
                self._update_input_shape()
                needs_redraw = True
            else:
                self.spin_angle = 0.0
                self._update_input_shape()
                needs_redraw = True

        # 2. Smooth inner Irisan bloom interpolation
        diff = self.target_progress - self.progress
        if abs(diff) > 0.001:
            self.progress += diff * 0.18
            self._update_input_shape()
            needs_redraw = True
        elif self.progress < 0.005:
            if self.progress != 0.0:
                self.progress = 0.0
                self.active_sector = None
                self._update_input_shape()
                needs_redraw = True
        elif self.progress > 0.995:
            if self.progress != 1.0:
                self.progress = 1.0
                self._update_input_shape()
                needs_redraw = True

        # 3. Smooth Targeted Bloom Card cluster interpolation
        target_cluster = 1.0 if self.active_sector is not None else 0.0
        c_diff = target_cluster - self.cluster_progress
        if abs(c_diff) > 0.001:
            self.cluster_progress += c_diff * 0.22
            self._update_input_shape()
            needs_redraw = True
        elif target_cluster == 0.0 and self.cluster_progress != 0.0:
            self.cluster_progress = 0.0
            self._update_input_shape()
            needs_redraw = True

        if self.progress > 0.05:
            needs_redraw = True
        if self.cleaner_running:
            needs_redraw = True
        elif self.cleaner_status_text:
            if time.time() < self.cleaner_status_until:
                needs_redraw = True
            else:
                self.cleaner_status_text = ""
                needs_redraw = True

        # 4. Smooth orbital node progress interpolation
        for st in self.node_states.values():
            if st["state"] == "processing":
                ndiff = st["progress"] - st["display_progress"]
                if abs(ndiff) > 0.002:
                    st["display_progress"] += ndiff * 0.22
                else:
                    st["display_progress"] = st["progress"]
                needs_redraw = True
            elif st["state"] in ("done", "error"):
                needs_redraw = True

        if self.hovered_node is not None or self.drag_hover_node is not None:
            needs_redraw = True

        if needs_redraw:
            self.queue_draw()
        return True

    def on_motion(self, _widget, event):
        # 1. Check outer 8 orbital nodes first
        hit_node = self._hit_test_node(event.x, event.y)
        prev_node = self.hovered_node
        self.hovered_node = hit_node

        # 2. Check inner Irisan & F-Cleaner
        dx = event.x - self.cx
        dy = event.y - self.cy
        dist = math.sqrt(dx * dx + dy * dy)

        prev_hover_card = self.hovered_card
        prev_hover_sec = self.hovered_sector
        prev_hover_core = self.hovered_core
        prev_hover_cleaner = self.hovered_cleaner

        self.hovered_card = None
        self.hovered_sector = None
        self.hovered_core = False
        self.hovered_cleaner = False

        if hit_node is None and self.progress > 0.1:
            if self.active_sector is not None and self.cluster_progress > 0.3:
                for (x, y, w, h, cid, idx, _atype, _target) in self.card_hitboxes:
                    if x <= event.x <= x + w and y <= event.y <= y + h:
                        self.hovered_card = (cid, idx)
                        break

            if self.hovered_card is None:
                if dist <= self.r_core:
                    self.hovered_core = True
                    pill_w = 112.0 * self.ui_scale
                    pill_h = 24.0 * self.ui_scale
                    pill_x = self.cx - pill_w / 2.0
                    pill_y = self.cy + 8.0 * self.ui_scale
                    if pill_x <= event.x <= pill_x + pill_w and pill_y <= event.y <= pill_y + pill_h:
                        self.hovered_cleaner = True
                elif self.r_in <= dist <= self.r_out:
                    deg = math.degrees(math.atan2(dy, dx))
                    if deg < 0:
                        deg += 360.0
                    if 302 <= deg <= 358:
                        self.hovered_sector = "fxcalc"
                    elif 2 <= deg <= 58:
                        self.hovered_sector = "internet"
                    elif 62 <= deg <= 118:
                        self.hovered_sector = "media"
                    elif 122 <= deg <= 178:
                        self.hovered_sector = "shutdown"
                    elif 182 <= deg <= 238:
                        self.hovered_sector = "oracle"
                    elif 242 <= deg <= 298:
                        self.hovered_sector = "trending"

        if (
            prev_node != self.hovered_node
            or prev_hover_card != self.hovered_card
            or prev_hover_sec != self.hovered_sector
            or prev_hover_core != self.hovered_core
            or prev_hover_cleaner != self.hovered_cleaner
        ):
            win = self.get_window()
            if win:
                if (
                    (self.hovered_node is not None and self.nodes[self.hovered_node]["active"])
                    or self.hovered_card is not None
                    or self.hovered_sector is not None
                    or self.hovered_cleaner
                    or self.hovered_core
                ):
                    win.set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "pointer"))
                else:
                    win.set_cursor(None)
            self.queue_draw()
        return False

    def on_leave(self, _widget, _event):
        changed = (
            self.hovered_node is not None
            or self.hovered_card is not None
            or self.hovered_sector is not None
            or self.hovered_core
            or self.hovered_cleaner
        )
        self.hovered_node = None
        self.hovered_card = None
        self.hovered_sector = None
        self.hovered_core = False
        self.hovered_cleaner = False
        if changed:
            self.queue_draw()
        return False

    def on_scroll_event(self, _widget, event):
        # Allow interactive spinner flick via mouse wheel
        direction = 1.0 if event.direction in (Gdk.ScrollDirection.UP, Gdk.ScrollDirection.RIGHT) else -1.0
        self.spin_velocity += direction * 18.0
        self.spin_velocity = max(-45.0, min(45.0, self.spin_velocity))
        self.queue_draw()
        return True

    def on_drag_motion(self, _widget, context, x, y, time_ms):
        hit = self._hit_test_node(x, y)
        if hit is not None and self.nodes[hit]["active"]:
            if self.drag_hover_node != hit:
                self.drag_hover_node = hit
                self.queue_draw()
            Gdk.drag_status(context, Gdk.DragAction.COPY, time_ms)
            return True
        if self.drag_hover_node is not None:
            self.drag_hover_node = None
            self.queue_draw()
        Gdk.drag_status(context, 0, time_ms)
        return False

    def on_drag_leave(self, _widget, _context, _time_ms):
        if self.drag_hover_node is not None:
            self.drag_hover_node = None
            self.queue_draw()

    def on_drag_data_received(self, _widget, context, x, y, selection_data, _info, time_ms):
        hit = self._hit_test_node(x, y)
        if hit is None:
            hit = self.drag_hover_node
        self.drag_hover_node = None
        self.queue_draw()

        if hit is None or not self.nodes[hit]["active"]:
            context.finish(False, False, time_ms)
            return

        node = self.nodes[hit]
        node_id = node["id"]
        is_image_node = node.get("media_type") == "image"
        allowed_exts = SUPPORTED_IMAGE_EXTS if is_image_node else SUPPORTED_AUDIO_EXTS
        raw = selection_data.get_text() or ""
        if not raw:
            uris = selection_data.get_uris()
            raw = "\n".join(uris)

        paths = []
        for line in raw.splitlines():
            item = line.strip()
            if not item:
                continue
            if item.startswith("file://"):
                parsed = urllib.parse.urlparse(item)
                local_path = urllib.parse.unquote(parsed.path)
            else:
                local_path = urllib.parse.unquote(item)
            if node_id == "file_manager":
                if os.path.exists(local_path):
                    paths.append(local_path)
            elif os.path.isfile(local_path):
                ext = os.path.splitext(local_path)[1].lower()
                if ext in allowed_exts:
                    paths.append(local_path)

        if not paths:
            err_msg = "IMAGE ONLY" if is_image_node else ("AUDIO/IMG ONLY" if is_all_node else "AUDIO ONLY")
            self._set_node_status(node_id, "error", 0.0, err_msg)
            self._schedule_reset(node_id, 3000)
            context.finish(False, False, time_ms)
            return

        context.finish(True, False, time_ms)
        if node_id == "file_manager":
            target = paths[0] if paths else None
            GLib.idle_add(self._open_file_manager_action, target)
            return
        if node_id == "renderer_4k":
            audio_exts = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"}
            img_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
            staged_audio = None
            staged_images = []
            for p in paths:
                ext = os.path.splitext(p)[1].lower()
                if ext in audio_exts and not staged_audio:
                    staged_audio = p
                elif ext in img_exts:
                    staged_images.append(p)
            GLib.idle_add(self._open_4k_renderer_dialog, staged_audio, staged_images)
            return
        if node_id == "suno_cover":
            if len(paths) >= 2:
                self.suno_cover_pending_left = None
                GLib.idle_add(self._open_suno_cover_dialog, paths[0], paths[1])
            elif self.suno_cover_pending_left and os.path.isfile(self.suno_cover_pending_left):
                left_img = self.suno_cover_pending_left
                self.suno_cover_pending_left = None
                GLib.idle_add(self._open_suno_cover_dialog, left_img, paths[0])
            else:
                self.suno_cover_pending_left = paths[0]
                self._set_node_status(node_id, "staged", 0.5, "1/2 DROP IMG 2")
            return
        self._enqueue_audio_files(node_id, paths)

    def _trigger_f_cleaner_headless(self):
        if self.cleaner_running:
            return
        self.cleaner_running = True
        self.cleaner_status_text = "PURGING..."
        self.cleaner_status_until = time.time() + 65.0
        self.queue_draw()

        def _worker():
            label = "CLEANED"
            try:
                proc = subprocess.run(
                    ["/opt/floworkos/bin/f-cleaner", "--one-click", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    data = json.loads(proc.stdout.strip())
                    mb = float(data.get("disk_freed_mb", 0.0))
                    ram = int(data.get("ram_reclaimed_mb", 0))
                    if mb >= 0.1:
                        label = f"OK {mb:.1f}MB"
                    elif ram > 0:
                        label = f"OK +{ram}MB"
                    else:
                        label = "CLEANED"
            except Exception:
                label = "CLEANED"

            def _done():
                self.cleaner_running = False
                self.cleaner_status_text = label
                self.cleaner_status_until = time.time() + 4.0
                self.queue_draw()
                return False

            GLib.idle_add(_done)

        threading.Thread(target=_worker, daemon=True).start()

    def on_button_press(self, _widget, event):
        # 1. Check outer 8 orbital nodes first
        hit_node = self._hit_test_node(event.x, event.y)
        if hit_node is not None and self.nodes[hit_node]["active"]:
            node = self.nodes[hit_node]
            node_id = node["id"]
            st = self.node_states[node_id]
            is_image_node = node.get("media_type") == "image"
            if event.button == 3:
                if is_image_node:
                    open_pictures_dir(get_pictures_dir())
                elif node_id == "renderer_4k":
                    target_dir = "/opt/floworkos/documents" if os.path.exists("/opt/floworkos/documents") else os.path.expanduser("~/Videos")
                    subprocess.Popen(["nemo", target_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif node_id == "file_manager":
                    target_dir = "/opt/floworkos" if os.path.exists("/opt/floworkos") else os.path.expanduser("~")
                    subprocess.Popen(["nemo", target_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                else:
                    open_music_dir(get_music_dir())
                return True
            if event.button == 1 and st["state"] != "processing":
                if node_id == "suno_cover":
                    self._open_suno_cover_dialog(self.suno_cover_pending_left, None)
                elif node_id == "title_generator":
                    self._open_title_generator_dialog()
                elif node_id == "renderer_4k":
                    self._open_4k_renderer_dialog()
                elif node_id == "file_manager":
                    self._open_file_manager_action()
                else:
                    self._open_audio_file_picker(node)
                return True
            return False

        if event.button != 1:
            return False

        now = time.time()
        if now - self.last_click_time < 0.30:
            return True
        self.last_click_time = now

        # 2. Click Targeted Bloom Card
        if self.active_sector is not None and self.cluster_progress > 0.3:
            for (x, y, w, h, _cid, _idx, action_type, target) in self.card_hitboxes:
                if x <= event.x <= x + w and y <= event.y <= y + h:
                    if target:
                        try:
                            if action_type == "url":
                                subprocess.Popen(["google-chrome", target], start_new_session=True)
                            elif action_type == "cmd":
                                subprocess.Popen(target, shell=True, start_new_session=True)
                        except Exception:
                            pass
                    self.active_sector = None
                    self.target_progress = 0.0
                    self._update_input_shape()
                    self.queue_draw()
                    return True

        # 3. Click Center Core -> Trigger F-CLEANER Purge
        dx = event.x - self.cx
        dy = event.y - self.cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= self.r_core and (self.progress > 0.1 or self.cleaner_running):
            self._trigger_f_cleaner_headless()
            return True

        # 4. Click Irisan Sector -> Toggle Targeted Bloom (oracle/shutdown = direct launch)
        if self.hovered_sector is not None:
            if self.hovered_sector == "oracle":
                # Direct launch Tarot Oracle — no submenu bloom
                try:
                    subprocess.Popen(["/opt/floworkos/bin/flowork-tarot-oracle"], start_new_session=True)
                except Exception:
                    pass
                self.active_sector = None
                self.target_progress = 0.0
                self._update_input_shape()
                self.queue_draw()
                return True
            if self.hovered_sector == "shutdown":
                # Direct launch Shutdown Timer — no submenu bloom
                try:
                    subprocess.Popen(["/opt/floworkos/bin/flowork-shutdown-timer"], start_new_session=True)
                except Exception:
                    pass
                self.active_sector = None
                self.target_progress = 0.0
                self._update_input_shape()
                self.queue_draw()
                return True
            if self.hovered_sector == "fxcalc":
                # Direct launch FXCalc via Right Cyber Wing
                try:
                    subprocess.Popen(["/opt/floworkos/bin/flowork-fxcalc"], start_new_session=True)
                except Exception:
                    pass
                self.active_sector = None
                self.target_progress = 0.0
                self._update_input_shape()
                self.queue_draw()
                return True
            if self.active_sector == self.hovered_sector:
                self.active_sector = None
            else:
                self.active_sector = self.hovered_sector
                self.cluster_progress = 0.05
            self._update_input_shape()
            self.queue_draw()
            return True

        # 5. Click outside -> Collapse active sector
        if self.active_sector is not None:
            self.active_sector = None
            self._update_input_shape()
            self.queue_draw()
            return True

        return False

    def _open_audio_file_picker(self, node: dict):
        dialog = Gtk.FileChooserDialog(
            title=node["picker_title"],
            parent=None,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        dialog.set_select_multiple(True)
        is_image_node = node.get("media_type") == "image"
        start_dir = get_pictures_dir() if is_image_node else get_music_dir()
        if os.path.isdir(start_dir):
            dialog.set_current_folder(start_dir)

        flt = Gtk.FileFilter()
        if is_image_node:
            flt.set_name("Image Files (PNG, JPG, WEBP, BMP, TIFF)")
            exts = SUPPORTED_IMAGE_EXTS
        else:
            flt.set_name("Audio Files (WAV, MP3, FLAC, M4A, OGG)")
            exts = SUPPORTED_AUDIO_EXTS
        for ext in sorted(exts):
            flt.add_pattern(f"*{ext}")
            flt.add_pattern(f"*{ext.upper()}")
        dialog.add_filter(flt)

        resp = dialog.run()
        files = dialog.get_filenames() if resp == Gtk.ResponseType.OK else []
        dialog.destroy()
        if files:
            self._enqueue_audio_files(node["id"], files)

    def _schedule_reset(self, node_id: str, delay_ms: int):
        st = self.node_states[node_id]
        node_cfg = next((n for n in self.nodes if n["id"] == node_id), {})
        default_stage = node_cfg.get("sub", "DROP WAV")
        if st["reset_timer_id"] is not None:
            GLib.source_remove(st["reset_timer_id"])
            st["reset_timer_id"] = None

        def _reset():
            st["reset_timer_id"] = None
            if st["state"] != "processing":
                st["state"] = "idle"
                st["progress"] = 0.0
                st["display_progress"] = 0.0
                st["stage"] = default_stage
                st["batch_label"] = ""
                self.queue_draw()
            return False

        st["reset_timer_id"] = GLib.timeout_add(delay_ms, _reset)

    def _set_node_status(
        self,
        node_id: str,
        state: str,
        progress: float,
        stage: str,
        batch_label: str = "",
    ):
        st = self.node_states[node_id]
        st["state"] = state
        st["progress"] = max(0.0, min(1.0, progress))
        if state in ("idle", "done", "error"):
            st["display_progress"] = st["progress"]
        st["stage"] = stage
        st["batch_label"] = batch_label
        self.queue_draw()

    def _open_suno_cover_dialog(self, left_path: str = None, right_path: str = None):
        dialog = Gtk.Dialog(
            title="Suno Cover Studio — Node 05",
            parent=None,
            flags=Gtk.DialogFlags.MODAL,
        )
        dialog.set_keep_above(True)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.set_default_size(560, 420)
        dialog.set_resizable(False)

        css = Gtk.CssProvider()
        css.load_from_data(
            b"""
            dialog, window {
                background-color: #0b101b;
                color: #e6f4ff;
            }
            label {
                color: #d8ecff;
            }
            entry {
                background-color: #121a2b;
                color: #ffe600;
                border: 1px solid #264060;
                border-radius: 6px;
                padding: 8px 10px;
                font-weight: bold;
            }
            entry:focus {
                border-color: #00e5ff;
            }
            button {
                background-color: #162238;
                color: #e6f4ff;
                border: 1px solid #2b486e;
                border-radius: 6px;
                padding: 6px 12px;
            }
            button:hover {
                background-color: #1e3050;
                border-color: #00e5ff;
            }
            button.suggested-action {
                background-color: #ffe600;
                color: #090d16;
                border: 1px solid #ffd000;
                font-weight: bold;
            }
            button.suggested-action:hover {
                background-color: #fff04d;
            }
            """
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        state = {
            "left": left_path if (left_path and os.path.isfile(left_path)) else None,
            "right": right_path if (right_path and os.path.isfile(right_path)) else None,
        }

        box = dialog.get_content_area()
        box.set_spacing(12)
        box.set_margin_top(16)
        box.set_margin_bottom(14)
        box.set_margin_start(18)
        box.set_margin_end(18)

        hdr = Gtk.Label()
        hdr.set_markup(
            "<span size='large' weight='bold' foreground='#00e5ff'>SUNO COVER STUDIO</span>"
            "  <span size='small' foreground='#8aa4c8'>Split 2 Penyanyi + Petir + Judul</span>"
        )
        hdr.set_xalign(0.0)
        box.pack_start(hdr, False, False, 0)

        slots_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(slots_row, False, False, 0)

        def _make_preview_slot(role_title: str, side_key: str):
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            lbl = Gtk.Label()
            lbl.set_markup(f"<span weight='bold' foreground='#9ec5eb'>{role_title}</span>")
            col.pack_start(lbl, False, False, 0)

            frame = Gtk.Frame()
            frame.set_size_request(210, 124)
            img_widget = Gtk.Image()
            frame.add(img_widget)

            ev_box = Gtk.EventBox()
            ev_box.add(frame)
            ev_box.drag_dest_set(
                Gtk.DestDefaults.ALL,
                [Gtk.TargetEntry.new("text/uri-list", 0, 0)],
                Gdk.DragAction.COPY,
            )
            col.pack_start(ev_box, False, False, 0)

            name_lbl = Gtk.Label(label="Belum dipilih")
            name_lbl.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            name_lbl.set_max_width_chars(24)
            col.pack_start(name_lbl, False, False, 0)

            pick_btn = Gtk.Button(label="Pilih Gambar...")
            col.pack_start(pick_btn, False, False, 0)

            def _refresh():
                p = state[side_key]
                if p and os.path.isfile(p):
                    name_lbl.set_text(os.path.basename(p))
                    try:
                        pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(p, 204, 118, True)
                        img_widget.set_from_pixbuf(pb)
                    except Exception:
                        img_widget.set_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)
                else:
                    name_lbl.set_text("Drop / Pilih Gambar")
                    img_widget.set_from_icon_name("insert-image", Gtk.IconSize.DIALOG)

            def _pick(_btn):
                fc = Gtk.FileChooserDialog(
                    title=f"Pilih {role_title}",
                    parent=dialog,
                    action=Gtk.FileChooserAction.OPEN,
                )
                fc.add_buttons(
                    Gtk.STOCK_CANCEL,
                    Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OPEN,
                    Gtk.ResponseType.OK,
                )
                flt = Gtk.FileFilter()
                flt.set_name("Image Files")
                for ext in sorted(SUPPORTED_IMAGE_EXTS):
                    flt.add_pattern(f"*{ext}")
                    flt.add_pattern(f"*{ext.upper()}")
                fc.add_filter(flt)
                if fc.run() == Gtk.ResponseType.OK:
                    chosen = fc.get_filename()
                    if chosen and os.path.isfile(chosen):
                        state[side_key] = chosen
                        _refresh()
                fc.destroy()

            def _on_slot_drop(_w, _ctx, _x, _y, sel, _info, _t):
                uris = sel.get_uris() or []
                for u in uris:
                    if u.startswith("file://"):
                        lp = urllib.parse.unquote(urllib.parse.urlparse(u).path)
                        if os.path.isfile(lp) and os.path.splitext(lp)[1].lower() in SUPPORTED_IMAGE_EXTS:
                            state[side_key] = lp
                            _refresh()
                            break

            pick_btn.connect("clicked", _pick)
            ev_box.connect("drag-data-received", _on_slot_drop)
            _refresh()
            return col, _refresh

        left_col, refresh_left = _make_preview_slot("1. Penyanyi Asli (Kiri)", "left")
        right_col, refresh_right = _make_preview_slot("2. Penyanyi Cover (Kanan)", "right")

        swap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        swap_box.set_valign(Gtk.Align.CENTER)
        swap_btn = Gtk.Button(label="<->\nTukar")
        swap_btn.set_tooltip_text("Tukar posisi gambar kiri dan kanan")

        def _on_swap(_btn):
            state["left"], state["right"] = state["right"], state["left"]
            refresh_left()
            refresh_right()

        swap_btn.connect("clicked", _on_swap)
        swap_box.pack_start(swap_btn, False, False, 0)

        slots_row.pack_start(left_col, True, True, 0)
        slots_row.pack_start(swap_box, False, False, 0)
        slots_row.pack_start(right_col, True, True, 0)

        title_lbl = Gtk.Label()
        title_lbl.set_markup("<span weight='bold' foreground='#ffe600'>Judul Cover (Wajib):</span>")
        title_lbl.set_xalign(0.0)
        box.pack_start(title_lbl, False, False, 0)

        title_entry = Gtk.Entry()
        title_entry.set_placeholder_text("Contoh: KOK BISA BEDA?! atau LAGU LAMA KALAH MEWAH?!")
        title_entry.set_activates_default(True)
        box.pack_start(title_entry, False, False, 0)

        sub_lbl = Gtk.Label()
        sub_lbl.set_markup("<span foreground='#8aa4c8'>Subjudul Opsional (kosongkan jika tidak perlu):</span>")
        sub_lbl.set_xalign(0.0)
        box.pack_start(sub_lbl, False, False, 0)

        sub_entry = Gtk.Entry()
        sub_entry.set_placeholder_text("Contoh: Cover Arab / Cover Mandarin (opsional)")
        sub_entry.set_activates_default(True)
        box.pack_start(sub_entry, False, False, 0)

        err_lbl = Gtk.Label(label="")
        err_lbl.set_xalign(0.0)
        box.pack_start(err_lbl, False, False, 0)

        dialog.add_button("Batal", Gtk.ResponseType.CANCEL)
        gen_btn = dialog.add_button("Generate Cover", Gtk.ResponseType.OK)
        gen_btn.get_style_context().add_class("suggested-action")
        dialog.set_default_response(Gtk.ResponseType.OK)

        dialog.show_all()
        if state["left"] and state["right"]:
            title_entry.grab_focus()

        while True:
            resp = dialog.run()
            if resp != Gtk.ResponseType.OK:
                dialog.destroy()
                return
            t_val = title_entry.get_text().strip()
            s_val = sub_entry.get_text().strip()
            if not state["left"] or not state["right"]:
                err_lbl.set_markup("<span foreground='#ff5c70'>Pilih 2 gambar dulu (Penyanyi Asli &amp; Penyanyi Cover).</span>")
                continue
            if not t_val:
                err_lbl.set_markup("<span foreground='#ff5c70'>Judul cover wajib diisi.</span>")
                title_entry.grab_focus()
                continue
            left_final = state["left"]
            right_final = state["right"]
            dialog.destroy()
            self.suno_cover_pending_left = None
            self._enqueue_suno_cover_job(left_final, right_final, t_val, s_val)
            return

    def _open_title_generator_dialog(self, default_title=""):
        dlg = Gtk.Dialog(
            title="👑 VIRAL DRACHIN TITLE GENERATOR — NODE 04 MASTER",
            transient_for=self,
            modal=True,
            flags=0,
        )
        dlg.set_default_size(780, 620)
        dlg.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        dlg.get_style_context().add_class("flowork-dialog")

        content = dlg.get_content_area()
        content.set_spacing(12)
        content.set_margin_start(20)
        content.set_margin_end(20)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        # Header
        header = Gtk.Label()
        header.set_markup(
            "<span font='14' weight='bold' color='#ffe600'>🔥 GENERATOR JUDUL VIRAL DRACHIN / MANDARIN MASTER</span>\n"
            "<span font='9' color='#8aa4c8'>Kombinatorik Sastra &amp; Sinematik Anti-Monoton | Narrative Storytelling &amp; Signature Maestro</span>"
        )
        header.set_xalign(0.0)
        content.pack_start(header, False, False, 0)

        # Input Row 1: Lagu & Count
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl1 = Gtk.Label(label="Judul Lagu / Artis:")
        lbl1.get_style_context().add_class("field-lbl")
        row1.pack_start(lbl1, False, False, 0)

        entry = Gtk.Entry()
        entry.set_placeholder_text("Contoh: Kisah Cintaku Chrisye / Bintang Kehidupan Nike Ardilla / Dan Sheila on 7")
        entry.set_hexpand(True)
        if default_title:
            entry.set_text(default_title)
        row1.pack_start(entry, True, True, 0)

        combo_count = Gtk.ComboBoxText()
        for c in ["5 Judul", "10 Judul", "15 Judul", "20 Judul"]:
            combo_count.append_text(c)
        combo_count.set_active(1)
        row1.pack_start(combo_count, False, False, 0)

        btn_gen = Gtk.Button(label="🔥 Generate Judul")
        btn_gen.get_style_context().add_class("btn-accent")
        row1.pack_start(btn_gen, False, False, 0)
        content.pack_start(row1, False, False, 0)

        # Input Row 2: Vibe Filter & Badge Option
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl2 = Gtk.Label(label="Karakter Vibe:")
        lbl2.get_style_context().add_class("field-lbl")
        row2.pack_start(lbl2, False, False, 0)

        mood_options = [
            ("all", "🎲 Semua Karakter (Campur Anti-Monoton)"),
            ("emotional", "😭 Air Mata & Nangis Kejer"),
            ("shock", "⚡ Syok & Bikin Kaget (CTR Tinggi)"),
            ("debate", "🔥 Debat Panas & Kontroversial"),
            ("douyin", "🇨🇳 Viral Douyin & Weibo China"),
            ("reaction", "👑 Reaksi Artis & Sang Maestro"),
            ("xianxia", "🌸 Kisah Tragis Xianxia (Reinkarnasi)"),
            ("kolosal", "⚔️ Kerajaan, Perang & Tahta Kaisar"),
            ("instrument", "🎻 Gesekan Erhu & Petikan Guzheng"),
        ]
        combo_mood = Gtk.ComboBoxText()
        for m_id, m_label in mood_options:
            combo_mood.append(m_id, m_label)
        combo_mood.set_active_id("all")
        row2.pack_start(combo_mood, False, False, 0)

        chk_badge = Gtk.CheckButton(label="Sertakan Badge Mandarin (Contoh: | 独家首播 / 影视原声)")
        chk_badge.set_active(True)
        row2.pack_start(chk_badge, False, False, 0)

        btn_random = Gtk.Button(label="🎲 Acak Ulang")
        row2.pack_start(btn_random, False, False, 0)
        content.pack_start(row2, False, False, 0)

        # Results Scroller
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(350)
        scroll.set_vexpand(True)

        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.add(list_box)
        content.pack_start(scroll, True, True, 0)

        init_lbl = Gtk.Label()
        init_lbl.set_markup("<span color='#8aa4c8' font='10'>Ketik nama lagu di atas lalu klik <b>🔥 Generate Judul</b>, atau drop file audio langsung ke Node 04.</span>")
        init_lbl.set_margin_top(50)
        list_box.pack_start(init_lbl, True, True, 0)

        generated_bundle = []
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        def do_generate(*_):
            raw_text = entry.get_text().strip()
            if not raw_text:
                return

            for ch in list_box.get_children():
                list_box.remove(ch)

            count_str = combo_count.get_active_text() or "10 Judul"
            count = int(count_str.split()[0])
            active_m = combo_mood.get_active_id() or "all"
            mood_param = None if active_m == "all" else active_m
            with_badge = chk_badge.get_active()

            clean_name = clean_song_name(raw_text)
            titles = generate_title_bundle(
                clean_name,
                count=count,
                mood=mood_param,
                with_badge=with_badge
            )
            generated_bundle.clear()
            generated_bundle.extend(titles)

            for item in titles:
                card = Gtk.Frame()
                card.get_style_context().add_class("slot-frame")
                card_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                card_box.set_margin_start(12)
                card_box.set_margin_end(12)
                card_box.set_margin_top(8)
                card_box.set_margin_bottom(8)

                badge = Gtk.Label()
                badge.set_markup(f"<span font='10' weight='bold' color='#ffe600'>[{item['index']:02d}]</span>")
                badge.set_valign(Gtk.Align.CENTER)
                card_box.pack_start(badge, False, False, 0)

                text_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                t_lbl = Gtk.Label()
                escaped_title = GLib.markup_escape_text(item["title"])
                t_lbl.set_markup(f"<span font='10' weight='bold' color='#ffffff'>{escaped_title}</span>")
                t_lbl.set_line_wrap(True)
                t_lbl.set_xalign(0.0)
                t_lbl.set_selectable(True)
                text_vbox.pack_start(t_lbl, True, True, 0)

                vibe_text = item.get("vibe", "DRACHIN VIRAL")
                tag_lbl = Gtk.Label()
                tag_lbl.set_markup(f"<span font='8' weight='bold' color='#00e5ff'>✦ {GLib.markup_escape_text(vibe_text)}</span>")
                tag_lbl.set_xalign(0.0)
                text_vbox.pack_start(tag_lbl, False, False, 0)

                card_box.pack_start(text_vbox, True, True, 0)

                btn_copy = Gtk.Button(label="📋 Salin")
                btn_copy.set_valign(Gtk.Align.CENTER)
                btn_copy.set_size_request(85, 32)

                def on_copy_clicked(btn, title_text=item["title"]):
                    clipboard.set_text(title_text, -1)
                    btn.set_label("✓ Tersalin!")
                    GLib.timeout_add(1500, lambda: btn.set_label("📋 Salin"))

                btn_copy.connect("clicked", on_copy_clicked)
                card_box.pack_start(btn_copy, False, False, 0)

                card.add(card_box)
                list_box.pack_start(card, False, False, 0)

            list_box.show_all()

        btn_gen.connect("clicked", do_generate)
        btn_random.connect("clicked", do_generate)
        combo_mood.connect("changed", do_generate)
        entry.connect("activate", do_generate)

        # Bottom Bar
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        btn_copy_all = Gtk.Button(label="📋 Salin Semua Judul")
        def _copy_all_titles(*_):
            if not generated_bundle:
                return
            all_text = "\n".join([f"{item['index']}. {item['title']}" for item in generated_bundle])
            clipboard.set_text(all_text, -1)
            btn_copy_all.set_label("✓ Semua Tersalin!")
            GLib.timeout_add(2000, lambda: btn_copy_all.set_label("📋 Salin Semua Judul"))
        btn_copy_all.connect("clicked", _copy_all_titles)
        bottom_box.pack_start(btn_copy_all, False, False, 0)

        btn_save_all = Gtk.Button(label="💾 Simpan ke File (.txt)")
        def do_save_all(*_):
            if not generated_bundle:
                return
            raw_text = entry.get_text().strip() or "Drachin_Song"
            clean_name = clean_song_name(raw_text)
            desktop_dir = os.path.expanduser("~/Desktop")
            out_file = os.path.join(desktop_dir, f"Judul_Viral_{clean_name.replace(' ', '_')}.txt")
            saved = export_bundle_to_file(clean_name, generated_bundle, out_file)
            btn_save_all.set_label("✓ Tersimpan!")
            GLib.timeout_add(2000, lambda: btn_save_all.set_label("💾 Simpan ke File (.txt)"))
            try:
                import subprocess
                subprocess.Popen(["xdg-open", saved], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        btn_save_all.connect("clicked", do_save_all)
        bottom_box.pack_start(btn_save_all, False, False, 0)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bottom_box.pack_start(spacer, True, True, 0)

        btn_close = Gtk.Button(label="✕ Tutup")
        btn_close.connect("clicked", lambda *_: dlg.destroy())
        bottom_box.pack_start(btn_close, False, False, 0)

        content.pack_start(bottom_box, False, False, 0)

        if default_title:
            GLib.idle_add(do_generate)

        dlg.show_all()

    def _open_4k_renderer_dialog(self, initial_audio=None, initial_images=None):
        dlg = Gtk.Dialog(
            title="👑 4K UHD AUDIO-VISUAL MASTER — NODE 07",
            transient_for=self,
            modal=True,
            destroy_with_parent=True,
        )
        dlg.set_default_size(900, 750)
        content = dlg.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(20)
        content.set_margin_end(20)

        # Apply dark style
        css_prov = Gtk.CssProvider()
        css_data = b"""
        dialog, window {
            background-color: #0b111a;
            color: #d1e4ff;
        }
        label.hud-title {
            font-size: 17px;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: #00e5ff;
        }
        label.hud-sub {
            font-size: 11px;
            color: #728ca6;
        }
        label.section-title {
            font-size: 12px;
            font-weight: bold;
            color: #ffd200;
            letter-spacing: 0.8px;
        }
        entry {
            background-color: #121c29;
            color: #ffffff;
            border: 1px solid #1f334d;
            border-radius: 6px;
            padding: 7px 10px;
            font-size: 12px;
        }
        entry:focus {
            border-color: #00e5ff;
        }
        combobox button {
            background-color: #121c29;
            color: #d1e4ff;
            border: 1px solid #1f334d;
            border-radius: 6px;
            padding: 5px 8px;
            font-size: 11px;
        }
        button.action-btn {
            background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%);
            color: #ffffff;
            font-weight: bold;
            border-radius: 6px;
            border: none;
            padding: 8px 14px;
        }
        button.action-btn:hover {
            background: linear-gradient(135deg, #0096c7 0%, #48cae4 100%);
        }
        button.render-btn {
            background: linear-gradient(135deg, #00b4d8 0%, #0077b6 50%, #7209b7 100%);
            color: #ffffff;
            font-size: 14px;
            font-weight: 800;
            border-radius: 8px;
            border: 1px solid #00e5ff;
            padding: 12px 24px;
            letter-spacing: 1px;
        }
        button.render-btn:hover {
            background: linear-gradient(135deg, #48cae4 0%, #0096c7 50%, #9d4edd 100%);
        }
        listbox {
            background-color: #0e1622;
            border: 1px solid #1a293d;
            border-radius: 6px;
        }
        listboxrow {
            padding: 6px 10px;
            border-bottom: 1px solid #162335;
        }
        listboxrow:selected {
            background-color: #19334d;
        }
        progressbar progress {
            background: linear-gradient(90deg, #00e5ff, #7928ca);
            border-radius: 4px;
        }
        progressbar trough {
            background-color: #121c29;
            border-radius: 4px;
            min-height: 10px;
        }
        """
        css_prov.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # State storage
        staged_images = list(initial_images or [])
        current_audio = initial_audio or ""

        # Header Box
        head_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        lbl_h = Gtk.Label(label="4K UHD AUDIO-VISUAL MASTER - NODE 07")
        lbl_h.get_style_context().add_class("hud-title")
        lbl_h.set_xalign(0.0)
        lbl_s = Gtk.Label(
            label="NVIDIA GeForce RTX 4060 NVENC Hardware Acceleration - 3840x2160 UHD - Dynamic Audio Mastering"
        )
        lbl_s.get_style_context().add_class("hud-sub")
        lbl_s.set_xalign(0.0)
        head_box.pack_start(lbl_h, False, False, 0)
        head_box.pack_start(lbl_s, False, False, 0)
        content.pack_start(head_box, False, False, 0)

        # --- SECTION 1: AUDIO TRACK ---
        sec_audio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        lbl_sec_audio = Gtk.Label(label="1. FILE AUDIO MASTER (MP3, WAV, FLAC, M4A)")
        lbl_sec_audio.get_style_context().add_class("section-title")
        lbl_sec_audio.set_xalign(0.0)
        sec_audio_box.pack_start(lbl_sec_audio, False, False, 0)

        audio_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        entry_audio = Gtk.Entry()
        entry_audio.set_hexpand(True)
        entry_audio.set_placeholder_text("Pilih atau drag & drop file audio master...")
        if current_audio:
            entry_audio.set_text(current_audio)

        btn_browse_audio = Gtk.Button(label="Pilih Audio...")
        btn_browse_audio.get_style_context().add_class("action-btn")
        audio_row.pack_start(entry_audio, True, True, 0)
        audio_row.pack_start(btn_browse_audio, False, False, 0)
        sec_audio_box.pack_start(audio_row, False, False, 0)

        lbl_audio_meta = Gtk.Label(label="Durasi: --:-- - Sample Rate: -- - Bitrate: --")
        lbl_audio_meta.set_xalign(0.0)
        lbl_audio_meta.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 0.9, 1.0, 0.9))
        sec_audio_box.pack_start(lbl_audio_meta, False, False, 0)
        content.pack_start(sec_audio_box, False, False, 0)

        # --- SECTION 2: IMAGES GALLERY ---
        sec_img_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        lbl_sec_img = Gtk.Label(label="2. DAFTAR GAMBAR COVER / SCENE (1 ATAU LEBIH)")
        lbl_sec_img.get_style_context().add_class("section-title")
        lbl_sec_img.set_xalign(0.0)
        sec_img_box.pack_start(lbl_sec_img, False, False, 0)

        img_scroll = Gtk.ScrolledWindow()
        img_scroll.set_min_content_height(105)
        img_scroll.set_max_content_height(140)
        img_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        img_listbox = Gtk.ListBox()
        img_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        img_scroll.add(img_listbox)
        sec_img_box.pack_start(img_scroll, True, True, 0)

        # Image action buttons
        img_btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_add_img = Gtk.Button(label="+ Tambah Gambar...")
        btn_add_img.get_style_context().add_class("action-btn")
        btn_remove_img = Gtk.Button(label="- Hapus Pilihan")
        btn_clear_imgs = Gtk.Button(label="Bersihkan Semua")
        lbl_img_count = Gtk.Label(label="[ 0 Gambar Dimuat ]")
        lbl_img_count.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.45, 0.65, 0.85, 1.0))
        img_btn_row.pack_start(btn_add_img, False, False, 0)
        img_btn_row.pack_start(btn_remove_img, False, False, 0)
        img_btn_row.pack_start(btn_clear_imgs, False, False, 0)
        img_btn_row.pack_end(lbl_img_count, False, False, 0)
        sec_img_box.pack_start(img_btn_row, False, False, 0)

        content.pack_start(sec_img_box, True, True, 0)

        # --- SECTION 3: PARAMETER CONTROLS GRID ---
        grid = Gtk.Grid()
        grid.set_column_spacing(18)
        grid.set_row_spacing(8)
        grid.set_hexpand(True)

        # 1. Motion Style
        lbl_motion = Gtk.Label(label="Gaya Gerak (Motion):")
        lbl_motion.set_xalign(0.0)
        combo_motion = Gtk.ComboBoxText()
        combo_motion.append("ken_burns", "Cinematic Ken Burns (Slow Pan & Zoom 1.06x)")
        combo_motion.append("crossfade", "Smooth Crossfade Dissolve (Transisi Halus)")
        combo_motion.append("still", "Crystal Still Frame (Ultra Fast 4K)")
        combo_motion.set_active_id("ken_burns")
        grid.attach(lbl_motion, 0, 0, 1, 1)
        grid.attach(combo_motion, 0, 1, 1, 1)

        # 2. Visual Audio Effect
        lbl_vis = Gtk.Label(label="Visual Reaktif Musik:")
        lbl_vis.set_xalign(0.0)
        combo_vis = Gtk.ComboBoxText()
        combo_vis.append("neon_wave", "Neon Cyan Waveform (Gelombang Menyala)")
        combo_vis.append("spectrum_bars", "Equalizer Spectrum Bars (Batang Frekuensi)")
        combo_vis.append("subtle_pulse", "Subtle Golden Wave (Gelombang Halus)")
        combo_vis.append("none", "Off (Murni Gambar Sinematik)")
        combo_vis.set_active_id("neon_wave")
        grid.attach(lbl_vis, 1, 0, 1, 1)
        grid.attach(combo_vis, 1, 1, 1, 1)

        # 3. Canvas Fit
        lbl_fit = Gtk.Label(label="Penyesuaian Rasio (Fit):")
        lbl_fit.set_xalign(0.0)
        combo_fit = Gtk.ComboBoxText()
        combo_fit.append("smart_blur", "Smart Blurred Background (Estetik Anti-Gepeng)")
        combo_fit.append("crop", "Cinematic Center Crop (16:9 Full Fill)")
        combo_fit.append("pad_black", "Pad Black Bars (Pilarbox/Letterbox Hitam)")
        combo_fit.set_active_id("smart_blur")
        grid.attach(lbl_fit, 0, 2, 1, 1)
        grid.attach(combo_fit, 0, 3, 1, 1)

        # 4. Audio Mastering
        lbl_master = Gtk.Label(label="Mastering Audio:")
        lbl_master.set_xalign(0.0)
        combo_master = Gtk.ComboBoxText()
        combo_master.append("youtube_lufs", "YouTube Broadcast (-14 LUFS + Limiter)")
        combo_master.append("clarity_boost", "Bass Punch & Vocal Clarity (-14 LUFS)")
        combo_master.append("original", "Original Direct Pass (Tanpa Filter)")
        combo_master.set_active_id("youtube_lufs")
        grid.attach(lbl_master, 1, 2, 1, 1)
        grid.attach(combo_master, 1, 3, 1, 1)

        content.pack_start(grid, False, False, 0)

        # --- SECTION 4: HARDWARE & OUTPUT PATH ---
        out_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        lbl_sec_out = Gtk.Label(label="3. HARDWARE ENCODER & TARGET OUTPUT 4K")
        lbl_sec_out.get_style_context().add_class("section-title")
        lbl_sec_out.set_xalign(0.0)
        out_box.pack_start(lbl_sec_out, False, False, 0)

        hw_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        combo_encoder = Gtk.ComboBoxText()
        best_enc = detect_best_encoder()
        if best_enc == "h264_nvenc":
            combo_encoder.append("h264_nvenc", "NVIDIA GeForce RTX 4060 NVENC (Hardware Acceleration 150+ FPS)")
            combo_encoder.append("libx264", "CPU libx264 (CRF 18 Master)")
            combo_encoder.set_active_id("h264_nvenc")
        else:
            combo_encoder.append("libx264", "CPU libx264 (CRF 18 Master)")
            combo_encoder.set_active_id("libx264")
        combo_encoder.set_hexpand(True)
        hw_row.pack_start(combo_encoder, True, True, 0)
        out_box.pack_start(hw_row, False, False, 0)

        out_path_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        entry_output = Gtk.Entry()
        entry_output.set_hexpand(True)
        entry_output.set_placeholder_text("Target output file (.mp4)...")
        btn_browse_output = Gtk.Button(label="Ubah Lokasi...")
        btn_browse_output.get_style_context().add_class("action-btn")
        out_path_row.pack_start(entry_output, True, True, 0)
        out_path_row.pack_start(btn_browse_output, False, False, 0)
        out_box.pack_start(out_path_row, False, False, 0)
        content.pack_start(out_box, False, False, 0)

        # --- SECTION 5: PROGRESS BAR & STATUS ---
        prog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_fraction(0.0)
        progress_bar.set_text("Standby")
        progress_bar.set_show_text(True)
        prog_box.pack_start(progress_bar, False, False, 0)

        lbl_status = Gtk.Label(label="Status: Siap render - Pilih file audio dan gambar")
        lbl_status.set_xalign(0.0)
        lbl_status.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.45, 0.65, 0.85, 1.0))
        prog_box.pack_start(lbl_status, False, False, 0)
        content.pack_start(prog_box, False, False, 0)

        # --- SECTION 6: BOTTOM ACTIONS ---
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_render = Gtk.Button(label="RENDER 4K UHD VIDEO")
        btn_render.get_style_context().add_class("render-btn")
        btn_render.set_hexpand(True)
        bottom_box.pack_start(btn_render, True, True, 0)

        btn_play = Gtk.Button(label="Putar Video (MPV)")
        btn_play.get_style_context().add_class("action-btn")
        btn_play.set_no_show_all(True)
        btn_play.hide()
        bottom_box.pack_start(btn_play, False, False, 0)

        btn_open_folder = Gtk.Button(label="Buka Folder")
        btn_open_folder.get_style_context().add_class("action-btn")
        btn_open_folder.set_no_show_all(True)
        btn_open_folder.hide()
        bottom_box.pack_start(btn_open_folder, False, False, 0)

        btn_close = Gtk.Button(label="Tutup")
        btn_close.connect("clicked", lambda *_: dlg.destroy())
        bottom_box.pack_start(btn_close, False, False, 0)
        content.pack_start(bottom_box, False, False, 0)

        # Helper: Refresh image list UI
        def refresh_image_list():
            for child in img_listbox.get_children():
                img_listbox.remove(child)
            for idx, img_p in enumerate(staged_images, start=1):
                row = Gtk.ListBoxRow()
                h_b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                fname = os.path.basename(img_p)
                lbl = Gtk.Label(label=f"#{idx}  {fname}")
                lbl.set_xalign(0.0)
                lbl.set_hexpand(True)
                btn_del = Gtk.Button(label="x")
                btn_del.connect("clicked", lambda _, p=img_p: remove_image(p))
                h_b.pack_start(lbl, True, True, 0)
                h_b.pack_start(btn_del, False, False, 0)
                row.add(h_b)
                img_listbox.add(row)
            img_listbox.show_all()
            lbl_img_count.set_text(f"[ {len(staged_images)} Gambar Dimuat ]")
            if len(staged_images) > 1 and combo_motion.get_active_id() == "still":
                combo_motion.set_active_id("crossfade")

        def remove_image(img_p):
            if img_p in staged_images:
                staged_images.remove(img_p)
                refresh_image_list()

        def update_audio_info(path):
            if not path or not os.path.exists(path):
                lbl_audio_meta.set_text("Durasi: --:-- - Sample Rate: -- - Bitrate: --")
                return
            try:
                meta = probe_audio_info(path)
                dur = meta["duration_str"]
                sr = meta["sample_rate"]
                br = int(meta["bit_rate"] / 1000) if meta["bit_rate"] else 320
                lbl_audio_meta.set_text(f"Durasi: {dur} - {sr} Hz ({meta['channels']} ch) - {br} kbps [{meta['codec'].upper()}]")
                if not entry_output.get_text().strip():
                    stem = os.path.splitext(os.path.basename(path))[0]
                    out_dir = "/opt/floworkos/documents" if os.path.exists("/opt/floworkos/documents") else os.path.dirname(path)
                    entry_output.set_text(os.path.join(out_dir, f"{stem}_4K_UHD.mp4"))
            except Exception as e:
                lbl_audio_meta.set_text(f"Gagal membaca audio: {e}")

        # Connect audio browse
        def do_browse_audio(*_):
            chooser = Gtk.FileChooserDialog(
                title="Pilih File Audio Master",
                parent=dlg,
                action=Gtk.FileChooserAction.OPEN
            )
            chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            filt = Gtk.FileFilter()
            filt.set_name("File Audio (*.mp3, *.wav, *.flac, *.m4a, *.ogg)")
            filt.add_mime_type("audio/*")
            for ext in ["*.mp3", "*.wav", "*.flac", "*.m4a", "*.aac", "*.ogg", "*.wma"]:
                filt.add_pattern(ext)
            chooser.add_filter(filt)
            if chooser.run() == Gtk.ResponseType.OK:
                selected = chooser.get_filename()
                entry_audio.set_text(selected)
                update_audio_info(selected)
            chooser.destroy()

        btn_browse_audio.connect("clicked", do_browse_audio)

        # Connect image browse
        def do_add_images(*_):
            chooser = Gtk.FileChooserDialog(
                title="Tambah Gambar Cover / Scene (Pilih Satu atau Lebih)",
                parent=dlg,
                action=Gtk.FileChooserAction.OPEN
            )
            chooser.set_select_multiple(True)
            chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            filt = Gtk.FileFilter()
            filt.set_name("Gambar (*.jpg, *.png, *.webp, *.jpeg)")
            filt.add_mime_type("image/*")
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"]:
                filt.add_pattern(ext)
            chooser.add_filter(filt)
            if chooser.run() == Gtk.ResponseType.OK:
                new_files = chooser.get_filenames()
                for nf in new_files:
                    if nf not in staged_images:
                        staged_images.append(nf)
                refresh_image_list()
            chooser.destroy()

        btn_add_img.connect("clicked", do_add_images)
        btn_clear_imgs.connect("clicked", lambda *_: (staged_images.clear(), refresh_image_list()))
        btn_remove_img.connect("clicked", lambda *_: remove_selected_image())

        def remove_selected_image():
            selected = img_listbox.get_selected_row()
            if selected:
                idx = selected.get_index()
                if 0 <= idx < len(staged_images):
                    staged_images.pop(idx)
                    refresh_image_list()

        # Connect output browse
        def do_browse_output(*_):
            chooser = Gtk.FileChooserDialog(
                title="Tentukan Lokasi & Nama File Output 4K",
                parent=dlg,
                action=Gtk.FileChooserAction.SAVE
            )
            chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
            chooser.set_current_name("Video_Musik_4K_UHD.mp4")
            if chooser.run() == Gtk.ResponseType.OK:
                entry_output.set_text(chooser.get_filename())
            chooser.destroy()

        btn_browse_output.connect("clicked", do_browse_output)

        # Render execution thread
        last_rendered_path = [None]

        def do_render(*_):
            audio_p = entry_audio.get_text().strip()
            if not audio_p or not os.path.exists(audio_p):
                lbl_status.set_text("ERROR: Silakan pilih file audio master yang valid terlebih dahulu!")
                return
            if not staged_images:
                lbl_status.set_text("ERROR: Minimal masukkan 1 file gambar untuk cover video 4K!")
                return

            out_p = entry_output.get_text().strip()
            if not out_p:
                stem = os.path.splitext(os.path.basename(audio_p))[0]
                out_p = f"/opt/floworkos/documents/{stem}_4K_UHD.mp4"
                entry_output.set_text(out_p)

            # Lock controls during render
            btn_render.set_sensitive(False)
            btn_browse_audio.set_sensitive(False)
            btn_add_img.set_sensitive(False)
            btn_clear_imgs.set_sensitive(False)
            btn_remove_img.set_sensitive(False)
            btn_play.hide()
            btn_open_folder.hide()

            motion = combo_motion.get_active_id() or "ken_burns"
            fit = combo_fit.get_active_id() or "smart_blur"
            vis = combo_vis.get_active_id() or "neon_wave"
            master = combo_master.get_active_id() or "youtube_lufs"
            encoder = combo_encoder.get_active_id() or "auto"

            # Set node HUD state to processing
            node_id = "renderer_4k"
            st = self.node_states[node_id]
            st["state"] = "processing"
            st["progress"] = 0.05
            st["text"] = "RENDERING 4K..."
            self.queue_draw()

            def progress_cb(info):
                pct = info.get("percent", 0.0)
                fps = info.get("fps", 0.0)
                speed = info.get("speed", "")
                enc = info.get("encoder", "")

                def update_ui():
                    progress_bar.set_fraction(pct / 100.0)
                    progress_bar.set_text(f"{pct:.1f}%")
                    lbl_status.set_text(f"Rendering [{enc}]: {pct:.1f}% | {fps:.1f} FPS | Speed: {speed}")
                    st["progress"] = pct / 100.0
                    self.queue_draw()
                GLib.idle_add(update_ui)

            def worker():
                try:
                    res = render_4k_bundle(
                        audio_file=audio_p,
                        image_files=list(staged_images),
                        output_path=out_p,
                        motion_style=motion,
                        fit_style=fit,
                        visualizer_style=vis,
                        audio_mastering=master,
                        encoder=encoder,
                        progress_callback=progress_cb
                    )
                    last_rendered_path[0] = res["output_path"]

                    def on_success():
                        btn_render.set_sensitive(True)
                        btn_browse_audio.set_sensitive(True)
                        btn_add_img.set_sensitive(True)
                        btn_clear_imgs.set_sensitive(True)
                        btn_remove_img.set_sensitive(True)
                        progress_bar.set_fraction(1.0)
                        progress_bar.set_text("100% SELESAI")
                        lbl_status.set_text(
                            f"RENDER 4K SUKSES! ({res['file_size_mb']} MB dalam {res['render_time_sec']}s - Rata-rata {res['avg_fps']} FPS)"
                        )
                        btn_play.show()
                        btn_open_folder.show()
                        st["state"] = "done"
                        st["progress"] = 1.0
                        st["text"] = "4K READY"
                        self.queue_draw()
                    GLib.idle_add(on_success)

                except Exception as err:
                    err_msg = str(err)
                    def on_err(msg=err_msg):
                        btn_render.set_sensitive(True)
                        btn_browse_audio.set_sensitive(True)
                        btn_add_img.set_sensitive(True)
                        btn_clear_imgs.set_sensitive(True)
                        btn_remove_img.set_sensitive(True)
                        progress_bar.set_text("GAGAL")
                        lbl_status.set_text(f"Render gagal: {msg}")
                        st["state"] = "idle"
                        st["text"] = "ERROR"
                        self.queue_draw()
                    GLib.idle_add(on_err)

            threading.Thread(target=worker, daemon=True).start()

        btn_render.connect("clicked", do_render)

        # Connect play & open folder buttons
        def do_play(*_):
            if last_rendered_path[0] and os.path.exists(last_rendered_path[0]):
                try:
                    subprocess.Popen(["mpv", last_rendered_path[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    subprocess.Popen(["xdg-open", last_rendered_path[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        def do_open_folder(*_):
            if last_rendered_path[0]:
                out_dir = os.path.dirname(last_rendered_path[0])
                try:
                    subprocess.Popen(["nemo", out_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    subprocess.Popen(["xdg-open", out_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        btn_play.connect("clicked", do_play)
        btn_open_folder.connect("clicked", do_open_folder)

        # Initial data loading
        if initial_audio:
            update_audio_info(initial_audio)
        refresh_image_list()

        dlg.show_all()

    def _open_file_manager_action(self, target_path=None):
        target = target_path if (target_path and os.path.exists(target_path)) else os.path.expanduser("~")
        if os.path.isfile(target):
            target = os.path.dirname(target)
        try:
            subprocess.Popen(
                ["nemo", target],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            self._set_node_status("file_manager", "done", 1.0, "OPENED", "")
            def _reset_fm():
                self._set_node_status("file_manager", "idle", 0.0, "STANDBY", "")
                return False
            GLib.timeout_add(2200, _reset_fm)
        except Exception:
            try:
                subprocess.Popen(
                    ["xdg-open", target],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                self._set_node_status("file_manager", "done", 1.0, "OPENED", "")
                def _reset_fm():
                    self._set_node_status("file_manager", "idle", 0.0, "STANDBY", "")
                    return False
                GLib.timeout_add(2200, _reset_fm)
            except Exception:
                self._set_node_status("file_manager", "idle", 0.0, "ERROR", "")

    def _enqueue_suno_cover_job(self, left_path: str, right_path: str, title: str, subtitle: str = ""):
        node_id = "suno_cover"
        st = self.node_states[node_id]
        if st["reset_timer_id"] is not None:
            GLib.source_remove(st["reset_timer_id"])
            st["reset_timer_id"] = None
        st["job_queue"].put([(left_path, right_path, title, subtitle)])
        if st["state"] != "processing":
            self._set_node_status(node_id, "processing", 0.05, "COMPOSING", "")
        if not st["worker_running"]:
            st["worker_running"] = True
            threading.Thread(target=self._node_worker, args=(node_id,), daemon=True).start()

    def _enqueue_audio_files(self, node_id: str, paths: list[str]):
        st = self.node_states[node_id]
        if st["reset_timer_id"] is not None:
            GLib.source_remove(st["reset_timer_id"])
            st["reset_timer_id"] = None
        st["job_queue"].put(paths)
        with st["worker_lock"]:
            if not st["worker_running"]:
                st["worker_running"] = True
                t = threading.Thread(
                    target=self._node_worker,
                    args=(node_id,),
                    daemon=True,
                )
                t.start()

    def _node_worker(self, node_id: str):
        st = self.node_states[node_id]
        while True:
            try:
                batch = st["job_queue"].get_nowait()
            except queue.Empty:
                with st["worker_lock"]:
                    st["worker_running"] = False
                break

            total = len(batch)
            last_music_dir = None
            last_ratio = None
            had_error = False

            for idx, audio_path in enumerate(batch, start=1):
                batch_lbl = f"{idx}/{total}" if total > 1 else ""

                def _on_prog(p: float, stage: str, b_lbl=batch_lbl, i=idx, n=total):
                    overall = ((i - 1) + p) / max(1, n)
                    GLib.idle_add(
                        self._set_node_status,
                        node_id,
                        "processing",
                        overall,
                        stage,
                        b_lbl,
                    )

                try:
                    if node_id == "vocal_master":
                        res = master_vocal_focus(audio_path, on_progress=_on_prog)
                    elif node_id == "stem_split":
                        res = separate_vocal_and_music(audio_path, on_progress=_on_prog)
                    elif node_id == "suno_59s":
                        res = render_suno_59s(audio_path, on_progress=_on_prog)
                        last_ratio = res.get("ratio")
                    elif node_id == "title_generator":
                        _on_prog(0.2, "ANALYZING")
                        clean_name = clean_song_name(audio_path)
                        _on_prog(0.5, "GENERATING")
                        titles = generate_title_bundle(clean_name, count=10)
                        _on_prog(0.8, "SAVING")
                        target_dir = os.path.dirname(audio_path) if os.path.isdir(os.path.dirname(audio_path)) else get_music_dir()
                        out_file = os.path.join(target_dir, f"{clean_name.replace(' ', '_')}_viral_titles.txt")
                        saved_path = export_bundle_to_file(clean_name, titles, out_file)
                        _on_prog(1.0, "TITLES READY")
                        try:
                            import subprocess
                            subprocess.Popen(["xdg-open", saved_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except Exception:
                            pass
                        res = {"output_path": saved_path, "count": len(titles), "titles": titles}
                        last_ratio = None
                    elif node_id == "bg_remove":
                        res = remove_background_image(audio_path, on_progress=_on_prog)
                    elif node_id == "suno_cover":
                        left_img, right_img, cov_title, cov_sub = audio_path
                        res = generate_suno_cover(
                            left_img,
                            right_img,
                            title=cov_title,
                            subtitle=cov_sub,
                            on_progress=_on_prog,
                        )
                    else:
                        raise RuntimeError(f"Unknown active node: {node_id}")
                    last_music_dir = res.get("pictures_dir") or res.get("output_dir") or res.get("music_dir") or (os.path.dirname(res["output_path"]) if "output_path" in res else None)
                except Exception as exc:
                    had_error = True
                    print(f"[OrbitalHUD:{node_id}] Error processing {audio_path}: {exc}", file=sys.stderr)
                    GLib.idle_add(self._set_node_status, node_id, "error", 0.0, "ERROR", batch_lbl)

            if not had_error:
                if node_id == "suno_59s" and last_ratio and total == 1:
                    done_lbl = f"{last_ratio:.2f}x 59S"
                elif node_id == "title_generator" and total == 1:
                    done_lbl = "10 TITLES"
                else:
                    done_lbl = ""
                GLib.idle_add(self._set_node_status, node_id, "done", 1.0, "DONE", done_lbl)
                if last_music_dir:
                    if node_id in ("bg_remove", "suno_cover"):
                        GLib.idle_add(open_pictures_dir, last_music_dir)
                    elif node_id == "title_generator":
                        pass
                    else:
                        GLib.idle_add(open_music_dir, last_music_dir)
                GLib.idle_add(self._schedule_reset, node_id, 3500)
            else:
                GLib.idle_add(self._schedule_reset, node_id, 3500)

            st["job_queue"].task_done()

    def on_draw(self, _widget, cr: cairo.Context):
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # 0. Sovereign Financial Wings (Upper Forex Calendar & Lower Crypto Telemetry)
        try:
            financial_orbit.radar.draw_financial_wings(cr, self.cx, self.cy, self.ui_scale, 1.0)
        except Exception:
            pass

        # 1. Subtle orbital guide ring connecting the 8 outer nodes
        cr.save()
        cr.new_path()
        cr.set_source_rgba(0.0, 0.88, 1.0, 0.35)
        cr.set_line_width(1.4 * self.ui_scale)
        cr.set_dash([6.0 * self.ui_scale, 8.0 * self.ui_scale])
        cr.arc(self.cx, self.cy, self.r_orbit, 0, 2.0 * math.pi)
        cr.stroke()
        cr.new_path()
        cr.restore()

        # 2. Draw the 8 outer orbital tool nodes
        for idx, node in enumerate(self.nodes):
            nx, ny = self._node_center(idx)
            if node["active"]:
                self._draw_active_node(cr, idx, nx, ny, node)
            else:
                self._draw_placeholder_node(cr, idx, nx, ny, node)

        # 3. Draw inner Center Purge (F-CLEANER) + 6-Sector Irisan Menu
        self._draw_inner_irisan_and_cleaner(cr)

        return False

    def _draw_inner_irisan_and_cleaner(self, cr: cairo.Context):
        p = self.progress
        cx, cy = self.cx, self.cy
        ui_scale = self.ui_scale
        pctx = PangoCairo.create_context(cr)
        layout = Pango.Layout.new(pctx)
        self.card_hitboxes = []

        r_in = self.r_in
        r_out = self.r_out

        sectors = [
            ("fxcalc", 302, 358, 330, C_GREEN, "FXCALC", "Forex Position Calc", self.fxcalc_apps, True, "right", -140, -10),
            ("internet", 2, 58, 30, C_CYAN, "WEB", "Browser & Network", self.internet_apps, True, "right", -40, 10),
            ("media", 62, 118, 90, C_AMBER, "MEDIA", "3D, Audio & Video", self.media_apps, True, "right", 60, -10),
            ("shutdown", 122, 178, 150, C_RED, "TIMER", "Shutdown Timer", self.sistem_apps, True, "left", 60, 10),
            ("oracle", 182, 238, 210, C_MINT, "TAROT", "Sovereign Oracle", self.oracle_apps, True, "left", -40, -10),
            ("trending", 242, 298, 270, C_GOLD, "TRENDING", "GitHub & Tech", self.trending_items, False, "left", -140, 10),
        ]

        if p > 0.01:
            # Draw 6 annular sectors blooming on hover
            p_sec = p
            for sid, d1, d2, d_mid, col, title, sub, _items, _is_app, _side, _by, _stag in sectors:
                is_active = self.active_sector == sid
                is_hovered = self.hovered_sector == sid

                a1 = math.radians(d1)
                a2 = math.radians(d2)
                r_o = r_out + (10.0 * ui_scale if is_active else (6.0 * ui_scale if is_hovered else 0.0))
                r_i = r_in

                cr.new_path()
                cr.arc(cx, cy, r_o, a1, a2)
                cr.arc_negative(cx, cy, r_i, a2, a1)
                cr.close_path()

                if is_active:
                    cr.set_source_rgba(col[0] * 0.22, col[1] * 0.22, col[2] * 0.22, 0.92 * p_sec)
                elif is_hovered:
                    cr.set_source_rgba(col[0] * 0.14, col[1] * 0.14, col[2] * 0.14, 0.88 * p_sec)
                else:
                    cr.set_source_rgba(0.01, 0.04, 0.09, 0.78 * p_sec)
                cr.fill_preserve()

                cr.set_line_width((2.2 if is_active else (1.8 if is_hovered else 1.0)) * ui_scale)
                cr.set_source_rgba(*col, (0.95 if is_active else (0.85 if is_hovered else 0.45)) * p_sec)
                cr.stroke()

                # Outer accent arc
                cr.new_path()
                cr.arc(cx, cy, r_o - 2.0 * ui_scale, a1 + 0.02, a2 - 0.02)
                cr.set_line_width((3.0 if is_active else 2.0) * ui_scale)
                cr.set_source_rgba(*col, (1.0 if is_active else (0.90 if is_hovered else 0.60)) * p_sec)
                cr.stroke()

                # Sector label
                rad_mid = math.radians(d_mid)
                r_txt = (r_i + r_o) / 2.0
                tx = cx + r_txt * math.cos(rad_mid)
                ty = cy + r_txt * math.sin(rad_mid)

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.0"))
                layout.set_text(title, -1)
                tw, th = layout.get_pixel_size()
                t_col = C_WHITE if (is_active or is_hovered) else col
                cr.set_source_rgba(*t_col, (1.0 if is_active else (0.90 if is_hovered else 0.80)) * p_sec)
                cr.move_to(tx - tw / 2.0, ty - th / 2.0 - 6)
                PangoCairo.show_layout(cr, layout)

                layout.set_font_description(Pango.FontDescription("JetBrains Mono 6.5"))
                layout.set_text(sub.split(" ")[0], -1)
                tw2, th2 = layout.get_pixel_size()
                sub_col = col if is_active else C_MUTED
                cr.set_source_rgba(*sub_col, (0.90 if is_active else (0.75 if is_hovered else 0.55)) * p_sec)
                cr.move_to(tx - tw2 / 2.0, ty - th2 / 2.0 + 8)
                PangoCairo.show_layout(cr, layout)
        else:
            # Idle first layer guide ring (exact circle where the 8 nodes touch)
            cr.save()
            cr.new_path()
            cr.set_dash([4.0 * ui_scale, 6.0 * ui_scale])
            cr.set_line_width(1.0 * ui_scale)
            cr.set_source_rgba(0.0, 0.95, 0.65, 0.22)
            cr.arc(cx, cy, self.r_out, 0, 2.0 * math.pi)
            cr.stroke()
            cr.new_path()
            # Subtle inner core guide ring
            cr.set_dash([3.0 * ui_scale, 5.0 * ui_scale])
            cr.set_source_rgba(*C_CYAN, 0.16)
            cr.arc(cx, cy, self.r_in, 0, 2.0 * math.pi)
            cr.stroke()
            cr.new_path()
            cr.restore()

        # Center Core (F-CLEANER / Purge)
        now_ts = time.time()
        core_p = 1.0 if (
            self.cleaner_running
            or (self.cleaner_status_text and now_ts < self.cleaner_status_until)
            or self.hovered_core
            or self.hovered_cleaner
        ) else p

        if core_p > 0.01:
            cr.new_path()
            cr.arc(cx, cy, self.r_core, 0, 2 * math.pi)
            cr.set_source_rgba(0.00, 0.04, 0.08, (0.90 if self.hovered_core else 0.82) * core_p)
            cr.fill_preserve()
            core_border_col = C_WHITE if self.hovered_core else C_CYAN
            cr.set_line_width((2.2 if self.hovered_core else 1.5) * ui_scale)
            cr.set_source_rgba(*core_border_col, (0.95 if self.hovered_core else 0.70) * core_p)
            cr.stroke()

            # Rotating inner scanner arc
            cr.new_path()
            cr.arc(cx, cy, self.r_core - 6.0 * ui_scale, self.rot_angle, self.rot_angle + math.pi * 0.6)
            cr.set_line_width(2.0 * ui_scale)
            cr.set_source_rgba(*C_CYAN, 0.85 * core_p)
            cr.stroke()

            cr.new_path()
            cr.arc(cx, cy, self.r_core - 6.0 * ui_scale, self.rot_angle + math.pi, self.rot_angle + math.pi * 1.6)
            cr.set_source_rgba(*C_GREEN, 0.75 * core_p)
            cr.stroke()

            if self.cleaner_running:
                core_col = (1.00, 0.72, 0.15)
                sub_txt = "PURGING..."
                pill_col = (1.00, 0.72, 0.15)
                pill_label = "PURGING..."
            elif self.cleaner_status_text and now_ts < self.cleaner_status_until:
                core_col = C_GREEN
                sub_txt = self.cleaner_status_text
                pill_col = C_GREEN
                pill_label = "CLEANED"
            else:
                core_col = C_CYAN if self.hovered_core else C_GREEN
                sub_txt = "HEADLESS CORE"
                pill_col = C_CYAN if self.hovered_cleaner else C_GREEN
                pill_label = "PURGE NOW"

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10.0"))
            layout.set_text("• F-CLEANER", -1)
            tw, _th = layout.get_pixel_size()
            cr.set_source_rgba(*core_col, 0.98 * core_p)
            cr.move_to(cx - tw / 2.0, cy - 34 * ui_scale)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.0"))
            layout.set_text(sub_txt, -1)
            tw_t, _th_t = layout.get_pixel_size()
            cr.set_source_rgba(*C_WHITE, 0.85 * core_p)
            cr.move_to(cx - tw_t / 2.0, cy - 15 * ui_scale)
            PangoCairo.show_layout(cr, layout)

            pill_w = 112.0 * ui_scale
            pill_h = 24.0 * ui_scale
            pill_x = cx - pill_w / 2.0
            pill_y = cy + 8.0 * ui_scale
            draw_rounded_rect(cr, pill_x, pill_y, pill_w, pill_h, 12.0 * ui_scale)
            cr.set_source_rgba(pill_col[0] * 0.22, pill_col[1] * 0.22, pill_col[2] * 0.22, (0.95 if self.hovered_cleaner else 0.82) * core_p)
            cr.fill_preserve()
            cr.set_line_width((1.8 if self.hovered_cleaner else 1.2) * ui_scale)
            cr.set_source_rgba(*pill_col, (1.0 if self.hovered_cleaner else 0.85) * core_p)
            cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.0"))
            layout.set_text(pill_label, -1)
            tw_p, th_p = layout.get_pixel_size()
            cr.set_source_rgba(*C_WHITE, 0.98 * core_p)
            cr.move_to(cx - tw_p / 2.0, pill_y + (pill_h - th_p) / 2.0)
            PangoCairo.show_layout(cr, layout)
        else:
            # Clean optical aperture allowing the ambient holographic reactor core to shine through
            cr.save()
            cr.arc(cx, cy, self.r_core * 0.42, 0, 2 * math.pi)
            cr.set_line_width(1.2 * ui_scale)
            cr.set_source_rgba(*C_CYAN, 0.40)
            cr.stroke()
            cr.restore()

        # Targeted Bloom Cards (placed cleanly OUTSIDE the 8 orbital nodes!)
        if self.active_sector is not None and self.cluster_progress > 0.02:
            cp = self.cluster_progress
            cur_sec = next((s for s in sectors if s[0] == self.active_sector), None)
            if cur_sec:
                sid, _d1, _d2, d_mid, col, title, _sub, items, is_app, side, by_off, x_stagger = cur_sec
                card_w = min(360, max(210, int((self.width - (self.r_orbit * 2 + self.r_node * 2 + 120 * ui_scale)) * 0.46)))
                card_h = max(40, int(round(52 * ui_scale)))
                gap = max(6, int(round(8 * ui_scale)))

                outer_edge = self.r_orbit + self.r_node + 36.0 * ui_scale
                if side == "right":
                    bx = cx + outer_edge + x_stagger * ui_scale
                    bx = min(bx, self.width - card_w - 20)
                else:
                    bx = cx - outer_edge - card_w + x_stagger * ui_scale
                    bx = max(20, bx)

                by = cy + by_off * ui_scale
                total_h = len(items) * (card_h + gap)
                by = max(40, min(self.height - total_h - 20, by))

                rad_mid = math.radians(d_mid)
                sx = cx + (r_out + 6.0 * ui_scale) * math.cos(rad_mid)
                sy = cy + (r_out + 6.0 * ui_scale) * math.sin(rad_mid)
                ex = bx if side == "right" else (bx + card_w)
                ey = by + 18.0 * ui_scale

                cr.new_path()
                cr.move_to(sx, sy)
                cr.line_to(ex, ey)
                cr.set_line_width(1.5 * ui_scale)
                cr.set_source_rgba(*col, 0.75 * cp)
                cr.stroke()

                cr.new_path()
                cr.arc(sx, sy, 3.5 * ui_scale, 0, 2 * math.pi)
                cr.set_source_rgba(*col, 0.95 * cp)
                cr.fill()

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10.0"))
                header_title = f"[ {title} // APPLICATIONS ]" if is_app else f"[ {title} // LIVE FEEDS ]"
                layout.set_text(header_title, -1)
                cr.set_source_rgba(*col, 0.95 * cp)
                cr.move_to(bx, by - 22 * ui_scale)
                PangoCairo.show_layout(cr, layout)

                for idx, item in enumerate(items):
                    iy = by + idx * (card_h + gap)
                    is_hov = self.hovered_card == (sid, idx)

                    draw_rounded_rect(cr, bx, iy, card_w, card_h, 8.0 * ui_scale)
                    if is_hov:
                        cr.set_source_rgba(col[0] * 0.18, col[1] * 0.18, col[2] * 0.18, 0.94 * cp)
                    else:
                        cr.set_source_rgba(0.01, 0.04, 0.09, 0.86 * cp)
                    cr.fill_preserve()

                    cr.set_line_width((1.8 if is_hov else 1.0) * ui_scale)
                    cr.set_source_rgba(*col, (0.95 if is_hov else 0.45) * cp)
                    cr.stroke()

                    badge = item.get("badge", "APP")
                    bw_b = 52.0 * ui_scale
                    bh_b = 20.0 * ui_scale
                    draw_rounded_rect(cr, bx + 10 * ui_scale, iy + (card_h - bh_b) / 2.0, bw_b, bh_b, 4.0 * ui_scale)
                    cr.set_source_rgba(*col, (0.28 if is_hov else 0.16) * cp)
                    cr.fill_preserve()
                    cr.set_line_width(0.8 * ui_scale)
                    cr.set_source_rgba(*col, 0.70 * cp)
                    cr.stroke()

                    layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
                    layout.set_text(badge, -1)
                    btw, bth = layout.get_pixel_size()
                    cr.set_source_rgba(*col, 0.95 * cp)
                    cr.move_to(bx + 10 * ui_scale + (bw_b - btw) / 2.0, iy + (card_h - bth) / 2.0)
                    PangoCairo.show_layout(cr, layout)

                    tx_c = bx + 72 * ui_scale
                    layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.5"))
                    layout.set_text(item.get("name", ""), -1)
                    layout.set_width(int((card_w - 84 * ui_scale) * Pango.SCALE))
                    layout.set_ellipsize(Pango.EllipsizeMode.END)
                    cr.set_source_rgba(*C_WHITE, (1.0 if is_hov else 0.92) * cp)
                    cr.move_to(tx_c, iy + 8 * ui_scale)
                    PangoCairo.show_layout(cr, layout)

                    layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
                    layout.set_text(item.get("meta", ""), -1)
                    cr.set_source_rgba(*C_MUTED, (0.90 if is_hov else 0.70) * cp)
                    cr.move_to(tx_c, iy + 27 * ui_scale)
                    PangoCairo.show_layout(cr, layout)
                    layout.set_width(-1)

                    atype = "cmd" if is_app else "url"
                    target = item.get("cmd") if is_app else item.get("url")
                    self.card_hitboxes.append((bx, iy, card_w, card_h, sid, idx, atype, target))

    def _draw_node_icon(self, cr: cairo.Context, node_id: str, nx: float, ny: float, s: float, glow_rgb: tuple):
        cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.95)
        cr.set_line_width(1.8 * s)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)

        if node_id == "vocal_master":
            mic_y = ny - 11.0 * s
            mw = 5.5 * s
            mh = 10.0 * s
            cr.arc(nx, mic_y - mh * 0.35, mw, math.pi, 0)
            cr.line_to(nx + mw, mic_y + mh * 0.35)
            cr.arc(nx, mic_y + mh * 0.35, mw, 0, math.pi)
            cr.close_path()
            cr.stroke()
            cr.arc(nx, mic_y + mh * 0.35, mw + 3.5 * s, 0.15, math.pi - 0.15)
            cr.stroke()
            cr.move_to(nx, mic_y + mh * 0.35 + mw + 3.5 * s)
            cr.line_to(nx, mic_y + mh * 0.35 + mw + 7.5 * s)
            cr.move_to(nx - 5.5 * s, mic_y + mh * 0.35 + mw + 7.5 * s)
            cr.line_to(nx + 5.5 * s, mic_y + mh * 0.35 + mw + 7.5 * s)
            cr.stroke()
            for side in (-1.0, 1.0):
                bx = nx + side * 13.5 * s
                cr.move_to(bx, mic_y - 3.0 * s)
                cr.line_to(bx, mic_y + 5.0 * s)
                bx2 = nx + side * 18.5 * s
                cr.move_to(bx2, mic_y - 1.0 * s)
                cr.line_to(bx2, mic_y + 3.0 * s)
            cr.stroke()
        elif node_id == "stem_split":
            cy_icon = ny - 9.0 * s
            cr.move_to(nx - 18.0 * s, cy_icon)
            cr.line_to(nx - 7.0 * s, cy_icon)
            cr.stroke()
            cr.arc(nx - 6.0 * s, cy_icon, 2.2 * s, 0, 2.0 * math.pi)
            cr.fill()

            cr.move_to(nx - 4.5 * s, cy_icon - 1.0 * s)
            cr.line_to(nx + 3.0 * s, cy_icon - 8.0 * s)
            cr.line_to(nx + 8.0 * s, cy_icon - 8.0 * s)
            cr.stroke()
            for i, h in enumerate((3.0, 5.5, 3.5)):
                wx = nx + (11.0 + i * 3.5) * s
                cr.move_to(wx, cy_icon - 8.0 * s - h * s)
                cr.line_to(wx, cy_icon - 8.0 * s + h * s)
            cr.stroke()

            cr.move_to(nx - 4.5 * s, cy_icon + 1.0 * s)
            cr.line_to(nx + 3.0 * s, cy_icon + 8.0 * s)
            cr.line_to(nx + 8.0 * s, cy_icon + 8.0 * s)
            cr.stroke()
            cr.arc(nx + 11.5 * s, cy_icon + 10.5 * s, 2.2 * s, 0, 2.0 * math.pi)
            cr.fill()
            cr.arc(nx + 18.0 * s, cy_icon + 9.5 * s, 2.2 * s, 0, 2.0 * math.pi)
            cr.fill()
            cr.move_to(nx + 13.3 * s, cy_icon + 10.5 * s)
            cr.line_to(nx + 13.3 * s, cy_icon + 3.0 * s)
            cr.line_to(nx + 19.8 * s, cy_icon + 2.0 * s)
            cr.line_to(nx + 19.8 * s, cy_icon + 9.5 * s)
            cr.stroke()
        elif node_id in ("auto_lyric", "title_generator"):
            # Title Document Sheet with Headline Banner & Text Lines
            cy_icon = ny - 8.5 * s
            cr.set_line_width(1.5 * s)
            w_sh = 8.0 * s
            h_sh = 10.5 * s
            cr.move_to(nx - w_sh, cy_icon - h_sh)
            cr.line_to(nx + w_sh - 4.0 * s, cy_icon - h_sh)
            cr.line_to(nx + w_sh, cy_icon - h_sh + 4.0 * s)
            cr.line_to(nx + w_sh, cy_icon + h_sh)
            cr.line_to(nx - w_sh, cy_icon + h_sh)
            cr.close_path()
            cr.stroke()
            # Fold corner
            cr.move_to(nx + w_sh - 4.0 * s, cy_icon - h_sh)
            cr.line_to(nx + w_sh - 4.0 * s, cy_icon - h_sh + 4.0 * s)
            cr.line_to(nx + w_sh, cy_icon - h_sh + 4.0 * s)
            cr.stroke()
            # Top headline bar
            cr.set_line_width(2.2 * s)
            cr.move_to(nx - w_sh + 3.0 * s, cy_icon - 3.5 * s)
            cr.line_to(nx + w_sh - 3.0 * s, cy_icon - 3.5 * s)
            cr.stroke()
            # 2 text lines
            cr.set_line_width(1.2 * s)
            for ly_off in [1.5 * s, 5.5 * s]:
                cr.move_to(nx - w_sh + 3.0 * s, cy_icon + ly_off)
                cr.line_to(nx + w_sh - 5.0 * s, cy_icon + ly_off)
                cr.stroke()
        elif node_id == "bg_remove":
            # Layered cutout frame + subject silhouette icon
            cy_icon = ny - 9.0 * s
            cr.set_line_width(1.6 * s)
            cr.set_dash([2.5 * s, 2.0 * s])
            cr.rectangle(nx - 12.0 * s, cy_icon - 10.0 * s, 16.0 * s, 16.0 * s)
            cr.stroke()
            cr.set_dash([])
            cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.28)
            cr.rectangle(nx - 4.0 * s, cy_icon - 4.0 * s, 16.0 * s, 16.0 * s)
            cr.fill()
            cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.95)
            cr.rectangle(nx - 4.0 * s, cy_icon - 4.0 * s, 16.0 * s, 16.0 * s)
            cr.stroke()
            cr.arc(nx + 4.0 * s, cy_icon + 1.5 * s, 3.0 * s, 0, 2.0 * math.pi)
            cr.fill()
            cr.arc(nx + 4.0 * s, cy_icon + 10.5 * s, 5.2 * s, math.pi, 2.0 * math.pi)
            cr.fill()
        elif node_id == "suno_59s":
            # Fast-forward double chevron inside speed-timer arc
            cy_icon = ny - 8.5 * s
            cr.set_line_width(1.8 * s)
            cr.arc(nx, cy_icon, 11.5 * s, -math.pi * 0.82, math.pi * 0.62)
            cr.stroke()
            # Left chevron
            cr.move_to(nx - 6.5 * s, cy_icon - 5.0 * s)
            cr.line_to(nx + 0.5 * s, cy_icon)
            cr.line_to(nx - 6.5 * s, cy_icon + 5.0 * s)
            cr.close_path()
            cr.fill()
            # Right chevron
            cr.move_to(nx + 0.5 * s, cy_icon - 5.0 * s)
            cr.line_to(nx + 7.5 * s, cy_icon)
            cr.line_to(nx + 0.5 * s, cy_icon + 5.0 * s)
            cr.close_path()
            cr.fill()
        elif node_id == "suno_cover":
            # Split 16:9 thumbnail frame with center lightning bolt
            cy_icon = ny - 8.5 * s
            cr.set_line_width(1.6 * s)
            cr.rectangle(nx - 13.0 * s, cy_icon - 8.5 * s, 26.0 * s, 17.0 * s)
            cr.stroke()
            # Center lightning bolt
            cr.move_to(nx + 1.5 * s, cy_icon - 8.0 * s)
            cr.line_to(nx - 3.0 * s, cy_icon + 0.5 * s)
            cr.line_to(nx + 0.5 * s, cy_icon + 0.5 * s)
            cr.line_to(nx - 1.5 * s, cy_icon + 8.0 * s)
            cr.line_to(nx + 3.5 * s, cy_icon - 0.5 * s)
            cr.line_to(nx - 0.2 * s, cy_icon - 0.5 * s)
            cr.close_path()
            cr.fill()
        elif node_id == "renderer_4k":
            # 4K Ultra HD Display & Play badge
            cy_icon = ny - 8.5 * s
            cr.set_line_width(1.6 * s)
            # Widescreen 16:9 monitor frame
            cr.rectangle(nx - 13.5 * s, cy_icon - 8.0 * s, 27.0 * s, 15.5 * s)
            cr.stroke()
            # Stand base
            cr.move_to(nx - 4.5 * s, cy_icon + 7.5 * s)
            cr.line_to(nx - 4.5 * s, cy_icon + 10.5 * s)
            cr.line_to(nx + 4.5 * s, cy_icon + 10.5 * s)
            cr.line_to(nx + 4.5 * s, cy_icon + 7.5 * s)
            cr.stroke()
            # Center play triangle
            cr.move_to(nx - 3.2 * s, cy_icon - 4.2 * s)
            cr.line_to(nx + 4.2 * s, cy_icon)
            cr.line_to(nx - 3.2 * s, cy_icon + 4.2 * s)
            cr.close_path()
            cr.fill()
        elif node_id == "file_manager":
            # High-tech Cyber Folder Icon
            cy_icon = ny - 8.5 * s
            cr.set_line_width(1.6 * s)
            # Folder Back & Tab Outline
            cr.move_to(nx - 13.0 * s, cy_icon - 3.5 * s)
            cr.line_to(nx - 13.0 * s, cy_icon - 7.5 * s)
            cr.line_to(nx - 5.0 * s, cy_icon - 7.5 * s)
            cr.line_to(nx - 2.0 * s, cy_icon - 4.5 * s)
            cr.line_to(nx + 13.0 * s, cy_icon - 4.5 * s)
            cr.line_to(nx + 13.0 * s, cy_icon + 7.5 * s)
            cr.line_to(nx - 13.0 * s, cy_icon + 7.5 * s)
            cr.close_path()
            cr.stroke()
            # Front flap divider
            cr.move_to(nx - 13.0 * s, cy_icon - 1.0 * s)
            cr.line_to(nx + 13.0 * s, cy_icon - 1.0 * s)
            cr.stroke()
            # Mini inner document / files badge
            cr.rectangle(nx - 4.5 * s, cy_icon + 1.2 * s, 9.0 * s, 4.5 * s)
            cr.fill()

    def _draw_active_node(self, cr: cairo.Context, idx: int, nx: float, ny: float, node: dict):
        cr.save()
        cr.new_path()
        s = self.ui_scale
        r = self.r_node
        st = self.node_states[node["id"]]
        state = st["state"]
        is_hover = self.hovered_node == idx
        is_drag = self.drag_hover_node == idx

        node_accent = node.get("accent_rgb", (0.0, 0.90, 1.0))
        node_bg_in = node.get("bg_inner_rgb", (0.05, 0.14, 0.22))
        node_bg_out = node.get("bg_outer_rgb", (0.02, 0.06, 0.11))

        if state == "error":
            glow_rgb = (1.0, 0.28, 0.36)
        elif state == "done":
            glow_rgb = (0.08, 0.94, 0.62)
        elif state == "staged":
            glow_rgb = (1.0, 0.82, 0.12)
        elif is_drag or is_hover:
            glow_rgb = (min(1.0, node_accent[0] * 1.2 + 0.1),
                        min(1.0, node_accent[1] * 1.2 + 0.1),
                        min(1.0, node_accent[2] * 1.2 + 0.1))
        else:
            glow_rgb = node_accent

        pulse = 0.5 + 0.5 * math.sin(self.phase * 2.0 + idx * 0.7)
        r_draw = r * (1.08 if is_drag else (1.04 if is_hover else 1.0))

        halo = cairo.RadialGradient(nx, ny, r_draw * 0.5, nx, ny, r_draw * 1.45)
        halo_alpha = 0.42 if (is_drag or state == "processing") else (0.30 if is_hover else 0.18)
        halo.add_color_stop_rgba(0.0, glow_rgb[0], glow_rgb[1], glow_rgb[2], halo_alpha)
        halo.add_color_stop_rgba(1.0, glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.0)
        cr.set_source(halo)
        cr.arc(nx, ny, r_draw * 1.45, 0, 2.0 * math.pi)
        cr.fill()

        bg = cairo.RadialGradient(nx, ny - r_draw * 0.25, 2.0, nx, ny, r_draw)
        bg.add_color_stop_rgba(0.0, node_bg_in[0], node_bg_in[1], node_bg_in[2], 0.92)
        bg.add_color_stop_rgba(1.0, node_bg_out[0], node_bg_out[1], node_bg_out[2], 0.96)
        cr.set_source(bg)
        cr.arc(nx, ny, r_draw, 0, 2.0 * math.pi)
        cr.fill()

        cr.set_line_width(1.2 * s)
        cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.28)
        cr.arc(nx, ny, r_draw - 5.0 * s, 0, 2.0 * math.pi)
        cr.stroke()

        cr.set_line_width((2.4 if (is_hover or is_drag) else 1.8) * s)
        cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.85 if (is_hover or is_drag) else (0.55 + 0.20 * pulse))
        cr.arc(nx, ny, r_draw, 0, 2.0 * math.pi)
        cr.stroke()

        if state == "processing":
            start_ang = -math.pi / 2.0
            end_ang = start_ang + max(0.03, st["display_progress"]) * 2.0 * math.pi
            cr.set_line_width(4.0 * s)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_source_rgba(0.0, 0.95, 1.0, 0.98)
            cr.arc(nx, ny, r_draw + 4.0 * s, start_ang, end_ang)
            cr.stroke()

            scan_a = self.phase * 2.2
            cr.set_line_width(1.8 * s)
            cr.set_source_rgba(0.45, 1.0, 0.92, 0.75)
            cr.arc(nx, ny, r_draw - 2.5 * s, scan_a, scan_a + 1.1)
            cr.stroke()
        elif state == "done":
            cr.set_line_width(3.5 * s)
            cr.set_source_rgba(0.08, 0.94, 0.62, 0.98)
            cr.arc(nx, ny, r_draw + 4.0 * s, 0, 2.0 * math.pi)
            cr.stroke()

        cr.save()
        if state == "processing":
            pct = int(round(st["display_progress"] * 100))
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(16.0 * s)
            txt = f"{pct}%"
            ext = cr.text_extents(txt)
            cr.set_source_rgba(0.92, 0.99, 1.0, 0.98)
            cr.move_to(nx - ext.width / 2.0 - ext.x_bearing, ny + 2.0 * s)
            cr.show_text(txt)

            cr.set_font_size(7.2 * s)
            cr.set_source_rgba(0.0, 0.92, 1.0, 0.92)
            st_ext = cr.text_extents(st["stage"])
            cr.move_to(nx - st_ext.width / 2.0 - st_ext.x_bearing, ny + 16.0 * s)
            cr.show_text(st["stage"])
        else:
            self._draw_node_icon(cr, node["id"], nx, ny, s, glow_rgb)

            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(7.4 * s)
            cr.set_source_rgba(0.92, 0.98, 1.0, 0.95)
            t1 = node["title"]
            e1 = cr.text_extents(t1)
            cr.move_to(nx - e1.width / 2.0 - e1.x_bearing, ny + 18.0 * s)
            cr.show_text(t1)

            cr.set_font_size(6.6 * s)
            cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.92)
            sub = node.get("sub", "DROP WAV") if state == "idle" else st["stage"]
            if is_drag:
                sub = "RELEASE!"
            e2 = cr.text_extents(sub)
            cr.move_to(nx - e2.width / 2.0 - e2.x_bearing, ny + 28.0 * s)
            cr.show_text(sub)
        cr.restore()

        if st["batch_label"] or is_drag or state == "done":
            pill_txt = st["batch_label"] or (node["drop_pill"] if is_drag else node.get("done_pill", "SAVED TO MUSIC"))
            cr.save()
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(8.5 * s)
            pe = cr.text_extents(pill_txt)
            pw = pe.width + 14.0 * s
            ph = 16.0 * s
            px = nx - pw / 2.0
            py = ny - r_draw - 24.0 * s
            cr.set_source_rgba(node_bg_out[0], node_bg_out[1], node_bg_out[2], 0.94)
            cr.rectangle(px, py, pw, ph)
            cr.fill()
            cr.set_line_width(1.0 * s)
            cr.set_source_rgba(glow_rgb[0], glow_rgb[1], glow_rgb[2], 0.85)
            cr.rectangle(px, py, pw, ph)
            cr.stroke()
            cr.set_source_rgba(0.95, 1.0, 1.0, 0.98)
            cr.move_to(nx - pe.width / 2.0 - pe.x_bearing, py + ph * 0.72)
            cr.show_text(pill_txt)
            cr.restore()
        cr.new_path()
        cr.restore()

    def _draw_placeholder_node(self, cr: cairo.Context, idx: int, nx: float, ny: float, node: dict):
        s = self.ui_scale
        r = self.r_node * 0.88
        is_hover = self.hovered_node == idx

        node_accent = node.get("accent_rgb", (0.00, 0.85, 1.0))
        node_bg_in = node.get("bg_inner_rgb", (0.02, 0.06, 0.11))
        node_bg_out = node.get("bg_outer_rgb", (0.01, 0.03, 0.06))

        cr.save()
        cr.new_path()
        cr.set_source_rgba(node_bg_in[0], node_bg_in[1], node_bg_in[2], 0.65 if is_hover else 0.45)
        cr.arc(nx, ny, r, 0, 2.0 * math.pi)
        cr.fill()

        cr.set_line_width(1.2 * s)
        cr.set_dash([4.0 * s, 4.0 * s])
        cr.set_source_rgba(node_accent[0], node_accent[1], node_accent[2], 0.50 if is_hover else 0.28)
        cr.arc(nx, ny, r, 0, 2.0 * math.pi)
        cr.stroke()
        cr.set_dash([])

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(11.0 * s)
        cr.set_source_rgba(node_accent[0], node_accent[1], node_accent[2], 0.70 if is_hover else 0.45)
        slot_txt = node["slot"]
        se = cr.text_extents(slot_txt)
        cr.move_to(nx - se.width / 2.0 - se.x_bearing, ny + 1.0 * s)
        cr.show_text(slot_txt)

        cr.set_font_size(6.5 * s)
        cr.set_source_rgba(0.70, 0.85, 0.95, 0.55 if is_hover else 0.32)
        sub_txt = "READY"
        sbe = cr.text_extents(sub_txt)
        cr.move_to(nx - sbe.width / 2.0 - sbe.x_bearing, ny + 13.0 * s)
        cr.show_text(sub_txt)
        cr.new_path()
        cr.restore()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    win = UnifiedReactorHudWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
