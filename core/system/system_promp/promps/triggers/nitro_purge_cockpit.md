# SOVEREIGN NITRO PURGE & RAM TACHOMETER COCKPIT DIRECTIVE

## 1. Context & Activation Scope
Triggered when managing system hygiene, clearing temporary cache, dropping kernel RAM buffers, purging TTS audio artifacts, or configuring the circular sports car cockpit purge widget (`flowork-nitro-purge`).

## 2. Mandatory Behavioral Invariants
- **Sole Hygiene Interface:** Enforce zero duplicate applications. The standalone `diskcraft.desktop` is permanently eliminated; all hygiene operations are centralized into the round cockpit widget `/opt/floworkos/bin/flowork-nitro-purge`.
- **Desktop Layer & Non-Intrusive Stacking:** Enforce `NORMAL` window type hint with `set_keep_below(True)` and `accept_focus=False`. Must ALWAYS sit behind normal application windows so it never obstructs or hovers over user workspaces.
- **Stealth Theme Integration & Ambient Watermark:** Maintain subtle, faint visibility at `0.32` opacity during idle state with smoked dark ruby glass, blending seamlessly into the Flowork OS desktop theme. Smoothly bloom to vivid `0.95` brightness with razor matrix green RPM tachometer on pointer hover.
- **Deep Clean Scope:** Purge targets must include: all empirical screenshot captures (`~/Pictures/Screenshots/*`, `/opt/floworkos/screenshots/*.png`, `/opt/floworkos/screenshots/thumbs/*`, `/dev/shm/*screen*`), temporary TTS/piper/voice audio files (`/tmp/*.wav`, `/tmp/*voice*`), thumbnail cache (`~/.cache/thumbnails`), user trash (`~/.local/share/Trash`), kernel cache drop (`vm.drop_caches=3`), memory compaction (`vm.compact_memory=1`), systemd journal vacuuming, and all registered application temporary cache/session directories under `/opt/floworkos/apps/` and `~/.cache/`. Dilarang keras menyisakan residu cache aplikasi atau tumpukan screenshot.
- **Auditory & Visual Telemetry:** Provide real-time concentric circular RAM tachometer arc with RPM ticks, blow-off valve SFX on click, and HUD feedback banner reporting exact MB/GB freed.

## 3. Strict Prohibitions
- NEVER resurrect standalone `diskcraft.desktop` launcher icons.
- Never let wallpaper obscure the cockpit widget.
- Never write persistent static prompts; always route through conditional triggers.
