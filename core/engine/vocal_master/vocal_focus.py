#!/usr/bin/env python3
"""
Flowork OS — Sovereign Headless Vocal Focus Mastering Engine
Replaces Kamidi GUI with a zero-bloat core engine implementing the exact
Kamidi 'Vocal Focus' preset + YouTube EBU R128 (-14 LUFS / -1.3 dBTP) mastering.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Callable, Optional

SUPPORTED_AUDIO_EXTS = {
    ".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".aiff", ".aif", ".wma"
}

# Exact DSP chain translated from Kamidi 'vocal' (Vocal Focus) preset:
# - Noise Reduction: nrThresh=-58 dB, nrAmount=0.4 -> afftdn=nf=-58:nr=8:tn=1
# - HPF: 80 Hz -> highpass=f=80:poles=2
# - EQ: low -1.0dB @ 250Hz, mid +4.0dB @ 2500Hz (Q=1.2), high +2.0dB @ 8000Hz
# - Mud control: 200Hz (-1.2dB), 500Hz (-0.8dB)
# - De-Esser: ~7kHz -> deesser=i=0.35:m=0.5:f=0.55:s=o
# - Compressor: thresh=-14dB, ratio=3.0, att=10ms, rel=120ms, makeup=+3dB, knee=6
# - Limiter: ceiling=-1.3dBTP, rel=250ms -> alimiter=limit=-1.3dB:attack=5:release=250:level=disabled
VOCAL_FOCUS_DSP_CHAIN = (
    "afftdn=nf=-58:nr=8:tn=1,"
    "highpass=f=80:poles=2,"
    "lowshelf=f=250:g=-1.0:t=q:w=0.707,"
    "equalizer=f=2500:t=q:w=1.2:g=4.0,"
    "highshelf=f=8000:g=2.0:t=q:w=0.707,"
    "equalizer=f=200:t=q:w=1.5:g=-1.2,"
    "equalizer=f=500:t=q:w=1.2:g=-0.8,"
    "deesser=i=0.35:m=0.5:f=0.55:s=o,"
    "acompressor=threshold=-14dB:ratio=3:attack=10:release=120:makeup=3dB:knee=6,"
    "alimiter=limit=-1.3dB:attack=5:release=250:level=disabled"
)


def build_ai_fingerprint_scrub_chain(sample_rate: int = 48000) -> str:
    """
    Sovereign AI Fingerprint & Watermark Scrubber:
    Fuses Audacity ai-sanitizer.ny DSP with neural watermark phase decorrelation:
    1. Steep brickwall lowpass (18.5 kHz, 4-pole cascade) to wipe ultrasonic carrier beacons.
    2. Multi-band all-pass phase decoherence (1.2 kHz, 4.8 kHz, 12.0 kHz, 15.5 kHz, 18.5 kHz)
       to break sample-locked and neural watermarks with 0 dB magnitude change.
    3. Imperceptible micro-resampling drift (+0.037%, <0.65 cents) via 64-bit SoXR (precision=28)
       and triangular TPDF dither to desynchronize frame-aligned watermark decoders.
    4. Analog tanh soft-clipping (threshold=0.98, oversample=2) for subtle harmonic warmth.
    """
    drifted_rate = int(round(sample_rate * 1.00037))
    return (
        f"lowpass=f=18500:poles=2,"
        f"lowpass=f=18500:poles=2,"
        f"allpass=f=1200:t=q:w=0.707,"
        f"allpass=f=4800:t=q:w=0.707,"
        f"allpass=f=12000:t=q:w=0.9,"
        f"allpass=f=15500:t=q:w=0.7,"
        f"allpass=f=18500:t=q:w=0.5,"
        f"aresample={sample_rate}:resampler=soxr:precision=28,"
        f"asetrate={drifted_rate},"
        f"aresample={sample_rate}:resampler=soxr:precision=28:dither_method=triangular,"
        f"asoftclip=type=tanh:threshold=0.98:oversample=2"
    )


def get_music_dir() -> str:
    """
    Dynamically resolve the active user's Music directory without ever
    hardcoding any username. Portable across any Linux user/PC.
    """
    home = os.path.expanduser("~")

    # 1. Parse ~/.config/user-dirs.dirs (standard XDG config)
    user_dirs_file = os.path.join(home, ".config", "user-dirs.dirs")
    if os.path.isfile(user_dirs_file):
        try:
            with open(user_dirs_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("XDG_MUSIC_DIR="):
                        raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                        raw = raw.replace("$HOME", home).replace("${HOME}", home)
                        expanded = os.path.expanduser(os.path.expandvars(raw))
                        if expanded and os.path.isabs(expanded):
                            os.makedirs(expanded, exist_ok=True)
                            return expanded
        except Exception:
            pass

    # 2. Try xdg-user-dir MUSIC if installed
    xdg_bin = shutil.which("xdg-user-dir")
    if xdg_bin:
        try:
            res = subprocess.run(
                [xdg_bin, "MUSIC"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            candidate = (res.stdout or "").strip()
            if res.returncode == 0 and candidate and os.path.isabs(candidate):
                os.makedirs(candidate, exist_ok=True)
                return candidate
        except Exception:
            pass

    # 3. Locale-aware fallback inside active user's $HOME
    music_en = os.path.join(home, "Music")
    music_id = os.path.join(home, "Musik")
    if os.path.isdir(music_id) and not os.path.isdir(music_en):
        return music_id
    os.makedirs(music_en, exist_ok=True)
    return music_en


def open_music_dir(music_dir: Optional[str] = None) -> None:
    """Open the Music directory detached in the user's file manager."""
    target = music_dir or get_music_dir()
    os.makedirs(target, exist_ok=True)
    opener = shutil.which("xdg-open") or shutil.which("nemo") or shutil.which("thunar")
    if not opener:
        return
    subprocess.Popen(
        [opener, target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


def build_unique_output_path(input_path: str, output_dir: Optional[str] = None) -> str:
    """Generate a non-clobbering output WAV path inside the Music directory."""
    target_dir = output_dir or get_music_dir()
    os.makedirs(target_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(input_path))[0]
    base_name = f"{stem}_vocal_master.wav"
    candidate = os.path.join(target_dir, base_name)
    if not os.path.exists(candidate):
        return candidate
    idx = 2
    while True:
        candidate = os.path.join(target_dir, f"{stem}_vocal_master_{idx}.wav")
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def probe_duration_seconds(input_path: str) -> float:
    ffprobe = shutil.which("ffprobe") or "/usr/bin/ffprobe"
    res = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return max(0.1, float((res.stdout or "0").strip()))
    except ValueError:
        return 1.0


def _run_ffmpeg_with_progress(
    cmd: list,
    duration_s: float,
    p_start: float,
    p_end: float,
    stage: str,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> tuple[int, str]:
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    if on_progress:
        on_progress(p_start, stage)

    if proc.stdout:
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if line.startswith("out_time_us="):
                try:
                    us = int(line.split("=", 1)[1])
                    frac = min(1.0, max(0.0, (us / 1_000_000.0) / max(0.1, duration_s)))
                    if on_progress:
                        on_progress(p_start + (p_end - p_start) * frac, stage)
                except ValueError:
                    pass
            elif line == "progress=end" and on_progress:
                on_progress(p_end, stage)

    stderr_text = proc.stderr.read() if proc.stderr else ""
    rc = proc.wait()
    return rc, stderr_text


def master_vocal_focus(
    input_path: str,
    output_path: Optional[str] = None,
    target_lufs: float = -14.0,
    true_peak_db: float = -1.3,
    lra: float = 7.0,
    sample_rate: int = 48000,
    strip_ai_fingerprint: bool = True,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> dict:
    """
    Master an audio file using the Kamidi Vocal Focus DSP chain + post-mix
    AI fingerprint/watermark scrubber + 2-pass YouTube EBU R128 loudness
    normalization, outputting metadata-free 24-bit WAV.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTS:
        raise ValueError(f"Unsupported audio format '{ext}'. Supported: {sorted(SUPPORTED_AUDIO_EXTS)}")

    ffmpeg = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
    out_path = output_path or build_unique_output_path(input_path)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    duration_s = probe_duration_seconds(input_path)
    if on_progress:
        on_progress(0.05, "ANALYZING")

    # Build post-mix DSP chain (Vocal Focus + optional AI Fingerprint Scrubber)
    dsp_chain = VOCAL_FOCUS_DSP_CHAIN
    if strip_ai_fingerprint:
        dsp_chain = f"{dsp_chain},{build_ai_fingerprint_scrub_chain(sample_rate)}"

    # Pass 1: Apply Vocal Focus + AI Scrub DSP + measure EBU R128 loudness stats
    pass1_filter = (
        f"{dsp_chain},"
        f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA={lra}:print_format=json"
    )
    pass1_cmd = [
        ffmpeg, "-y", "-hide_banner", "-nostats",
        "-progress", "pipe:1",
        "-i", input_path,
        "-vn",
        "-af", pass1_filter,
        "-f", "null", "-",
    ]
    rc1, stderr1 = _run_ffmpeg_with_progress(
        pass1_cmd, duration_s, 0.08, 0.48, "VOCAL FOCUS", on_progress
    )
    if rc1 != 0:
        raise RuntimeError(f"Vocal Focus pass 1 failed: {stderr1.strip()[-400:]}")

    match = re.search(r"\{[\s\S]*?\"input_i\"[\s\S]*?\}", stderr1)
    if not match:
        raise RuntimeError("Failed to parse EBU R128 loudness telemetry from FFmpeg")
    stats = json.loads(match.group(0))

    # Pass 2: Linear loudnorm + metadata-free 24-bit WAV export for YouTube
    pass2_filter = (
        f"{dsp_chain},"
        f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA={lra}:"
        f"measured_I={stats['input_i']}:"
        f"measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:"
        f"measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:"
        f"linear=true:print_format=summary"
    )
    pass2_cmd = [
        ffmpeg, "-y", "-hide_banner", "-nostats",
        "-progress", "pipe:1",
        "-i", input_path,
        "-vn",
        "-af", pass2_filter,
        "-map_metadata", "-1",
        "-map_chapters", "-1",
        "-fflags", "+bitexact",
        "-flags:a", "+bitexact",
        "-ar", str(sample_rate),
        "-c:a", "pcm_s24le",
        out_path,
    ]
    rc2, stderr2 = _run_ffmpeg_with_progress(
        pass2_cmd, duration_s, 0.50, 0.98, "YOUTUBE MASTER", on_progress
    )
    if rc2 != 0 or not os.path.isfile(out_path):
        raise RuntimeError(f"Vocal Focus pass 2 failed: {stderr2.strip()[-400:]}")

    if on_progress:
        on_progress(1.0, "DONE")

    return {
        "status": "ok",
        "preset": "vocal_focus",
        "input": os.path.abspath(input_path),
        "output": os.path.abspath(out_path),
        "music_dir": os.path.dirname(os.path.abspath(out_path)),
        "target_lufs": target_lufs,
        "true_peak_db": true_peak_db,
        "ai_fingerprint_scrubbed": strip_ai_fingerprint,
        "duration_s": round(duration_s, 3),
        "bytes": os.path.getsize(out_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flowork OS Headless Vocal Focus Mastering Engine"
    )
    parser.add_argument("input", help="Input audio file (.wav, .mp3, .flac, etc.)")
    parser.add_argument("-o", "--output", help="Optional explicit output WAV path")
    parser.add_argument("--output-dir", help="Optional output directory (defaults to user Music dir)")
    parser.add_argument("--lufs", type=float, default=-14.0, help="Target LUFS (default: -14.0)")
    parser.add_argument("--tp", type=float, default=-1.3, help="True peak ceiling dBTP (default: -1.3)")
    parser.add_argument("--no-fingerprint-scrub", action="store_true", help="Disable post-mix AI fingerprint/watermark scrubbing")
    parser.add_argument("--open-folder", action="store_true", help="Open Music folder when finished")
    parser.add_argument("--json-progress", action="store_true", help="Emit JSON progress lines")
    args = parser.parse_args()

    out_path = args.output
    if not out_path and args.output_dir:
        out_path = build_unique_output_path(args.input, args.output_dir)

    def _emit(p: float, stage: str) -> None:
        if args.json_progress:
            print(json.dumps({"progress": round(p, 4), "stage": stage}), flush=True)

    try:
        result = master_vocal_focus(
            args.input,
            output_path=out_path,
            target_lufs=args.lufs,
            true_peak_db=args.tp,
            strip_ai_fingerprint=not args.no_fingerprint_scrub,
            on_progress=_emit,
        )
        if args.open_folder:
            open_music_dir(result["music_dir"])
        print(json.dumps(result), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
