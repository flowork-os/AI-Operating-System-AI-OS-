#!/usr/bin/env python3
"""
02_phase1_prepare.py
All-in-one Phase 1 pipeline for Drachin Suno v6 OST production:
1. Auto-bootstrap Python venv (/tmp/suno_phase1/venv) with demucs, numpy, soundfile, faster-whisper
2. Download YouTube audio as WAV (or accept local audio)
3. Estimate original BPM/tempo & recommend Drachin OST re-genre
4. Separate vocals via Demucs (htdemucs) & delete instrumental (no_vocals.wav)
5. Speed up vocals to 59.0s (asetrate=44100*factor,aresample=44100) -> vocals_59s.mp3
6. Extract Indonesian lyrics via faster-whisper (CPU int8 + soundfile numpy array)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"[CMD] {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, check=check)


def ensure_venv(venv_dir: str) -> str:
    py_bin = os.path.join(venv_dir, "bin", "python")
    if not os.path.exists(py_bin):
        print(f"[SETUP] Creating venv at {venv_dir}...", flush=True)
        if shutil.which("uv"):
            run(["uv", "venv", venv_dir])
        else:
            run([sys.executable, "-m", "venv", venv_dir])

    check_imports = subprocess.run(
        [py_bin, "-c", "import demucs, numpy, soundfile, faster_whisper"],
        capture_output=True,
    )
    if check_imports.returncode != 0:
        print("[SETUP] Installing demucs, numpy, soundfile, faster-whisper...", flush=True)
        pkgs = ["demucs", "numpy", "soundfile", "faster-whisper"]
        if shutil.which("uv"):
            run(["uv", "pip", "install", "--python", py_bin, *pkgs])
        else:
            run([py_bin, "-m", "pip", "install", *pkgs])
    return py_bin


def get_duration(path: str) -> float:
    res = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(res.stdout.strip())


def estimate_bpm_and_transcribe(py_bin: str, orig_wav: str, vocals_wav: str, out_dir: str) -> dict:
    vocals_16k = os.path.join(out_dir, "vocals_16k.wav")
    orig_16k = os.path.join(out_dir, "orig_16k.wav")
    run(["ffmpeg", "-y", "-i", vocals_wav, "-ar", "16000", "-ac", "1", vocals_16k])
    run(["ffmpeg", "-y", "-i", orig_wav, "-ar", "16000", "-ac", "1", orig_16k])

    lyrics_raw = os.path.join(out_dir, "lyrics_raw.txt")
    helper_code = f"""
import json, numpy as np, soundfile as sf
from faster_whisper import WhisperModel

# 1. Lightweight BPM estimation via onset energy autocorrelation
y, sr = sf.read({orig_16k!r}, dtype="float32")
if y.ndim > 1:
    y = y.mean(axis=1)
hop = 512
frames = len(y) // hop
env = np.sqrt(np.mean(y[:frames * hop].reshape(frames, hop) ** 2, axis=1))
onset = np.maximum(0.0, np.diff(env, prepend=env[0]))
onset = onset - np.mean(onset)
ac = np.correlate(onset, onset, mode="full")[len(onset) - 1:]
fps = sr / hop
min_lag = int(fps * 60.0 / 140.0)
max_lag = int(fps * 60.0 / 55.0)
best_lag = min_lag + int(np.argmax(ac[min_lag:max_lag]))
bpm = round(60.0 * fps / best_lag, 1)

# 2. Transcribe vocals via faster-whisper (CPU int8 + numpy array)
v, vsr = sf.read({vocals_16k!r}, dtype="float32")
if v.ndim > 1:
    v = v.mean(axis=1)
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(v, language="id", beam_size=5, vad_filter=True)
lines = []
for seg in segments:
    lines.append(f"[{{seg.start:06.2f}} -> {{seg.end:06.2f}}] {{seg.text.strip()}}")
with open({lyrics_raw!r}, "w", encoding="utf-8") as f:
    f.write("\\n".join(lines) + "\\n")

print(json.dumps({{"bpm": bpm, "lines": len(lines), "lyrics_raw": {lyrics_raw!r}}}))
"""
    res = subprocess.run([py_bin, "-c", helper_code], capture_output=True, text=True, check=True)
    for line in reversed(res.stdout.strip().splitlines()):
        if line.startswith("{"):
            return json.loads(line)
    return {"bpm": 0.0, "lines": 0, "lyrics_raw": lyrics_raw}


def main():
    parser = argparse.ArgumentParser(description="Phase 1 all-in-one audio & lyric preparation for Suno v6.")
    parser.add_argument("--url", help="YouTube URL to download")
    parser.add_argument("--audio", help="Local audio file path (skips yt-dlp)")
    default_music_dir = os.path.join(os.path.expanduser("~"), "Music", "suno_phase1")
    parser.add_argument("--out-dir", default=default_music_dir, help="Working output directory (default: $HOME/Music/suno_phase1)")
    parser.add_argument("--target-sec", type=float, default=59.0, help="Target speedup duration in seconds (default: 59.0)")
    args = parser.parse_args()

    if not args.url and not args.audio:
        parser.error("Provide either --url or --audio")

    os.makedirs(args.out_dir, exist_ok=True)
    venv_dir = "/tmp/suno_phase1_venv"
    py_bin = ensure_venv(venv_dir)

    orig_wav = os.path.join(args.out_dir, "orig.wav")
    if args.url:
        run([
            "yt-dlp",
            "-x",
            "--audio-format",
            "wav",
            "--audio-quality",
            "0",
            "-o",
            os.path.join(args.out_dir, "orig.%(ext)s"),
            args.url,
        ])
    else:
        run(["ffmpeg", "-y", "-i", args.audio, orig_wav])

    orig_dur = get_duration(orig_wav)
    speed_factor = orig_dur / args.target_sec

    # Demucs vocal separation
    sep_dir = os.path.join(args.out_dir, "separated")
    demucs_bin = os.path.join(venv_dir, "bin", "demucs")
    run([demucs_bin, "--two-stems", "vocals", "-n", "htdemucs", "-o", sep_dir, orig_wav])

    vocals_wav = os.path.join(sep_dir, "htdemucs", "orig", "vocals.wav")
    no_vocals_wav = os.path.join(sep_dir, "htdemucs", "orig", "no_vocals.wav")
    if os.path.exists(no_vocals_wav):
        os.remove(no_vocals_wav)
        print(f"[CLEANUP] Deleted instrumental: {no_vocals_wav}", flush=True)

    # Speed up vocals to 59s
    vocals_59s = os.path.join(args.out_dir, "vocals_59s.mp3")
    run([
        "ffmpeg",
        "-y",
        "-i",
        vocals_wav,
        "-filter:a",
        f"asetrate=44100*{speed_factor:.6f},aresample=44100",
        "-b:a",
        "192k",
        vocals_59s,
    ])
    final_dur = get_duration(vocals_59s)

    # BPM estimation + Faster-Whisper transcription
    analysis = estimate_bpm_and_transcribe(py_bin, orig_wav, vocals_wav, args.out_dir)

    summary = {
        "orig_wav": orig_wav,
        "orig_duration_sec": round(orig_dur, 3),
        "estimated_bpm": analysis["bpm"],
        "speed_factor": round(speed_factor, 6),
        "vocals_wav": vocals_wav,
        "vocals_59s_mp3": vocals_59s,
        "vocals_59s_duration_sec": round(final_dur, 3),
        "lyrics_raw_txt": analysis["lyrics_raw"],
        "transcribed_lines": analysis["lines"],
    }
    print("\n=== PHASE 1 COMPLETE ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
