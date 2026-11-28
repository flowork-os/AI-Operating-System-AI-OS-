#!/usr/bin/env python3
# =============================================================================
# 🚀 Flowork Sovereign OS — Quantum Glass Wallpaper Manager
# Ultra-Modern Frosted Glass Wallpaper Center
# Zero Broken Menus, 100% Instant Live Desktop Updating.
# =============================================================================

import os
import sys
import subprocess
import json
import time
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio, GLib

WALLPAPERS = [
    ("Flowork Aurora Glass (Default)", "/opt/floworkos/theme/flowork-quantum-wallpaper.png"),
    ("Flowork Aurora Dark", "/opt/floworkos/theme/wallpapers/flowork-aurora-dark.jpg"),
    ("Flowork Monolith Quantum", "/opt/floworkos/theme/wallpapers/flowork-monolith-dark.jpg"),
    ("Sonoma Dark Glass", "/opt/floworkos/theme/wallpapers/Sonoma-dark.jpg"),
    ("Sonoma Light Glass", "/opt/floworkos/theme/wallpapers/Sonoma-light.jpg"),
    ("Ventura Dark Glass", "/opt/floworkos/theme/wallpapers/Ventura-dark.jpg"),
    ("Ventura Light Glass", "/opt/floworkos/theme/wallpapers/Ventura-light.jpg"),
    ("Monterey Dark Indigo", "/opt/floworkos/theme/wallpapers/Monterey-dark.jpg"),
    ("Monterey Morning Amber", "/opt/floworkos/theme/wallpapers/Monterey-morning.jpg"),
    ("WhiteSur Dark Obsidian", "/opt/floworkos/theme/wallpapers/WhiteSur-dark.jpg"),
    ("WhiteSur Clean Glass", "/opt/floworkos/theme/wallpapers/WhiteSur.jpg"),
    ("Blobs Dark Wave", "/usr/share/backgrounds/gnome/blobs-d.svg"),
    ("Blobs Light Wave", "/usr/share/backgrounds/gnome/blobs-l.svg"),
    ("Morphogenesis Cyber", "/usr/share/backgrounds/gnome/morphogenesis-d.svg"),
    ("Pills Minimalist", "/usr/share/backgrounds/gnome/pills-d.jpg"),
    ("Adwaita Night Sky", "/usr/share/backgrounds/gnome/adwaita-d.jpg"),
    ("Truchet Geometric", "/usr/share/backgrounds/gnome/truchet-d.jpg"),
]

def apply_wallpaper_file(file_path):
    if not os.path.isfile(file_path):
        return False

    # 1. Update canonical state file
    try:
        with open("/opt/floworkos/theme/current-wallpaper.path", "w") as f:
            f.write(file_path)
    except Exception:
        pass

    # 2. Write atomic SHM state for instant real-time live sync (<50ms)
    try:
        shm_data = {
            "path": file_path,
            "timestamp": time.time(),
        }
        with open("/dev/shm/flowork-wallpaper.json", "w") as f:
            json.dump(shm_data, f)
    except Exception:
        pass

    # 3. Update current-theme.json if present
    theme_file = "/opt/floworkos/theme/current-theme.json"
    if os.path.exists(theme_file):
        try:
            with open(theme_file, "r") as f:
                tdata = json.load(f)
            tdata["wallpaper"] = file_path
            with open(theme_file, "w") as f:
                json.dump(tdata, f, indent=2)
        except Exception:
            pass

    # 4. Update motion-config.json
    config_file = "/opt/floworkos/theme/motion-config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                cdata = json.load(f)
            cdata["wallpaper"] = file_path
            with open(config_file, "w") as f:
                json.dump(cdata, f, indent=2)
        except Exception:
            pass

    # 5. Update GSettings for background daemons
    try:
        c_settings = Gio.Settings.new("org.cinnamon.desktop.background")
        c_settings.set_string("picture-uri", f"file://{file_path}")
    except Exception:
        pass

    try:
        g_settings = Gio.Settings.new("org.gnome.desktop.background")
        g_settings.set_string("picture-uri", f"file://{file_path}")
    except Exception:
        pass

    # 6. Paint immediately to X11 root window as fallback
    target = file_path
    if file_path.lower().endswith(".svg"):
        cache_png = f"/run/user/{os.getuid()}/flowork_wallpaper_rendered.png"
        try:
            subprocess.run(["rsvg-convert", "-w", "2560", "-h", "1080", file_path, "-o", cache_png], check=True)
            target = cache_png
        except Exception:
            pass

    subprocess.run(["feh", "--no-fehbg", "--bg-fill", target], check=False)
    return True

class WallpaperManagerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Flowork Desktop Wallpaper")
        self.set_default_size(860, 580)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(16)

        # Frosted glass CSS
        css = b'''
        window {
            background-color: rgba(8, 14, 24, 0.94);
            color: #f1f5f9;
        }
        .header-title {
            color: #00f2fe;
            font-family: 'JetBrains Mono', monospace;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        .header-sub {
            color: #7b8ea8;
            font-size: 12px;
        }
        .wallpaper-card {
            background-color: rgba(255, 255, 255, 0.04);
            border: 1.5px solid rgba(0, 242, 254, 0.20);
            border-radius: 14px;
            padding: 8px;
            transition: all 150ms ease;
        }
        .wallpaper-card:hover {
            background-color: rgba(0, 242, 254, 0.15);
            border-color: #00f2fe;
            box-shadow: 0 0 16px rgba(0, 242, 254, 0.40);
        }
        .wallpaper-title {
            color: #ffffff;
            font-family: 'Inter', system-ui, sans-serif;
            font-size: 12px;
            font-weight: 600;
            margin-top: 6px;
        }
        .action-btn {
            background: linear-gradient(180deg, rgba(0, 242, 254, 0.25) 0%, rgba(13, 22, 38, 0.8) 100%);
            border: 1px solid #00f2fe;
            border-radius: 10px;
            color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 700;
            padding: 8px 16px;
        }
        .action-btn:hover {
            background: #00f2fe;
            color: #030712;
            box-shadow: 0 0 16px rgba(0, 242, 254, 0.6);
        }
        '''
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(main_box)

        # Header Bar
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        vbox_titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_lbl = Gtk.Label(label="[ 🖼️ ]  FLOWORK WALLPAPER MANAGER")
        title_lbl.set_xalign(0)
        title_lbl.get_style_context().add_class('header-title')
        sub_lbl = Gtk.Label(label="Click any wallpaper to apply live to desktop • Instant zero-lag sync")
        sub_lbl.set_xalign(0)
        sub_lbl.get_style_context().add_class('header-sub')
        vbox_titles.pack_start(title_lbl, False, False, 0)
        vbox_titles.pack_start(sub_lbl, False, False, 0)
        header.pack_start(vbox_titles, True, True, 0)

        # Custom Browse Button
        browse_btn = Gtk.Button(label="+ Choose Image...")
        browse_btn.get_style_context().add_class('action-btn')
        browse_btn.connect("clicked", self._on_browse_clicked)
        header.pack_end(browse_btn, False, False, 0)

        main_box.pack_start(header, False, False, 0)

        # Scrolled Grid
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(14)
        grid.set_row_spacing(14)
        grid.set_halign(Gtk.Align.CENTER)
        scroller.add(grid)

        self.cards = {}
        # Resolve active wallpaper
        current_wp = ""
        if os.path.exists("/opt/floworkos/theme/current-wallpaper.path"):
            try:
                with open("/opt/floworkos/theme/current-wallpaper.path", "r") as f:
                    current_wp = f.read().strip()
            except Exception:
                pass
        if not current_wp and os.path.exists("/opt/floworkos/theme/current-theme.json"):
            try:
                with open("/opt/floworkos/theme/current-theme.json", "r") as f:
                    current_wp = json.load(f).get("wallpaper", "")
            except Exception:
                pass

        col = 0
        row = 0
        for name, path in WALLPAPERS:
            card = self._create_card(name, path)
            self.cards[path] = card
            if path == current_wp:
                card.get_style_context().add_class('active')
            grid.attach(card, col, row, 1, 1)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        self.connect("destroy", Gtk.main_quit)

    def _create_card(self, name, path):
        btn = Gtk.Button()
        btn.get_style_context().add_class('wallpaper-card')
        btn.connect("clicked", lambda w, p=path: self._on_select(p))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        btn.add(vbox)

        # Thumbnail
        thumb_path = path
        if path.lower().endswith(".svg"):
            cache_thumb = f"/tmp/thumb_{abs(hash(path))}.png"
            if not os.path.exists(cache_thumb):
                try:
                    subprocess.run(["rsvg-convert", "-w", "240", "-h", "135", path, "-o", cache_thumb], check=True)
                except Exception:
                    pass
            if os.path.exists(cache_thumb):
                thumb_path = cache_thumb

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(thumb_path, 240, 135, False)
            img = Gtk.Image.new_from_pixbuf(pixbuf)
        except Exception:
            img = Gtk.Image.new_from_icon_name("preferences-desktop-wallpaper", Gtk.IconSize.DIALOG)

        vbox.pack_start(img, False, False, 0)

        lbl = Gtk.Label(label=name)
        lbl.get_style_context().add_class('wallpaper-title')
        vbox.pack_start(lbl, False, False, 0)

        return btn

    def _on_select(self, path):
        apply_wallpaper_file(path)
        for p, card in self.cards.items():
            if p == path:
                card.get_style_context().add_class('active')
            else:
                card.get_style_context().remove_class('active')

    def _on_browse_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Custom Wallpaper",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images (*.png, *.jpg, *.jpeg, *.svg, *.webp)")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/svg+xml")
        filter_img.add_mime_type("image/webp")
        filter_img.add_pattern("*.png")
        filter_img.add_pattern("*.jpg")
        filter_img.add_pattern("*.jpeg")
        filter_img.add_pattern("*.svg")
        filter_img.add_pattern("*.webp")
        dialog.add_filter(filter_img)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            chosen = dialog.get_filename()
            dialog.destroy()
            if chosen and os.path.isfile(chosen):
                apply_wallpaper_file(chosen)
                for p, card in self.cards.items():
                    if p == chosen:
                        card.get_style_context().add_class('active')
                    else:
                        card.get_style_context().remove_class('active')
        else:
            dialog.destroy()

def main():
    win = WallpaperManagerWindow()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
