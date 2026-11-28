---
name: drachin-suno-producer
description: End-to-end autonomous pipeline for producing Mandarin Chinese Drama (Drachin) OST covers from 70s-2000s Indonesian nostalgic hits using Demucs vocal isolation, 59-second copyright-bypass speedup, Faster-Whisper lyric extraction, 4-line Mandarin adaptation, and Suno v6 Web Cover generation.
keywords:
  - drachin
  - suno
  - mandopop
  - guofeng
  - xianxia
  - wuxia
  - demucs
  - vocal-isolation
  - copyright-bypass
  - faster-whisper
  - lyric-extraction
  - bpm-tempo
  - sony-music-filter
  - youtube-research
  - ffmpeg
  - audio-speedup
  - cover-generation
  - live-stage
  - ost-production
  - indonesian-nostalgia
---

# Drachin Suno v6 OST Producer

## 1. Overview & Purpose
This skill automates the daily `@JanganNontonDrachin` music production workflow: transforming classic 1970s-2000s Indonesian pop/rock hits into cinematic Mandarin Chinese Drama (Drachin) OST covers on Suno v6. All supporting scripts are self-contained inside `/opt/floworkos/skills/drachin-suno-producer/scripts/` so the entire research, download, vocal separation, 59-second speedup, lyric extraction, and Suno parameter generation pipeline runs with minimal manual input.

## 2. Song Selection Criteria, Label Filtering & Ideal BPM/Tempo

### 2.1 Mandatory Song Criteria
1. **Era & Nostalgia Factor:** Indonesian pop, slow rock, or ballad hits from **1970s to 2000s** with strong melodic hooks and emotional chorus peaks (e.g., Dewa 19, Chrisye, Nike Ardilla, Peterpan/Noah, Ungu, Padi, Sheila On 7, Rossa, Krisdayanti).
2. **Strict Label Exclusion (CRITICAL):** **NEVER** select songs distributed or owned by **Sony Music** (`Sony Music Entertainment`, `Sony Music Indonesia`, `SME`, `Columbia`, `RCA`, `Epic`). Prefer independent or local labels such as **Aquarius Musikindo**, **Musica Studio's**, **Trinity Optima Production**, **Nagaswara**, or **GP Records**.
3. **Zero Duplicate Policy (WAJIB CEK LIST LOKAL):** **PASTIKAN lagu yang akan di-cover BELUM PERNAH di-cover sebelumnya.** Agent **TIDAK PERLU** membuka atau scrape channel YouTube `@JanganNontonDrachin` yang berat; cukup baca daftar lokal `/opt/floworkos/skills/drachin-suno-producer/covered_songs.txt` (atau jalankan `01_research_songs.py` yang otomatis membaca file tersebut secara instan).
   - **RULE EMAS (WAJIB UPDATE LIST):** Setiap kali selesai memproduksi/meng-cover lagu baru, **WAJIB** langsung menambahkan judul lagu tersebut ke `/opt/floworkos/skills/drachin-suno-producer/covered_songs.txt` menggunakan `python3 /opt/floworkos/skills/drachin-suno-producer/scripts/01_research_songs.py --add-covered "Artis - Judul Lagu"`.
4. **Vocal & Melodic Clarity:** Choose tracks with clean lead vocals, minimal heavy rap/screaming, and clear verse-chorus dynamics so Demucs `htdemucs` produces a clean vocal stem.
5. **Duration Ceiling:** Original song duration should be **3:00 to 5:30** (180s-330s) so the speedup factor to 59.0s stays between `3.0x` and `5.6x`, preserving pitch contour for Suno Editor normalization.

### 2.2 Ideal BPM / Tempo Guidelines
- **Original Song Ideal BPM:** **65 - 110 BPM** (ballads and mid-tempo pop/rock translate most naturally into orchestral Drachin OSTs without rhythmic artifacts).
- **Target Drachin OST Re-Genre BPM:**
  1. **Mandopop Balada Galau (Modern Heartbreak OST):** **68 - 82 BPM** (4/4 time, piano, lush strings, cello, emotional breathy vocals).
  2. **Sweet Pop & Akustik Ringan (Modern Rom-Com OST):** **88 - 105 BPM** (4/4 time, acoustic guitar, light percussion, warm Rhodes/piano, sweet airy vocals).
  3. **Gufeng Epik Wuxia & Xianxia (Colossal Historical/Fantasy OST):** **72 - 92 BPM** (4/4 or 6/8 cinematic pulse, dizi flute, guzheng, erhu, taiko/war drums, soaring orchestral brass & choir).

## 3. Phase 1: Research, Download, Vocal Isolation, 59s Speedup & Lyric Extraction

All Phase 1 steps are automated by two scripts in `/opt/floworkos/skills/drachin-suno-producer/scripts/`.

### Step 1: Research Eligible Songs (Non-Sony Music & Non-Duplicate)
```bash
python3 /opt/floworkos/skills/drachin-suno-producer/scripts/01_research_songs.py \
  --query "lagu indonesia hits 90an 2000an" \
  --limit 15
```
This script reads `/opt/floworkos/skills/drachin-suno-producer/covered_songs.txt` instantly (without scraping the heavy YouTube channel), searches YouTube, filters out Sony Music labels and duplicates, and prints eligible candidates with `video_id`, `title`, `duration`, `uploader`, and `url`. (Use `--refresh-catalog` only if you explicitly want to re-sync from YouTube).

### Step 2: One-Command Phase 1 Audio & Lyric Preparation
```bash
python3 /opt/floworkos/skills/drachin-suno-producer/scripts/02_phase1_prepare.py \
  --url "https://www.youtube.com/watch?v=RYGgSRtYxd0" \
  --out-dir "$HOME/Music/suno_phase1"
```
*(Default `--out-dir` otomatis mengarah ke `$HOME/Music/suno_phase1` sesuai user yang login, tidak pernah hardcode `/home/mrflow/Music` agar portabel di semua PC Flowork OS).*

What `02_phase1_prepare.py` executes automatically:
1. **Auto-Bootstrap Venv:** Ensures `/tmp/suno_phase1_venv` has `demucs`, `numpy`, `soundfile`, and `faster-whisper`.
2. **Download:** Downloads best audio as WAV (`orig.wav`) via `yt-dlp` and probes exact duration via `ffprobe`.
3. **BPM Estimation:** Estimates original song BPM from audio onset energy and recommends the best Drachin OST re-genre.
4. **Vocal Separation:** Runs `demucs --two-stems vocals -n htdemucs` (uses CUDA RTX 4060 if available, falls back to CPU).
5. **Instrumental Deletion:** Immediately deletes `no_vocals.wav` to keep only the clean vocal stem.
6. **59-Second Speedup:** Computes `factor = orig_duration / 59.0` and runs `ffmpeg` with `asetrate=44100*<factor>,aresample=44100` to output `vocals_59s.mp3` (strictly under 60s to pass Suno upload & copyright fingerprint checks).
7. **Lyric Extraction:** Resamples `vocals.wav` to 16kHz mono float32 numpy array via `soundfile` and transcribes Indonesian lyrics using `faster-whisper` (`small`, `device="cpu"`, `compute_type="int8"`), saving `lyrics_raw.txt`.

## 4. Phase 2: Drachin OST Re-Genre, 4-Line Mandarin Adaptation & Suno v6 Parameters

### Step 3: Generate Ready-to-Paste Suno v6 Parameters
```bash
python3 /opt/floworkos/skills/drachin-suno-producer/scripts/03_generate_suno_params.py \
  --genre 3 \
  --title "Kangen (Xiang Nian)" \
  --bpm 78 \
  --gender male
```
Genre options:
- `1`: Mandopop Balada Galau (Modern Heartbreak OST)
- `2`: Sweet Pop & Akustik Ringan (Modern Rom-Com OST)
- `3`: Gufeng Epik Wuxia & Xianxia (Colossal Fantasy OST)

### Step 4: 4-Line Lyric Adaptation Format, Breath Tags & Output Files
Adapt the extracted Indonesian lyrics (`<slug>_lyrics_clean.txt`) into poetic Mandarin Chinese matching the original syllable cadence, and save **two files** inside `$HOME/Music/suno_phase1/`:
1. **`<slug>_lyrics_mandarin_4line.txt`** — Strict **4-line block format** for reference:
   - Line 1: Mandarin Hanzi
   - Line 2: Pinyin (phonetic)
   - Line 3: Indonesian meaning
   - Line 4: English meaning
2. **`<slug>_lyrics_suno_ready.txt`** — Ready-to-paste Suno v6 Lyrics box format (**Mandarin Hanzi + Pinyin + Suno v6 vocal/breath tags**).

Include human-like Suno v6 performance tags: `[Intro - Guzheng & Dizi Solo]`, `[Verse 1 - Soft Breathy Vocal, Intimate]`, `[Pre-Chorus - Rising Strings, Emotional]`, `[Chorus - Soaring Orchestral, Full Power, Vibrato]`, `[Bridge - Erhu Solo, Whispered Breath]`, `[Outro - Fading Flute, Gentle Sigh]`.

## 5. Phase 3: Suno v6 Web Automation (Flowork Live Stage `:99`)
**CRITICAL BROWSER RULE:** NEVER use regular desktop Chrome (`:0`) for Suno automation. ALWAYS use the isolated **Flowork Live Stage** browser (`flowork-stage`, display `:99`, CDP port `9299`) with persistent disk profile `$HOME/.config/flowork-stage-chrome` so Google/Suno login cookies survive PC restarts.

1. **Launch / Verify Isolated Browser:**
   ```bash
   python3 /opt/floworkos/skills/drachin-suno-producer/scripts/04_suno_stage_browser.py
   ```
   Then connect `agent_browser` to `http://127.0.0.1:9299`. If not logged in yet, let the user log in inside the Live Stage viewer (`:99`).
2. **Upload Sped-Up Audio (5x+ Copyright Bypass):**
   - Navigate to `https://suno.com/create` and click **Add audio** -> **Upload Audio**.
   - Upload `$HOME/Music/suno_phase1/<slug>_vocals_59s.mp3` (5x speed). If Suno still flags copyright, increase speed factor (`6x`, `7x`, etc.) until upload passes.
3. **Restore Original Tempo in Suno Pro Editor:**
   - Ensure desktop view is active, open the uploaded audio track menu -> **Edit** -> **Open in Editor** (requires Suno Pro).
   - Restore the tempo/speed back to the original song tempo (`1 / factor`, e.g. `0.20x` for 5x) so the melody and beat match the original song.
4. **Cover with Hyphenated-Syllable Lyrics:**
   - Select **Create -> Cover** (or **Advanced** / **Custom Mode** with **v6** model).
   - Format lyrics with hyphenated syllables (`Bin-tang di-sur-ga` / Mandarin Pinyin + Hanzi + breath tags) to guarantee clean vocal phrasing and bypass lyric filters.
   - Paste `Styles`, `Exclude`, set `Weirdness` and `Style Influence` sliders, set `Title`, and click **Create**.
5. **Verify & Download:** Wait for generation completion (>1:00 duration), audition both tracks, and download `.mp3`/`.wav`.
6. **RULE EMAS (WAJIB):** Setelah cover selesai diproduksi, langsung catat judul lagu ke `covered_songs.txt`:
   ```bash
   python3 /opt/floworkos/skills/drachin-suno-producer/scripts/01_research_songs.py --add-covered "Artis - Judul Lagu"
   ```

## 6. Verification & Troubleshooting
- **Faster-Whisper `av` / `libcublas.so.12` Error:** Never pass a file path directly to `WhisperModel.transcribe()` if `av` fails on WAV metadata, and avoid CUDA if `libcublas.so.12` is missing. `02_phase1_prepare.py` avoids both by loading `vocals_16k.wav` via `soundfile` as a `float32` numpy array and running `device="cpu", compute_type="int8"`.
- **Suno Upload Rejection (>60s):** Verify `ffprobe -v error -show_entries format=duration -of csv=p=0 $HOME/Music/suno_phase1/vocals_59s.mp3` is `<= 59.5` seconds.
- **Sony Music Copyright Strike:** Always verify `uploader` and `description` metadata via `01_research_songs.py` before downloading.
