#!/usr/bin/env python3
"""
MrFlow Router — Native Linux Desktop GUI (GTK3 / PyGObject)
Pure offline native interface. Zero Google Chrome dependency.
Zero prompt injection. Clean engineering terminology.
"""

import sys
import os
import json
import urllib.request
import urllib.error
import threading
import time
import subprocess
import shutil
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf, Pango

def get_base_dir():
    if os.environ.get("FLOWORK_CONNECTOR_DIR") and os.path.isdir(os.environ["FLOWORK_CONNECTOR_DIR"]):
        return os.environ["FLOWORK_CONNECTOR_DIR"]
    if os.environ.get("MRFLOW_CONNECTOR_DIR") and os.path.isdir(os.environ["MRFLOW_CONNECTOR_DIR"]):
        return os.environ["MRFLOW_CONNECTOR_DIR"]
    script_path = os.path.realpath(__file__)
    candidate = os.path.abspath(os.path.join(os.path.dirname(script_path), ".."))
    if os.path.exists(os.path.join(candidate, "bin", "flowork-connector")) or os.path.exists(os.path.join(candidate, "gui", "assets", "icon.png")):
        return candidate
    for p in ["/opt/floworkos/connector", "/opt/floworkos/apps/connector", os.path.expanduser("~/mrflow/connector")]:
        if os.path.exists(os.path.join(p, "bin", "flowork-connector")) or os.path.exists(os.path.join(p, "gui", "assets", "icon.png")):
            return p
    return candidate

BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "gui", "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.png")

PORT = 9099
BASE_URL = f"http://127.0.0.1:{PORT}"

DARK_CSS = b"""
window, dialog {
    background-color: #0d1826;
    color: #f1f5f9;
    font-family: 'Inter', 'Segoe UI', 'Ubuntu', sans-serif;
}

headerbar, .header-card {
    background: linear-gradient(180deg, #16283f 0%, #0e1c2d 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    padding: 14px 20px;
}

.glass-panel {
    background: linear-gradient(135deg, #16273e 0%, #111e30 100%);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.card {
    background: linear-gradient(135deg, #14243b 0%, #0f1c2e 100%);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

button {
    background: linear-gradient(180deg, #1e334f 0%, #16273d 100%);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 10px;
    padding: 7px 16px;
    font-weight: 600;
    transition: all 150ms ease-in-out;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

button:hover {
    background: linear-gradient(180deg, #274368 0%, #1c324f 100%);
    border-color: rgba(56, 189, 248, 0.6);
    box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25);
}

button:active {
    background: #142338;
}

button.suggested-action, .btn-emerald {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.85) 0%, rgba(5, 150, 105, 0.75) 100%);
    border: 1px solid rgba(255, 255, 255, 0.35);
    color: #ffffff;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
}

button.suggested-action:hover, .btn-emerald:hover {
    background: linear-gradient(135deg, rgba(52, 211, 153, 0.9) 0%, rgba(16, 185, 129, 0.85) 100%);
    border-color: rgba(255, 255, 255, 0.5);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
}

button.destructive-action, .btn-danger {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.8) 0%, rgba(185, 28, 28, 0.7) 100%);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #ffffff;
}

button.destructive-action:hover, .btn-danger:hover {
    background: linear-gradient(135deg, rgba(248, 113, 113, 0.9) 0%, rgba(220, 38, 38, 0.85) 100%);
}

.btn-preset {
    background: linear-gradient(135deg, rgba(30, 58, 138, 0.6) 0%, rgba(30, 41, 59, 0.7) 100%);
    border: 1px solid rgba(96, 165, 250, 0.45);
    color: #93c5fd;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
}

.btn-preset:hover {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.85) 0%, rgba(30, 58, 138, 0.85) 100%);
    border-color: #60a5fa;
    color: #ffffff;
}

.btn-chip {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #cbd5e1;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
}

.btn-chip:hover {
    background: rgba(56, 189, 248, 0.25);
    border-color: #38bdf8;
    color: #ffffff;
}

entry {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 12px;
    padding: 8px 14px;
}

entry:focus {
    border-color: #38bdf8;
    background: rgba(255, 255, 255, 0.12);
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
}

treeview {
    background-color: #0b1523;
    color: #f1f5f9;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
}

treeview:selected {
    background: linear-gradient(90deg, rgba(14, 165, 233, 0.5) 0%, rgba(14, 165, 233, 0.2) 100%);
    color: #ffffff;
}

treeview header button {
    background: #14243b;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
    padding: 6px;
}

.badge-online {
    background: rgba(16, 185, 129, 0.2);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.45);
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: bold;
}

.badge-offline {
    background: rgba(239, 68, 68, 0.2);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.45);
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: bold;
}

.badge-user {
    background: rgba(56, 189, 248, 0.18);
    color: #7dd3fc;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: bold;
}

stackswitcher button {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 10px;
    margin-right: 4px;
}

stackswitcher button:checked {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.75) 0%, rgba(2, 132, 199, 0.65) 100%);
    border: 1px solid rgba(255, 255, 255, 0.35);
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
}

/* Antigravity Model Selector Dropdown & Menus - 100% Solid Dark / Zero Transparency */
menu, .antigravity-menu, popover, popover.background, window.popup {
    background-color: #121721;
    background-image: none;
    color: #f1f5f9;
    border: 1px solid #23354a;
    border-radius: 8px;
    padding: 6px 4px;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.95);
    opacity: 1.0;
}

menuitem {
    background-color: #121721;
    background-image: none;
    color: #e2e8f0;
    padding: 7px 12px;
    margin: 1px 2px;
    border-radius: 6px;
    font-size: 13px;
    opacity: 1.0;
    border: 1px solid transparent;
}

menuitem:hover {
    background-color: #1a2738;
    background-image: none;
    color: #00ff66;
    border: 1px solid rgba(0, 255, 102, 0.3);
}

menuitem:disabled {
    color: #64748b;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
    padding: 6px 12px 4px 12px;
    background-color: transparent;
}

menuitem label {
    color: #e2e8f0;
    font-weight: 500;
}

menuitem:hover label {
    color: #00ff66;
    font-weight: 600;
}

menuitem:disabled label {
    color: #64748b;
    font-size: 11px;
    font-weight: bold;
}

menuitem arrow {
    color: #94a3b8;
    min-height: 12px;
    min-width: 12px;
}

menuitem:hover arrow {
    color: #00ff66;
}

.antigravity-model-btn {
    background: #0d1520;
    border: 1px solid #1f334d;
    border-radius: 8px;
    padding: 7px 14px;
    color: #f1f5f9;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.antigravity-model-btn:hover {
    border-color: #00ff66;
    background: #121e2e;
    box-shadow: 0 0 14px rgba(0, 255, 102, 0.25);
}

/* Base Window, Containers & FlowBox (Solid, never transparent) */
window, dialog, .window, .dialog {
    background-color: #0b121b;
    color: #f1f5f9;
}

scrolledwindow, viewport {
    background-color: transparent;
    border: none;
}

flowbox, flowboxchild {
    background-color: transparent;
    border: none;
    padding: 0;
}

treeview, treeview.view {
    background-color: #0c1522;
    color: #f1f5f9;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
}

treeview.view:selected, treeview:selected {
    background: #162c44;
    color: #00ff66;
}

treeview header button {
    background: #111c2c;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
    padding: 6px;
}
"""

class MrFlowRouterWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="MrFlow Router")

        # Responsive sizing for small & large monitors (laptops, 720p, 1080p, 4K)
        display = Gdk.Display.get_default()
        screen_w = 1280
        screen_h = 768
        if display:
            monitor = display.get_primary_monitor() or (display.get_monitor(0) if display.get_n_monitors() > 0 else None)
            if monitor:
                geom = monitor.get_geometry()
                screen_w = geom.width
                screen_h = geom.height

        # Start at comfortable compact size
        target_w = min(820, max(460, int(screen_w * 0.65)))
        target_h = min(580, max(360, int(screen_h * 0.70)))
        self.set_default_size(target_w, target_h)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)

        # Allow dragging smaller down to compact netbook sizes (e.g. 440x320)
        geom_hints = Gdk.Geometry()
        geom_hints.min_width = 440
        geom_hints.min_height = 320
        self.set_geometry_hints(None, geom_hints, Gdk.WindowHints.MIN_SIZE)

        # Set App Icon
        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except Exception:
                pass

        # Apply Dark Theme CSS with USER priority (800) so it cannot be overridden
        self.apply_css()

        self.current_state = {}
        self.active_provider = "connector"
        self.accounts_data = []
        self.connector_models = []
        self.grouped_models_data = {}
        self.active_model = ""
        self._last_models_sync_ts = 0.0

        # Build Main Layout
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # 1. Top Header Bar
        header = self.build_header()
        main_vbox.pack_start(header, False, False, 0)

        # 2. Provider Navigation Stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(180)

        # Tab 1: Sovereign Connector
        self.connector_view = self.build_connector_tab()
        self.stack.add_titled(self.connector_view, "connector", "Connector")

        # Tab 2: Ollama Local Engine
        self.ollama_view = self.build_ollama_tab()
        self.stack.add_titled(self.ollama_view, "ollama", "Ollama")

        # Tab 3: 9Router Gateway
        self.nine_router_view = self.build_nine_router_tab()
        self.stack.add_titled(self.nine_router_view, "9router", "9Router")

        # Stack Switcher Tab Bar
        switcher_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        switcher_box.set_margin_start(14)
        switcher_box.set_margin_end(14)
        switcher_box.set_margin_top(8)
        switcher_box.set_margin_bottom(6)

        lbl_engine = Gtk.Label(label="<b>Engine:</b>", use_markup=True)
        switcher_box.pack_start(lbl_engine, False, False, 0)

        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        switcher_box.pack_start(self.stack_switcher, True, True, 0)

        btn_activate_engine = Gtk.Button(label="Apply Mode")
        btn_activate_engine.connect("clicked", self.on_apply_engine_clicked)
        switcher_box.pack_start(btn_activate_engine, False, False, 0)

        main_vbox.pack_start(switcher_box, False, False, 0)
        main_vbox.pack_start(self.stack, True, True, 0)

        # 3. Bottom Status Footer
        self.footer_bar = self.build_footer()
        main_vbox.pack_start(self.footer_bar, False, False, 0)

        # Periodic refresh
        GLib.timeout_add(3500, self.auto_refresh_tick)
        self.refresh_status_async()
        self.refresh_models_async(force=False)

    def apply_css(self):
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(DARK_CSS)
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def build_header(self):
        header_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_card.get_style_context().add_class("header-card")

        # Left: App Title and Icon
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        left_box.set_valign(Gtk.Align.CENTER)

        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_PATH, 32, 32, True)
                app_icon = Gtk.Image.new_from_pixbuf(pixbuf)
                app_icon.set_valign(Gtk.Align.CENTER)
                left_box.pack_start(app_icon, False, False, 0)
            except Exception:
                pass

        title_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_vbox.set_valign(Gtk.Align.CENTER)
        title_lbl = Gtk.Label(label="<span size='large' weight='bold'>MrFlow Router</span>", use_markup=True)
        title_lbl.set_xalign(0)
        title_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        sub_lbl = Gtk.Label(label="<span size='small' color='#94a3b8'>Universal AI Gateway &amp; Multi-Account Rotator</span>", use_markup=True)
        sub_lbl.set_xalign(0)
        sub_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        sub_lbl.set_max_width_chars(28)
        title_vbox.pack_start(title_lbl, False, False, 0)
        title_vbox.pack_start(sub_lbl, False, False, 0)
        left_box.pack_start(title_vbox, False, False, 0)
        header_card.pack_start(left_box, False, False, 0)

        # Right: User Passport Badge & Status Badge & Actions in 2-row layout
        header_card.pack_start(Gtk.Box(), True, True, 0)

        right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        right_vbox.set_valign(Gtk.Align.CENTER)

        badges_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        badges_box.set_halign(Gtk.Align.END)

        self.user_badge = Gtk.Label(label="👤 Unauthenticated")
        self.user_badge.get_style_context().add_class("badge-user")
        self.user_badge.set_ellipsize(Pango.EllipsizeMode.END)
        self.user_badge.set_max_width_chars(18)
        badges_box.pack_start(self.user_badge, False, False, 0)

        self.status_badge = Gtk.Label(label="● Checking Server...")
        self.status_badge.get_style_context().add_class("badge-offline")
        self.status_badge.set_ellipsize(Pango.EllipsizeMode.END)
        self.status_badge.set_max_width_chars(16)
        badges_box.pack_start(self.status_badge, False, False, 0)
        right_vbox.pack_start(badges_box, False, False, 0)

        btns_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btns_box.set_halign(Gtk.Align.END)

        self.btn_login = Gtk.Button(label="🔑 Flowork Login")
        self.btn_login.get_style_context().add_class("btn-emerald")
        self.btn_login.connect("clicked", self.on_passport_login_clicked)
        btns_box.pack_start(self.btn_login, False, False, 0)

        self.btn_switch = Gtk.Button(label="🔄 Switch")
        self.btn_switch.get_style_context().add_class("btn-preset")
        self.btn_switch.connect("clicked", self.on_passport_login_clicked)
        self.btn_switch.set_no_show_all(True)
        btns_box.pack_start(self.btn_switch, False, False, 0)

        self.btn_logout = Gtk.Button(label="🚪 Logout")
        self.btn_logout.get_style_context().add_class("btn-danger")
        self.btn_logout.connect("clicked", self.on_passport_logout_clicked)
        self.btn_logout.set_no_show_all(True)
        btns_box.pack_start(self.btn_logout, False, False, 0)
        right_vbox.pack_start(btns_box, False, False, 0)

        header_card.pack_start(right_vbox, False, False, 0)

        return header_card

    def build_connector_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_start(14)
        box.set_margin_end(14)
        box.set_margin_top(8)
        box.set_margin_bottom(12)

        # Responsive Action Toolbar (Wraps on small screens)
        tb_card = Gtk.FlowBox()
        tb_card.get_style_context().add_class("card")
        tb_card.set_selection_mode(Gtk.SelectionMode.NONE)
        tb_card.set_homogeneous(False)
        tb_card.set_min_children_per_line(2)
        tb_card.set_max_children_per_line(10)
        tb_card.set_row_spacing(6)
        tb_card.set_column_spacing(8)

        btn_sync = Gtk.Button(label="☁️ Cloud Sync")
        btn_sync.connect("clicked", self.on_sync_cloud_clicked)
        tb_card.add(btn_sync)

        btn_backup = Gtk.Button(label="⬆️ Cloud Backup")
        btn_backup.connect("clicked", self.on_push_cloud_clicked)
        tb_card.add(btn_backup)

        btn_oauth = Gtk.Button(label="➕ Connect Google")
        btn_oauth.get_style_context().add_class("btn-emerald")
        btn_oauth.connect("clicked", self.on_connect_google_clicked)
        tb_card.add(btn_oauth)

        btn_add_manual = Gtk.Button(label="➕ Add Manual")
        btn_add_manual.connect("clicked", self.on_add_account_dialog)
        tb_card.add(btn_add_manual)

        btn_clear = Gtk.Button(label="⚡ Reset Cooldowns")
        btn_clear.connect("clicked", self.on_clear_cooldowns_clicked)
        tb_card.add(btn_clear)

        btn_refresh = Gtk.Button(label="🔄 Refresh")
        btn_refresh.connect("clicked", lambda _: (self.refresh_status_async(), self.refresh_models_async(force=True)))
        tb_card.add(btn_refresh)

        box.pack_start(tb_card, False, False, 0)

        # Strategy Controls & Summary (Single Focus Exhaustion Queue)
        strat_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        strat_card.get_style_context().add_class("card")

        lbl_strat_badge = Gtk.Label(
            label="<span background='#0c4a6e' foreground='#38bdf8' font_weight='bold'>  ⚡ SINGLE FOCUS ROTATION  </span> <span foreground='#94a3b8' size='small'>Locks on 1 account until limit/error</span>",
            use_markup=True
        )
        lbl_strat_badge.set_ellipsize(Pango.EllipsizeMode.END)
        lbl_strat_badge.set_max_width_chars(42)
        lbl_strat_badge.set_xalign(0)
        strat_card.pack_start(lbl_strat_badge, False, False, 0)

        strat_card.pack_start(Gtk.Box(), True, True, 0)

        self.lbl_pool_summary = Gtk.Label(label="Pool: 0 accounts loaded", use_markup=True)
        self.lbl_pool_summary.set_ellipsize(Pango.EllipsizeMode.END)
        self.lbl_pool_summary.set_max_width_chars(38)
        self.lbl_pool_summary.set_xalign(1)
        strat_card.pack_start(self.lbl_pool_summary, False, False, 0)

        box.pack_start(strat_card, False, False, 0)

        # Active Google Model Selector (Antigravity Style with Submenus)
        model_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        model_card.get_style_context().add_class("card")

        lbl_model_badge = Gtk.Label(
            label="<span background='#064e3b' foreground='#00ff66' font_weight='bold'>  🤖 ACTIVE MODEL  </span>",
            use_markup=True
        )
        model_card.pack_start(lbl_model_badge, False, False, 0)

        # Antigravity MenuButton with hierarchical Gtk.Menu
        self.btn_model_selector = Gtk.MenuButton()
        self.btn_model_selector.set_use_popover(False)
        self.btn_model_selector.get_style_context().add_class("antigravity-model-btn")

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.lbl_active_model_btn = Gtk.Label(label="<b>Loading live models...</b>", use_markup=True)
        self.lbl_active_model_btn.set_xalign(0)
        self.lbl_active_model_btn.set_ellipsize(Pango.EllipsizeMode.END)
        btn_box.pack_start(self.lbl_active_model_btn, True, True, 0)

        lbl_chevron = Gtk.Label(label="▾")
        btn_box.pack_start(lbl_chevron, False, False, 0)

        self.btn_model_selector.add(btn_box)

        self.model_menu = Gtk.Menu()
        self.model_menu.get_style_context().add_class("antigravity-menu")
        self.btn_model_selector.set_popup(self.model_menu)
        model_card.pack_start(self.btn_model_selector, True, True, 0)

        self.lbl_model_sync_status = Gtk.Label(label="<span foreground='#94a3b8'>Syncing...</span>", use_markup=True)
        model_card.pack_start(self.lbl_model_sync_status, False, False, 0)

        btn_sync_models = Gtk.Button(label="🔄 Sync Models")
        btn_sync_models.connect("clicked", lambda _: self.refresh_models_async(force=True))
        model_card.pack_start(btn_sync_models, False, False, 0)

        box.pack_start(model_card, False, False, 0)

        # Accounts TreeView
        # Model columns: [is_active_str, email, status_str, requests_str, last_used_str, account_id]
        self.account_store = Gtk.ListStore(str, str, str, str, str, str)

        self.treeview = Gtk.TreeView(model=self.account_store)

        cell_act = Gtk.CellRendererText()
        col_active = Gtk.TreeViewColumn("Active", cell_act, text=0)
        col_active.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_active.set_fixed_width(55)
        col_active.set_resizable(True)
        self.treeview.append_column(col_active)

        cell_email = Gtk.CellRendererText()
        cell_email.set_property("ellipsize", Pango.EllipsizeMode.END)
        cell_email.set_property("width-chars", 16)
        col_email = Gtk.TreeViewColumn("Account Email", cell_email, text=1)
        col_email.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_email.set_fixed_width(190)
        col_email.set_resizable(True)
        self.treeview.append_column(col_email)

        cell_stat = Gtk.CellRendererText()
        col_status = Gtk.TreeViewColumn("Status", cell_stat, text=2)
        col_status.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_status.set_fixed_width(80)
        col_status.set_resizable(True)
        self.treeview.append_column(col_status)

        cell_req = Gtk.CellRendererText()
        col_reqs = Gtk.TreeViewColumn("Requests", cell_req, text=3)
        col_reqs.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_reqs.set_fixed_width(70)
        col_reqs.set_resizable(True)
        self.treeview.append_column(col_reqs)

        cell_used = Gtk.CellRendererText()
        cell_used.set_property("ellipsize", Pango.EllipsizeMode.END)
        cell_used.set_property("width-chars", 11)
        col_used = Gtk.TreeViewColumn("Last Used", cell_used, text=4)
        col_used.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_used.set_fixed_width(135)
        col_used.set_resizable(True)
        self.treeview.append_column(col_used)

        # Native Tooltip: show full email on hover
        self.treeview.set_tooltip_column(1)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(100)
        scrolled.set_min_content_width(260)
        scrolled.add(self.treeview)
        box.pack_start(scrolled, True, True, 0)

        # Row Action Buttons for Selected Account
        row_actions = Gtk.FlowBox()
        row_actions.get_style_context().add_class("actions-bar")
        row_actions.set_selection_mode(Gtk.SelectionMode.NONE)
        row_actions.set_homogeneous(False)
        row_actions.set_min_children_per_line(1)
        row_actions.set_max_children_per_line(5)
        row_actions.set_row_spacing(6)
        row_actions.set_column_spacing(8)
        row_actions.set_margin_top(6)

        btn_set_active = Gtk.Button(label="Set as Primary")
        btn_set_active.connect("clicked", self.on_set_primary_clicked)
        row_actions.add(btn_set_active)

        btn_test_token = Gtk.Button(label="Test Token")
        btn_test_token.connect("clicked", self.on_test_token_clicked)
        row_actions.add(btn_test_token)

        btn_remove = Gtk.Button(label="Remove Account")
        btn_remove.get_style_context().add_class("btn-danger")
        btn_remove.connect("clicked", self.on_remove_account_clicked)
        row_actions.add(btn_remove)

        box.pack_start(row_actions, False, False, 0)

        tab_scrolled = Gtk.ScrolledWindow()
        tab_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tab_scrolled.set_min_content_width(300)
        tab_scrolled.set_min_content_height(180)
        tab_scrolled.add(box)
        return tab_scrolled

    def populate_ollama_chips(self, models):
        if not hasattr(self, "box_ollama_chips"):
            return
        for child in self.box_ollama_chips.get_children():
            self.box_ollama_chips.remove(child)
        for m in models:
            display_name = m
            if len(display_name) > 32 and "/" in display_name:
                display_name = display_name.split("/")[-1][:30] + "…"
            btn = Gtk.Button(label=display_name)
            btn.set_tooltip_text(m)
            btn.get_style_context().add_class("btn-chip")
            btn.connect("clicked", lambda b, model_name=m: self.entry_ollama_model.set_text(model_name))
            self.box_ollama_chips.add(btn)
        self.box_ollama_chips.show_all()

    def build_ollama_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(14)
        box.set_margin_bottom(14)

        desc_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        desc_card.get_style_context().add_class("card")
        d_title = Gtk.Label(label="<b>Ollama Sovereign Local Engine</b>", use_markup=True)
        d_title.set_xalign(0)
        d_sub = Gtk.Label(label="Offline high-performance AI inference running on local GPU / CPU. Zero data leaves your machine.", use_markup=True)
        d_sub.set_xalign(0)
        d_sub.set_line_wrap(True)
        desc_card.pack_start(d_title, False, False, 0)
        desc_card.pack_start(d_sub, False, False, 0)
        box.pack_start(desc_card, False, False, 0)

        form_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        form_card.get_style_context().add_class("card")

        lbl_h = Gtk.Label(label="<b>Ollama Host URL:</b>", use_markup=True)
        lbl_h.set_xalign(0)
        self.entry_ollama_host = Gtk.Entry()
        self.entry_ollama_host.set_text("http://127.0.0.1:11434")
        form_card.pack_start(lbl_h, False, False, 0)
        form_card.pack_start(self.entry_ollama_host, False, False, 0)

        lbl_m = Gtk.Label(label="<b>Active Ollama Model:</b>", use_markup=True)
        lbl_m.set_xalign(0)
        self.entry_ollama_model = Gtk.Entry()
        self.entry_ollama_model.set_text("deepseek-v4-9b-uncensored:latest")
        form_card.pack_start(lbl_m, False, False, 0)
        form_card.pack_start(self.entry_ollama_model, False, False, 0)

        # Dual-Agent Architecture Quick Presets
        lbl_presets = Gtk.Label(label="<b>Dual-Agent Architecture Presets:</b>", use_markup=True)
        lbl_presets.set_xalign(0)
        form_card.pack_start(lbl_presets, False, False, 0)

        presets_box = Gtk.FlowBox()
        presets_box.set_selection_mode(Gtk.SelectionMode.NONE)
        presets_box.set_homogeneous(False)
        presets_box.set_min_children_per_line(1)
        presets_box.set_max_children_per_line(4)
        presets_box.set_row_spacing(6)
        presets_box.set_column_spacing(8)

        btn_preset_deepseek = Gtk.Button(label="🧠 DeepSeek-V4 (Architect / Reasoning)")
        btn_preset_deepseek.get_style_context().add_class("btn-preset")
        btn_preset_deepseek.connect("clicked", lambda b: self.entry_ollama_model.set_text("deepseek-v4-9b-uncensored:latest"))
        presets_box.add(btn_preset_deepseek)

        btn_preset_qwen = Gtk.Button(label="⚙️ Qwen2.5-Coder (Executor / Tools)")
        btn_preset_qwen.get_style_context().add_class("btn-preset")
        btn_preset_qwen.connect("clicked", lambda b: self.entry_ollama_model.set_text("qwen2.5-coder:7b"))
        presets_box.add(btn_preset_qwen)
        form_card.pack_start(presets_box, False, False, 0)

        # Detected Local Models Chips
        lbl_chips = Gtk.Label(label="<b>Detected Local Models (Click to Select):</b>", use_markup=True)
        lbl_chips.set_xalign(0)
        form_card.pack_start(lbl_chips, False, False, 0)

        self.box_ollama_chips = Gtk.FlowBox()
        self.box_ollama_chips.set_selection_mode(Gtk.SelectionMode.NONE)
        self.box_ollama_chips.set_homogeneous(False)
        self.box_ollama_chips.set_min_children_per_line(1)
        self.box_ollama_chips.set_max_children_per_line(8)
        self.box_ollama_chips.set_row_spacing(6)
        self.box_ollama_chips.set_column_spacing(6)
        form_card.pack_start(self.box_ollama_chips, False, False, 0)

        lbl_c = Gtk.Label(label="<b>Available Models (comma separated):</b>", use_markup=True)
        lbl_c.set_xalign(0)
        self.entry_ollama_custom = Gtk.Entry()
        self.entry_ollama_custom.set_text("deepseek-v4-9b-uncensored:latest, qwen2.5-coder:7b, qwen2.5-coder:1.5b")
        form_card.pack_start(lbl_c, False, False, 0)
        form_card.pack_start(self.entry_ollama_custom, False, False, 0)

        act_box = Gtk.FlowBox()
        act_box.set_selection_mode(Gtk.SelectionMode.NONE)
        act_box.set_homogeneous(False)
        act_box.set_min_children_per_line(1)
        act_box.set_max_children_per_line(4)
        act_box.set_row_spacing(6)
        act_box.set_column_spacing(10)

        btn_test = Gtk.Button(label="⚡ Test & Auto-Detect Models")
        btn_test.connect("clicked", self.on_test_ollama_clicked)
        btn_save = Gtk.Button(label="💾 Save Ollama Settings")
        btn_save.get_style_context().add_class("btn-emerald")
        btn_save.connect("clicked", self.on_save_ollama_clicked)

        act_box.add(btn_test)
        act_box.add(btn_save)
        self.lbl_ollama_test_result = Gtk.Label(label="")
        act_box.add(self.lbl_ollama_test_result)

        form_card.pack_start(act_box, False, False, 0)
        box.pack_start(form_card, False, False, 0)
        box.pack_start(Gtk.Box(), True, True, 0)

        self.populate_ollama_chips(["deepseek-v4-9b-uncensored:latest", "qwen2.5-coder:7b", "qwen2.5-coder:1.5b"])

        tab_scrolled = Gtk.ScrolledWindow()
        tab_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tab_scrolled.set_min_content_width(300)
        tab_scrolled.set_min_content_height(180)
        tab_scrolled.add(box)
        return tab_scrolled

    def build_nine_router_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(14)
        box.set_margin_bottom(14)

        desc_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        desc_card.get_style_context().add_class("card")
        d_title = Gtk.Label(label="<b>9Router Universal Gateway</b>", use_markup=True)
        d_title.set_xalign(0)
        d_sub = Gtk.Label(label="Forward AI requests to 9Router universal proxy for commercial/open-source API aggregation.", use_markup=True)
        d_sub.set_xalign(0)
        d_sub.set_line_wrap(True)
        desc_card.pack_start(d_title, False, False, 0)
        desc_card.pack_start(d_sub, False, False, 0)
        box.pack_start(desc_card, False, False, 0)

        form_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        form_card.get_style_context().add_class("card")

        lbl_h = Gtk.Label(label="<b>9Router Host URL:</b>", use_markup=True)
        lbl_h.set_xalign(0)
        self.entry_9r_host = Gtk.Entry()
        self.entry_9r_host.set_text("http://127.0.0.1:20128")
        form_card.pack_start(lbl_h, False, False, 0)
        form_card.pack_start(self.entry_9r_host, False, False, 0)

        lbl_k = Gtk.Label(label="<b>API Key:</b>", use_markup=True)
        lbl_k.set_xalign(0)
        self.entry_9r_key = Gtk.Entry()
        self.entry_9r_key.set_visibility(False)
        form_card.pack_start(lbl_k, False, False, 0)
        form_card.pack_start(self.entry_9r_key, False, False, 0)

        lbl_m = Gtk.Label(label="<b>Default Model:</b>", use_markup=True)
        lbl_m.set_xalign(0)
        self.entry_9r_model = Gtk.Entry()
        self.entry_9r_model.set_text("clinepass/cline-pass/glm-5.2")
        form_card.pack_start(lbl_m, False, False, 0)
        form_card.pack_start(self.entry_9r_model, False, False, 0)

        act_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_test = Gtk.Button(label="Test Connection")
        btn_test.connect("clicked", self.on_test_9r_clicked)
        btn_save = Gtk.Button(label="Save 9Router Settings")
        btn_save.get_style_context().add_class("btn-emerald")
        btn_save.connect("clicked", self.on_save_9r_clicked)

        act_box.pack_start(btn_test, False, False, 0)
        act_box.pack_start(btn_save, False, False, 0)
        self.lbl_9r_test_result = Gtk.Label(label="")
        act_box.pack_start(self.lbl_9r_test_result, False, False, 0)

        form_card.pack_start(act_box, False, False, 0)
        box.pack_start(form_card, False, False, 0)
        box.pack_start(Gtk.Box(), True, True, 0)

        tab_scrolled = Gtk.ScrolledWindow()
        tab_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tab_scrolled.set_min_content_width(300)
        tab_scrolled.set_min_content_height(180)
        tab_scrolled.add(box)
        return tab_scrolled

    def build_footer(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bar.set_margin_start(16)
        bar.set_margin_end(16)
        bar.set_margin_top(4)
        bar.set_margin_bottom(6)

        self.lbl_footer_status = Gtk.Label(label="Ready.")
        self.lbl_footer_status.set_xalign(0)
        self.lbl_footer_status.set_ellipsize(Pango.EllipsizeMode.END)
        self.lbl_footer_status.set_max_width_chars(45)
        bar.pack_start(self.lbl_footer_status, True, True, 0)

        lbl_binding = Gtk.Label(label=f"<span color='#64748b'>Port {PORT}</span>", use_markup=True)
        bar.pack_start(lbl_binding, False, False, 0)
        return bar

    # ── Logic & API Interactions ──
    def auto_refresh_tick(self):
        self.refresh_status_async()
        if time.time() - self._last_models_sync_ts >= 60.0:
            self.refresh_models_async(force=False)
        return True

    def refresh_models_async(self, force=False):
        self._last_models_sync_ts = time.time()
        def worker():
            try:
                if force:
                    req = urllib.request.Request(
                        f"{BASE_URL}/api/router/models/refresh",
                        data=b"{}",
                        headers={"User-Agent": "MrFlow-GUI/1.0", "Content-Type": "application/json"},
                        method="POST"
                    )
                else:
                    req = urllib.request.Request(
                        f"{BASE_URL}/api/router/models",
                        headers={"User-Agent": "MrFlow-GUI/1.0"}
                    )
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    GLib.idle_add(self.update_models_ui, data)
            except Exception as e:
                GLib.idle_add(self.update_models_error, str(e))
        threading.Thread(target=worker, daemon=True).start()

    def update_models_error(self, err_msg):
        if hasattr(self, "lbl_model_sync_status"):
            self.lbl_model_sync_status.set_markup(f"<span foreground='#f87171'>● Sync Error</span>")
        self.lbl_footer_status.set_text(f"Model sync error: {err_msg}")

    def update_models_ui(self, data):
        models = data.get("models", [])
        active = data.get("active_model", "") or ""
        source = data.get("source", "")
        grouped = data.get("grouped_models", {})
        if not isinstance(grouped, dict):
            grouped = {}

        self.connector_models = models
        self.active_model = active
        self.grouped_models_data = grouped
        self.models_source = source

        # Rebuild Antigravity Hierarchical Menu
        for child in self.model_menu.get_children():
            self.model_menu.remove(child)

        # Header item: Model
        hdr = Gtk.MenuItem()
        lbl_hdr = Gtk.Label(label="<span foreground='#64748b' size='small' weight='bold'>Model</span>", use_markup=True)
        lbl_hdr.set_xalign(0)
        hdr.add(lbl_hdr)
        hdr.set_sensitive(False)
        self.model_menu.append(hdr)
        self.model_menu.append(Gtk.SeparatorMenuItem())

        consumed_ids = set()
        active_display_str = active

        # 1. Grouped Models with Hierarchical Flyout Submenus
        for gkey, ginfo in grouped.items():
            gdisp = ginfo.get("displayName", gkey)
            levels = ginfo.get("supportedThinkingLevels", [])
            group_mids = [f"{gkey}-{lvl.get('thinkingSuffix', '')}" for lvl in levels]
            for mid in group_mids:
                consumed_ids.add(mid)

            is_group_active = (active in group_mids)
            active_lvl_disp = ""
            for lvl in levels:
                mid = f"{gkey}-{lvl.get('thinkingSuffix', '')}"
                if mid == active:
                    active_lvl_disp = lvl.get("thinkingDisplayName", "")
                    active_display_str = f"{gdisp} ({active_lvl_disp})"
                    break

            group_item = Gtk.MenuItem()
            box_g = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            title_g = Gtk.Label(label=gdisp)
            title_g.set_xalign(0)
            box_g.pack_start(title_g, True, True, 0)

            if is_group_active and active_lvl_disp:
                lbl_lvl = Gtk.Label(label=f"<span foreground='#94a3b8' size='small'>{active_lvl_disp}</span>", use_markup=True)
                box_g.pack_start(lbl_lvl, False, False, 0)

            # Check tag from matching models
            tag_text = ""
            for m in models:
                if m.get("id") in group_mids and m.get("tag_title"):
                    tag_text = m.get("tag_title")
                    break

            if tag_text:
                tag_badge = self._build_tag_badge(tag_text)
                box_g.pack_start(tag_badge, False, False, 0)

            if is_group_active:
                chk = Gtk.Label(label="<span foreground='#00ff66' weight='bold'> ✓</span>", use_markup=True)
                box_g.pack_start(chk, False, False, 0)

            group_item.add(box_g)

            # Submenu for thinking levels
            sub_menu = Gtk.Menu()
            sub_menu.get_style_context().add_class("antigravity-menu")
            for lvl in levels:
                lvl_disp = lvl.get("thinkingDisplayName", "")
                suffix = lvl.get("thinkingSuffix", "")
                target_mid = f"{gkey}-{suffix}"
                is_sub_active = (target_mid == active)

                sub_item = Gtk.MenuItem()
                box_sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                lbl_sub = Gtk.Label(label=lvl_disp)
                lbl_sub.set_xalign(0)
                box_sub.pack_start(lbl_sub, True, True, 0)

                if is_sub_active:
                    sub_chk = Gtk.Label(label="<span foreground='#00ff66' weight='bold'>✓</span>", use_markup=True)
                    box_sub.pack_start(sub_chk, False, False, 0)

                sub_item.add(box_sub)
                sub_item.connect("activate", lambda _, mid=target_mid: self.on_model_menu_item_selected(mid))
                sub_menu.append(sub_item)

            group_item.set_submenu(sub_menu)
            self.model_menu.append(group_item)

        # 2. Standalone Models (Not in grouped_models)
        for m in models:
            mid = m.get("id", "")
            if not mid or mid in consumed_ids:
                continue

            disp = m.get("display_name", "") or mid
            tag = m.get("tag_title")
            is_unavail = m.get("unavailable") or m.get("disabled")
            is_active = (mid == active)
            if is_active:
                active_display_str = disp

            item = Gtk.MenuItem()
            box_item = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            lbl_title = Gtk.Label(label=disp)
            lbl_title.set_xalign(0)
            box_item.pack_start(lbl_title, True, True, 0)

            if tag:
                box_item.pack_start(self._build_tag_badge(tag), False, False, 0)
            elif is_unavail:
                box_item.pack_start(self._build_tag_badge("Unavailable"), False, False, 0)

            if is_active:
                chk = Gtk.Label(label="<span foreground='#00ff66' weight='bold'> ✓</span>", use_markup=True)
                box_item.pack_start(chk, False, False, 0)

            item.add(box_item)
            item.connect("activate", lambda _, target_id=mid: self.on_model_menu_item_selected(target_id))
            self.model_menu.append(item)

        self.model_menu.show_all()

        # Update MenuButton Label
        self.lbl_active_model_btn.set_markup(
            f"<span weight='bold' foreground='#ffffff'>🤖 {active_display_str}</span>"
        )

        # Update sync status pill
        if source == "cloudcode_live":
            self.lbl_model_sync_status.set_markup(
                f"<span foreground='#00ff66'>● CloudCode Live ({len(models)})</span>"
            )
        else:
            self.lbl_model_sync_status.set_markup(
                f"<span foreground='#fbbf24'>● Fallback ({len(models)})</span>"
            )

    def _build_tag_badge(self, tag_text):
        tag_lower = tag_text.lower()
        if "leaving" in tag_lower:
            markup = f"<span background='#78350f' foreground='#fde68a' size='smaller'>  {tag_text} ⓘ  </span>"
        elif "new" in tag_lower:
            markup = f"<span background='#064e3b' foreground='#6ee7b7' size='smaller'>  {tag_text} ⓘ  </span>"
        elif "unavail" in tag_lower:
            markup = f"<span background='#334155' foreground='#94a3b8' size='smaller'>  {tag_text} ⓘ  </span>"
        else:
            markup = f"<span background='#1e293b' foreground='#94a3b8' size='smaller'>  {tag_text} ⓘ  </span>"
        lbl = Gtk.Label(label=markup, use_markup=True)
        return lbl

    def on_model_menu_item_selected(self, model_id):
        if not model_id or model_id == self.active_model:
            return

        self.lbl_active_model_btn.set_markup(
            f"<span weight='bold' foreground='#38bdf8'>Switching to {model_id}...</span>"
        )

        def worker():
            try:
                payload = json.dumps({"model": model_id}).encode("utf-8")
                req = urllib.request.Request(
                    f"{BASE_URL}/api/router/select-model",
                    data=payload,
                    headers={"User-Agent": "MrFlow-GUI/1.0", "Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    GLib.idle_add(self.on_model_select_done, res, model_id)
            except Exception as e:
                GLib.idle_add(self.on_model_select_done, {"success": False, "error": str(e)}, model_id)
        threading.Thread(target=worker, daemon=True).start()

    def on_model_select_done(self, res, requested_id):
        if res.get("success"):
            resolved = res.get("active_model", requested_id)
            self.active_model = resolved
            self.update_models_ui({
                "models": self.connector_models,
                "active_model": resolved,
                "source": getattr(self, "models_source", "cloudcode_live"),
                "grouped_models": self.grouped_models_data
            })
            self.lbl_footer_status.set_text(f"Active Google model switched to: {resolved}")
        else:
            err = res.get("error", "Unknown error")
            self.lbl_footer_status.set_text(f"Model switch failed: {err}")
            self.update_models_ui({
                "models": self.connector_models,
                "active_model": self.active_model,
                "source": getattr(self, "models_source", "cloudcode_live"),
                "grouped_models": self.grouped_models_data
            })

    def refresh_status_async(self):
        def worker():
            try:
                req = urllib.request.Request(f"{BASE_URL}/auth/router/status", headers={"User-Agent": "MrFlow-GUI/1.0"})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    GLib.idle_add(self.update_ui_state, data)
            except Exception as e:
                GLib.idle_add(self.update_ui_offline, str(e))
        threading.Thread(target=worker, daemon=True).start()

    def update_ui_offline(self, err_msg):
        self.status_badge.set_text("● Server Offline")
        self.status_badge.get_style_context().remove_class("badge-online")
        self.status_badge.get_style_context().add_class("badge-offline")
        self.lbl_footer_status.set_text(f"Unable to reach server on {BASE_URL}: {err_msg}")

    def update_ui_state(self, data):
        self.current_state = data
        self.status_badge.set_text("● Online (Port 9099)")
        self.status_badge.get_style_context().remove_class("badge-offline")
        self.status_badge.get_style_context().add_class("badge-online")

        # Update User Passport & Dynamic Auth Actions
        user = data.get("user")
        if user and user.get("username"):
            tier = user.get("tier", "pro").upper()
            username = user.get("username")
            self.user_badge.set_text(f"👤 @{username} [{tier}]")
            self.btn_login.hide()
            self.btn_switch.show()
            self.btn_logout.show()
        else:
            self.user_badge.set_text("👤 Unauthenticated")
            self.btn_login.show()
            self.btn_switch.hide()
            self.btn_logout.hide()

        # Update Active Provider
        prov = data.get("active_provider", "connector").lower()
        self.active_provider = prov
        current_visible = self.stack.get_visible_child_name()
        if not current_visible:
            self.stack.set_visible_child_name(prov)

        # Update Accounts Table
        accounts = data.get("accounts", [])
        self.accounts_data = accounts
        self.account_store.clear()

        healthy = data.get("healthy_count", 0)
        cooldown = data.get("cooldown_count", 0)
        total = len(accounts)
        active_email = data.get("active_email", "None")

        disp_email = active_email
        if len(disp_email) > 22:
            disp_email = disp_email[:20] + "…"
        self.lbl_pool_summary.set_markup(
            f"<b>Pool:</b> <span color='#34d399'>{healthy} Ready</span> | "
            f"<span color='#f59e0b'>{cooldown} CD</span> | "
            f"Total: {total} | <b>{disp_email}</b>"
        )

        for a in accounts:
            is_active_str = "● Active" if a.get("is_active") else "○"
            status_raw = a.get("status", "ready")
            if status_raw == "cooldown":
                cd_rem = a.get("cooldown_remaining_sec", 0)
                status_str = f"Cooldown ({cd_rem}s)"
            elif status_raw == "error":
                status_str = "Error"
            else:
                status_str = "Ready"

            reqs_str = str(a.get("requests_count", 0))
            last_used = a.get("last_used_at") or a.get("added_at") or "-"
            if len(last_used) > 19:
                last_used = last_used[:19].replace("T", " ")

            self.account_store.append([
                is_active_str,
                a.get("email", ""),
                status_str,
                reqs_str,
                last_used,
                a.get("id", "")
            ])

        # Fill Provider Settings
        providers_data = data.get("providers", {})
        inner_providers = providers_data.get("providers", providers_data) if isinstance(providers_data, dict) else {}
        ollama_cfg = providers_data.get("ollama") or inner_providers.get("ollama", {})

        host_val = ollama_cfg.get("host") or ollama_cfg.get("endpoint")
        if host_val and not self.entry_ollama_host.has_focus():
            self.entry_ollama_host.set_text(host_val)

        model_val = ollama_cfg.get("default_model") or ollama_cfg.get("model")
        if model_val and not self.entry_ollama_model.has_focus():
            self.entry_ollama_model.set_text(model_val)

        custom_val = ollama_cfg.get("custom_models")
        if isinstance(custom_val, list) and not self.entry_ollama_custom.has_focus():
            self.entry_ollama_custom.set_text(", ".join(custom_val))
            self.populate_ollama_chips(custom_val)

        r9_cfg = providers_data.get("9router", {}) or inner_providers.get("9router", {})
        if r9_cfg.get("host") and not self.entry_9r_host.has_focus():
            self.entry_9r_host.set_text(r9_cfg.get("host"))
        if r9_cfg.get("default_model") and not self.entry_9r_model.has_focus():
            self.entry_9r_model.set_text(r9_cfg.get("default_model"))
        if r9_cfg.get("api_key") and not self.entry_9r_key.has_focus():
            self.entry_9r_key.set_text(r9_cfg.get("api_key"))

        self.lbl_footer_status.set_text(f"Engine [{prov.upper()}] active. All local endpoints operating.")

    # ── Button Handlers ──
    def on_apply_engine_clicked(self, widget):
        selected_prov = self.stack.get_visible_child_name()
        if not selected_prov:
            return
        def worker():
            try:
                payload = json.dumps({"active_provider": selected_prov}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/provider-config", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    pass
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to switch provider: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_rotation_mode_changed(self, combo):
        mode = combo.get_active_id()
        if not mode:
            return
        def worker():
            try:
                payload = json.dumps({"mode": mode}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/set-rotation-mode", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0):
                    pass
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to set rotation strategy: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_sync_cloud_clicked(self, widget):
        self.lbl_footer_status.set_text("Syncing accounts from auth.floworkos.com Cloud Vault...")
        def worker():
            try:
                req = urllib.request.Request(f"{BASE_URL}/auth/router/sync-cloud", data=b"{}", headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    msg = res.get("message", "Cloud Vault synchronized.")
                    GLib.idle_add(self.show_info_dialog, "Cloud Sync Successful", msg)
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Cloud Sync Failed: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_push_cloud_clicked(self, widget):
        self.lbl_footer_status.set_text("Backing up accounts pool to auth.floworkos.com...")
        def worker():
            try:
                # We can call push by saving rotation mode or via index
                payload = json.dumps({"mode": self.current_state.get("rotation_mode", "failover")}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/set-rotation-mode", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8.0):
                    GLib.idle_add(self.show_info_dialog, "Cloud Backup", "Accounts pool successfully backed up to auth.floworkos.com!")
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Cloud Backup Failed: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_connect_google_clicked(self, widget):
        self.lbl_footer_status.set_text("Opening Google authorization in active browser...")
        def worker():
            try:
                req = urllib.request.Request(f"{BASE_URL}/auth/router/login-url")
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    login_url = data.get("loginUrl") or data.get("login_url")
                    if login_url:
                        self.open_url_in_active_browser(login_url)
                        GLib.idle_add(self.lbl_footer_status.set_text, "Authorization tab opened in your active browser.")
                    else:
                        GLib.idle_add(self.show_error_dialog, "Server did not return a valid login URL.")
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to start OAuth flow: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_passport_login_clicked(self, widget):
        self.lbl_footer_status.set_text("Opening Flowork login in active browser...")
        def worker():
            try:
                req = urllib.request.Request(f"{BASE_URL}/auth/login-url?no_open=1")
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    gate_url = data.get("gate_url") or data.get("login_url")
                    if gate_url:
                        self.open_url_in_active_browser(gate_url)
                        GLib.idle_add(self.lbl_footer_status.set_text, "Flowork login tab opened in your active browser.")
                    else:
                        GLib.idle_add(self.show_error_dialog, "Server did not return a valid gate URL.")
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to start login: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_passport_logout_clicked(self, widget):
        current_user = "Flowork"
        if hasattr(self, "current_state") and self.current_state:
            u = self.current_state.get("user")
            if u and u.get("username"):
                current_user = f"@{u.get('username')}"

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text=f"Logout from account {current_user}?"
        )
        dialog.format_secondary_text(
            "Flowork Passport session will be disconnected. Local Google accounts in vault remain preserved."
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        btn_confirm = dialog.add_button("🚪 Logout", Gtk.ResponseType.OK)
        btn_confirm.get_style_context().add_class("btn-danger")

        chk_purge = Gtk.CheckButton(label="Also purge all Google accounts from local vault")
        chk_purge.set_margin_start(18)
        chk_purge.set_margin_top(8)
        dialog.get_content_area().pack_start(chk_purge, False, False, 0)
        chk_purge.show()

        res = dialog.run()
        should_purge = chk_purge.get_active()
        dialog.destroy()

        if res != Gtk.ResponseType.OK:
            return

        self.lbl_footer_status.set_text("Logging out from Flowork passport...")

        def worker():
            try:
                payload = json.dumps({"purge_accounts": should_purge}).encode("utf-8")
                req = urllib.request.Request(
                    f"{BASE_URL}/auth/logout",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    msg = resp_data.get("message", "Logged out successfully")
                    GLib.idle_add(self.lbl_footer_status.set_text, f"Flowork Passport: {msg}")
                    GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to logout: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def open_url_in_active_browser(self, target_url):
        env = dict(os.environ)
        if "DISPLAY" not in env:
            env["DISPLAY"] = ":0"

        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(target_url, -1)
        except Exception:
            pass

        try:
            subprocess.Popen(["xdg-open", target_url], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass

        for cmd in ["google-chrome-stable", "google-chrome", "chromium", "firefox"]:
            if shutil.which(cmd):
                try:
                    subprocess.Popen([cmd, target_url], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
                except Exception:
                    pass

    def on_clear_cooldowns_clicked(self, widget):
        def worker():
            try:
                req = urllib.request.Request(f"{BASE_URL}/auth/router/clear-cooldown", data=b"{}", headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    c = res.get("cleared_count", 0)
                    GLib.idle_add(self.lbl_footer_status.set_text, f"Cleared cooldown state for {c} accounts.")
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Error clearing cooldowns: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def get_selected_account_id(self):
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            return model[treeiter][5]
        return None

    def on_set_primary_clicked(self, widget):
        acc_id = self.get_selected_account_id()
        if not acc_id:
            self.show_error_dialog("Please select an account from the table first.")
            return
        def worker():
            try:
                payload = json.dumps({"id": acc_id}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/select-account", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0):
                    pass
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to switch primary account: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_test_token_clicked(self, widget):
        acc_id = self.get_selected_account_id()
        if not acc_id:
            self.show_error_dialog("Please select an account from the table first.")
            return
        self.lbl_footer_status.set_text(f"Refreshing and testing token for account {acc_id}...")
        def worker():
            try:
                payload = json.dumps({"id": acc_id}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/test-account", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    if res.get("success"):
                        GLib.idle_add(self.show_info_dialog, "Token Test OK", f"Token for {res.get('email')} is valid and ready!")
                    else:
                        GLib.idle_add(self.show_error_dialog, f"Token test failed: {res.get('error') or res.get('details')}")
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Token verification error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_remove_account_clicked(self, widget):
        acc_id = self.get_selected_account_id()
        if not acc_id:
            self.show_error_dialog("Please select an account from the table first.")
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Remove Account from Pool?"
        )
        dialog.format_secondary_text(f"Are you sure you want to delete account {acc_id}? Cloud backup will be synchronized.")
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.YES:
            return

        def worker():
            try:
                payload = json.dumps({"id": acc_id}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/remove-account", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5.0):
                    pass
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to remove account: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def on_add_account_dialog(self, widget):
        dialog = Gtk.Dialog(title="Add Google Account Manually", transient_for=self, flags=0)
        dialog.set_default_size(440, 260)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        btn_add = dialog.add_button("Add & Backup to Cloud", Gtk.ResponseType.OK)
        btn_add.get_style_context().add_class("btn-emerald")

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        lbl_e = Gtk.Label(label="<b>Email Address:</b>", use_markup=True)
        lbl_e.set_xalign(0)
        entry_email = Gtk.Entry()
        entry_email.set_placeholder_text("developer@gmail.com")
        content.pack_start(lbl_e, False, False, 0)
        content.pack_start(entry_email, False, False, 0)

        lbl_rt = Gtk.Label(label="<b>OAuth Refresh Token:</b>", use_markup=True)
        lbl_rt.set_xalign(0)
        entry_rt = Gtk.Entry()
        entry_rt.set_placeholder_text("1//0g...")
        content.pack_start(lbl_rt, False, False, 0)
        content.pack_start(entry_rt, False, False, 0)

        content.show_all()
        response = dialog.run()
        email_val = entry_email.get_text().strip()
        rt_val = entry_rt.get_text().strip()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            if not email_val or not rt_val:
                self.show_error_dialog("Both Email and Refresh Token are required.")
                return
            def worker():
                try:
                    payload = json.dumps({"email": email_val, "refresh_token": rt_val}).encode("utf-8")
                    req = urllib.request.Request(f"{BASE_URL}/auth/router/add-account", data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=8.0) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        bk = res.get("cloud_backup", {})
                        bk_msg = "Cloud Backup OK" if bk.get("success") else "Saved locally"
                        GLib.idle_add(self.show_info_dialog, "Account Added", f"Account {email_val} added to pool.\n{bk_msg}")
                    GLib.idle_add(self.refresh_status_async)
                except Exception as e:
                    GLib.idle_add(self.show_error_dialog, f"Failed to add account: {e}")
            threading.Thread(target=worker, daemon=True).start()

    # ── Ollama Handlers ──
    def on_test_ollama_clicked(self, widget=None):
        host = self.entry_ollama_host.get_text().strip()
        self.lbl_ollama_test_result.set_text("Testing connection...")
        def worker():
            try:
                payload = json.dumps({"provider": "ollama", "host": host}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/test-provider", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    if res.get("success"):
                        models = res.get("models", [])
                        m_count = len(models)
                        def on_success_ui():
                            self.lbl_ollama_test_result.set_markup(f"<span color='#34d399'>● Connected ({m_count} models found)</span>")
                            if models:
                                self.entry_ollama_custom.set_text(", ".join(models))
                                self.populate_ollama_chips(models)
                                curr_model = self.entry_ollama_model.get_text().strip()
                                if not curr_model or curr_model == "llama3.3:latest" or curr_model not in models:
                                    preferred = next((m for m in models if "deepseek" in m.lower()), models[0])
                                    self.entry_ollama_model.set_text(preferred)
                        GLib.idle_add(on_success_ui)
                    else:
                        GLib.idle_add(self.lbl_ollama_test_result.set_markup, f"<span color='#ef4444'>● Failed: {res.get('error')}</span>")
            except Exception as e:
                GLib.idle_add(self.lbl_ollama_test_result.set_markup, f"<span color='#ef4444'>● Error: {e}</span>")
        threading.Thread(target=worker, daemon=True).start()

    def on_save_ollama_clicked(self, widget):
        host = self.entry_ollama_host.get_text().strip()
        model = self.entry_ollama_model.get_text().strip()
        custom = [m.strip() for m in self.entry_ollama_custom.get_text().split(",") if m.strip()]
        def worker():
            try:
                payload = json.dumps({
                    "ollama": {
                        "host": host,
                        "endpoint": host,
                        "default_model": model,
                        "model": model,
                        "custom_models": custom
                    }
                }).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/provider-config", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0):
                    GLib.idle_add(self.show_info_dialog, "Settings Saved", f"Ollama settings updated! Active model: {model}")
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to save Ollama config: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # ── 9Router Handlers ──
    def on_test_9r_clicked(self, widget):
        host = self.entry_9r_host.get_text().strip()
        key = self.entry_9r_key.get_text().strip()
        self.lbl_9r_test_result.set_text("Testing connection...")
        def worker():
            try:
                payload = json.dumps({"provider": "9router", "host": host, "api_key": key}).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/test-provider", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    if res.get("success"):
                        GLib.idle_add(self.lbl_9r_test_result.set_markup, "<span color='#34d399'>● Connected successfully!</span>")
                    else:
                        GLib.idle_add(self.lbl_9r_test_result.set_markup, f"<span color='#ef4444'>● Failed: {res.get('error')}</span>")
            except Exception as e:
                GLib.idle_add(self.lbl_9r_test_result.set_markup, f"<span color='#ef4444'>● Error: {e}</span>")
        threading.Thread(target=worker, daemon=True).start()

    def on_save_9r_clicked(self, widget):
        host = self.entry_9r_host.get_text().strip()
        key = self.entry_9r_key.get_text().strip()
        model = self.entry_9r_model.get_text().strip()
        def worker():
            try:
                payload = json.dumps({
                    "9router": {
                        "host": host,
                        "api_key": key,
                        "default_model": model
                    }
                }).encode("utf-8")
                req = urllib.request.Request(f"{BASE_URL}/auth/router/provider-config", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0):
                    GLib.idle_add(self.show_info_dialog, "Settings Saved", "9Router provider configuration updated!")
                GLib.idle_add(self.refresh_status_async)
            except Exception as e:
                GLib.idle_add(self.show_error_dialog, f"Failed to save 9Router config: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # ── Dialog Utilities ──
    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_info_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def main():
    # Ensure server daemon is active
    try:
        req = urllib.request.Request(f"{BASE_URL}/auth/router/status", headers={"User-Agent": "MrFlow-GUI/1.0"})
        urllib.request.urlopen(req, timeout=1.0)
    except Exception:
        # Start server daemon (Pure Rust flowork-connector)
        daemon_bin = (
            shutil.which("mrflow-router-daemon")
            or ("/usr/local/bin/mrflow-router-daemon" if os.path.exists("/usr/local/bin/mrflow-router-daemon") else "/opt/floworkos/connector/bin/flowork-connector")
        )
        if os.path.exists(daemon_bin):
            subprocess.Popen([daemon_bin], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    win = MrFlowRouterWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
