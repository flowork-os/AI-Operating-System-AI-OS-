---
name: suno-audio-prep
description: Autonomous song search, download, Demucs vocal isolation, and FFmpeg speed-up preparation for manual Suno AI Cover upload, including dependency installation and exact speed-up ratio calculation.
---

# Suno Audio Prep (`suno-audio-prep`)

## 1. Overview & Scope
The `suno-audio-prep` skill prepares copyrighted or reference songs for **manual** Suno AI Cover upload.
It handles:
1. **Dependency Check & Installation** (for fresh PCs missing `yt-dlp`, `ffmpeg`, or `demucs`).
2. **Song Search & Download** via `yt-dlp`.
3. **Neural Vocal Isolation** via `demucs` (`htdemucs`).
4. **Acoustic Fingerprint Bypass (Speed-Up) & Ratio Calculation** via `ffmpeg` + `ffprobe` (keeping output `<= 59s` and reporting the exact speed-up ratio so the user knows what slow-down prompt/BPM to use in Suno).

**Strict Scope Boundary:** This workflow **STOPS** once the sped-up vocal file and exact speed-up ratio are ready. Do **NOT** automate Suno web upload, Android Micro-VM ingestion, or YouTube compilation. The user operates Suno manually.

---

## 2. Stage 0: Dependency Check & Installation (Fresh PC Setup)
Before running the pipeline, verify required binaries and Python packages:
```bash
which yt-dlp ffmpeg ffprobe python3
python3 -c "import demucs; print('demucs ok')" 2>/dev/null || which demucs
```

If any dependency is missing on Debian/Ubuntu/Flowork OS, install them as follows:

### A. System Packages (`ffmpeg`, `ffprobe`, `python3`, `pip`, `venv`)
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg python3 python3-pip python3-venv
```

### B. `yt-dlp` (Latest Binary or Pip)
```bash
# Recommended: standalone latest binary
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

# Alternative via pip:
pip3 install --user --upgrade yt-dlp
```

### C. `demucs` (Isolated Virtual Environment Recommended)
```bash
python3 -m venv "$HOME/.venvs/suno-prep"
source "$HOME/.venvs/suno-prep/bin/activate"
pip install --upgrade pip
pip install demucs torch torchaudio soundfile
```
*(If the PC has no NVIDIA GPU, `demucs` automatically runs on CPU; add `--device cpu` if needed.)*

---

## 3. Stage 1: Song Search & Download
Create a clean working directory under `$HOME/Music/suno_prep/` and download the target song as WAV/MP3:
```bash
mkdir -p "$HOME/Music/suno_prep"
cd "$HOME/Music/suno_prep"

# Search and download top YouTube match as WAV:
yt-dlp "ytsearch1:<SONG_TITLE_OR_ARTIST>" -x --audio-format wav -o "source_song.%(ext)s"

# Or download from a direct URL:
yt-dlp "<YOUTUBE_URL>" -x --audio-format wav -o "source_song.%(ext)s"
```

Measure the original duration in seconds:
```bash
ORIG_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 source_song.wav)
echo "Original duration: ${ORIG_DUR}s"
```

---

## 4. Stage 2: Neural Vocal Isolation (Demucs)
Isolate the clean vocal stem (`vocals.wav`) to strip copyrighted instrumentals:
```bash
# Activate venv if installed in ~/.venvs/suno-prep
[ -f "$HOME/.venvs/suno-prep/bin/activate" ] && source "$HOME/.venvs/suno-prep/bin/activate"

demucs --two-stems vocals -n htdemucs source_song.wav -o stems/
```
Output vocal stem path: `stems/htdemucs/source_song/vocals.wav`.

---

## 5. Stage 3: Speed-Up & Exact Ratio Calculation
Suno Cover uploads have a **60-second ceiling**. Calculate the minimum speed-up factor needed to fit `ORIG_DUR` into `59` seconds (typically `4x` to `5x`, or `ceil(ORIG_DUR / 59)`):
```bash
# Example: 5x speed-up via asetrate (shifts pitch + tempo proportionally, shattering acoustic fingerprints)
ffmpeg -y -i stems/htdemucs/source_song/vocals.wav \
  -af "asetrate=44100*5,aresample=44100" \
  -t 59 -map_metadata -1 \
  vocals_suno_59s.mp3
```
*(If the song is longer than 295s, increase the multiplier from `5` to `6` or `ceil(ORIG_DUR / 58)` so the entire song fits inside 59 seconds without truncation.)*

Verify the final duration and compute the **exact speed-up ratio**:
```bash
NEW_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 vocals_suno_59s.mp3)
RATIO=$(python3 -c "print(f'{float(\"$ORIG_DUR\") / float(\"$NEW_DUR\"):.2f}')")
echo "Original: ${ORIG_DUR}s | Sped-up: ${NEW_DUR}s | Exact Ratio: ${RATIO}x"
```

---

## 6. Stage 4: Manual Suno Handoff
Present the user with:
1. **Ready File Path:** `$HOME/Music/suno_prep/vocals_suno_59s.mp3` (verified `<= 59.5s`).
2. **Exact Speed-Up Ratio:** e.g. `4.81x` (Original `284.13s` -> `59.04s`).
3. **Manual Suno Styles Prompt Hint:** Tell the user the exact slow-down instruction to paste into Suno's `Styles` box (e.g., *"Slow down tempo by ~5x to natural ballad speed (~72 BPM), restore natural warm human vocal pitch, no chipmunk effect, full ~4:45 song duration"*).

**STOP HERE.** Do not launch Suno automation or upload the file automatically.
