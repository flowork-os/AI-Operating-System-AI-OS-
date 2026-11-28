#!/usr/bin/env python3
"""
04_suno_stage_browser.py
Ensures Flowork Live Stage isolated browser (:99, CDP 9299) is running with
persistent profile ($HOME/.config/flowork-stage-chrome) and opens Suno Create.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request


CDP_URL = "http://127.0.0.1:9299"
PROFILE_DIR = os.path.expanduser("~/.config/flowork-stage-chrome")


def cdp_alive() -> bool:
    try:
        with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_stage_running() -> None:
    if cdp_alive():
        print(f"[OK] flowork-stage CDP already active at {CDP_URL}")
        print(f"[OK] Persistent profile: {PROFILE_DIR}")
        return

    print("[INFO] Starting flowork-stage isolated browser (:99, CDP 9299)...")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    env = os.environ.copy()
    env["FLOWORK_STAGE_PROFILE"] = PROFILE_DIR
    subprocess.run(["flowork-stage", "start", "--with-browser"], env=env, check=True)

    for _ in range(20):
        if cdp_alive():
            print(f"[OK] flowork-stage CDP ready at {CDP_URL}")
            print(f"[OK] Persistent profile: {PROFILE_DIR}")
            return
        time.sleep(0.5)

    print("[ERROR] flowork-stage CDP did not respond on port 9299", file=sys.stderr)
    sys.exit(1)


def open_url_via_cdp(target_url: str) -> None:
    with urllib.request.urlopen(f"{CDP_URL}/json/list", timeout=3) as resp:
        pages = json.loads(resp.read().decode("utf-8"))

    for page in pages:
        if page.get("type") == "page" and "suno.com" in page.get("url", ""):
            print(f"[OK] Suno tab already open: {page.get('url')}")
            return

    req = urllib.request.Request(
        f"{CDP_URL}/json/new?{target_url}",
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        info = json.loads(resp.read().decode("utf-8"))
        print(f"[OK] Opened {target_url} in isolated stage tab: {info.get('id')}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch/verify Flowork Live Stage isolated browser for Suno v6."
    )
    parser.add_argument(
        "--url",
        default="https://suno.com/create",
        help="Target Suno URL to open (default: https://suno.com/create)",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Only check if flowork-stage CDP is alive without launching.",
    )
    args = parser.parse_args()

    if args.status_only:
        if cdp_alive():
            print(f"[OK] flowork-stage CDP active at {CDP_URL} (profile: {PROFILE_DIR})")
            sys.exit(0)
        print("[WARN] flowork-stage CDP is not running.")
        sys.exit(1)

    ensure_stage_running()
    open_url_via_cdp(args.url)
    print("[NEXT] Connect agent_browser to http://127.0.0.1:9299 and run snapshot.")


if __name__ == "__main__":
    main()
