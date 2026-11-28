#!/usr/bin/env python3
"""
Flowork OS — Sovereign Headless 59s Suno Audio Speed-Up Engine (Node 03)
Compresses any audio track to <= 59 seconds using exact sample-rate pitch/tempo
scaling (aresample=44100,asetrate=44100*factor,aresample=44100) with metadata
stripping (-map_metadata -1) for manual Suno AI Cover upload.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Callable, Optional, Tuple

TARGET_MAX_SEC = 58.8
HARD_CAP_SEC = 59.0

SUPPORTED_AUDIO_EXTS = {
    ".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus",
    ".wma", ".aiff", ".aif", ".mp4", ".mkv", ".webm",
}


def resolve_music_dir() -> str:
    home = os.path.expanduser("~")
    fallback = os.path.join(home, "Music")
    if shutil.which("xdg-user-dir"):
        try:
            res = subprocess.run(
                ["xdg-user-dir", "MUSIC"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            candidate = (res.stdout or "").strip()
            if res.returncode == 0 and candidate and os.path.isabs(candidate):
                os.makedirs(candidate, exist_ok=True)
                return candidate
        except Exception:
            pass
    os.makedirs(fallback, exist_ok=True)
    return fallback


def _unique_output_path(target_dir: str, stem: str, ratio: float) -> str:
    tag = f"_{ratio:.2f}x" if ratio > 1.01 else ""
    base_name = f"{stem}_suno_59s{tag}.mp3"
    candidate = os.path.join(target_dir, base_name)
    if not os.path.exists(candidate):
        return candidate
    idx = 2
    while True:
        candidate = os.path.join(target_dir, f"{stem}_suno_59s{tag}_{idx}.mp3")
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def probe_audio(input_path: str) -> Tuple[float, int]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate:format=duration",
        "-of", "json",
        input_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {(res.stderr or '').strip()}")
    data = json.loads(res.stdout or "{}")
    dur_raw = (data.get("format") or {}).get("duration")
    if dur_raw is None:
        raise RuntimeError("Could not determine audio duration via ffprobe")
    orig_dur = float(dur_raw)
    if orig_dur <= 0.05:
        raise RuntimeError(f"Audio duration too short ({orig_dur:.3f}s)")

    orig_sr = 44100
    streams = data.get("streams") or []
    if streams and streams[0].get("sample_rate"):
        try:
            orig_sr = int(streams[0]["sample_rate"])
        except (TypeError, ValueError):
            orig_sr = 44100
    return orig_dur, orig_sr


def render_suno_59s(
    input_path: str,
    output_path: Optional[str] = None,
    target_sec: float = TARGET_MAX_SEC,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> dict:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input audio not found: {input_path}")

    def emit(p: float, stage: str):
        if on_progress:
            on_progress(max(0.0, min(1.0, p)), stage)

    emit(0.05, "PROBING")
    orig_dur, orig_sr = probe_audio(input_path)

    safe_target = min(max(5.0, float(target_sec)), HARD_CAP_SEC)
    if orig_dur > safe_target:
        factor = orig_dur / safe_target
        af_chain = f"aresample=44100,asetrate=44100*{factor:.6f},aresample=44100"
        expected_out_dur = safe_target
    else:
        factor = 1.0
        af_chain = "aresample=44100"
        expected_out_dur = orig_dur

    emit(0.15, f"SPEED {factor:.2f}x")

    tmp_fd, tmp_mp3 = tempfile.mkstemp(prefix="flowork_suno_59s_", suffix=".mp3", dir="/tmp")
    os.close(tmp_fd)

    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-i", input_path,
            "-vn",
            "-af", af_chain,
            "-t", "59",
            "-map_metadata", "-1",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-progress", "pipe:1",
            "-nostats",
            tmp_mp3,
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        out_time_re = re.compile(r"^out_time_us=(\d+)$")
        if proc.stdout:
            for raw_line in proc.stdout:
                line = raw_line.strip()
                m = out_time_re.match(line)
                if m and expected_out_dur > 0:
                    cur_sec = int(m.group(1)) / 1_000_000.0
                    frac = min(1.0, max(0.0, cur_sec / expected_out_dur))
                    emit(0.15 + frac * 0.75, f"SPEED {factor:.2f}x")

        stderr_text = proc.stderr.read() if proc.stderr else ""
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"ffmpeg failed (rc={rc}): {stderr_text.strip()}")

        emit(0.93, "VERIFYING")
        new_dur, _ = probe_audio(tmp_mp3)
        if new_dur > 59.05:
            raise RuntimeError(f"Output exceeded 59s ceiling ({new_dur:.2f}s)")

        exact_ratio = orig_dur / new_dur if new_dur > 0 else factor

        if output_path:
            final_path = os.path.abspath(output_path)
            target_dir = os.path.dirname(final_path)
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = resolve_music_dir()
            stem = os.path.splitext(os.path.basename(input_path))[0]
            final_path = _unique_output_path(target_dir, stem, exact_ratio)

        shutil.move(tmp_mp3, final_path)
        os.chmod(final_path, 0o644)

        emit(1.0, "DONE")
        return {
            "output_path": final_path,
            "music_dir": target_dir,
            "orig_dur": round(orig_dur, 3),
            "orig_sr": orig_sr,
            "new_dur": round(new_dur, 3),
            "ratio": round(exact_ratio, 2),
            "suno_hint": (
                f"Slow down tempo {exact_ratio:.2f}x to restore original pitch "
                f"and full {orig_dur:.1f}s duration"
            ),
        }
    finally:
        if os.path.exists(tmp_mp3):
            try:
                os.remove(tmp_mp3)
            except OSError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flowork OS Node 03 — 59s Suno Audio Speed-Up Engine"
    )
    parser.add_argument("input", help="Input audio file path")
    parser.add_argument("-o", "--output", help="Optional explicit output MP3 path")
    parser.add_argument(
        "--target",
        type=float,
        default=TARGET_MAX_SEC,
        help=f"Target max duration in seconds (default: {TARGET_MAX_SEC})",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    args = parser.parse_args()

    try:
        res = render_suno_59s(args.input, output_path=args.output, target_sec=args.target)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(
                f"[✓] Saved: {res['output_path']} "
                f"({res['orig_dur']}s -> {res['new_dur']}s, ratio {res['ratio']}x)"
            )
            print(f"[i] Suno Styles Hint: {res['suno_hint']}")
        return 0
    except Exception as exc:
        print(f"[✗] Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
