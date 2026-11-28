# SUNO AUDIO PREP & COPYRIGHT BYPASS DIRECTIVE

## 1. Context & Activation Scope
Triggered whenever the user mentions `suno`, `cover`, `demucs`, `vocal`, `stem`, `lagu`, `lirik`, or audio speed-up preparation.

## 2. Mandatory Behavioral Invariants
- **Activate Skill Immediately:** Call `activate_skill` with `name: "suno-audio-prep"` as soon as a Suno or vocal-prep request is detected.
- **Dependency Check First:** If `yt-dlp`, `ffmpeg`, `ffprobe`, or `demucs` is missing on the host PC, guide or install them using the Stage 0 commands in `suno-audio-prep`.
- **Audio Prep Pipeline:** Search and download the song via `yt-dlp`, isolate clean vocals via Demucs (`--two-stems vocals -n htdemucs`), and speed up the vocal stem via FFmpeg (`asetrate=44100*<factor>,aresample=44100`) to fit under 59 seconds (`-t 59 -map_metadata -1`).
- **Exact Ratio Calculation:** Always measure original duration vs sped-up duration with `ffprobe` and report the exact speed-up ratio (e.g. `4.81x`) plus a ready-to-paste Suno `Styles` slow-down prompt hint.

## 3. Strict Prohibitions
- **STOP AT AUDIO PREP:** Never automate Suno web upload, Suno generation, Android Micro-VM ingestion, or YouTube compilation. The user operates Suno manually.
- Never upload or recommend unmodulated full instrumental stems; always isolate and speed up vocals first.
- Never hardcode personal user directories in scripts; resolve dynamically via `$HOME`.
