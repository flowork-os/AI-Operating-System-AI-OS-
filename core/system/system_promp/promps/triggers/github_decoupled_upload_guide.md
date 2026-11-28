# GITHUB DECOUPLED UPLOAD & RELEASE ARCHITECTURE

## 1. Context & Activation Scope
Activated when executing `git` or `push` workflows, syncing system changes, packaging decoupled assets, or publishing Live ISOs to `https://github.com/flowork-os/AI-Operating-System-AI-OS-.git`.

## 2. Mandatory Behavioral Invariants
- **Layer 1 — Core & System Sync (`main`):** Run `flowork-upload` (or `~/Downloads/upload-flowork-os.sh`) for daily and OTA synchronization. It executes a `.gitignore`-driven two-way mirror (`/opt/floworkos` -> `core/`, `/usr/local/bin` -> `system/bin/`, `/etc/skel` -> `skel/`, `/opt/floworkos/iso-builder` -> `iso-builder/`) into `~/flowork-os-repo`, authenticates via `~/Downloads/token` (`GIT_ASKPASS`), runs `/opt/floworkos/bin/flowork-manifest-gen` (`manifest.json` and `manifest.json.gz`), verifies SHA-256 zero-drift, and updates `/opt/floworkos/system/version.json`. Use `--dry-run` to preview, `-m "message"` for custom commits, or pass explicit file paths for targeted uploads.
- **Layer 2 — Decoupled Heavy Assets (`v7.3.0` Release):** Package heavy subsystems (`android`, `audacity`, `social-auto-upload`, `wine-staging`) via `bash /opt/floworkos/iso-builder/package-assets.sh` into `~/Downloads/flowork-release-assets/*.tar.zst` and `flowork-on-demand-assets.sha256`, then upload via `gh release upload v7.3.0 ... --repo flowork-os/AI-Operating-System-AI-OS- --clobber` for `flowork-hydrate`.
- **Layer 3 — Live ISO Release:** Publish `> 2 GiB` ISOs via `bash /opt/floworkos/iso-builder/release-iso.sh` (add `--update` for existing tags, or use `~/Downloads/burn-and-release-flowork-iso.sh`) to split `< 1.8 GiB` chunks with SHA-256 verification.

## 3. Strict Prohibitions
- Never commit secrets (`*token*`, `*vault.json*`, `*.key`, `*.pem`, `*.db`, `history/chats/*`, `screenshots/*`, `connector/data/*`) or files exceeding `95 MB` to `main`.
- Never run `git push --force` or modify `/opt/floworkos/connector/` (`@lock @freez`).
