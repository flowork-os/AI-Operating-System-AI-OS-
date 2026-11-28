#!/usr/bin/env python3
"""
Flowork App Manager — Ultra-Lightweight Sovereign GTK3 Uninstaller & OS Cleaner
Zero WebKit overhead, instant startup, powered by flowork-uninstall.
"""

import json
import subprocess
import sys
import threading
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

CSS = b"""
window, .main-bg {
    background-color: #0b0f17;
    color: #e2e8f0;
}
.header-bar {
    background-color: #111827;
    border-bottom: 1px solid #1e293b;
    padding: 12px 18px;
}
.title-label {
    font-size: 18px;
    font-weight: bold;
    color: #00e5ff;
}
.subtitle-label {
    font-size: 12px;
    color: #94a3b8;
}
.search-entry {
    background-color: #131a26;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}
.filter-btn {
    background-color: #131a26;
    color: #cbd5e1;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: bold;
}
.filter-btn:checked {
    background-color: #00e5ff;
    color: #0b0f17;
    border-color: #00e5ff;
}
.clean-btn {
    background-color: #10b981;
    color: #052e16;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    border: none;
}
.clean-btn:hover {
    background-color: #34d399;
}
.app-row {
    background-color: #131a26;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 4px 12px;
}
.app-name {
    font-size: 14px;
    font-weight: bold;
    color: #f8fafc;
}
.app-desc {
    font-size: 12px;
    color: #94a3b8;
}
.badge-flowork {
    background-color: #0e7490;
    color: #ecfeff;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: bold;
}
.badge-apt {
    background-color: #4338ca;
    color: #eef2ff;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: bold;
}
.badge-core {
    background-color: #334155;
    color: #cbd5e1;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: bold;
}
.size-label {
    font-size: 13px;
    font-weight: bold;
    color: #38bdf8;
}
.uninstall-btn {
    background-color: #be123c;
    color: #fff1f2;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: bold;
    border: none;
}
.uninstall-btn:hover {
    background-color: #e11d48;
}
.status-bar {
    background-color: #111827;
    border-top: 1px solid #1e293b;
    padding: 8px 16px;
    font-size: 12px;
    color: #94a3b8;
}
"""


class FloworkAppManager(Gtk.Window):
    def __init__(self, target_desktop=None, target_name=None):
        super().__init__(title="Flowork App Manager")
        self.set_default_size(920, 640)
        self.set_position(Gtk.WindowPosition.CENTER)

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.all_apps = []
        self.orphans = {}
        self.current_filter = "all"
        self.search_query = ""
        self.purge_mode = False
        self.target_desktop = target_desktop
        self.target_name = target_name

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.get_style_context().add_class("main-bg")
        self.add(root)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.get_style_context().add_class("header-bar")
        root.pack_start(header, False, False, 0)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_title = Gtk.Label(label="Flowork App Manager")
        lbl_title.set_xalign(0)
        lbl_title.get_style_context().add_class("title-label")
        self.lbl_subtitle = Gtk.Label(label="Scanning installed apps & system cache...")
        self.lbl_subtitle.set_xalign(0)
        self.lbl_subtitle.get_style_context().add_class("subtitle-label")
        title_box.pack_start(lbl_title, False, False, 0)
        title_box.pack_start(self.lbl_subtitle, False, False, 0)
        header.pack_start(title_box, True, True, 0)

        self.chk_purge = Gtk.CheckButton(label="Purge Config & Cache")
        self.chk_purge.connect("toggled", self.on_purge_toggled)
        header.pack_start(self.chk_purge, False, False, 6)

        self.btn_clean = Gtk.Button(label="Deep Clean OS")
        self.btn_clean.get_style_context().add_class("clean-btn")
        self.btn_clean.connect("clicked", self.on_clean_clicked)
        header.pack_start(self.btn_clean, False, False, 0)

        # Toolbar: Search + Filter Tabs
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        toolbar.set_margin_top(12)
        toolbar.set_margin_bottom(8)
        toolbar.set_margin_start(14)
        toolbar.set_margin_end(14)
        root.pack_start(toolbar, False, False, 0)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search apps or packages...")
        self.search_entry.get_style_context().add_class("search-entry")
        self.search_entry.connect("changed", self.on_search_changed)
        toolbar.pack_start(self.search_entry, True, True, 0)

        self.filter_buttons = {}
        for key, label in [("all", "All"), ("flowork", "Flowork Apps"), ("apt", "System (APT)")]:
            btn = Gtk.ToggleButton(label=label)
            btn.get_style_context().add_class("filter-btn")
            if key == "all":
                btn.set_active(True)
            btn.connect("toggled", self.on_filter_toggled, key)
            toolbar.pack_start(btn, False, False, 0)
            self.filter_buttons[key] = btn

        btn_refresh = Gtk.Button(label="Refresh")
        btn_refresh.get_style_context().add_class("filter-btn")
        btn_refresh.connect("clicked", lambda *_: self.load_data())
        toolbar.pack_start(btn_refresh, False, False, 0)

        # Scrolled List
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        root.pack_start(scroll, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.listbox)

        # Status Bar
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_box.get_style_context().add_class("status-bar")
        self.lbl_status = Gtk.Label(label="Ready.")
        self.lbl_status.set_xalign(0)
        status_box.pack_start(self.lbl_status, True, True, 0)
        root.pack_start(status_box, False, False, 0)

        self.load_data()

    def on_purge_toggled(self, widget):
        self.purge_mode = widget.get_active()

    def on_search_changed(self, entry):
        self.search_query = entry.get_text().strip().lower()
        self.render_list()

    def on_filter_toggled(self, widget, key):
        if widget.get_active():
            self.current_filter = key
            for k, b in self.filter_buttons.items():
                if k != key and b.get_active():
                    b.set_active(False)
            self.render_list()
        elif self.current_filter == key:
            widget.set_active(True)

    def set_status(self, text):
        GLib.idle_add(self.lbl_status.set_text, text)

    def load_data(self):
        self.set_status("Scanning Flowork apps, APT packages, and orphans...")

        def worker():
            try:
                out = subprocess.check_output(
                    ["flowork-uninstall", "list", "--json"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                data = json.loads(out)
                fw = data.get("flowork", [])
                apt = data.get("apt", [])
                orphans = data.get("orphans", {})
                combined = sorted(fw + apt, key=lambda x: x.get("size_bytes", 0), reverse=True)
                GLib.idle_add(self._on_data_loaded, combined, orphans)
            except Exception as e:
                self.set_status(f"Scan error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _on_data_loaded(self, combined, orphans):
        self.all_apps = combined
        self.orphans = orphans
        fw_count = sum(1 for a in combined if a["type"] == "flowork")
        apt_count = sum(1 for a in combined if a["type"] == "apt")
        cache_h = orphans.get("apt_cache_human", "0 B")
        broken = len(orphans.get("broken_symlinks", [])) + len(orphans.get("orphaned_desktops", []))
        self.lbl_subtitle.set_text(
            f"{fw_count} Flowork Apps  |  {apt_count} User APT Packages  |  {broken} Orphans  |  {cache_h} APT Cache"
        )
        self.set_status("Scan complete. Select an app to uninstall or run Deep Clean OS.")
        self.render_list()
        if self.target_desktop or self.target_name:
            desktop_path = self.target_desktop
            app_name = self.target_name
            self.target_desktop = None
            self.target_name = None
            GLib.idle_add(self._handle_uninstall_target, desktop_path, app_name)

    def _handle_uninstall_target(self, desktop_path, app_name):
        matched = None
        candidates = []
        if desktop_path:
            base = os.path.basename(desktop_path)
            stem = base[:-8] if base.endswith(".desktop") else base
            candidates.append(stem.lower())
            if stem.startswith("flowork-"):
                candidates.append(stem[8:].lower())
            try:
                with open(desktop_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith("Exec="):
                            exec_val = line.split("=", 1)[1].strip().split()[0]
                            candidates.append(os.path.basename(exec_val).lower())
                            if "/opt/floworkos/apps/" in exec_val:
                                part = exec_val.split("/opt/floworkos/apps/", 1)[1].split("/", 1)[0]
                                candidates.append(part.lower())
            except Exception:
                pass
            try:
                res = subprocess.run(
                    ["dpkg", "-S", desktop_path],
                    capture_output=True, text=True, timeout=3
                )
                if res.returncode == 0 and ":" in res.stdout:
                    pkg = res.stdout.split(":", 1)[0].strip().lower()
                    candidates.insert(0, pkg)
            except Exception:
                pass

        if app_name:
            candidates.append(app_name.strip().lower())

        for app in self.all_apps:
            aid = app.get("id", "").lower()
            aname = app.get("name", "").lower()
            if aid in candidates or aname in candidates:
                matched = app
                break

        if not matched and app_name:
            q = app_name.strip().lower()
            for app in self.all_apps:
                if q in app.get("name", "").lower() or q in app.get("id", "").lower():
                    matched = app
                    break

        if matched:
            self.search_entry.set_text(matched["id"])
            self.on_remove_clicked(None, matched)
        else:
            if app_name:
                self.search_entry.set_text(app_name)
            dlg = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=f"Cannot Uninstall '{app_name or desktop_path}'",
            )
            dlg.format_secondary_text(
                "This application is either a protected core Flowork OS / Linux system component, "
                "or it is not registered as a removable package."
            )
            dlg.run()
            dlg.destroy()
        return False

    def render_list(self):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        filtered = []
        for app in self.all_apps:
            if self.current_filter != "all" and app["type"] != self.current_filter:
                continue
            if self.search_query:
                hay = f"{app['id']} {app['name']} {app['description']}".lower()
                if self.search_query not in hay:
                    continue
            filtered.append(app)

        for app in filtered:
            row = Gtk.ListBoxRow()
            card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            card.get_style_context().add_class("app-row")

            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            top_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            lbl_name = Gtk.Label(label=app["name"])
            lbl_name.set_xalign(0)
            lbl_name.get_style_context().add_class("app-name")
            top_line.pack_start(lbl_name, False, False, 0)

            badge = Gtk.Label(label=app["type"].upper())
            badge.get_style_context().add_class(
                "badge-flowork" if app["type"] == "flowork" else "badge-apt"
            )
            top_line.pack_start(badge, False, False, 0)

            lbl_desc = Gtk.Label(label=app["description"][:90])
            lbl_desc.set_xalign(0)
            lbl_desc.get_style_context().add_class("app-desc")

            info_box.pack_start(top_line, False, False, 0)
            info_box.pack_start(lbl_desc, False, False, 0)
            card.pack_start(info_box, True, True, 0)

            lbl_size = Gtk.Label(label=app["size_human"])
            lbl_size.get_style_context().add_class("size-label")
            card.pack_start(lbl_size, False, False, 8)

            if app.get("protected"):
                core_lbl = Gtk.Label(label="CORE OS")
                core_lbl.get_style_context().add_class("badge-core")
                card.pack_start(core_lbl, False, False, 0)
            else:
                btn_del = Gtk.Button(label="Uninstall")
                btn_del.get_style_context().add_class("uninstall-btn")
                btn_del.connect("clicked", self.on_uninstall_clicked, app)
                card.pack_start(btn_del, False, False, 0)

            row.add(card)
            self.listbox.add(row)

        self.listbox.show_all()

    def on_uninstall_clicked(self, widget, app):
        purge_txt = " (including user config & cache)" if self.purge_mode else ""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Uninstall {app['name']}?",
        )
        dialog.format_secondary_text(
            f"Type: {app['type'].upper()}\n"
            f"Target: {app['id']}\n"
            f"Estimated space freed: {app['size_human']}{purge_txt}"
        )
        resp = dialog.run()
        dialog.destroy()
        if resp != Gtk.ResponseType.YES:
            return

        self.set_status(f"Uninstalling {app['name']}...")

        def worker():
            cmd = ["flowork-uninstall", "remove", app["id"], "--type", app["type"], "-y"]
            if self.purge_mode:
                cmd.append("--purge")
            res = subprocess.run(cmd, capture_output=True, text=True)
            msg = res.stdout.strip() or res.stderr.strip() or "Done."
            self.set_status(msg)
            GLib.idle_add(self.load_data)

        threading.Thread(target=worker, daemon=True).start()

    def on_clean_clicked(self, widget):
        self.set_status("Running Deep Clean OS (orphans + APT autoremove + cache)...")

        def worker():
            res = subprocess.run(["flowork-uninstall", "clean", "-y"], capture_output=True, text=True)
            msg = res.stdout.strip() or res.stderr.strip() or "Clean complete."
            self.set_status(msg)
            GLib.idle_add(self.load_data)

        threading.Thread(target=worker, daemon=True).start()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Flowork App Manager")
    parser.add_argument("--uninstall-desktop", default=None, help="Path to .desktop file to uninstall")
    parser.add_argument("--name", default=None, help="Display name of application")
    args, _ = parser.parse_known_args()

    win = FloworkAppManager(target_desktop=args.uninstall_desktop, target_name=args.name)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
