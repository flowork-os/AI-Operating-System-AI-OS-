# PASSIVE TRIGGER: UNIFIED RUNTIME DEPENDENCY ISOLATION & ISO PACKAGING

## 1. Context & Activation Scope
Triggered when installing, refactoring, or auditing dependencies, Python virtual environments (`venv`), AI models, or runtimes for Flowork OS core nodes (`vocal_master`, `stem_split`, `bg_remove`, voice TTS/STT) and primary applications (`/opt/floworkos/apps/`).

## 2. Mandatory Behavioral Invariants
- **Unified Runtime Root:** Place all core node and primary app dependencies, Python virtual environments (`venvs/`), and AI models (`models/`) strictly inside `/opt/floworkos/runtime/` (or `/opt/floworkos/apps/<app>/runtime/` for app-scoped runtimes) with world read+traverse permissions (`o+rx`).
- **Mandatory Git Exclusion:** Exclude `runtime/` and `core/runtime/` in `/opt/floworkos/.gitignore`, `/opt/floworkos/iso-builder/.gitignore`, and `/home/mrflow/flowork-os-repo/.gitignore` so heavy venvs and models never enter GitHub commits.
- **Mandatory ISO Builder Inclusion:** Keep `/opt/floworkos/runtime/` unexcluded in SquashFS (`squashfs_excludes.txt`) and enforce pre-flight existence and permission checks in `/opt/floworkos/iso-builder/build-live-iso.sh` so every Live ISO bundles all required runtimes.
- **Zero Stale Paths & Cache Hygiene:** Point all scripts, binaries, and systemd units exclusively to `/opt/floworkos/runtime/` and register transient caches in `/opt/floworkos/bin/f-cleaner`.

## 3. Strict Prohibitions
- NEVER scatter node or primary app venvs, libraries, or AI models into `~/.cache`, `~/.local`, `~/.u2net`, `~/.rembg`, or duplicate app folders.
- NEVER commit or push `runtime/` or `core/runtime/` payloads to GitHub.
- NEVER exclude `/opt/floworkos/runtime/` from SquashFS or omit pre-flight checks in `build-live-iso.sh`.
