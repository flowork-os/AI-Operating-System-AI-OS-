#!/usr/bin/env python3
"""
01_research_songs.py
Search 70s-2000s Indonesian nostalgic hits on YouTube, strictly exclude Sony Music
labels, and cross-check against @JanganNontonDrachin to prevent duplicate covers.
"""
import argparse
import json
import os
import re
import subprocess
import sys

SONY_BLOCKLIST = [
    "sony music",
    "sony music entertainment",
    "sony music indonesia",
    "sme",
    "columbia records",
    "rca records",
    "epic records",
]

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERED_LIST_FILE = os.path.join(SKILL_DIR, "covered_songs.txt")


def load_drachin_catalog(refresh: bool = False) -> list[str]:
    existing = []
    if os.path.exists(COVERED_LIST_FILE):
        with open(COVERED_LIST_FILE, "r", encoding="utf-8") as f:
            existing = [line.strip() for line in f if line.strip()]

    if refresh:
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print",
            "%(title)s",
            "https://www.youtube.com/@JanganNontonDrachin/videos",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            seen = {t.lower() for t in existing}
            for line in res.stdout.splitlines():
                t = line.strip()
                if t and t.lower() not in seen:
                    existing.append(t)
                    seen.add(t.lower())
            with open(COVERED_LIST_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(existing) + "\n")

    return [t.lower() for t in existing]


def add_covered_song(title: str) -> None:
    title = title.strip()
    if not title:
        return
    existing = []
    if os.path.exists(COVERED_LIST_FILE):
        with open(COVERED_LIST_FILE, "r", encoding="utf-8") as f:
            existing = [line.strip() for line in f if line.strip()]
    if title.lower() not in {t.lower() for t in existing}:
        existing.append(title)
        with open(COVERED_LIST_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(existing) + "\n")
        print(f"[OK] Added to covered_songs.txt: {title}")
    else:
        print(f"[SKIP] Already in covered_songs.txt: {title}")


def is_sony_music(meta: dict) -> bool:
    haystack = " ".join(
        str(meta.get(k, "") or "")
        for k in ("uploader", "channel", "creator", "album", "description", "title")
    ).lower()
    return any(term in haystack for term in SONY_BLOCKLIST)


def is_duplicate(title: str, catalog: list[str]) -> bool:
    clean = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    tokens = [t for t in clean.split() if len(t) > 3 and t not in {"official", "video", "lyric", "lyrics", "audio", "music", "lagu", "cover"}]
    for cat in catalog:
        matches = sum(1 for t in tokens if t in cat)
        if matches >= 2:
            return True
    return False


def search_youtube(query: str, limit: int) -> list[dict]:
    cmd = [
        "yt-dlp",
        f"ytsearch{limit}:{query}",
        "--dump-json",
        "--no-playlist",
        "--skip-download",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    results = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return results


def main():
    parser = argparse.ArgumentParser(description="Research non-Sony Indonesian hits for Drachin OST covers.")
    parser.add_argument("--query", default="lagu indonesia hits 90an 2000an official audio", help="YouTube search query")
    parser.add_argument("--limit", type=int, default=12, help="Number of search results to inspect")
    parser.add_argument("--refresh-catalog", action="store_true", help="Refresh covered_songs.txt from @JanganNontonDrachin")
    parser.add_argument("--add-covered", default="", help="Append a newly covered song title to covered_songs.txt and exit")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.add_covered:
        add_covered_song(args.add_covered)
        return

    catalog = load_drachin_catalog(refresh=args.refresh_catalog)
    raw_items = search_youtube(args.query, args.limit)

    eligible = []
    rejected = []
    for item in raw_items:
        vid = item.get("id", "")
        title = item.get("title", "")
        dur = item.get("duration") or 0
        uploader = item.get("uploader") or item.get("channel") or "Unknown"
        url = item.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}"

        if is_sony_music(item):
            rejected.append({"title": title, "reason": "Sony Music label excluded"})
            continue
        if dur < 150 or dur > 360:
            rejected.append({"title": title, "reason": f"Duration {dur}s outside 150-360s ideal range"})
            continue
        if is_duplicate(title, catalog):
            rejected.append({"title": title, "reason": "Already covered on @JanganNontonDrachin"})
            continue

        eligible.append({
            "id": vid,
            "title": title,
            "duration_sec": dur,
            "uploader": uploader,
            "url": url,
        })

    if args.json:
        print(json.dumps({"eligible": eligible, "rejected": rejected}, indent=2, ensure_ascii=False))
    else:
        print(f"=== ELIGIBLE CANDIDATES ({len(eligible)}) ===")
        for idx, c in enumerate(eligible, 1):
            print(f"{idx}. [{c['duration_sec']}s] {c['title']} | Label/Channel: {c['uploader']} | {c['url']}")
        print(f"\n=== REJECTED ({len(rejected)}) ===")
        for r in rejected:
            print(f"- {r['title']} -> {r['reason']}")


if __name__ == "__main__":
    main()
