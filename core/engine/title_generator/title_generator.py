#!/usr/bin/env python3
"""
👑 FLOWORK OS — SOVEREIGN VIRAL TITLE GENERATOR (NODE 04)
Master Engine Khusus Kanal Drachin / Xianxia:
Menghasilkan judul video YouTube berdaya pikat tinggi (CTR Masif), kaya variasi sastra,
sinematik, dan psikologis, dengan ratusan kombinasi agar tidak pernah monoton.
"""

import os
import sys
import random
import re
import argparse
import json
from typing import List, Dict, Tuple, Optional

# ==============================================================================
# 1. EXPANSIVE BANK: AWALAN (PREFIXES / EMOTIONAL HOOKS)
# ==============================================================================

HOOKS_SHOCK = [
    "SYOK!", "GILA!", "DI LUAR NALAR!", "BUKAN HOAX!", "GAK MASUK AKAL!",
    "SUMPAH KAGET!", "NGERI BANGET!", "MERINDING DISKO!", "PARAH BANGET!",
    "ASLI BIKIN KAGET!", "GAK NYANGKA!", "SHOCKING!", "BENGONG!", "LANGSUNG TERDIAM!",
    "GEMPAR!", "SIAP-SIAP KAGET!", "JANTUNG MAU COPOT!", "TERLALU GILA!",
    "MATI KUTU!", "MERINDING SEKUJUR TUBUH!", "GAK BISA BERKATA-KATA!", "SPEECHLESS TOTAL!",
    "HANCUR PERTAHANAN!", "LANGSUNG SHOCK!", "BENGONG SEHARIAN!", "BERGETAR SELURUH BADAN!"
]

HOOKS_EMOTIONAL = [
    "MERINDING!", "AUTO NANGIS!", "BIKIN SESAK DI DADA!", "NYESEK PARAH!",
    "AWAS BANJIR AIR MATA!", "NANGIS KEJER!", "AIR MATA GAK BISA TAHAN!",
    "EMOSIONAL PARAH!", "HATI TERIRIS!", "PEDIH BANGET!", "TERLALU MENYAYAT HATI!",
    "LANGSUNG SESAK NAFAS!", "TIDAK KUAT DENGARNYA!", "MERINDING TOTAL!",
    "NANGIS DIPERJALANAN!", "PILU BANGET!", "BAPER MAKSIMAL!", "SUASANANYA TERLALU DALAM!",
    "SIAPKAN TISU!", "HANCUR BERKEPING-KEPING!", "SEDIH TAK BERUJUNG!", "PEDIH MENEMBUS TULANG!",
    "RASA SAKIT YANG PURA-PURA HILANG!", "AIR MATA DIAM-DIAM MENETES!", "SEAKAN DUNIA RUNTUH!"
]

HOOKS_DEBATE = [
    "KOK JAUH LEBIH MEWAH?!", "BANYAK YANG GAK TERIMA!", "JUJUR, LEBIH SAKIT VERSI INI!",
    "VERSI ASLINYA KALAH TELAK?!", "LEBIH ENAK DARI VERSI ASLI!", "VERSI ASLI LANGSUNG LUPA!",
    "DEBAT PANAS!", "NETIZEN TERPECAH DUA!", "JAUH LEBIH BERKELAS?!",
    "GAK BISA DIBANDINGIN LAGI!", "VERSI INI BENAR-BENAR JUARA!", "JAUH MENINGGALKAN ASLINYA!",
    "KOK BISA SEKEREN INI?!", "ASLINYA BAGUS TAPI INI GILA!", "TERLALU MEWAH UNTUK GRATISAN!",
    "GAK RELA TAPI INI FAKTA!", "MAAFKAN AKU TAPI VERSI INI MENANG!", "FANS ASLI PASTI KETAR-KETIR!",
    "BUKAN MEREMEHKAN ASLINYA, TAPI...", "KUALITASNYA DI LUAR BATAS!"
]

HOOKS_DOUYIN_CHINA = [
    "VIRAL DI DOUYIN CHINA!", "TRENDING DI WEIBO TIONGKOK!", "HEBOH DI CHINA!",
    "NETIZEN CHINA GEGER!", "DOUYIN TEMBUS JUTAAN VIEWS!", "DIKIRA LAGU ASLI CHINA!",
    "NETIZEN TIONGKOK TAKJUB!", "BOOMING DI DARATAN TIONGKOK!", "VIRAL SAMPAI KE BEIJING!",
    "ORANG CHINA KIRA INI OST RESMI!", "TEMBUS FYP DOUYIN!", "VIRAL SEANTERO TIONGKOK!",
    "GEGER DI DARATAN CHINA!", "WARGA TIONGKOK PENASARAN ASALNYA!", "JADI SOUND HITS DI DOUYIN!",
    "MASUK CHARTS MUSIK TIONGKOK!", "PENCARIAN NOMOR SATU DI WEIBO!"
]

HOOKS_REAKSI = [
    "PENYANYI ASLINYA PASTI KAGET!", "KALAU DENGAR PASTI MERINDING!",
    "PENCIPTA LAGUNYA PASTI BANGGA!", "KOMPOSERNYA PASTI GELENG KEPALA!",
    "ARTIS ASLI PASTI SPEECHLESS!", "SEMUA MUSISI ANGKAT TOPI!",
    "KALAU DIMAINKAN DI KONSER BAKAL PECAH!", "MAESTRO PUN PASTI TERKAGUM!",
    "SANG LEGENDA PASTI TERSENYUM BANGGA!", "PENIKMAT MUSIK KELAS BERAT PASTI SUKA!"
]

HOOKS_EKSKLUSIF = [
    "EKSKLUSIF:", "MAHAKARYA LANGKA:", "VERSI EMAS:", "EDISI SPESIAL:",
    "TRANSFORMASI MAUT:", "ARANSEMEN RAJALELA:", "VERSI SULTAN:", "MASTERPIECE:",
    "PRODUKSI TERBESAR:", "ARANSEMEN DINASTI:", "VERSI MAHKOTA:"
]

HOOKS_PENASARAN = [
    "JANGAN DENGAR SENDIRIAN!", "DENGARKAN DI MENIT KE 01:30!", "HANYA 1% YANG TAHU ASLINYA!",
    "TEBAK INI LAGU SIAPA?!", "KAMU PASTI GAK AKAN NYANGKA!", "RAHASIA DIBALIK LAGU INI!",
    "DARI PETIKAN PERTAMA SUDAH TAHU!", "AWAS KECANDUAN!", "DIPUTAR BERKALI-KALI GAK BOSEN!"
]

ALL_HOOKS_CATEGORIES = {
    "shock": HOOKS_SHOCK,
    "emotional": HOOKS_EMOTIONAL,
    "debate": HOOKS_DEBATE,
    "douyin": HOOKS_DOUYIN_CHINA,
    "reaction": HOOKS_REAKSI,
    "exclusive": HOOKS_EKSKLUSIF,
    "curiosity": HOOKS_PENASARAN
}

# ==============================================================================
# 2. EXPANSIVE BANK: AKHIRAN (SUFFIXES / TRANSFORMATION NARRATIVES)
# ==============================================================================

SUFFIXES_KOLOSAL = [
    "Disulap Jadi Soundtrack Kerajaan Kolosal Termahal!",
    "Berubah Jadi Mahakarya Kerajaan Dinasti Kuno yang Megah!",
    "Dari Pop Biasa Jadi Orkestra Kolosal yang Bikin Merinding!",
    "Aransemen Megah Kerajaan Tiongkok Paling Berbudget Triliunan!",
    "Disulap Jadi Musik Perang & Tahta Kaisar yang Menggetarkan Jiwa!",
    "Versi Kerajaan Kolosal Termahal yang Pernah Ada!",
    "Megah Bak Perjamuan Kaisar di Istana Terlarang!",
    "Dentuman Orkestra Kolosalnya Serasa Perang Perebutan Tahta!",
    "Berubah Menjadi Lagu Penobatan Kaisar Teragung!",
    "Nuansa Megah Kerajaannya Benar-Benar Bikin Merinding!",
    "Serasa Pasukan 10.000 Berkuda Menyambut Sang Raja!",
    "Iringan Terompet & Genderang Perang Kerajaan yang Bikin Gempar!",
    "Kemewahan Dinasti Tang dalam Setiap Ketukan Orkestra!",
    "Serasa Menatap Kemegahan Istana Terlarang di Bawah Guyuran Hujan!",
    "Aransemen Sultan yang Layak Masuk Film Box Office Kerajaan!"
]

SUFFIXES_XIANXIA_TRAGIS = [
    "Serasa OST Xianxia 3 Kehidupan Paling Menyayat Hati!",
    "Cocok Jadi Soundtrack Reinkarnasi Dewa & Dewi Tragis!",
    "Hancur Hati! Pas Banget Buat Scene Kematian Ratu di Medan Tempur!",
    "Nuansa Kutukan Abadi & Cinta Terlarang yang Bikin Nangis Kejer!",
    "Kisah Cinta 10.000 Tahun yang Berakhir Pedih di Ujung Pedang!",
    "Pas Buat Scene Pengorbanan Nyawa Demi Sang Kekasih!",
    "Serasa Terjebak di Alam Fana Menanti Reinkarnasi!",
    "Nyeseknya Nembus ke Tulang, Cocok Buat Ending Drama Tragis!",
    "Soundtrack Paling Cocok Buat Kisah Cinta Beda Kasta Dewa & Manusia!",
    "Bikin Sesak di Dada, Serasa Ditinggal Mati di Puncak Awan!",
    "Ketika Sang Kaisar Menangis Memeluk Jasad Sang Permaisuri...",
    "Kisah Tragis Cinta Abadi yang Terhalang Takdir Langit!",
    "Patah Hati Paling Sunyi di Tengah Hujan Salju Abadi!",
    "Pas Banget Buat Momen Perpisahan Terakhir di Jembatan Takdir!",
    "Serasa Jiwa Tertinggal di Lembah Bunga Persik Tanpa Akhir!"
]

SUFFIXES_INSTRUMEN = [
    "Tarikan Gesekan Erhu & Guqin-nya Bikin Merinding Parah!",
    "Petikan Guzheng Mautnya Sukses Bikin Air Mata Ngalir Deras!",
    "Tiupan Seruling Bambu Dizi-nya Terlalu Dalam Menusuk Hati!",
    "Tarikan Falsetto & Alat Musik Kuno Tiongkok yang Mematikan!",
    "Perpaduan Suara Erhu dan Orkestra Barat yang Terlalu Sempurna!",
    "Hawa Mistis dan Suara Seruling Kuno yang Menggetarkan Jiwa!",
    "Harmonisasi Petikan Kecapi Cina Kuno yang Bikin Terdiam!",
    "Gesekan Rebab Kuno Erhu-nya Mengiris Hati Sejak Detik Pertama!",
    "Suara Lonceng Kuno & Denting Pipa yang Bikin Merem Melek!",
    "Sentuhan Akustik Suling Bambu yang Mengingatkan Kampung Halaman Kuno!"
]

SUFFIXES_PERBANDINGAN = [
    "Ternyata Jauh Lebih Mewah Dari Versi Aslinya!",
    "Banyak yang Gak Percaya Ini Aslinya Lagu Lawas Indonesia!",
    "Dikira Soundtrack Asli Drachin Berbudget Ratusan Miliar!",
    "Gak Kalah Sama Soundtrack Drama Korea & Tiongkok Papan Atas!",
    "Buktikan Sendiri! Versi Ini Terlalu Berkelas Buat Dilewatkan!",
    "Bukan Kaleng-Kaleng! Kualitasnya Layak Masuk Bioskop Internasional!",
    "Sekali Dengar Langsung Lupa Sama Versi Pop Aslinya!",
    "Bahkan Netizen Asing Mengira Ini Lagu Rakyat Kuno Dinasti Tang!",
    "Level Musikalitasnya Jauh di Atas Standar Lagu Biasa!",
    "Aransemen yang Berani Mengubah Lagu Pop Menjadi Karya Monumental!"
]

SUFFIXES_PENASARAN = [
    "Tebak Ini Lagu Siapa? Tarikan Vokalnya Bikin Merinding!",
    "Ternyata Lagu Legendaris Indonesia Ini Disulap Jadi Semegah Ini!",
    "Dengarkan di Menit ke 01:45, Dijamin Bulu Kuduk Berdiri!",
    "Bikin Sesak di Dada Pas Bagian Reff-nya Masuk!",
    "Ending-nya Benar-Benar Bikin Hati Hancur Berkeping-keping!",
    "Bagian Reff Kedua Dijamin Bikin Napas Terhenti Sejenak!",
    "Jangan Nonton Sampai Habis Kalau Gak Kuat Tahan Tangis!"
]

ALL_SUFFIXES_CATEGORIES = {
    "kolosal": SUFFIXES_KOLOSAL,
    "xianxia": SUFFIXES_XIANXIA_TRAGIS,
    "instrument": SUFFIXES_INSTRUMEN,
    "comparison": SUFFIXES_PERBANDINGAN,
    "curiosity": SUFFIXES_PENASARAN
}

# ==============================================================================
# 3. BADGES & SUB-TITLES MANDARIN AUTHENTIC
# Memberi sentuhan estetika kanal profesional Tiongkok
# ==============================================================================

MANDARIN_BADGES = [
    "| 独家首播 (Eksklusif)",
    "| 影视原声 (OST Resmi)",
    "| 仙侠虐恋 (Xianxia Paling Pedih)",
    "| 古风巨制 (Produksi Megah Kuno)",
    "| 虐心之作 (Mahakarya Patah Hati)",
    "| 国风交响 (Symphony Budaya Kuno)",
    "| 泪崩预警 (Awas Air Mata)",
    "| 经典翻唱 (Cover Legendaris)",
    "| 震撼全网 (Mengguncang Netizen)",
    "| 宿命交织 (Ikatan Takdir Abadi)"
]

ROMAN_BADGES = [
    "(Versi OST Drachin Megah)",
    "(Versi Kerajaan Tiongkok)",
    "(Soundtrack Kolosal Paling Menyayat Hati)",
    "(Cover Mandarin Bikin Merinding)",
    "[Orkestra Kerajaan Termahal]",
    "(Bikin Sesak di Dada 💔)",
    "(Versi Paling Nyesek)",
    "[Mahakarya Dinasti Kuno]"
]

# ==============================================================================
# 4. ARTIST-AWARE METADATA ENGINE (DETEKSI PENYANYI KHUSUS)
# ==============================================================================

ARTIST_SIGNATURES = {
    "chrisye": {
        "hooks": [
            "ALMARHUM CHRISYE PASTI BANGGA!", "SANG MAESTRO TERSENYUM DI ATAS SANA!",
            "TARIKAN FALSETTO MAUT CHRISYE!"
        ],
        "suffixes": [
            "Menjadi Soundtrack Cinta Abadi yang Menembus Ribuan Tahun!",
            "Karya Emas Sang Legenda Indonesia Disulap Menjadi Mahakarya Dinasti Kuno!"
        ]
    },
    "nike ardilla": {
        "hooks": [
            "MENGENANG LADY ROCKER SEJATI!", "SUARA EMAS NIKE ARDILLA!",
            "FANS NIKE ARDILLA PASTI MENANGIS!"
        ],
        "suffixes": [
            "Versi Mandarin Bintang Kehidupan yang Bikin Merinding Sekujur Tubuh!",
            "Aransemen Megah Pengantar Ratu Rocker Menuju Alam Abadi!"
        ]
    },
    "sheila on 7": {
        "hooks": [
            "EROS & DUTA PASTI GELENG KEPALA!", "NOSTALGIA ERA 2000-AN PECAH!",
            "LIRIK PUITIS SHEILA ON 7!"
        ],
        "suffixes": [
            "Disulap Jadi Soundtrack Romansa Sekolah Dinasti Kuno Paling Manis!",
            "Melodi Patah Hati Sheila on 7 yang Jauh Lebih Megah Dari Aslinya!"
        ]
    },
    "peterpan": {
        "hooks": [
            "ARIEL PASTI KAGET DENGAR INI!", "MELODI LEGENDARIS PETERPAN!",
            "SEKALI DENGAR LANGSUNG MERINDING!"
        ],
        "suffixes": [
            "Lagu 'Yang Terdalam' Menjelma Jadi Ratapan Jiwa Kaisar Terbuang!",
            "Aransemen Megah Menggetarkan Jiwa Penggemar Musik Indonesia & China!"
        ]
    },
    "noah": {
        "hooks": [
            "ARIEL PASTI KAGET DENGAR INI!", "MELODI LEGENDARIS NOAH!",
            "SEKALI DENGAR LANGSUNG MERINDING!"
        ],
        "suffixes": [
            "Menjelma Jadi Ratapan Jiwa Kaisar Terbuang di Medan Tempur!",
            "Aransemen Megah Menggetarkan Jiwa Penggemar Musik Indonesia & China!"
        ]
    },
    "krisdayanti": {
        "hooks": [
            "DIVA INDONESIA DIAKUI TIONGKOK!", "SUARA EMAS KRISDAYANTI!",
            "MERINDING SEKUJUR BADAN!"
        ],
        "suffixes": [
            "Menjadi Lagu Penobatan Ratu Teragung dalam Sejarah Kerajaan!",
            "Vokal Berkelas Diva yang Cocok Banget Jadi OST Xianxia Triliunan!"
        ]
    },
    "nia daniaty": {
        "hooks": [
            "NIA DANIATY PASTI BENGONG!", "HITS 80-AN DISULAP JADI RATAPAN RATU!",
            "PATAH HATI PALING MAHAL!"
        ],
        "suffixes": [
            "Gelas Gelas Kaca Berubah Jadi Tangisan Ratu di Istana Terlarang!",
            "Melodi Nostalgia Indonesia yang Mengguncang Emosi Penonton Tiongkok!"
        ]
    },
    "titiek puspa": {
        "hooks": [
            "MAHAKARYA EYANG TITIEK PUSPA!", "LAGU INDONESIA PALING SAKRAL!",
            "DIKIRA LAGU RAKYAT KUNO DINASTI TANG!"
        ],
        "suffixes": [
            "Kupu Kupu Malam Berubah Jadi Soundtrack Pengorbanan Jiwa Paling Tragis!",
            "Kualitas Musikalitas Tingkat Tinggi yang Melintasi Benua & Zaman!"
        ]
    }
}

# ==============================================================================
# 5. MULTI-PERSPECTIVE NARRATIVE TEMPLATES
# Format struktur judul yang mengalir alami dari berbagai sudut pandang pembuat konten
# ==============================================================================

NARRATIVE_TEMPLATES = [
    # 1. First-Person Confession / Curhat Emosional (Sangat Tinggi CTR)
    "Jujur, Pas Denger '{clean_title}' Versi Ini Air Mata Gak Bisa Ditahan Lagi...",
    "Awalnya Iseng Dengar, Tapi Pas Bagian Reff '{clean_title}' Langsung Merinding Sekujur Tubuh!",
    "Gue Kira Lagu Daerah Kuno Tiongkok, Ternyata Lagu '{clean_title}' yang Disulap Semegah Ini!",
    "Baru Tahu Lagu '{clean_title}' Kalau Diubah Jadi Versi Kerajaan Bisa Bikin Hati Sehancur Ini!",
    
    # 2. Cinematic & Visual Scene Hook
    "Serasa Melihat Sang Kaisar Menangis di Bawah Salju! Lagu '{clean_title}' Versi Paling Menyayat Hati",
    "Cocok Banget Buat Scene Perpisahan Terakhir di Medan Perang! '{clean_title}' Versi Orkestra Kolosal",
    "Visualisasinya Serasa Perang 1000 Prajurit Memperebutkan Tahta! '{clean_title}' Megah Parah!",
    "Bikin Sesak di Dada Pas Adegan Ratu Rela Berkorban Nyawa! Lagu '{clean_title}' Versi Drachin Tragis",

    # 3. Controversy & Netizen Battle
    "BANYAK YANG HUJAT TAPI FAKTA! Lagu '{clean_title}' Versi Ini Jauh Lebih Nyesek Dari Aslinya!",
    "Gak Rela Versi Aslinya Kalah! Tapi '{clean_title}' Versi Mandarin Ini Bikin Speechless!",
    "Bikin Geger Fans Asli! Lagu '{clean_title}' Dirombak Total Jadi Nuansa Kutukan Abadi Xianxia!",
    "Debat Panas di Komentar! Katanya Versi Mandarin Lagu '{clean_title}' Ini Terlalu Berkelas?",

    # 4. Mystery & Discovery
    "Jangan Kaget Pas Menit 02:15! Kamu Pasti Sadar Ini Sebenarnya Lagu '{clean_title}'!",
    "Hanya yang Mengerti Musik yang Nalar! Melodi Mistis Ini Ternyata Lagu '{clean_title}'!",
    "Orang Indonesia Pasti Tahu Lagu Ini! Pas Dibuat Versi Kerajaan Malah Bikin Merinding Parah!",

    # 5. Douyin & Global Phenomenon
    "Trending di Daratan Tiongkok! Lagu '{clean_title}' Versi Mandarin Tembus Jutaan Views di Douyin!",
    "Netizen China Bingung Cari Asal Lagunya! Ternyata '{clean_title}' Asli Indonesia Disulap Semegah Ini!",
    "Dikira Soundtrack Resmi Xianxia Berbudget Triliunan! Lagu Lawas '{clean_title}' Guncang Weibo!",

    # 6. Standard Punchy 3-Tier (Hook + Clean + Suffix)
    "{hook} {clean_title} {suffix}",
    "{hook} '{clean_title}' {suffix}",
    "{hook} Lagu \"{clean_title}\" {suffix}",
    "{hook} {clean_title} | {suffix}",
    "{hook} - {clean_title} ({suffix})",
    "{clean_title} {suffix} - {hook}",
    "{hook} Gak Ada Lawan! {clean_title} {suffix}"
]


def clean_song_name(raw_name: str) -> str:
    base = os.path.basename(raw_name)
    base = os.path.splitext(base)[0]

    # Hilangkan pola prefix angka
    base = re.sub(r'^\d+[\s_\-\.]+', '', base)

    # Hilangkan suffix teknis
    for junk in [
        "_original", "_vocals", "_instrumental", "_59s", "_cover",
        "_lyrics", "_master", "_cleaned", "- vocals", "(vocals)",
        "_cut", "_norm", "_vocal"
    ]:
        base = re.sub(re.escape(junk), '', base, flags=re.IGNORECASE)

    # Ubah underscore jadi spasi
    base = base.replace('_', ' ').strip()
    # Bersihkan spasi ganda
    base = re.sub(r'\s+', ' ', base)
    return base


def detect_artist_in_title(song_title: str) -> Optional[str]:
    low = song_title.lower()
    for artist_key in ARTIST_SIGNATURES:
        if artist_key in low:
            return artist_key
    return None


def get_random_hook(category: Optional[str] = None) -> str:
    if category and category in ALL_HOOKS_CATEGORIES:
        return random.choice(ALL_HOOKS_CATEGORIES[category])
    all_h = [h for cat in ALL_HOOKS_CATEGORIES.values() for h in cat]
    return random.choice(all_h)


def get_random_suffix(category: Optional[str] = None) -> str:
    if category and category in ALL_SUFFIXES_CATEGORIES:
        return random.choice(ALL_SUFFIXES_CATEGORIES[category])
    all_s = [s for cat in ALL_SUFFIXES_CATEGORIES.values() for s in cat]
    return random.choice(all_s)


def generate_single_title(
    song_title: str,
    mood: Optional[str] = None,
    with_badge: bool = True
) -> Dict[str, str]:
    clean = clean_song_name(song_title)
    artist_key = detect_artist_in_title(clean)

    h_cat = "viral"
    s_cat = "kolosal"

    # 1. Cek apakah ada signature khusus artis
    if artist_key and random.random() < 0.40 and not mood:
        data = ARTIST_SIGNATURES[artist_key]
        hook = random.choice(data["hooks"])
        suffix = random.choice(data["suffixes"])
        title_str = f"{hook} {clean} {suffix}"
        vibe_str = f"ARTIS [{artist_key.upper()}] + KOLOSAL"
        h_cat = "artist"
        s_cat = "kolosal"
    else:
        # Tentukan kategori hook & suffix berdasarkan mood jika dispesifikasikan
        if mood:
            m = mood.lower()
            if m in ALL_HOOKS_CATEGORIES:
                h_cat = m
                s_cat = random.choice(list(ALL_SUFFIXES_CATEGORIES.keys()))
            elif m in ALL_SUFFIXES_CATEGORIES:
                h_cat = random.choice(list(ALL_HOOKS_CATEGORIES.keys()))
                s_cat = m
            else:
                h_cat = random.choice(list(ALL_HOOKS_CATEGORIES.keys()))
                s_cat = random.choice(list(ALL_SUFFIXES_CATEGORIES.keys()))
        else:
            h_cat = random.choice(list(ALL_HOOKS_CATEGORIES.keys()))
            s_cat = random.choice(list(ALL_SUFFIXES_CATEGORIES.keys()))

        # 40% kemungkinan memakai narrative storytelling jika mood tidak dikunci
        if not mood and random.random() < 0.40:
            narrative_choices = NARRATIVE_TEMPLATES[:17]
            tmpl = random.choice(narrative_choices)
            title_str = tmpl.format(clean_title=clean)
            vibe_str = "CINEMATIC STORYTELLING"
        else:
            hook = get_random_hook(h_cat)
            suffix = get_random_suffix(s_cat)
            standard_choices = NARRATIVE_TEMPLATES[17:]
            tmpl = random.choice(standard_choices)
            title_str = tmpl.format(hook=hook, clean_title=clean, suffix=suffix)
            vibe_str = f"{h_cat.upper()} + {s_cat.upper()}"

    # 3. Tambahkan badge jika diaktifkan (60% kesempatan agar tidak berjejalan)
    if with_badge and random.random() < 0.60:
        badge = random.choice(MANDARIN_BADGES if random.random() < 0.65 else ROMAN_BADGES)
        title_str = f"{title_str} {badge}".strip()

    return {
        "title": title_str,
        "vibe": vibe_str,
        "hook_category": h_cat,
        "suffix_category": s_cat
    }


def generate_title_bundle(
    song_title: str,
    count: int = 10,
    mood: Optional[str] = None,
    with_badge: bool = True
) -> List[Dict[str, str]]:
    clean = clean_song_name(song_title)
    results = []
    used_titles = set()

    for i in range(count):
        # Generate kandidat unik
        candidate = None
        for _ in range(20):
            res = generate_single_title(clean, mood=mood, with_badge=with_badge)
            t_text = res["title"]
            if t_text not in used_titles:
                used_titles.add(t_text)
                candidate = res
                break

        if not candidate:
            candidate = generate_single_title(clean, mood=mood, with_badge=with_badge)

        results.append({
            "index": i + 1,
            "title": candidate["title"],
            "vibe": candidate["vibe"],
            "hook_category": candidate.get("hook_category", "viral"),
            "suffix_category": candidate.get("suffix_category", "drachin")
        })

    return results


def export_bundle_to_file(
    song_title: str,
    titles: List[Dict[str, str]],
    target_path: Optional[str] = None
) -> str:
    clean = clean_song_name(song_title)
    if not target_path:
        target_path = f"{clean.replace(' ', '_')}_viral_titles.txt"

    lines = [
        "=" * 68,
        "👑 FLOWORK OS — VIRAL DRACHIN TITLE GENERATOR (NODE 04 MASTER)",
        f"Lagu Target : {clean}",
        f"Total Opsi  : {len(titles)} Variasi Judul Anti-Monoton & Bernilai CTR Tinggi",
        "=" * 68,
        ""
    ]

    for item in titles:
        lines.append(f"[{item['index']:02d}] {item['title']}")
        lines.append(f"     └─ Vibe Karakter: {item['vibe']}")
        lines.append("")

    content = "\n".join(lines)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    return target_path


def main():
    parser = argparse.ArgumentParser(description="Flowork OS Sovereign Viral Title Generator (Node 04)")
    parser.add_argument("title", nargs="?", help="Judul lagu / nama artis atau path audio file")
    parser.add_argument("-n", "--count", type=int, default=10, help="Jumlah variasi judul (default: 10)")
    parser.add_argument("-m", "--mood", help="Filter mood/kategori hook (shock, emotional, debate, douyin, reaction)")
    parser.add_argument("--no-badge", action="store_true", help="Jangan sertakan badge Mandarin/eksklusif")
    parser.add_argument("-o", "--output", help="Path file text tujuan simpan")
    parser.add_argument("--json", action="store_true", help="Output dalam format JSON")
    args = parser.parse_args()

    if not args.title:
        parser.print_help()
        sys.exit(1)

    titles = generate_title_bundle(
        args.title,
        count=args.count,
        mood=args.mood,
        with_badge=not args.no_badge
    )

    if args.json:
        print(json.dumps(titles, indent=2, ensure_ascii=False))
        return

    saved_file = export_bundle_to_file(args.title, titles, args.output)

    print("\n" + "=" * 68)
    print(f"🔥 HASIL REKOMENDASI JUDUL VIRAL (Target: {clean_song_name(args.title)})")
    print("=" * 68)
    for item in titles:
        print(f"\n{item['index']:2d}. {item['title']}")
        print(f"    [Vibe: {item['vibe']}]")
    print("\n" + "=" * 68)
    print(f"💾 Disimpan rapi di: {saved_file}\n")


if __name__ == "__main__":
    main()
