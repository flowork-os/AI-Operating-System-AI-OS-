#!/usr/bin/env python3
"""
Flowork OS — Sovereign Lightweight Vocal & Music Stem Separator (Node 02)
Modeled after Audacity's "Vocal Reduction and Isolation" spectral center-channel
DSP algorithm using pure NumPy + SciPy + FFmpeg (zero PyTorch/CUDA bloat).
Runs blazingly fast on any CPU including Intel Core i3.
Outputs <stem>_vocal.wav and <stem>_music.wav at original speed/pitch into
the active user's dynamic Music directory.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Callable, Optional

import numpy as np
from scipy.io import wavfile
from scipy.signal import istft, stft

sys.path.insert(0, "/opt/floworkos/engine/vocal_master")
from vocal_focus import (  # noqa: E402
    SUPPORTED_AUDIO_EXTS,
    get_music_dir,
    open_music_dir,
)


def build_unique_stem_paths(input_path: str, output_dir: Optional[str] = None) -> tuple[str, str]:
    """Generate non-clobbering <stem>_vocal.wav and <stem>_music.wav paths in Music dir."""
    target_dir = output_dir or get_music_dir()
    os.makedirs(target_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(input_path))[0]

    vocal_path = os.path.join(target_dir, f"{stem}_vocal.wav")
    music_path = os.path.join(target_dir, f"{stem}_music.wav")
    if not os.path.exists(vocal_path) and not os.path.exists(music_path):
        return vocal_path, music_path

    idx = 2
    while True:
        vocal_path = os.path.join(target_dir, f"{stem}_vocal_{idx}.wav")
        music_path = os.path.join(target_dir, f"{stem}_music_{idx}.wav")
        if not os.path.exists(vocal_path) and not os.path.exists(music_path):
            return vocal_path, music_path
        idx += 1


def _decode_to_stereo_f32(input_path: str, wav_path: str, sample_rate: int = 44100) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-v", "error",
        "-i", input_path,
        "-vn",
        "-ac", "2",
        "-ar", str(sample_rate),
        "-c:a", "pcm_f32le",
        wav_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg decode failed: {res.stderr.strip()}")


def _encode_24bit_wav(f32_wav_path: str, out_wav_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-v", "error",
        "-i", f32_wav_path,
        "-c:a", "pcm_s24le",
        "-map_metadata", "-1",
        out_wav_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed: {res.stderr.strip()}")


def _vocal_band_weights(freqs: np.ndarray, low_cut: float = 120.0, high_cut: float = 8500.0) -> np.ndarray:
    """
    Smooth Audacity-style vocal frequency band mask:
    - Keeps sub-bass/kick (< ~120 Hz) in the Music stem
    - Keeps high percussion/air (> ~8.5 kHz) in the Music stem
    """
    w = np.ones_like(freqs, dtype=np.float32)

    # Low-cut cosine transition: 80 Hz -> 160 Hz
    low_lo = max(20.0, low_cut * 0.65)
    low_hi = low_cut * 1.35
    w[freqs <= low_lo] = 0.0
    low_mask = (freqs > low_lo) & (freqs < low_hi)
    if np.any(low_mask):
        t = (freqs[low_mask] - low_lo) / (low_hi - low_lo)
        w[low_mask] = 0.5 * (1.0 - np.cos(np.pi * t))

    # High-cut cosine transition: 7200 Hz -> 10200 Hz
    hi_lo = high_cut * 0.85
    hi_hi = high_cut * 1.20
    w[freqs >= hi_hi] = 0.0
    hi_mask = (freqs > hi_lo) & (freqs < hi_hi)
    if np.any(hi_mask):
        t = (freqs[hi_mask] - hi_lo) / (hi_hi - hi_lo)
        w[hi_mask] = 0.5 * (1.0 + np.cos(np.pi * t))

    return w


def separate_vocal_and_music(
    input_path: str,
    output_dir: Optional[str] = None,
    strength: float = 1.15,
    low_cut: float = 120.0,
    high_cut: float = 8500.0,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> dict:
    """
    Separate input audio into clean Vocal and Music WAV files at original speed
    using Audacity-style spectral center-channel reduction & isolation.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTS:
        raise ValueError(f"Unsupported audio format '{ext}'. Supported: {sorted(SUPPORTED_AUDIO_EXTS)}")

    target_dir = output_dir or get_music_dir()
    os.makedirs(target_dir, exist_ok=True)

    tmp_dir = tempfile.mkdtemp(prefix="flowork_stem_split_")
    try:
        if on_progress:
            on_progress(0.10, "DECODING")

        decoded_wav = os.path.join(tmp_dir, "decoded.wav")
        _decode_to_stereo_f32(input_path, decoded_wav, sample_rate=44100)

        sr, data = wavfile.read(decoded_wav)
        if data.ndim == 1:
            data = np.stack([data, data], axis=1)
        data = data.astype(np.float32, copy=False)
        n_samples = data.shape[0]
        left = data[:, 0]
        right = data[:, 1]

        if on_progress:
            on_progress(0.30, "ANALYZING")

        nperseg = 4096
        noverlap = 3072
        freqs, _times, z_l = stft(left, fs=sr, window="hann", nperseg=nperseg, noverlap=noverlap)
        _, _, z_r = stft(right, fs=sr, window="hann", nperseg=nperseg, noverlap=noverlap)

        if on_progress:
            on_progress(0.55, "ISOLATING")

        # Mid (center) and Side (stereo) spectra
        z_mid = 0.5 * (z_l + z_r)
        z_side = 0.5 * (z_l - z_r)

        mag_m = np.abs(z_mid)
        mag_s = np.abs(z_side)

        # Audacity-style spectral center-channel mask
        center_mask = np.clip((mag_m - strength * mag_s) / (mag_m + mag_s + 1e-9), 0.0, 1.0) ** 1.35
        band_w = _vocal_band_weights(freqs, low_cut=low_cut, high_cut=high_cut)[:, None]
        vocal_mask = center_mask * band_w

        z_vocal = z_mid * vocal_mask
        z_music_l = z_l - z_vocal
        z_music_r = z_r - z_vocal

        if on_progress:
            on_progress(0.78, "RENDERING")

        _, vocal_mono = istft(z_vocal, fs=sr, window="hann", nperseg=nperseg, noverlap=noverlap)
        _, music_l = istft(z_music_l, fs=sr, window="hann", nperseg=nperseg, noverlap=noverlap)
        _, music_r = istft(z_music_r, fs=sr, window="hann", nperseg=nperseg, noverlap=noverlap)

        vocal_mono = vocal_mono[:n_samples]
        music_l = music_l[:n_samples]
        music_r = music_r[:n_samples]

        vocal_stereo = np.stack([vocal_mono, vocal_mono], axis=1).astype(np.float32)
        music_stereo = np.stack([music_l, music_r], axis=1).astype(np.float32)

        # Prevent digital clipping
        for arr in (vocal_stereo, music_stereo):
            peak = float(np.max(np.abs(arr))) if arr.size else 0.0
            if peak > 0.98:
                arr *= 0.98 / peak

        if on_progress:
            on_progress(0.90, "SAVING WAV")

        tmp_vocal_f32 = os.path.join(tmp_dir, "vocal_f32.wav")
        tmp_music_f32 = os.path.join(tmp_dir, "music_f32.wav")
        wavfile.write(tmp_vocal_f32, sr, vocal_stereo)
        wavfile.write(tmp_music_f32, sr, music_stereo)

        dst_vocal, dst_music = build_unique_stem_paths(input_path, target_dir)
        _encode_24bit_wav(tmp_vocal_f32, dst_vocal)
        _encode_24bit_wav(tmp_music_f32, dst_music)

        if on_progress:
            on_progress(1.0, "DONE")

        return {
            "status": "ok",
            "engine": "flowork_spectral_center_dsp",
            "input": os.path.abspath(input_path),
            "vocal_output": os.path.abspath(dst_vocal),
            "music_output": os.path.abspath(dst_music),
            "music_dir": os.path.abspath(target_dir),
            "vocal_bytes": os.path.getsize(dst_vocal),
            "music_bytes": os.path.getsize(dst_music),
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flowork OS Lightweight Audacity-Style Vocal & Music Stem Separator"
    )
    parser.add_argument("input", help="Input audio file (.wav, .mp3, .flac, etc.)")
    parser.add_argument("--output-dir", help="Optional output directory (defaults to user Music dir)")
    parser.add_argument("--strength", type=float, default=1.15, help="Center isolation strength (default: 1.15)")
    parser.add_argument("--low-cut", type=float, default=120.0, help="Vocal low-cut Hz (default: 120)")
    parser.add_argument("--high-cut", type=float, default=8500.0, help="Vocal high-cut Hz (default: 8500)")
    parser.add_argument("--open-folder", action="store_true", help="Open Music folder when finished")
    parser.add_argument("--json-progress", action="store_true", help="Emit JSON progress lines")
    args = parser.parse_args()

    def _emit(p: float, stage: str) -> None:
        if args.json_progress:
            print(json.dumps({"progress": round(p, 4), "stage": stage}), flush=True)

    try:
        result = separate_vocal_and_music(
            args.input,
            output_dir=args.output_dir,
            strength=args.strength,
            low_cut=args.low_cut,
            high_cut=args.high_cut,
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
