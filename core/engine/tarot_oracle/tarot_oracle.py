#!/usr/bin/env python3
# ==============================================================================
# 🔮 FLOWORK OS — SOVEREIGN TAROT ORACLE & POKÉMON-STYLE SUMMON ENGINE
# High-Fidelity Pure Optical Crystal Glass HUD & 3D Holographic Gacha Reveal
# ==============================================================================
import os
import sys
import re
import math
import time
import json
import random
import threading
import subprocess
import datetime
import urllib.request
import socket
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("PangoCairo", "1.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo, GdkPixbuf
import cairo

# Color Palettes
C_WHITE  = (1.00, 1.00, 1.00)
C_GREEN  = (0.00, 1.00, 0.40)  # #00ff66
C_CYAN   = (0.00, 0.95, 1.00)  # #00f2fe
C_AMBER  = (1.00, 0.70, 0.00)  # #ffb300
C_PURPLE = (0.70, 0.53, 1.00)  # #b388ff
C_RED    = (1.00, 0.32, 0.32)  # #ff5252
C_MUTED  = (0.55, 0.65, 0.75)
C_GOLD   = (1.00, 0.84, 0.00)

DATA_PATH = "/opt/floworkos/assets/tarot/cards_index.json"
DAILY_CACHE_PATH = os.path.expanduser("~/.cache/flowork/tarot_daily.json")
JOURNAL_PATH = os.path.expanduser("~/.local/share/flowork/tarot_journal.json")
SFX_WHOOSH = "/opt/floworkos/documents/videos/cyber-sqli-short/sfx/whoosh.wav"
SFX_LASER = "/opt/floworkos/documents/videos/cyber-sqli-short/sfx/laser.wav"
SFX_SUCCESS = "/opt/floworkos/documents/videos/cyber-sqli-short/sfx/success.wav"


def play_sfx(path):
    if os.path.exists(path) and os.path.exists("/usr/bin/paplay"):
        def _run():
            try:
                subprocess.run(["/usr/bin/paplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()


def draw_rounded_rect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def calc_birth_card(dob_str):
    """Calculates Tarot Life Path / Soul Birth Card (0 - 21)."""
    if not dob_str:
        return None
    digits = [int(d) for d in re.findall(r"\d", dob_str)]
    if len(digits) < 4:
        return None
    total = sum(digits)
    while total > 21:
        total = sum(int(d) for d in str(total))
    return total


MAJOR_SOUL_NAMES = {
    0: ("The Fool", "Si Pengembara Bebas"),
    1: ("The Magician", "Sang Manifestor & Kreator"),
    2: ("The High Priestess", "Penjaga Misteri & Intuisi"),
    3: ("The Empress", "Kelimpahan & Cinta Murni"),
    4: ("The Emperor", "Pemimpin Strategis & Otoritas"),
    5: ("The Hierophant", "Pembawa Kebijaksanaan Tradisi"),
    6: ("The Lovers", "Harmoni & Pilihan Hati"),
    7: ("The Chariot", "Fokus Tekad & Kemenangan"),
    8: ("Strength", "Kekuatan Batin & Welas Asih"),
    9: ("The Hermit", "Pencari Cahaya Jiwa"),
    10: ("Wheel of Fortune", "Siklus Takdir & Peluang"),
    11: ("Justice", "Kebenaran & Keseimbangan"),
    12: ("The Hanged Man", "Transparansi & Pencerahan Diri"),
    13: ("Death", "Transformasi & Kebangkitan Baru"),
    14: ("Temperance", "Harmoni & Alkimia Kehidupan"),
    15: ("The Devil", "Pembebasan dari Belenggu Ilusi"),
    16: ("The Tower", "Pelepasan Topeng & Kebenaran"),
    17: ("The Star", "Harapan Abadi & Ketenangan Jiwa"),
    18: ("The Moon", "Menembus Ilusi Bawah Sadar"),
    19: ("The Sun", "Kejayaan, Vitalitas & Kegembiraan"),
    20: ("Judgement", "Panggilan Jiwa & Kelahiran Kembali"),
    21: ("The World", "Kesempurnaan & Pencapaian Kosmik")
}


class TarotOracleWindow(Gtk.Window):
    def __init__(self, name="", dob="", focus="", spread="three", auto_summon=False):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Flowork Sovereign Tarot Oracle")
        self.set_role("tarot_oracle")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(980, 620)
        self.set_size_request(980, 620)
        self.set_keep_above(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Load Database
        self.cards_db = []
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                self.cards_db = json.load(f)

        # State: "FORM", "PICKING", "ANIMATING", "RESULT", "JOURNAL"
        self.state = "FORM"
        self.auto_summon_mode = auto_summon

        # Form Data
        self.user_name = ""
        self.user_dob = ""
        self.user_focus = ""
        self.selected_spread = spread if spread in ("single", "three", "five") else "three"
        self.birth_card_id = None
        self.birth_card_name = ""

        # Interactive Fan Picking Data
        self.fan_pool = []
        self.picked_indices = []
        self.hovered_fan_idx = -1

        # Result Data
        self.drawn_cards = []
        self.active_card_idx = 0
        self.ai_synthesis = ""
        self.ai_loading = False
        self.voice_proc = None
        self.journal_entries = []
        self.lang = "ID"
        self.hovered_tab_idx = -1

        # Animation Timing & Interpolation
        self.anim_t = 0.0          # Current time in seconds
        self.anim_duration = 3.2   # Total reveal time
        self.rot_vortex = 0.0
        self.particles = []
        self._init_particles()
        self.card_flipped_sfx_played = False
        self.card_reveal_sfx_played = False

        # Pixbuf Cache
        self.pixbuf_cache = {}

        # Interactive Hover & Button States
        self.hovered_btn = None
        self.feedback_msg = ""
        self.feedback_timer = 0

        # Fixed Container for Input Widgets
        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        self._build_form_inputs()

        # Auto-load Sovereign User Identity if CLI parameters are not provided
        if not name or not dob:
            for prof_path in (
                os.path.expanduser("~/.config/floworkos/user_profile.json"),
                "/opt/floworkos/config/user_profile.json",
            ):
                if os.path.exists(prof_path):
                    try:
                        with open(prof_path, "r", encoding="utf-8") as pf:
                            pdata = json.load(pf)
                        if not name and pdata.get("full_name"):
                            name = str(pdata["full_name"]).strip()
                        if not dob and pdata.get("birth_date"):
                            dob = str(pdata["birth_date"]).strip()
                        if name and dob:
                            break
                    except Exception:
                        pass

        # Pre-fill from CLI parameters or Sovereign User Profile
        if name:
            self.entry_name.set_text(name)
        if dob:
            self.entry_dob.set_text(dob)
            self._on_dob_changed(self.entry_dob)
        if focus:
            self.entry_focus.set_text(focus)

        if auto_summon:
            GLib.timeout_add(300, self.start_summon)

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.KEY_PRESS_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-press-event", self.on_key_press)

        # 60 FPS Animation Tick
        GLib.timeout_add(16, self.on_tick)

    def get_pos_label(self, item):
        if self.lang == "EN":
            return item.get("pos_label_en", item.get("pos_label", "CARD"))
        return item.get("pos_label_id", item.get("pos_label", "KARTU"))

    def _clear_feedback(self):
        self.feedback_msg = ""
        self.feedback_timer = 0
        self.queue_draw()
        return False

    def set_language(self, new_lang):
        if self.lang == new_lang:
            return
        self.lang = new_lang
        if hasattr(self, "entry_name"):
            if self.lang == "EN":
                self.entry_name.set_placeholder_text("Full Name / Seeker Persona (e.g. Sovereign Seeker)")
                self.entry_dob.set_placeholder_text("Date of Birth: DD-MM-YYYY (e.g. 01-01-1990)")
                self.entry_focus.set_placeholder_text("Inquiry Focus (e.g. Career Direction & Life Path)")
            else:
                self.entry_name.set_placeholder_text("Nama Lengkap / Persona (e.g. Sovereign Seeker)")
                self.entry_dob.set_placeholder_text("Tanggal Lahir: DD-MM-YYYY (e.g. 01-01-1990)")
                self.entry_focus.set_placeholder_text("Fokus Pertanyaan (e.g. Arah Karier & Visi Masa Depan)")
        if self.state == "RESULT":
            self.ai_synthesis = self._build_local_synthesis()
            self.feedback_msg = "Language set to English" if self.lang == "EN" else "Bahasa diubah ke Indonesia"
            if self.feedback_timer:
                GLib.source_remove(self.feedback_timer)
            self.feedback_timer = GLib.timeout_add(2500, self._clear_feedback)
        self.queue_draw()

    def _init_particles(self):
        self.particles = []
        for _ in range(45):
            self.particles.append({
                "ang": random.uniform(0, 2 * math.pi),
                "dist": random.uniform(60, 240),
                "speed": random.uniform(1.2, 3.5),
                "size": random.uniform(2.0, 4.5),
                "col": random.choice([C_GREEN, C_CYAN, C_GOLD, C_PURPLE]),
                "alpha": random.uniform(0.3, 0.9)
            })

    def _build_form_inputs(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            entry {
                background: rgba(0, 20, 30, 0.65);
                border: 1px solid rgba(0, 242, 254, 0.35);
                border-radius: 8px;
                color: #ffffff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11.5px;
                padding: 6px 12px;
            }
            entry:focus {
                border-color: #00ff66;
                background: rgba(0, 30, 45, 0.85);
            }
            entry placeholder {
                color: rgba(255, 255, 255, 0.30);
            }
        """)

        # 1. Name Entry
        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text("Nama Anda / Persona (e.g. Awenkaudico)")
        self.entry_name.set_size_request(420, 34)
        self.entry_name.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.entry_name.connect("changed", self._on_input_changed)
        self.entry_name.connect("activate", lambda e: self.entry_dob.grab_focus())
        self.fixed.put(self.entry_name, 280, 148)

        # 2. Birth Date Entry
        self.entry_dob = Gtk.Entry()
        self.entry_dob.set_placeholder_text("Tanggal Lahir: DD-MM-YYYY (e.g. 15-05-1995)")
        self.entry_dob.set_size_request(420, 34)
        self.entry_dob.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.entry_dob.connect("changed", self._on_dob_changed)
        self.entry_dob.connect("activate", lambda e: self.entry_focus.grab_focus())
        self.fixed.put(self.entry_dob, 280, 214)

        # 3. Focus / Question Entry
        self.entry_focus = Gtk.Entry()
        self.entry_focus.set_placeholder_text("Fokus / Pertanyaan Batin (e.g. Arah Karier & Visi 2027)")
        self.entry_focus.set_size_request(420, 34)
        self.entry_focus.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.entry_focus.connect("changed", self._on_input_changed)
        self.entry_focus.connect("activate", lambda e: self.start_summon())
        self.fixed.put(self.entry_focus, 280, 294)

    def _on_dob_changed(self, entry):
        val = entry.get_text().strip()
        bc_num = calc_birth_card(val)
        if bc_num is not None and bc_num in MAJOR_SOUL_NAMES:
            self.birth_card_id = bc_num
            en_name, id_name = MAJOR_SOUL_NAMES[bc_num]
            self.birth_card_name = f"{en_name} ({id_name})"
        else:
            self.birth_card_id = None
            self.birth_card_name = ""
        self.queue_draw()

    def _on_input_changed(self, entry):
        self.queue_draw()

    def on_tick(self):
        if self.state == "ANIMATING":
            self.anim_t += 0.016
            self.rot_vortex = (self.rot_vortex + 0.06) % (2 * math.pi)

            # Sound Cues
            if self.anim_t >= 1.0 and not self.card_flipped_sfx_played:
                play_sfx(SFX_WHOOSH)
                self.card_flipped_sfx_played = True

            if self.anim_t >= 2.0 and not self.card_reveal_sfx_played:
                play_sfx(SFX_LASER)
                self.card_reveal_sfx_played = True

            # Particle Motion
            for p in self.particles:
                p["ang"] += 0.04
                p["dist"] += p["speed"]
                if p["dist"] > 320:
                    p["dist"] = random.uniform(30, 90)

            if self.anim_t >= self.anim_duration:
                self.state = "RESULT"
                play_sfx(SFX_SUCCESS)
                self.queue_draw()

            self.queue_draw()
        return True

    def start_summon(self, force_auto=False):
        self.user_name = self.entry_name.get_text().strip() or "Sovereign Traveler"
        self.user_dob = self.entry_dob.get_text().strip()
        self.user_focus = self.entry_focus.get_text().strip() or "Pencerahan & Arah Takdir"

        self.birth_card_id = calc_birth_card(self.user_dob)
        self.birth_card_name = MAJOR_SOUL_NAMES.get(self.birth_card_id, ("", ""))[0] if self.birth_card_id is not None else ""

        # Hide inputs during summon & result
        self.entry_name.hide()
        self.entry_dob.hide()
        self.entry_focus.hide()

        # Seed quantum random generator
        seed_str = f"{self.user_name}_{self.user_dob}_{self.user_focus}_{time.time_ns()}"
        rng = random.Random(seed_str)

        count_map = {"single": 1, "three": 3, "five": 5}
        count = count_map.get(self.selected_spread, 3)
        pool = list(self.cards_db) if self.cards_db else []
        rng.shuffle(pool)

        if force_auto or self.auto_summon_mode or len(pool) < 9:
            chosen_cards = pool[:count]
            self._finalize_drawn_cards(chosen_cards, rng)
        else:
            # Interactive Fan Spread: deal 9 face-down cards for user to pick
            self.fan_pool = pool[:9]
            self.picked_indices = []
            self.hovered_fan_idx = -1
            self.state = "PICKING"
            play_sfx(SFX_WHOOSH)
            self.queue_draw()

    def _finalize_drawn_cards(self, chosen_cards, rng=None):
        if rng is None:
            rng = random.Random(f"{self.user_name}_{time.time_ns()}")

        pos_labels_id = {
            "single": ["PANDUAN & ENERGI UTAMA"],
            "three": ["01. MASA LALU", "02. SITUASI SAAT INI", "03. MASA DEPAN & SOLUSI"],
            "five": ["01. INTI PERSOALAN", "02. AKAR BAWAH SADAR", "03. RINTANGAN UTAMA", "04. POTENSI TERSEMBUNYI", "05. HASIL & MANTRA TAKDIR"]
        }
        pos_labels_en = {
            "single": ["PRIMARY GUIDANCE & ENERGY"],
            "three": ["01. PAST INFLUENCE", "02. PRESENT SITUATION", "03. FUTURE & OUTCOME"],
            "five": ["01. CORE INQUIRY", "02. SUBCONSCIOUS ROOT", "03. MAIN OBSTACLE", "04. HIDDEN POTENTIAL", "05. DESTINY SYNTHESIS"]
        }
        labels_id = pos_labels_id.get(self.selected_spread, pos_labels_id["three"])
        labels_en = pos_labels_en.get(self.selected_spread, pos_labels_en["three"])
        drawn = []
        for i, chosen in enumerate(chosen_cards):
            is_upright = rng.random() < 0.72
            pos_id = labels_id[i] if i < len(labels_id) else f"KARTU {i+1}"
            pos_en = labels_en[i] if i < len(labels_en) else f"CARD {i+1}"
            drawn.append({
                "pos_label_id": pos_id,
                "pos_label_en": pos_en,
                "pos_label": pos_en if self.lang == "EN" else pos_id,
                "card": chosen,
                "is_upright": is_upright
            })
        self.drawn_cards = drawn
        self.active_card_idx = 0
        self.ai_synthesis = self._build_local_synthesis()
        self.ai_loading = True

        # Persist result to /tmp/flowork_tarot_result.json for agent integration
        self._save_cache_file()

        # Async AI Synthesis enrichment
        threading.Thread(target=self._fetch_ai_synthesis, daemon=True).start()

        # Reset Animation Parameters
        self.state = "ANIMATING"
        self.anim_t = 0.0
        self.card_flipped_sfx_played = False
        self.card_reveal_sfx_played = False
        self._init_particles()
        self.queue_draw()

    def _save_daily_and_journal(self, cache_data):
        today_str = datetime.date.today().isoformat()
        first = cache_data["cards"][0] if cache_data.get("cards") else None
        if first:
            os.makedirs(os.path.dirname(DAILY_CACHE_PATH), exist_ok=True)
            daily_payload = {
                "date": today_str,
                "name": first["name"],
                "indo_name": first["indo_name"],
                "element": first["element"],
                "is_upright": first["is_upright"],
                "orientation": first["orientation"],
                "advice": first["meanings"][0] if first.get("meanings") else "",
                "focus": cache_data.get("focus", "")
            }
            with open(DAILY_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(daily_payload, f, indent=2, ensure_ascii=False)

        os.makedirs(os.path.dirname(JOURNAL_PATH), exist_ok=True)
        entries = []
        if os.path.exists(JOURNAL_PATH):
            try:
                with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            except Exception:
                entries = []
        entries.insert(0, {
            "timestamp": cache_data["timestamp"],
            "name": cache_data["user_name"],
            "focus": cache_data["focus"],
            "spread": cache_data["spread"],
            "soul_birth_card": cache_data["soul_birth_card"],
            "cards": [
                {
                    "pos_label": c["pos_label"],
                    "name": c["name"],
                    "indo_name": c["indo_name"],
                    "element": c["element"],
                    "is_upright": c["is_upright"]
                }
                for c in cache_data["cards"]
            ]
        })
        entries = entries[:50]
        with open(JOURNAL_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

    def _load_journal(self):
        if os.path.exists(JOURNAL_PATH):
            try:
                with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
                    self.journal_entries = json.load(f)
                    return
            except Exception:
                pass
        self.journal_entries = []

    def _build_local_synthesis(self):
        if not self.drawn_cards:
            return ""
        elems = [dc["card"].get("element", "Spirit") for dc in self.drawn_cards]
        dom_elem = max(set(elems), key=elems.count)
        upright_cnt = sum(1 for dc in self.drawn_cards if dc["is_upright"])
        if self.lang == "EN":
            tone = "energy is clear, open, and strongly supportive" if upright_cnt >= len(self.drawn_cards) / 2 else "energy invites mindful pause, inner reflection, and patience"
            names = ", ".join(f"{dc['card']['name']} ({'Upright' if dc['is_upright'] else 'Reversed'})" for dc in self.drawn_cards)
            soul_note = f" Aligned with Soul Birth Card {self.birth_card_name}," if self.birth_card_name else ""
            return (
                f"Cosmic Synthesis ({dom_elem}): Combination of {names} indicates {tone}.{soul_note} "
                f"Focus on '{self.user_focus}' calls for decisive strategic action while honoring cosmic intuition."
            )
        else:
            names = ", ".join(f"{dc['card'].get('indo_name', dc['card']['name'])} ({'Tegak' if dc['is_upright'] else 'Terbalik'})" for dc in self.drawn_cards)
            tone = "arus energi terbuka dan mendukung eksekusi" if upright_cnt >= len(self.drawn_cards) / 2 else "fase refleksi dan kalibrasi ulang strategi"
            soul_note = f" Selaras dengan Soul Card {self.birth_card_name}," if self.birth_card_name else ""
            return (
                f"Sintesis Kuantum ({dom_elem}): Kombinasi {names} menunjukkan {tone}.{soul_note} "
                f"Fokus '{self.user_focus}' menuntut ketegasan langkah pertama tanpa mengabaikan intuisi."
            )

    def _fetch_ai_synthesis(self):
        if self.lang == "EN":
            cards_desc = "; ".join(
                f"{self.get_pos_label(dc)}: {dc['card']['name']} ({'Upright' if dc['is_upright'] else 'Reversed'}, {dc['card'].get('element', '')})"
                for dc in self.drawn_cards
            )
            prompt = (
                f"Provide a concise, empowering tarot synthesis (max 2 dense sentences in natural English, no weird symbols) "
                f"for {self.user_name} (Soul Card: {self.birth_card_name or 'Unknown'}), focus: '{self.user_focus}'. "
                f"Cards: {cards_desc}."
            )
        else:
            cards_desc = "; ".join(
                f"{self.get_pos_label(dc)}: {dc['card'].get('indo_name', dc['card']['name'])} ({'Tegak' if dc['is_upright'] else 'Terbalik'}, {dc['card'].get('element', '')})"
                for dc in self.drawn_cards
            )
            prompt = (
                f"Berikan sintesis tarot singkat (maksimal 2 kalimat padat dalam Bahasa Indonesia natural, tanpa simbol aneh) "
                f"untuk {self.user_name} (Soul Card: {self.birth_card_name or 'Unknown'}), fokus: '{self.user_focus}'. "
                f"Kartu: {cards_desc}."
            )
        result_text = None
        for url, payload in [
            ("http://127.0.0.1:9099/v1/chat/completions", {
                "model": "auto",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 140,
                "temperature": 0.7
            }),
            ("http://127.0.0.1:11434/api/generate", {
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False
            })
        ]:
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if "choices" in data and data["choices"]:
                        result_text = data["choices"][0]["message"]["content"].strip()
                    elif "response" in data:
                        result_text = data["response"].strip()
                if result_text:
                    break
            except Exception:
                continue

        def _apply():
            self.ai_loading = False
            if result_text:
                self.ai_synthesis = result_text.replace("\n", " ").strip()
                self._save_cache_file()
            self.queue_draw()
            return False
        GLib.idle_add(_apply)

    def _save_cache_file(self):
        if not self.drawn_cards:
            return None
        try:
            cache_data = {
                "user_name": self.user_name,
                "user_dob": self.user_dob,
                "soul_birth_card": self.birth_card_name,
                "focus": self.user_focus,
                "spread": self.selected_spread,
                "language": self.lang,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cards": [
                    {
                        "pos_label": dc.get("pos_label_en" if self.lang == "EN" else "pos_label_id", dc.get("pos_label", "")),
                        "name": dc["card"]["name"],
                        "indo_name": dc["card"]["indo_name"],
                        "is_upright": dc["is_upright"],
                        "orientation": "UPRIGHT" if (self.lang == "EN" and dc["is_upright"]) else ("REVERSED" if self.lang == "EN" else ("TEGAK" if dc["is_upright"] else "TERBALIK")),
                        "rarity": dc["card"]["rarity"],
                        "element": dc["card"]["element"],
                        "zodiac": dc["card"]["zodiac"],
                        "keywords": dc["card"]["keywords"],
                        "meanings": dc["card"]["upright_meaning"] if dc["is_upright"] else dc["card"]["reversed_meaning"],
                        "fortune_telling": dc["card"]["fortune_telling"]
                    }
                    for dc in self.drawn_cards
                ],
                "ai_synthesis": self.ai_synthesis or self._build_local_synthesis()
            }
            with open("/tmp/flowork_tarot_result.json", "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            if hasattr(self, "_save_daily_and_journal"):
                self._save_daily_and_journal(cache_data)
            print("[FLOWORK TAROT] Cache updated at /tmp/flowork_tarot_result.json", flush=True)
            return cache_data
        except Exception as e:
            print(f"[FLOWORK TAROT ERROR] Failed saving cache: {e}", flush=True)
            return None

    def ask_mrflow(self):
        if not self.drawn_cards:
            return

        # 1. Update /tmp/flowork_tarot_result.json with latest state
        self._save_cache_file()

        # 2. Tactile SFX feedback
        try:
            subprocess.Popen(["flowork-sound-forge", "play", "pop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # 3. Formulate prompt to activate passive trigger and metaphysics skill
        spread_cnt = len(self.drawn_cards)
        user_name = self.user_name or "Seeker"
        user_focus = self.user_focus or ("Pencerahan & Arah Takdir" if self.lang == "ID" else "Destiny Guidance")

        if self.lang == "EN":
            prompt = (
                f"Please read and interpret my tarot card spread ({spread_cnt}-card spread) in depth for {user_name} "
                f"focusing on '{user_focus}' using the metaphysics-oracle-engine skill based on the generated "
                f"result in /tmp/flowork_tarot_result.json. Analyze each card's archetype, upright/reversed dynamics, "
                f"resonance with my Soul Birth Card ({self.birth_card_name}), and provide actionable philosophical guidance."
            )
        else:
            prompt = (
                f"Tolong bacakan dan interpretasikan secara mendalam hasil tebaran kartu tarot saya "
                f"(tebaran {spread_cnt} kartu) untuk {user_name} dengan fokus '{user_focus}' menggunakan "
                f"skill metaphysics-oracle-engine berdasarkan hasil generate di /tmp/flowork_tarot_result.json. "
                f"Mohon berikan analisis arketipe tiap kartu, dinamika posisi tegak/terbalik, resonansi Soul Birth Card "
                f"({self.birth_card_name}), dan panduan praktis yang solutif."
            )

        # 4. Inject prompt to Flowork Neural Conduit via UNIX socket
        user = os.environ.get("USER", "mrflow")
        sock_path = f"/tmp/flowork-neural-conduit-{user}.sock"
        dispatched = False

        if os.path.exists(sock_path):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(2.5)
                s.connect(sock_path)
                payload = json.dumps({"action": "send_prompt", "prompt": prompt})
                s.sendall(payload.encode("utf-8"))
                resp = s.recv(1024)
                s.close()
                if b"OK" in resp:
                    dispatched = True
            except Exception as ex:
                print(f"[flowork-tarot-oracle] Socket send error: {ex}", file=sys.stderr)

        if not dispatched:
            try:
                subprocess.Popen(["flowork-neural-conduit", "--prompt", prompt], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                dispatched = True
            except Exception:
                try:
                    subprocess.Popen(["mrflow", "-p", prompt, "-o", "stream-json", "--sovereign"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    dispatched = True
                except Exception as ex:
                    print(f"[flowork-tarot-oracle] CLI fallback error: {ex}", file=sys.stderr)

        # 5. Visual HUD feedback
        if dispatched:
            self.feedback_msg = "✨ Prompt dikirim ke Mr. Flow! Menunggu bacaan..." if self.lang == "ID" else "✨ Sent to Mr. Flow! Oracle reading initiated..."
        else:
            self.feedback_msg = "⚠️ Gagal mengirim prompt ke Mr. Flow" if self.lang == "ID" else "⚠️ Failed to dispatch prompt to Mr. Flow"

        if self.feedback_timer:
            GLib.source_remove(self.feedback_timer)
        self.feedback_timer = GLib.timeout_add(3500, self._clear_feedback)
        self.queue_draw()

    def _toggle_voice_oracle(self):
        if self.voice_proc and self.voice_proc.poll() is None:
            try:
                self.voice_proc.terminate()
            except Exception:
                pass
            self.voice_proc = None
            self.feedback_msg = "Mr. Flow voice stopped" if self.lang == "EN" else "Suara Mr. Flow dihentikan"
            if self.feedback_timer:
                GLib.source_remove(self.feedback_timer)
            self.feedback_timer = GLib.timeout_add(2000, self._clear_feedback)
            self.queue_draw()
            return

        if not self.drawn_cards:
            return

        dc = self.drawn_cards[self.active_card_idx]
        card = dc["card"]
        if self.lang == "EN":
            ori = "Upright" if dc["is_upright"] else "Reversed"
            speech_text = (
                f"Card {self.active_card_idx + 1}: {card['name']}, in {ori} position. "
                f"Oracle guidance from Mr. Flow: {self.ai_synthesis or self._build_local_synthesis()}"
            )
            lang_code = "en"
        else:
            ori = "tegak" if dc["is_upright"] else "terbalik"
            speech_text = (
                f"Kartu {self.active_card_idx + 1}: {card.get('indo_name', card['name'])}, dalam posisi {ori}. "
                f"Nasihat kosmik dari Mr. Flow: {self.ai_synthesis or self._build_local_synthesis()}"
            )
            lang_code = "id"

        try:
            self.voice_proc = subprocess.Popen(
                ["/opt/floworkos/bin/flowork-say", "--lang", lang_code, speech_text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.feedback_msg = "✨ Mr. Flow is speaking..." if self.lang == "EN" else "✨ Mr. Flow sedang menarasikan ramalan..."
            if self.feedback_timer:
                GLib.source_remove(self.feedback_timer)
            self.feedback_timer = GLib.timeout_add(3000, self._clear_feedback)
        except Exception as e:
            print(f"[FLOWORK TAROT] Voice error: {e}", flush=True)

        self.queue_draw()

    def reset_to_form(self):
        if self.voice_proc and self.voice_proc.poll() is None:
            try:
                self.voice_proc.terminate()
            except Exception:
                pass
            self.voice_proc = None
        self.state = "FORM"
        self.entry_name.show()
        self.entry_dob.show()
        self.entry_focus.show()
        self.queue_draw()

    def save_oracle_reading(self):
        if not self.drawn_cards:
            return
        self.copy_oracle_reading()
        try:
            cache_data = {
                "user_name": self.user_name,
                "user_dob": self.user_dob,
                "soul_birth_card": self.birth_card_name,
                "focus": self.user_focus,
                "spread": self.selected_spread,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cards": [
                    {
                        "pos_label": self.get_pos_label(dc),
                        "name": dc["card"]["name"],
                        "indo_name": dc["card"].get("indo_name", dc["card"]["name"]),
                        "is_upright": dc["is_upright"],
                        "orientation": "UPRIGHT" if dc["is_upright"] else "REVERSED",
                        "rarity": dc["card"].get("rarity", "MYTHIC"),
                        "element": dc["card"].get("element", "Cosmic"),
                        "zodiac": dc["card"].get("zodiac", "Cosmic"),
                        "keywords": dc["card"].get("keywords", []),
                        "meanings": dc["card"]["upright_meaning"] if dc["is_upright"] else dc["card"]["reversed_meaning"],
                        "fortune_telling": dc["card"].get("fortune_telling", [])
                    }
                    for dc in self.drawn_cards
                ],
                "synthesis": self.ai_synthesis or self._build_local_synthesis()
            }
            self._save_to_journal(cache_data)
        except Exception:
            pass
        self.feedback_msg = "✓ Reading saved to Journal & copied to Clipboard!" if self.lang == "EN" else "✓ Ramalan tersimpan di Jurnal & disalin ke Clipboard!"
        if self.feedback_timer:
            GLib.source_remove(self.feedback_timer)
        self.feedback_timer = GLib.timeout_add(3000, self._clear_feedback)
        self.queue_draw()

    def copy_oracle_reading(self):
        if not self.drawn_cards:
            return
        lines = [
            "==================================================",
            f"🔮 FLOWORK OS — SOVEREIGN TAROT ORACLE READING",
            "==================================================",
            f"Seeker / Penanya : {self.user_name} (DOB: {self.user_dob or 'N/A'})",
            f"Soul Birth Card  : {self.birth_card_name or 'Cosmic Archetype'}",
            f"Focus / Persoalan: {self.user_focus}",
            f"Spread / Tebaran : {self.selected_spread.upper()}",
            f"Timestamp        : {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "--------------------------------------------------"
        ]
        for i, dc in enumerate(self.drawn_cards):
            card = dc["card"]
            ori = ("UPRIGHT" if dc["is_upright"] else "REVERSED") if self.lang == "EN" else ("TEGAK" if dc["is_upright"] else "TERBALIK")
            pos_label = self.get_pos_label(dc)
            lines.append(f"\n[{pos_label}] {card['name'].upper()} ({card.get('indo_name', card['name'])})")
            lines.append(f"Status           : {ori}")
            lines.append(f"Element & Zodiac : {card.get('element', '')} • {card.get('zodiac', '')}")
            meanings = card.get("upright_meaning" if dc["is_upright"] else "reversed_meaning", [])
            lines.append(f"Key Meanings     : {', '.join(meanings[:3])}")

        lines.append("\n--------------------------------------------------")
        guidance_title = "💡 SYNTHESIS & PRACTICAL GUIDANCE:" if self.lang == "EN" else "💡 SINTESIS & NASIHAT TAKDIR:"
        lines.append(f"{guidance_title}\n{self.ai_synthesis or self._build_local_synthesis()}")
        lines.append("==================================================")
        lines.append("Generated by Flowork Sovereign Metaphysics Oracle Engine.")

        text = "\n".join(lines)
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()

        self.feedback_msg = "✓ Reading copied to clipboard!" if self.lang == "EN" else "✓ Ramalan berhasil disalin ke clipboard!"
        if self.feedback_timer:
            GLib.source_remove(self.feedback_timer)
        self.feedback_timer = GLib.timeout_add(3000, self._clear_feedback)
        self.queue_draw()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False

    def _get_fan_card_pos(self, idx, total=9):
        mid = (total - 1) / 2.0
        offset = idx - mid
        angle = offset * 0.11
        cx = 490 + offset * 78
        cy = 320 + (offset * offset) * 4.5
        if idx == self.hovered_fan_idx and idx not in self.picked_indices:
            cy -= 24
        elif idx in self.picked_indices:
            cy -= 34
        return cx, cy, angle

    def on_motion(self, widget, event):
        x, y = event.x, event.y
        old_hov = self.hovered_btn
        self.hovered_btn = None

        # Global Top Bar hover check
        if 910 <= x <= 960 and 20 <= y <= 50:
            self.hovered_btn = "close"
        elif 790 <= x <= 875 and 20 <= y <= 50:
            self.hovered_btn = "lang_toggle"

        if self.state == "FORM":
            if 345 <= y <= 377:
                if 280 <= x <= 410:
                    self.hovered_btn = "spread_single"
                elif 425 <= x <= 555:
                    self.hovered_btn = "spread_three"
                elif 570 <= x <= 700:
                    self.hovered_btn = "spread_five"

            if 280 <= x <= 700 and 395 <= y <= 445:
                self.hovered_btn = "summon"

            if 675 <= x <= 775 and 22 <= y <= 48:
                self.hovered_btn = "journal"

        elif self.state == "PICKING":
            if 390 <= x <= 590 and 520 <= y <= 570:
                self.hovered_btn = "cancel"

            # Interactive Fan Cards hover
            self.hovered_fan_idx = -1
            for idx in range(len(self.fan_pool) - 1, -1, -1):
                cx, cy, _ = self._get_fan_card_pos(idx, len(self.fan_pool))
                if (cx - 55) <= x <= (cx + 55) and (cy - 90) <= y <= (cy + 90):
                    self.hovered_fan_idx = idx
                    break

        elif self.state == "RESULT":
            # Tab hover
            self.hovered_tab_idx = -1
            if len(self.drawn_cards) > 1 and 48 <= y <= 80:
                for idx in range(len(self.drawn_cards)):
                    tx = 40 + idx * 165
                    if tx <= x <= tx + 155:
                        self.hovered_tab_idx = idx
                        break

            # Bottom 5 buttons hover
            if 555 <= y <= 595:
                if 40 <= x <= 200:
                    self.hovered_btn = "reshuffle"
                elif 215 <= x <= 390:
                    self.hovered_btn = "ask_mrflow"
                elif 405 <= x <= 550:
                    self.hovered_btn = "save"
                elif 565 <= x <= 705:
                    self.hovered_btn = "history"
                elif 840 <= x <= 940:
                    self.hovered_btn = "close"

        elif self.state == "JOURNAL":
            if 555 <= y <= 595:
                if 40 <= x <= 200:
                    self.hovered_btn = "back_form"
                elif 830 <= x <= 940:
                    self.hovered_btn = "close"

        if self.hovered_btn != old_hov:
            self.queue_draw()

    def on_button_press(self, widget, event):
        if event.button != 1:
            return
        x, y = event.x, event.y
        print(f"[FLOWORK TAROT CLICK] state={self.state} x={x} y={y}", flush=True)

        # Global Top Bar Actions
        if 910 <= x <= 960 and 20 <= y <= 50:
            print(f"[FLOWORK TAROT DESTROY] Global close icon clicked at x={x} y={y}", flush=True)
            self.destroy()
            return

        if 790 <= x <= 875 and 20 <= y <= 50:
            if x < 832:
                self.set_language("ID")
            else:
                self.set_language("EN")
            return

        if self.state == "FORM":
            if 675 <= x <= 775 and 22 <= y <= 48:
                self._load_journal()
                self.entry_name.hide()
                self.entry_dob.hide()
                self.entry_focus.hide()
                self.state = "JOURNAL"
                self.queue_draw()
                return

            if 345 <= y <= 377:
                if 280 <= x <= 410:
                    self.selected_spread = "single"
                    play_sfx(SFX_CHIME)
                    self.queue_draw()
                    return
                elif 425 <= x <= 555:
                    self.selected_spread = "three"
                    play_sfx(SFX_CHIME)
                    self.queue_draw()
                    return
                elif 570 <= x <= 700:
                    self.selected_spread = "five"
                    play_sfx(SFX_CHIME)
                    self.queue_draw()
                    return

            if 280 <= x <= 700 and 395 <= y <= 445:
                self.start_summon()
                return

        elif self.state == "PICKING":
            if 390 <= x <= 590 and 520 <= y <= 570:
                self.reset_to_form()
                return

            needed = 1 if self.selected_spread == "single" else (3 if self.selected_spread == "three" else 5)
            # Center fan quick pick
            if 420 <= x <= 560 and 450 <= y <= 500:
                remaining = [i for i in range(len(self.fan_pool)) if i not in self.picked_indices]
                random.shuffle(remaining)
                while len(self.picked_indices) < needed and remaining:
                    self.picked_indices.append(remaining.pop(0))
                chosen = [self.fan_pool[i] for i in self.picked_indices]
                self._finalize_drawn_cards(chosen)
                return

            for idx in range(len(self.fan_pool) - 1, -1, -1):
                cx, cy, _ = self._get_fan_card_pos(idx, len(self.fan_pool))
                if (cx - 55) <= x <= (cx + 55) and (cy - 90) <= y <= (cy + 90):
                    if idx not in self.picked_indices:
                        self.picked_indices.append(idx)
                        play_sfx(SFX_WHOOSH)
                        if len(self.picked_indices) >= needed:
                            chosen = [self.fan_pool[i] for i in self.picked_indices]
                            self._finalize_drawn_cards(chosen)
                        self.queue_draw()
                    return

        elif self.state == "RESULT":
            if 48 <= y <= 80:
                for idx in range(len(self.drawn_cards)):
                    tx = 40 + idx * 165
                    if tx <= x <= tx + 155:
                        self.active_card_idx = idx
                        self.queue_draw()
                        return

            # Bottom 5 buttons clicks
            if 555 <= y <= 595:
                if 40 <= x <= 200:
                    print("[FLOWORK TAROT] Button reshuffle clicked", flush=True)
                    self.reset_to_form()
                    return
                elif 215 <= x <= 390:
                    print("[FLOWORK TAROT] Button ask_mrflow clicked", flush=True)
                    self.ask_mrflow()
                    return
                elif 405 <= x <= 550:
                    print("[FLOWORK TAROT] Button save clicked", flush=True)
                    self.save_oracle_reading()
                    return
                elif 565 <= x <= 720:
                    print("[FLOWORK TAROT] Button journal clicked", flush=True)
                    self._load_journal()
                    self.state = "JOURNAL"
                    self.queue_draw()
                    return
                elif 735 <= x <= 940:
                    print("[FLOWORK TAROT] Button close clicked", flush=True)
                    self.destroy()
                    return

        elif self.state == "JOURNAL":
            if 555 <= y <= 595:
                if 40 <= x <= 200:
                    self.reset_to_form()
                    return
                elif 830 <= x <= 940:
                    self.destroy()
                    return

    def on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        w, h = 980, 620
        layout = PangoCairo.create_layout(cr)

        # 1. Main Outer Crystal Glass HUD Body
        draw_rounded_rect(cr, 10, 10, w - 20, h - 20, 22)
        cr.set_source_rgba(0.01, 0.03, 0.07, 0.96)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 0.40)
        cr.set_line_width(1.2)
        cr.stroke()

        # Top Highlight Specular Rim
        cr.save()
        cr.move_to(28, 12)
        cr.line_to(w - 28, 12)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.28)
        cr.set_line_width(1.0)
        cr.stroke()
        cr.restore()

        # Close Icon Top-Right
        cx_btn, cy_btn, cw_btn, ch_btn = 910, 22, 45, 26
        draw_rounded_rect(cr, cx_btn, cy_btn, cw_btn, ch_btn, 6)
        is_close_hov = (self.hovered_btn == "close")
        cr.set_source_rgba(0.20, 0.04, 0.06, 0.85 if is_close_hov else 0.40)
        cr.fill_preserve()
        cr.set_source_rgba(*C_RED, 0.80 if is_close_hov else 0.40)
        cr.set_line_width(0.8)
        cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        layout.set_text("✕ ESC", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.90)
        cr.move_to(cx_btn + (cw_btn - tw) / 2, cy_btn + (ch_btn - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Language Switcher Toggle [ ID | EN ] Top-Right
        lx_btn, ly_btn, lw_btn, lh_btn = 790, 22, 85, 26
        draw_rounded_rect(cr, lx_btn, ly_btn, lw_btn, lh_btn, 6)
        cr.set_source_rgba(0.03, 0.07, 0.12, 0.85)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.40)
        cr.set_line_width(0.8)
        cr.stroke()

        # ID Pill
        idx_w = 38
        draw_rounded_rect(cr, lx_btn + 2, ly_btn + 2, idx_w, lh_btn - 4, 4)
        if self.lang == "ID":
            cr.set_source_rgba(0.0, 0.50, 0.35, 0.75)
            cr.fill_preserve()
            cr.set_source_rgba(*C_GREEN, 0.85)
            cr.set_line_width(0.8)
            cr.stroke()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        layout.set_text("ID", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*(C_WHITE if self.lang == "ID" else (0.6, 0.7, 0.8)), 0.95 if self.lang == "ID" else 0.45)
        cr.move_to(lx_btn + 2 + (idx_w - tw) / 2, ly_btn + 2 + (lh_btn - 4 - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # EN Pill
        enx_w = 38
        draw_rounded_rect(cr, lx_btn + 43, ly_btn + 2, enx_w, lh_btn - 4, 4)
        if self.lang == "EN":
            cr.set_source_rgba(0.0, 0.50, 0.35, 0.75)
            cr.fill_preserve()
            cr.set_source_rgba(*C_GREEN, 0.85)
            cr.set_line_width(0.8)
            cr.stroke()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        layout.set_text("EN", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*(C_WHITE if self.lang == "EN" else (0.6, 0.7, 0.8)), 0.95 if self.lang == "EN" else 0.45)
        cr.move_to(lx_btn + 43 + (enx_w - tw) / 2, ly_btn + 2 + (lh_btn - 4 - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Render Specific State
        if self.state == "FORM":
            self._render_form(cr, layout, w, h)
        elif self.state == "PICKING":
            self._render_picking(cr, layout, w, h)
        elif self.state == "ANIMATING":
            self._render_animating(cr, layout, w, h)
        elif self.state == "RESULT":
            self._render_result(cr, layout, w, h)
        elif self.state == "JOURNAL":
            self._render_journal(cr, layout, w, h)

    def _render_form(self, cr, layout, w, h):
        # Header Badge & Title
        cr.arc(50, 48, 5.0, 0, 2 * math.pi)
        cr.set_source_rgba(*C_PURPLE, 0.95)
        cr.fill()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 14.0"))
        layout.set_text("🔮 FLOWORK SOVEREIGN TAROT ORACLE", -1)
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(65, 38)
        PangoCairo.show_layout(cr, layout)

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text("Quantum Synchronicity & Archetypal Destiny Engine (Carl Jung Archetypes + RWS 78 Cards)", -1)
        cr.set_source_rgba(*C_CYAN, 0.70)
        cr.move_to(65, 62)
        PangoCairo.show_layout(cr, layout)

        # Journal Button Top-Right
        jx, jy, jw, jh = 675, 22, 100, 26
        draw_rounded_rect(cr, jx, jy, jw, jh, 6)
        is_j_hov = (self.hovered_btn == "journal")
        cr.set_source_rgba(0.10, 0.06, 0.22, 0.85 if is_j_hov else 0.45)
        cr.fill_preserve()
        cr.set_source_rgba(*C_PURPLE, 0.85 if is_j_hov else 0.45)
        cr.set_line_width(0.8)
        cr.stroke()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        j_lbl = "📜 HISTORY" if self.lang == "EN" else "📜 RIWAYAT"
        layout.set_text(j_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.92)
        cr.move_to(jx + (jw - tw) / 2, jy + (jh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Hairline Separator
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.08)
        cr.set_line_width(0.8)
        cr.move_to(35, 86)
        cr.line_to(w - 35, 86)
        cr.stroke()

        # Center Card Deco Hologram (Face Down Preview on Left)
        self._render_card_back(cr, 65, 140, 180, 310)

        # Form Field Labels
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))

        # Label 1: Nama
        f_lbl1 = "1. FULL NAME / COSMIC PERSONA:" if self.lang == "EN" else "1. NAMA LENGKAP / PERSONA KOSMIK:"
        layout.set_text(f_lbl1, -1)
        cr.set_source_rgba(*C_CYAN, 0.85)
        cr.move_to(280, 130)
        PangoCairo.show_layout(cr, layout)

        # Label 2: Tanggal Lahir
        f_lbl2 = "2. DATE OF BIRTH (FOR SOUL BIRTH CARD & ZODIAC):" if self.lang == "EN" else "2. TANGGAL LAHIR (UNTUK TAROT BIRTH CARD & ZODIAK):"
        layout.set_text(f_lbl2, -1)
        cr.set_source_rgba(*C_PURPLE, 0.85)
        cr.move_to(280, 196)
        PangoCairo.show_layout(cr, layout)

        # Live Birth Card Indicator
        if self.birth_card_name:
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.0"))
            layout.set_text(f"🌟 SOUL BIRTH CARD: {self.birth_card_name.upper()}", -1)
            cr.set_source_rgba(*C_GOLD, 0.95)
            cr.move_to(282, 256)
            PangoCairo.show_layout(cr, layout)

        # Label 3: Pertanyaan
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        f_lbl3 = "3. INQUIRY FOCUS / INNER INTENTION:" if self.lang == "EN" else "3. FOKUS PERSOALAN / NIAT BATIN (INTENTION):"
        layout.set_text(f_lbl3, -1)
        cr.set_source_rgba(*C_GREEN, 0.85)
        cr.move_to(280, 276)
        PangoCairo.show_layout(cr, layout)

        # Spread Selector Buttons
        sp_y = 345
        spread_opts = [
            ("single", "1 CARD (QUICK)" if self.lang == "EN" else "1 KARTU (QUICK)", 280, 130),
            ("three", "3 CARDS (TIME)" if self.lang == "EN" else "3 KARTU (PAST-PRES-FUT)", 425, 130),
            ("five", "5 CARDS (DEPTH)" if self.lang == "EN" else "5 KARTU (DECISION)", 570, 130)
        ]
        for sp_key, sp_lbl, sx, sw in spread_opts:
            is_sel = (self.selected_spread == sp_key)
            is_hov = (self.hovered_btn == f"spread_{sp_key}")

            draw_rounded_rect(cr, sx, sp_y, sw, 32, 8)
            if is_sel:
                cr.set_source_rgba(0.00, 0.35, 0.25, 0.85)
                cr.fill_preserve()
                cr.set_source_rgba(*C_GREEN, 0.90)
                cr.set_line_width(1.2)
                cr.stroke()
            else:
                cr.set_source_rgba(0.00, 0.10, 0.18, 0.65 if is_hov else 0.45)
                cr.fill_preserve()
                cr.set_source_rgba(*C_CYAN, 0.60 if is_hov else 0.25)
                cr.set_line_width(0.8)
                cr.stroke()

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.0"))
            layout.set_text(sp_lbl, -1)
            tw, th = layout.get_pixel_size()
            cr.set_source_rgba(*C_WHITE, 0.95 if is_sel else 0.70)
            cr.move_to(sx + (sw - tw) / 2, sp_y + (32 - th) / 2)
            PangoCairo.show_layout(cr, layout)

        # Big Summon Action Button
        btn_x, btn_y, btn_w, btn_h = 280, 395, 420, 48
        draw_rounded_rect(cr, btn_x, btn_y, btn_w, btn_h, 14)
        is_s_hov = (self.hovered_btn == "summon")
        cr.set_source_rgba(0.00, 0.40, 0.28, 0.95 if is_s_hov else 0.85)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 1.0 if is_s_hov else 0.65)
        cr.set_line_width(1.5 if is_s_hov else 1.0)
        cr.stroke()

        # Inner Specular
        cr.save()
        cr.move_to(btn_x + 12, btn_y + 2)
        cr.line_to(btn_x + btn_w - 12, btn_y + 2)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.40)
        cr.set_line_width(1.0)
        cr.stroke()
        cr.restore()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10.5"))
        s_btn_lbl = "✨ SUMMON DESTINY SPREAD (REVEAL) ✨" if self.lang == "EN" else "✨ BUKA KARTU TAKDIR (SUMMON ORACLE) ✨"
        layout.set_text(s_btn_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.98)
        cr.move_to(btn_x + (btn_w - tw) / 2, btn_y + (btn_h - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # Footer Tip
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.0"))
        layout.set_text("💡 HINT: Tanggal lahir opsional; jika diisi, kartu akan otomatis beresonansi dengan Tarot Birth Card jiwa Anda.", -1)
        cr.set_source_rgba(*C_MUTED, 0.70)
        cr.move_to(140, 520)
        PangoCairo.show_layout(cr, layout)

    def _render_picking(self, cr, layout, w, h):
        needed = 1 if self.selected_spread == "single" else (3 if self.selected_spread == "three" else 5)
        picked_cnt = len(self.picked_indices)

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 13.0"))
        p_hdr = f"✦ CHOOSE {needed} DESTINY CARD(S) ({picked_cnt}/{needed})" if self.lang == "EN" else f"✦ PILIH {needed} KARTU TAKDIRMU ({picked_cnt}/{needed})"
        layout.set_text(p_hdr, -1)
        tw, _ = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to((w - tw) / 2, 42)
        PangoCairo.show_layout(cr, layout)

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 8.0"))
        layout.set_text(f"Fokus: {self.user_focus}  •  Klik kartu di kipas untuk menarik energi", -1)
        tw2, _ = layout.get_pixel_size()
        cr.set_source_rgba(*C_CYAN, 0.78)
        cr.move_to((w - tw2) / 2, 70)
        PangoCairo.show_layout(cr, layout)

        # Draw 9 face-down cards in a curved fan arc
        cw, ch = 110, 180
        for idx in range(len(self.fan_pool)):
            cx, cy, angle = self._get_fan_card_pos(idx, len(self.fan_pool))
            is_hov = (idx == self.hovered_fan_idx)
            is_picked = (idx in self.picked_indices)

            cr.save()
            cr.translate(cx, cy)
            cr.rotate(angle)

            # Card shadow
            draw_rounded_rect(cr, -cw / 2 + 4, -ch / 2 + 6, cw, ch, 10)
            cr.set_source_rgba(0.0, 0.0, 0.0, 0.45)
            cr.fill()

            # Card back body
            draw_rounded_rect(cr, -cw / 2, -ch / 2, cw, ch, 10)
            pat = cairo.LinearGradient(-cw / 2, -ch / 2, cw / 2, ch / 2)
            if is_picked:
                pat.add_color_stop_rgba(0.0, 0.22, 0.16, 0.04, 0.98)
                pat.add_color_stop_rgba(1.0, 0.10, 0.06, 0.18, 0.98)
            elif is_hov:
                pat.add_color_stop_rgba(0.0, 0.06, 0.20, 0.30, 0.98)
                pat.add_color_stop_rgba(1.0, 0.12, 0.06, 0.26, 0.98)
            else:
                pat.add_color_stop_rgba(0.0, 0.05, 0.07, 0.16, 0.96)
                pat.add_color_stop_rgba(1.0, 0.09, 0.04, 0.18, 0.96)
            cr.set_source(pat)
            cr.fill_preserve()

            if is_picked:
                cr.set_source_rgba(*C_GOLD, 0.95)
                cr.set_line_width(2.2)
            elif is_hov:
                cr.set_source_rgba(*C_CYAN, 0.95)
                cr.set_line_width(2.0)
            else:
                cr.set_source_rgba(*C_PURPLE, 0.45)
                cr.set_line_width(1.0)
            cr.stroke()

            # Inner sacred geometry diamond
            draw_rounded_rect(cr, -cw / 2 + 8, -ch / 2 + 8, cw - 16, ch - 16, 6)
            cr.set_source_rgba(*(C_GOLD if is_picked else (C_CYAN if is_hov else C_PURPLE)), 0.35)
            cr.set_line_width(0.8)
            cr.stroke()

            cr.arc(0, 0, 22, 0, 2 * math.pi)
            cr.set_source_rgba(*(C_GOLD if is_picked else C_CYAN), 0.25 if not is_hov else 0.55)
            cr.set_line_width(1.0)
            cr.stroke()

            if is_picked:
                slot_num = self.picked_indices.index(idx) + 1
                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 14.0"))
                layout.set_text(f"#{slot_num}", -1)
                stw, sth = layout.get_pixel_size()
                cr.set_source_rgba(*C_GOLD, 0.98)
                cr.move_to(-stw / 2, -sth / 2)
                PangoCairo.show_layout(cr, layout)
            else:
                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 11.0"))
                layout.set_text("✦", -1)
                stw, sth = layout.get_pixel_size()
                cr.set_source_rgba(*(C_CYAN if is_hov else C_PURPLE), 0.85)
                cr.move_to(-stw / 2, -sth / 2)
                PangoCairo.show_layout(cr, layout)

            cr.restore()

        # Auto Pick Button
        ax, ay, aw, ah = 390, 545, 200, 40
        draw_rounded_rect(cr, ax, ay, aw, ah, 8)
        is_auto_hov = (self.hovered_btn == "auto_pick")
        cr.set_source_rgba(0.06, 0.14, 0.22, 0.90 if is_auto_hov else 0.60)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.85 if is_auto_hov else 0.45)
        cr.set_line_width(1.0)
        cr.stroke()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.5"))
        layout.set_text("⚡ AUTO PICK REMAINING", -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(ax + (aw - tw) / 2, ay + (ah - th) / 2)
        PangoCairo.show_layout(cr, layout)

    def _render_journal(self, cr, layout, w, h):
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 13.0"))
        layout.set_text("📜 SOVEREIGN TAROT JOURNAL & PATTERN TRACKER", -1)
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(40, 34)
        PangoCairo.show_layout(cr, layout)

        # Element Pattern Summary
        elem_counts = {}
        for entry in self.journal_entries:
            for c in entry.get("cards", []):
                el = c.get("element", "Spirit")
                elem_counts[el] = elem_counts.get(el, 0) + 1
        if elem_counts:
            dom_el = max(elem_counts, key=elem_counts.get)
            summary = f"Total Bacaan: {len(self.journal_entries)}  •  Elemen Dominan: {dom_el} ({elem_counts[dom_el]}x)"
        else:
            summary = "Belum ada riwayat bacaan tersimpan."

        layout.set_font_description(Pango.FontDescription("JetBrains Mono 8.0"))
        layout.set_text(summary, -1)
        cr.set_source_rgba(*C_CYAN, 0.85)
        cr.move_to(40, 62)
        PangoCairo.show_layout(cr, layout)

        # List up to 6 recent entries
        y_cur = 96
        for entry in self.journal_entries[:6]:
            draw_rounded_rect(cr, 40, y_cur, w - 80, 66, 8)
            cr.set_source_rgba(0.06, 0.09, 0.16, 0.75)
            cr.fill_preserve()
            cr.set_source_rgba(*C_PURPLE, 0.30)
            cr.set_line_width(0.8)
            cr.stroke()

            ts = entry.get("timestamp", "")
            focus = entry.get("focus", "")
            cards_str = "  |  ".join(
                f"{c.get('indo_name', c.get('name'))} ({'T' if c.get('is_upright') else 'R'})"
                for c in entry.get("cards", [])
            )

            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.0"))
            layout.set_text(f"{ts}  •  {entry.get('name', '')}  •  Fokus: {focus[:48]}", -1)
            cr.set_source_rgba(*C_GOLD, 0.92)
            cr.move_to(56, y_cur + 10)
            PangoCairo.show_layout(cr, layout)

            layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
            layout.set_text(cards_str[:110], -1)
            cr.set_source_rgba(*C_WHITE, 0.85)
            cr.move_to(56, y_cur + 34)
            PangoCairo.show_layout(cr, layout)

            y_cur += 74

        # Bottom Buttons: [ <- KEMBALI ] [ TUTUP ]
        bx1, by, bw1, bh = 40, 555, 160, 40
        draw_rounded_rect(cr, bx1, by, bw1, bh, 8)
        is_b_hov = (self.hovered_btn == "back_form")
        cr.set_source_rgba(0.06, 0.14, 0.22, 0.90 if is_b_hov else 0.60)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.85 if is_b_hov else 0.45)
        cr.set_line_width(1.0)
        cr.stroke()
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.5"))
        j_back = "← BACK" if self.lang == "EN" else "← KEMBALI"
        layout.set_text(j_back, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(bx1 + (bw1 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        bx3, bw3 = w - 155, 110
        draw_rounded_rect(cr, bx3, by, bw3, bh, 8)
        is_c_hov = (self.hovered_btn == "close")
        cr.set_source_rgba(0.20, 0.04, 0.06, 0.85 if is_c_hov else 0.45)
        cr.fill_preserve()
        cr.set_source_rgba(*C_RED, 0.80 if is_c_hov else 0.40)
        cr.set_line_width(1.0)
        cr.stroke()
        j_close = "✕ CLOSE" if self.lang == "EN" else "✕ TUTUP"
        layout.set_text(j_close, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.90)
        cr.move_to(bx3 + (bw3 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

    def _render_animating(self, cr, layout, w, h):
        cx, cy = w / 2.0, h / 2.0 - 12.0
        t = self.anim_t
        n_cards = max(1, len(self.drawn_cards))

        # 1. Jarvis Holographic Telemetry Grid & Counter-Rotating Orbital Rings
        cr.save()
        cr.translate(cx, cy)

        cr.set_source_rgba(*C_CYAN, 0.07)
        cr.set_line_width(0.8)
        for r_grid in (110, 190, 270, 350):
            cr.arc(0, 0, r_grid, 0, math.tau)
            cr.stroke()
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            cr.move_to(math.cos(rad) * 70, math.sin(rad) * 70)
            cr.line_to(math.cos(rad) * 360, math.sin(rad) * 360)
            cr.stroke()

        for i in range(4):
            r_ring = 85 + i * 52
            cr.save()
            cr.rotate(self.rot_vortex * (1.2 if i % 2 == 0 else -1.0) + i * 0.5)
            ring_col = [C_CYAN, C_GOLD, C_GREEN, C_PURPLE][i % 4]
            cr.set_source_rgba(*ring_col, 0.32 - i * 0.05)
            cr.set_line_width(1.6 if i % 2 == 0 else 1.0)
            if i % 2 == 1:
                cr.set_dash([14, 8, 4, 8])
            cr.arc(0, 0, r_ring, 0.15, 1.75 * math.pi)
            cr.stroke()
            cr.restore()

        core_r = 26 + 6 * math.sin(t * 8.0)
        core_grad = cairo.RadialGradient(0, 0, 2, 0, 0, core_r * 2.2)
        core_grad.add_color_stop_rgba(0.0, *C_CYAN, 0.55)
        core_grad.add_color_stop_rgba(0.5, *C_GOLD, 0.18)
        core_grad.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        cr.set_source(core_grad)
        cr.arc(0, 0, core_r * 2.2, 0, math.tau)
        cr.fill()
        cr.restore()

        # Top Jarvis Subject Telemetry Header
        subj_txt = f"JARVIS QUANTUM MATRIX  //  SUBJECT: {self.user_name.upper()}  //  DOB: {self.user_dob or 'SYNCED'}"
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 9.0"))
        layout.set_text(subj_txt, -1)
        stw, _ = layout.get_pixel_size()
        cr.set_source_rgba(*C_CYAN, 0.85)
        cr.move_to(cx - stw / 2.0, 68)
        PangoCairo.show_layout(cr, layout)

        # 2. Compute Target Arc Positions for all N cards
        card_w = 128.0 if n_cards >= 5 else 156.0
        card_h = 206.0 if n_cards >= 5 else 250.0
        spacing = min(158.0, (w - 140.0) / max(1, n_cards))
        deploy_p = min(1.0, t / 0.90)
        ease_deploy = 1.0 - (1.0 - deploy_p) ** 3

        positions = []
        for idx in range(n_cards):
            offset_idx = idx - (n_cards - 1) / 2.0
            tx = cx + offset_idx * spacing
            ty = cy + (abs(offset_idx) ** 1.5) * 14.0 - 10.0
            px = cx + (tx - cx) * ease_deploy
            py = cy + (ty - cy) * ease_deploy
            tilt = offset_idx * 0.055 * ease_deploy
            positions.append((px, py, tilt))

        # 3. Energy Constellation Conduits between cards
        if ease_deploy > 0.35 and n_cards > 1:
            conduit_alpha = min(0.65, (ease_deploy - 0.35) * 1.0)
            cr.set_source_rgba(*C_CYAN, conduit_alpha * 0.55)
            cr.set_line_width(1.4)
            for idx in range(n_cards - 1):
                x1, y1, _ = positions[idx]
                x2, y2, _ = positions[idx + 1]
                cr.move_to(x1, y1)
                cr.curve_to((x1 + x2) / 2.0, min(y1, y2) - 28.0, (x1 + x2) / 2.0, min(y1, y2) - 28.0, x2, y2)
                cr.stroke()

        # 4. Sweeping Jarvis Laser Scanner (0.85s -> 2.55s)
        if 0.85 <= t <= 2.55:
            scan_p = (t - 0.85) / 1.70
            scan_x = (cx - (n_cards * spacing) / 2.0 - 40) + scan_p * (n_cards * spacing + 80)
            scan_grad = cairo.LinearGradient(scan_x - 24, 0, scan_x + 24, 0)
            scan_grad.add_color_stop_rgba(0.0, *C_CYAN, 0.0)
            scan_grad.add_color_stop_rgba(0.5, *C_CYAN, 0.55)
            scan_grad.add_color_stop_rgba(1.0, *C_CYAN, 0.0)
            cr.set_source(scan_grad)
            cr.rectangle(scan_x - 24, cy - 160, 48, 320)
            cr.fill()
            cr.set_source_rgba(*C_GOLD, 0.85)
            cr.set_line_width(1.5)
            cr.move_to(scan_x, cy - 160)
            cr.line_to(scan_x, cy + 160)
            cr.stroke()

        # 5. Render Each Card with Sequential 3D Flip & Shockwave
        for idx, dc in enumerate(self.drawn_cards):
            px, py, tilt = positions[idx]
            flip_start = 0.95 + idx * (1.25 / max(1, n_cards))
            flip_dur = 0.42
            local_flip = max(0.0, min(1.0, (t - flip_start) / flip_dur))

            if 0.05 < local_flip < 0.95:
                sr = 30 + local_flip * 85
                cr.set_source_rgba(*C_GOLD, (1.0 - local_flip) * 0.75)
                cr.set_line_width(1.8)
                cr.arc(px, py, sr, 0, math.tau)
                cr.stroke()

            angle = local_flip * math.pi
            scale_x = max(0.04, abs(math.cos(angle)))
            show_front = local_flip >= 0.5
            hover_y = py + math.sin(t * 4.0 + idx * 0.9) * 4.0

            cr.save()
            cr.translate(px, hover_y)
            cr.rotate(tilt)
            cr.scale(scale_x, 1.0)
            if not show_front:
                self._render_card_back(cr, -card_w / 2.0, -card_h / 2.0, card_w, card_h)
            else:
                self._render_card_front_with_frame(
                    cr, -card_w / 2.0, -card_h / 2.0, card_w, card_h, dc["card"], dc["is_upright"]
                )
                if t > flip_start + flip_dur:
                    foil_p = min(1.0, (t - (flip_start + flip_dur)) / 0.7)
                    self._render_foil_sheen(cr, -card_w / 2.0, -card_h / 2.0, card_w, card_h, foil_p)
            cr.restore()

            if show_front:
                cname = dc["card"]["name"]
                if len(cname) > 16:
                    cname = cname[:15] + "…"
                orient = "UPRIGHT" if dc["is_upright"] else "REVERSED"
                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.0"))
                layout.set_text(f"{cname}\n[{orient}]", -1)
                layout.set_alignment(Pango.Alignment.CENTER)
                lw, _ = layout.get_pixel_size()
                cr.set_source_rgba(*(C_GOLD if dc["is_upright"] else C_CYAN), 0.92)
                cr.move_to(px - lw / 2.0, hover_y + card_h / 2.0 + 10)
                PangoCairo.show_layout(cr, layout)
                layout.set_alignment(Pango.Alignment.LEFT)

        # 6. Bottom Jarvis Status Telemetry
        if t < 0.95:
            status_text = f"DEPLOYING {n_cards}-CARD QUANTUM MATRIX..."
            status_col = C_CYAN
        elif t < 2.45:
            status_text = "SCANNING & UNLOCKING HOLOGRAPHIC SEALS..."
            status_col = C_GOLD
        else:
            status_text = f"{n_cards}-CARD MATRIX SYNCHRONIZED // GENERATING QUANTUM SYNTHESIS..."
            status_col = C_GREEN

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10.0"))
        layout.set_text(status_text, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*status_col, 0.95)
        cr.move_to(cx - tw / 2.0, h - 52)
        PangoCairo.show_layout(cr, layout)

    def _render_result(self, cr, layout, w, h):
        if not self.drawn_cards:
            return

        cur_item = self.drawn_cards[self.active_card_idx]
        card = cur_item["card"]
        is_upright = cur_item["is_upright"]
        pos_label = cur_item["pos_label"]

        # Top Tabs if multiple cards
        if len(self.drawn_cards) > 1:
            for idx, dc in enumerate(self.drawn_cards):
                tx = 40 + idx * 165
                is_active = (idx == self.active_card_idx)
                is_hov = (self.hovered_btn == f"tab_{idx}")

                draw_rounded_rect(cr, tx, 48, 155, 28, 6)
                if is_active:
                    cr.set_source_rgba(0.00, 0.32, 0.22, 0.85)
                    cr.fill_preserve()
                    cr.set_source_rgba(*C_GREEN, 0.90)
                    cr.set_line_width(1.0)
                    cr.stroke()
                else:
                    cr.set_source_rgba(0.00, 0.08, 0.15, 0.60 if is_hov else 0.35)
                    cr.fill_preserve()
                    cr.set_source_rgba(*C_CYAN, 0.50 if is_hov else 0.20)
                    cr.set_line_width(0.7)
                    cr.stroke()

                layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
                tab_text = self.get_pos_label(dc)
                if len(tab_text) > 20:
                    tab_text = tab_text[:19] + "…"
                layout.set_text(tab_text, -1)
                ttw, tth = layout.get_pixel_size()
                cr.set_source_rgba(*C_WHITE, 0.95 if is_active else 0.65)
                cr.move_to(tx + (155 - ttw) / 2, 48 + (28 - tth) / 2)
                PangoCairo.show_layout(cr, layout)

        # Hairline
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.08)
        cr.set_line_width(0.8)
        cr.move_to(35, 86)
        cr.line_to(w - 35, 86)
        cr.stroke()

        # Left Column: Card Artwork Display
        card_x, card_y, card_w, card_h = 45, 110, 245, 415
        self._render_card_front_with_frame(cr, card_x, card_y, card_w, card_h, card, is_upright)

        # Right Column: The Prophecy Ledger
        deck_x = 315
        deck_y = 110
        deck_w = w - deck_x - 45
        deck_h = 425

        draw_rounded_rect(cr, deck_x, deck_y, deck_w, deck_h, 14)
        cr.set_source_rgba(0.00, 0.05, 0.10, 0.70)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.30)
        cr.set_line_width(0.9)
        cr.stroke()

        # Position Tag
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.5"))
        pos_hdr = "❖ SPREAD POSITION:" if self.lang == "EN" else "❖ POSISI BACAAN:"
        layout.set_text(f"{pos_hdr} {self.get_pos_label(cur_item)}", -1)
        cr.set_source_rgba(*C_CYAN, 0.90)
        cr.move_to(deck_x + 18, deck_y + 16)
        PangoCairo.show_layout(cr, layout)

        # Card Title
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 12.0"))
        card_heading = card['name'].upper() if self.lang == "EN" else f"{card['name'].upper()} • {card.get('indo_name', card['name']).upper()}"
        layout.set_text(card_heading, -1)
        cr.set_source_rgba(*C_WHITE, 0.98)
        cr.move_to(deck_x + 18, deck_y + 36)
        PangoCairo.show_layout(cr, layout)

        # Badges Row: Rarity, Orientation, Element/Zodiac
        badge_y = deck_y + 65
        ori_badge = ("🌟 UPRIGHT" if is_upright else "🔄 REVERSED") if self.lang == "EN" else ("🌟 TEGAK" if is_upright else "🔄 TERBALIK")
        badges = [
            (card.get("rarity", "MYTHIC"), C_GOLD),
            (ori_badge, C_GREEN if is_upright else C_AMBER),
            (f"⚡ {card.get('element', card.get('zodiac', 'Cosmic'))}", C_PURPLE)
        ]
        bx_cur = deck_x + 18
        for b_text, b_col in badges:
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.5"))
            layout.set_text(b_text, -1)
            btw, bth = layout.get_pixel_size()
            draw_rounded_rect(cr, bx_cur - 4, badge_y - 2, btw + 10, bth + 4, 4)
            cr.set_source_rgba(*b_col, 0.15)
            cr.fill_preserve()
            cr.set_source_rgba(*b_col, 0.50)
            cr.set_line_width(0.7)
            cr.stroke()
            cr.set_source_rgba(*b_col, 0.95)
            cr.move_to(bx_cur, badge_y)
            PangoCairo.show_layout(cr, layout)
            bx_cur += btw + 18

        # Birth Card Synergy Notice
        if self.birth_card_name:
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 6.8"))
            syn_text = f"🧬 Soul Synergy: Resonating with Soul Birth Card [{self.birth_card_name}]" if self.lang == "EN" else f"🧬 Sinergi Jiwa: Dihubungkan dengan Soul Birth Card [{self.birth_card_name}]"
            layout.set_text(syn_text, -1)
            cr.set_source_rgba(*C_GOLD, 0.85)
            cr.move_to(deck_x + 18, deck_y + 92)
            PangoCairo.show_layout(cr, layout)

        # Hairline inner
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.06)
        cr.set_line_width(0.8)
        cr.move_to(deck_x + 18, deck_y + 112)
        cr.line_to(deck_x + deck_w - 18, deck_y + 112)
        cr.stroke()

        # Keywords Matrix
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.2"))
        kw_hdr = "🔑 ENERGY KEYWORDS:" if self.lang == "EN" else "🔑 KATA KUNCI ENERGI:"
        layout.set_text(kw_hdr, -1)
        cr.set_source_rgba(*C_GREEN, 0.85)
        cr.move_to(deck_x + 18, deck_y + 122)
        PangoCairo.show_layout(cr, layout)

        kw_list = card.get("keywords", [])[:6]
        kw_text = " • ".join(kw_list) if kw_list else ("Intuition, Synchronicity, Clarity" if self.lang == "EN" else "Intuisi, Sinkronisitas, Transformasi")
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text(kw_text, -1)
        cr.set_source_rgba(*C_WHITE, 0.85)
        cr.move_to(deck_x + 18, deck_y + 138)
        PangoCairo.show_layout(cr, layout)

        # Oracle Interpretation (Light vs Shadow)
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.2"))
        if self.lang == "EN":
            meaning_hdr = "📜 UPRIGHT ARCHETYPE & ESSENCE:" if is_upright else "📜 REVERSED ARCHETYPE & SHADOW LESSON:"
        else:
            meaning_hdr = "📜 MAKNA TEGAK & PESAN TAKDIR:" if is_upright else "📜 MAKNA TERBALIK & TANTANGAN JIWA:"
        layout.set_text(meaning_hdr, -1)
        cr.set_source_rgba(*C_CYAN, 0.85)
        cr.move_to(deck_x + 18, deck_y + 168)
        PangoCairo.show_layout(cr, layout)

        meanings = card.get("upright_meaning" if is_upright else "reversed_meaning", [])
        if not meanings:
            meanings = ["Cosmic energy flows quietly through this archetype." if self.lang == "EN" else "Energi misterius mengalir dalam fase ini."]
        m_lines = "\n".join([f"• {m}" for m in meanings[:4]])
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text(m_lines, -1)
        cr.set_source_rgba(*C_WHITE, 0.90)
        cr.move_to(deck_x + 18, deck_y + 185)
        PangoCairo.show_layout(cr, layout)

        # Fortune Telling Prophecy
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.2"))
        prophecy_hdr = "🔮 INTUITIVE GUIDANCE & DIRECTION:" if self.lang == "EN" else "🔮 INTUISI RAMALAN / PERKIRAAN ARAH:"
        layout.set_text(prophecy_hdr, -1)
        cr.set_source_rgba(*C_PURPLE, 0.90)
        cr.move_to(deck_x + 18, deck_y + 270)
        PangoCairo.show_layout(cr, layout)

        fortunes = card.get("fortune_telling", [])
        if fortunes:
            f_text = fortunes[0]
        else:
            f_text = "Opportunity is wide open; center your resolve and inner clarity." if self.lang == "EN" else "Peluang terbuka lebar; pusatkan tekad dan kejernihan batin."
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.5"))
        layout.set_text(f"\"{f_text}\"", -1)
        cr.set_source_rgba(*C_AMBER, 0.95)
        cr.move_to(deck_x + 18, deck_y + 288)
        PangoCairo.show_layout(cr, layout)

        # Actionable Advice Box
        adv_y = deck_y + 325
        draw_rounded_rect(cr, deck_x + 18, adv_y, deck_w - 36, 75, 8)
        cr.set_source_rgba(0.00, 0.15, 0.12, 0.60)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 0.35)
        cr.set_line_width(0.8)
        cr.stroke()

        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.2"))
        guidance_hdr = "💡 SYNTHESIS & PRACTICAL GUIDANCE:" if self.lang == "EN" else "💡 TINDAKAN PRAKTIS & MANTRA JIWA:"
        layout.set_text(guidance_hdr, -1)
        cr.set_source_rgba(*C_GREEN, 0.90)
        cr.move_to(deck_x + 30, adv_y + 10)
        PangoCairo.show_layout(cr, layout)

        advice = self.ai_synthesis or (
            "Ambil langkah tegas hari ini tanpa keraguan. Sinkronkan logika pikiran dengan getaran batin; "
            "energi semesta sedang mendukung inisiatif yang dimulai dengan integritas."
        )
        layout.set_font_description(Pango.FontDescription("JetBrains Mono 7.0"))
        layout.set_width(Pango.units_from_double(deck_w - 60))
        layout.set_wrap(Pango.WrapMode.WORD)
        layout.set_text(advice, -1)
        cr.set_source_rgba(*C_WHITE, 0.88)
        cr.move_to(deck_x + 30, adv_y + 28)
        PangoCairo.show_layout(cr, layout)
        layout.set_width(-1)  # reset wrap

        # Bottom Bar Buttons: [ COPY ALL ] [ TARIK LAGI ] [ VOICE ] [ JOURNAL ] [ TUTUP ]
        self._render_bottom_buttons(cr, layout, w, h)

    def _render_bottom_buttons(self, cr, layout, w, h):
        by = 555
        bh = 38

        # 1. Reshuffle Button (Kocok Ulang)
        bx1, bw1 = 40, 160
        is_shuf_hov = (self.hovered_btn == "reshuffle")
        draw_rounded_rect(cr, bx1, by, bw1, bh, 8)
        cr.set_source_rgba(0.02, 0.14, 0.22, 0.85 if is_shuf_hov else 0.55)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.80 if is_shuf_hov else 0.35)
        cr.set_line_width(1.0)
        cr.stroke()

        shuf_lbl = "🔄 RESHUFFLE" if self.lang == "EN" else "🔄 KOCOK ULANG"
        layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 8.0"))
        layout.set_text(shuf_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(bx1 + (bw1 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 2. Ask Mr. Flow Button (Tanya Mr. Flow / Prompt Injection)
        bx2, bw2 = 215, 175
        is_ask_hov = (self.hovered_btn == "ask_mrflow")
        is_sent = bool(self.feedback_msg and "Mr. Flow" in self.feedback_msg)
        draw_rounded_rect(cr, bx2, by, bw2, bh, 8)
        cr.set_source_rgba(0.18, 0.08, 0.30, 0.85 if (is_ask_hov or is_sent) else 0.55)
        cr.fill_preserve()
        cr.set_source_rgba(*(C_CYAN if is_sent else C_PURPLE), 0.95 if (is_ask_hov or is_sent) else 0.40)
        cr.set_line_width(1.3 if is_sent else 1.0)
        cr.stroke()

        if is_sent:
            ask_lbl = "✓ DISPATCHED" if self.lang == "EN" else "✓ TERKIRIM"
        else:
            ask_lbl = "✨ ASK MR. FLOW" if self.lang == "EN" else "✨ TANYA MR. FLOW"
        layout.set_text(ask_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*(C_CYAN if is_sent else C_WHITE), 0.95)
        cr.move_to(bx2 + (bw2 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 3. Save Button (Simpan & Salin)
        bx3, bw3 = 405, 145
        is_save_hov = (self.hovered_btn == "save")
        draw_rounded_rect(cr, bx3, by, bw3, bh, 8)
        cr.set_source_rgba(0.00, 0.28, 0.20, 0.85 if is_save_hov else 0.55)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GREEN, 0.80 if is_save_hov else 0.35)
        cr.set_line_width(1.0)
        cr.stroke()

        save_lbl = "💾 SAVE" if self.lang == "EN" else "💾 SIMPAN"
        layout.set_text(save_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(bx3 + (bw3 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 4. History Button (Riwayat)
        bx4, bw4 = 565, 140
        is_hist_hov = (self.hovered_btn == "history")
        draw_rounded_rect(cr, bx4, by, bw4, bh, 8)
        cr.set_source_rgba(0.18, 0.14, 0.02, 0.85 if is_hist_hov else 0.55)
        cr.fill_preserve()
        cr.set_source_rgba(*C_GOLD, 0.75 if is_hist_hov else 0.35)
        cr.set_line_width(1.0)
        cr.stroke()

        hist_lbl = "📜 HISTORY" if self.lang == "EN" else "📜 RIWAYAT"
        layout.set_text(hist_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(bx4 + (bw4 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 5. Close Button (Tutup)
        bx5, bw5 = 840, 100
        is_close_hov = (self.hovered_btn == "close")
        draw_rounded_rect(cr, bx5, by, bw5, bh, 8)
        cr.set_source_rgba(0.25, 0.04, 0.06, 0.85 if is_close_hov else 0.55)
        cr.fill_preserve()
        cr.set_source_rgba(*C_RED, 0.80 if is_close_hov else 0.35)
        cr.set_line_width(1.0)
        cr.stroke()

        close_lbl = "✕ CLOSE" if self.lang == "EN" else "✕ TUTUP"
        layout.set_text(close_lbl, -1)
        tw, th = layout.get_pixel_size()
        cr.set_source_rgba(*C_WHITE, 0.95)
        cr.move_to(bx5 + (bw5 - tw) / 2, by + (bh - th) / 2)
        PangoCairo.show_layout(cr, layout)

        # 6. Elegant Feedback Toast HUD Banner
        if self.feedback_msg:
            layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 10"))
            layout.set_text(self.feedback_msg, -1)
            tw, th = layout.get_pixel_size()
            toast_x = (980 - tw) / 2
            toast_y = 525
            draw_rounded_rect(cr, toast_x - 14, toast_y - 4, tw + 28, th + 8, 8)
            cr.set_source_rgba(0.02, 0.08, 0.14, 0.94)
            cr.fill_preserve()
            cr.set_source_rgba(*C_CYAN, 0.85)
            cr.set_line_width(1.0)
            cr.stroke()

            cr.set_source_rgba(*C_WHITE, 1.0)
            cr.move_to(toast_x, toast_y)
            PangoCairo.show_layout(cr, layout)

    def _render_card_back(self, cr, x, y, w, h):
        draw_rounded_rect(cr, x, y, w, h, 10)
        cr.set_source_rgba(0.01, 0.04, 0.08, 0.95)
        cr.fill_preserve()
        cr.set_source_rgba(*C_CYAN, 0.70)
        cr.set_line_width(1.2)
        cr.stroke()

        # Sacred Geometry Pattern on Back
        cr.save()
        cr.translate(x + w / 2, y + h / 2)
        for i in range(3):
            cr.arc(0, 0, (w / 3.0) - i * 12, 0, 2 * math.pi)
            cr.set_source_rgba(*C_GREEN, 0.35)
            cr.set_line_width(1.0)
            cr.stroke()

        # Diamond Grid
        cr.move_to(0, -h / 3)
        cr.line_to(w / 3, 0)
        cr.line_to(0, h / 3)
        cr.line_to(-w / 3, 0)
        cr.close_path()
        cr.set_source_rgba(*C_CYAN, 0.45)
        cr.set_line_width(1.0)
        cr.stroke()
        cr.restore()

    def _render_active_card_front(self, cr, x, y, w, h):
        if not self.drawn_cards:
            return
        cur_item = self.drawn_cards[self.active_card_idx]
        self._render_card_front_with_frame(cr, x, y, w, h, cur_item["card"], cur_item["is_upright"])

    def _render_card_front_with_frame(self, cr, x, y, w, h, card, is_upright):
        # Outer Card Bevel
        draw_rounded_rect(cr, x, y, w, h, 10)
        cr.set_source_rgba(0.01, 0.03, 0.06, 0.98)
        cr.fill_preserve()
        if not is_upright:
            border_col = C_AMBER
        elif card.get("is_major"):
            border_col = C_GOLD
        else:
            border_col = C_CYAN
        cr.set_source_rgba(*border_col, 0.90)
        cr.set_line_width(1.8 if not is_upright else 1.4)
        cr.stroke()

        # Inner Card Margin (4px)
        ix, iy, iw, ih = x + 4, y + 4, w - 8, h - 8
        cr.save()
        draw_rounded_rect(cr, ix, iy, iw, ih, 7)
        cr.clip()

        # Draw Artwork Pixbuf - ALWAYS UPRIGHT (No 180 deg upside-down flip)
        img_path = card.get("image_path")
        if img_path and os.path.exists(img_path):
            cache_key = f"{img_path}_{int(iw)}_{int(ih)}"
            if cache_key not in self.pixbuf_cache:
                try:
                    pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, int(iw), int(ih), False)
                    self.pixbuf_cache[cache_key] = pix
                except Exception:
                    self.pixbuf_cache[cache_key] = None

            pix = self.pixbuf_cache.get(cache_key)
            if pix:
                cr.save()
                pw = pix.get_width()
                ph = pix.get_height()
                px = ix + (iw - pw) / 2
                py = iy + (ih - ph) / 2

                Gdk.cairo_set_source_pixbuf(cr, pix, px, py)
                draw_rounded_rect(cr, px, py, pw, ph, 6)
                cr.clip()
                cr.paint()
                cr.restore()
        else:
            cr.set_source_rgba(0.06, 0.04, 0.12, 1.0)
            cr.paint()

        # Holographic Foil Sheen for Major Arcana
        if card.get("is_major"):
            self._render_foil_sheen(cr, ix, iy, iw, ih, (self.anim_t * 0.45) % 1.0)

        # Orientation Indicator Badge inside card at bottom
        badge_h = 24
        badge_w = iw - 20
        badge_x = ix + 10
        badge_y = iy + ih - badge_h - 10
        draw_rounded_rect(cr, badge_x, badge_y, badge_w, badge_h, 6)
        if is_upright:
            cr.set_source_rgba(0.01, 0.18, 0.12, 0.88)
            cr.fill_preserve()
            cr.set_source_rgba(*C_GREEN, 0.80)
            badge_text = "🌟 UPRIGHT" if self.lang == "EN" else "🌟 TEGAK"
            text_color = C_GREEN
        else:
            cr.set_source_rgba(0.22, 0.08, 0.02, 0.90)
            cr.fill_preserve()
            cr.set_source_rgba(*C_AMBER, 0.85)
            badge_text = "🔄 REVERSED" if self.lang == "EN" else "🔄 TERBALIK"
            text_color = C_AMBER
        cr.set_line_width(1.0)
        cr.stroke()

        badge_layout = PangoCairo.create_layout(cr)
        badge_layout.set_font_description(Pango.FontDescription("JetBrains Mono Bold 7.0"))
        badge_layout.set_text(badge_text, -1)
        btw, bth = badge_layout.get_pixel_size()
        cr.set_source_rgba(*text_color, 0.95)
        cr.move_to(badge_x + (badge_w - btw) / 2, badge_y + (badge_h - bth) / 2)
        PangoCairo.show_layout(cr, badge_layout)

        cr.restore()

    def _render_foil_sheen(self, cr, x, y, w, h, progress):
        # Sweeping metallic diagonal gradient
        cr.save()
        draw_rounded_rect(cr, x, y, w, h, 10)
        cr.clip()

        shift = (progress * 2.0 - 0.5) * (w + h)
        pat = cairo.LinearGradient(x - w + shift, y - h + shift, x + w + shift, y + h + shift)
        pat.add_color_stop_rgba(0.0, 0.0, 1.0, 0.8, 0.0)
        pat.add_color_stop_rgba(0.35, 1.0, 0.8, 0.0, 0.25)
        pat.add_color_stop_rgba(0.50, 1.0, 1.0, 1.0, 0.55)
        pat.add_color_stop_rgba(0.65, 0.8, 0.3, 1.0, 0.25)
        pat.add_color_stop_rgba(1.0, 0.0, 0.95, 1.0, 0.0)

        cr.set_source(pat)
        cr.paint()
        cr.restore()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Flowork Sovereign Tarot Oracle")
    parser.add_argument("--name", default="", help="User's name")
    parser.add_argument("--dob", default="", help="User's date of birth (DD-MM-YYYY)")
    parser.add_argument("--focus", default="", help="Question or intention of reading")
    parser.add_argument("--spread", choices=["single", "three", "five"], default="three", help="Spread type")
    parser.add_argument("--auto-summon", action="store_true", help="Automatically trigger summon animation on launch")
    args = parser.parse_args()

    win = TarotOracleWindow(
        name=args.name,
        dob=args.dob,
        focus=args.focus,
        spread=args.spread,
        auto_summon=args.auto_summon
    )
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
