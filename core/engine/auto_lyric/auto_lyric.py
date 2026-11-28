#!/usr/bin/env python3
"""
Flowork OS — Sovereign Auto Lyric Transcriber Engine (Node 04)
Extracts singing vocals and speech directly to clean text (.txt) and synced lyric (.lrc)
files using offline faster-whisper without external network or SaaS dependencies.
Spawns isolated worker process in /opt/floworkos/runtime/venvs/voice.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Callable, Optional, Dict, Any

MODEL_SNAPSHOT_DIR = (
    "/opt/floworkos/runtime/models/whisper-tiny/models--Systran--faster-whisper-tiny/"
    "snapshots/d90ca5fe260221311c53c58e660288d3deb8d356"
)
VOICE_VENV_PYTHON = "/opt/floworkos/runtime/venvs/voice/bin/python3"

SUPPORTED_AUDIO_EXTS = {
    ".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus",
    ".wma", ".aiff", ".aif", ".mp4", ".mkv", ".webm",
}


def resolve_docs_dir() -> str:
    home = os.path.expanduser("~")
    target = os.path.join(home, "Documents", "lyrics")
    os.makedirs(target, exist_ok=True)
    os.makedirs("/opt/floworkos/documents/lyrics", exist_ok=True)
    return target


_WORKER_CODE = r'''
import json
import os
import sys

def emit(p, stage):
    print(json.dumps({"progress": round(float(p), 4), "stage": stage}), flush=True)

def format_lrc_timestamp(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"[{mins:02d}:{secs:05.2f}]"

def main():
    in_path = sys.argv[1]
    out_txt = sys.argv[2]
    out_lrc = sys.argv[3]
    snapshot_dir = sys.argv[4]
    req_lang = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5].strip() else "id"
    if req_lang.lower() in ("auto", "none"):
        req_lang = None

    emit(0.05, "INITIALIZING")
    from faster_whisper import WhisperModel

    emit(0.15, "LOADING MODEL")
    model_path = snapshot_dir if os.path.exists(snapshot_dir) else "tiny"
    model = WhisperModel(model_path, device="cpu", compute_type="int8")

    import subprocess, re
    target_audio = in_path
    note_banner = ""
    folder = os.path.dirname(os.path.abspath(in_path))

    # Smart detection: Check if input is a Suno 59s sped-up file (e.g. 4x chipmunk audio)
    is_59s = "_59s" in os.path.basename(in_path).lower()
    if is_59s and folder and os.path.exists(folder):
        orig_candidates = [f for f in os.listdir(folder) if "original" in f.lower() and f.endswith((".mp3", ".wav", ".flac", ".m4a"))]
        suno_info = os.path.join(folder, "suno_info.txt")
        if orig_candidates:
            target_audio = os.path.join(folder, orig_candidates[0])
            note_banner = f"Note: Input '{os.path.basename(in_path)}' adalah vokal yang di-speed-up untuk Suno 59s. Engine otomatis mentranskripsi file master original '{orig_candidates[0]}' agar vokal jernih dan akurat.\n\n"
        elif os.path.exists(suno_info):
            try:
                with open(suno_info, "r", encoding="utf-8") as sf:
                    m = re.search(r'Rasio Percepatan\s*:\s*([0-9.]+)x', sf.read())
                    if m:
                        factor = float(m.group(1))
                        tmp_restored = "/tmp/auto_lyric_restored_1x.wav"
                        subprocess.run(
                            ["ffmpeg", "-y", "-i", in_path, "-filter:a", f"asetrate=44100/{factor},aresample=44100", tmp_restored],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        if os.path.exists(tmp_restored):
                            target_audio = tmp_restored
                            note_banner = f"Note: Input '{os.path.basename(in_path)}' adalah audio vokal 59s (dipercepat {factor}x). Engine otomatis memperlambat kembali ke tempo normal 1x.\n\n"
            except Exception:
                pass

    emit(0.30, f"TRANSCRIBING [{req_lang.upper() if req_lang else 'AUTO'}]")
    transcribe_kwargs = {
        "beam_size": 5,
        "word_timestamps": False,
        "vad_filter": False,
    }
    if req_lang:
        transcribe_kwargs["language"] = req_lang

    segments_gen, info = model.transcribe(target_audio, **transcribe_kwargs)

    detected_lang = req_lang if req_lang else getattr(info, "language", "unknown")
    lang_prob = getattr(info, "language_probability", 1.0 if req_lang else 0.0)
    duration = getattr(info, "duration", 0.0)

    lyrics_lines = []
    lrc_lines = []

    for seg in segments_gen:
        txt = (seg.text or "").strip()
        if not txt:
            continue
        lyrics_lines.append(txt)
        ts = format_lrc_timestamp(seg.start)
        lrc_lines.append(f"{ts}{txt}")
        if duration > 0:
            seg_p = 0.35 + min(0.50, (seg.end / duration) * 0.50)
            emit(seg_p, f"VOCAL {detected_lang.upper()} {seg.end:.1f}s")

    # Check for existing lyrics reference if available in folder
    ref_lyrics = ""
    if folder and os.path.exists(folder):
        for ref_candidate in ["lirik_indonesia.txt", "lirik.txt", "lyrics.txt"]:
            ref_path = os.path.join(folder, ref_candidate)
            if os.path.exists(ref_path):
                try:
                    with open(ref_path, "r", encoding="utf-8") as rf:
                        ref_lyrics = rf.read().strip()
                    break
                except Exception:
                    pass

    emit(0.88, "SAVING")
    stem = os.path.splitext(os.path.basename(in_path))[0]
    header = (
        "================================================================\n"
        f"👑 FLOWORK OS — AUTO LYRIC TRANSCRIPTION\n"
        f"File: {os.path.basename(in_path)}\n"
        f"Target Source: {os.path.basename(target_audio)}\n"
        f"Language: {detected_lang.upper()} (Confidence: {lang_prob*100:.1f}%)\n"
        f"Duration: {duration:.1f}s\n"
        "================================================================\n\n"
    )
    if note_banner:
        header += note_banner

    if lyrics_lines:
        full_body = "\n".join(lyrics_lines)
        if ref_lyrics:
            full_body += "\n\n----------------------------------------------------------------\n"
            full_body += "📜 REFERENSI LIRIK ASLI DARI PROYEK:\n"
            full_body += "----------------------------------------------------------------\n"
            full_body += ref_lyrics
    else:
        if ref_lyrics:
            full_body = (
                "[Transkripsi AI vokal kosong / instrumental]\n\n"
                "📜 REFERENSI LIRIK DARI PROYEK:\n"
                "----------------------------------------------------------------\n"
                f"{ref_lyrics}"
            )
        else:
            full_body = "[Instrumental / No detectable singing vocal. Tip: Gunakan file lagu berkecepatan normal 1x atau stem vokal asli]"

    full_content = header + full_body + "\n"

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(full_content)

    with open(out_lrc, "w", encoding="utf-8") as f:
        f.write(f"[ti:{stem}]\n[ar:Flowork OS]\n[al:Auto Lyric Transcriber]\n\n")
        f.write("\n".join(lrc_lines) + "\n")

    emit(1.0, "COMPLETE")
    print(json.dumps({
        "result": {
            "status": "ok",
            "output_path": out_txt,
            "lrc_path": out_lrc,
            "lyrics": full_body,
            "language": detected_lang,
            "probability": lang_prob,
            "duration": duration,
            "line_count": len(lyrics_lines),
        }
    }), flush=True)

if __name__ == "__main__":
    main()
'''


def extract_lyrics(
    input_path: str,
    output_path: Optional[str] = None,
    on_progress: Optional[Callable[[float, str], None]] = None,
    language: str = "id",
) -> Dict[str, Any]:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    stem = os.path.splitext(os.path.basename(input_path))[0]

    if output_path:
        out_txt = output_path
    else:
        in_dir = os.path.dirname(os.path.abspath(input_path))
        if os.access(in_dir, os.W_OK):
            out_txt = os.path.join(in_dir, f"{stem}_lyrics.txt")
        else:
            out_txt = os.path.join(resolve_docs_dir(), f"{stem}_lyrics.txt")

    out_lrc = os.path.splitext(out_txt)[0] + ".lrc"

    python_bin = VOICE_VENV_PYTHON if os.path.exists(VOICE_VENV_PYTHON) else sys.executable

    cmd = [
        python_bin,
        "-c",
        _WORKER_CODE,
        input_path,
        out_txt,
        out_lrc,
        MODEL_SNAPSHOT_DIR,
        language,
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    final_result = None

    for raw_line in proc.stdout:
        line = raw_line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if "progress" in data and on_progress:
                on_progress(float(data["progress"]), str(data.get("stage", "")))
            if "result" in data:
                final_result = data["result"]
        except Exception:
            pass

    proc.wait()
    if proc.returncode != 0:
        err_msg = proc.stderr.read()
        raise RuntimeError(f"Auto Lyric worker exited with code {proc.returncode}: {err_msg}")

    if not final_result:
        final_result = {
            "status": "ok",
            "output_path": out_txt,
            "lrc_path": out_lrc,
        }

    # Mirror to Documents folder
    docs_dir = resolve_docs_dir()
    mirror_txt = os.path.join(docs_dir, os.path.basename(out_txt))
    mirror_lrc = os.path.join(docs_dir, os.path.basename(out_lrc))
    if os.path.abspath(out_txt) != os.path.abspath(mirror_txt):
        try:
            shutil.copy2(out_txt, mirror_txt)
            shutil.copy2(out_lrc, mirror_lrc)
        except Exception:
            pass

    try:
        subprocess.Popen(["xdg-open", out_txt], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    return final_result


def main():
    parser = argparse.ArgumentParser(description="Flowork OS Sovereign Auto Lyric Transcriber (Node 04)")
    parser.add_argument("input", nargs="?", help="Path to input vocal/audio file")
    parser.add_argument("-o", "--output", help="Optional output .txt path")
    parser.add_argument("-l", "--lang", default="id", help="Target language (default: 'id' for Indonesian, or 'auto')")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    def print_progress(p: float, stage: str):
        if not args.json:
            bar_len = 24
            filled = int(bar_len * p)
            bar = "=" * filled + "-" * (bar_len - filled)
            print(f"\r[{bar}] {int(p*100):3d}% | {stage:<16}", end="", flush=True)

    try:
        res = extract_lyrics(args.input, args.output, on_progress=print_progress, language=args.lang)
        if not args.json:
            print("\n")
            print(f"✅ Success! Lyrics saved to:\n   {res['output_path']}")
            print(f"   {res['lrc_path']}")
            print(f"Detected: {res.get('language', 'N/A').upper()} ({res.get('line_count', 0)} lines)")
        else:
            print(json.dumps(res, indent=2))
        sys.exit(0)
    except Exception as exc:
        if not args.json:
            print(f"\n❌ Error: {exc}", file=sys.stderr)
        else:
            print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
