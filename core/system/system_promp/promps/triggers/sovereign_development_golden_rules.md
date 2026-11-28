# SOVEREIGN DEVELOPMENT GOLDEN MANDATES

## 1. Context & Activation Scope
Activated on all development, file editing, bug fixing, refactoring, build orchestration, and system maintenance operations in Flowork OS.

## 2. Mandatory Behavioral Invariants
- **Mandatory GitHub Auto-Push (Code/System Edits Only):** ONLY when you actually edited, created, or fixed source/system files in `/opt/floworkos`, `/usr/local/bin`, `/etc/systemd/system`, or `/etc/skel`, synchronize and push to `https://github.com/flowork-os/AI-Operating-System-AI-OS-.git` using `/home/mrflow/Downloads/upload-flowork-os.sh` or `flowork-upload`. NEVER run git status or git push during read-only queries, oracle/tarot readings, or `/tmp/` cache writes.
- **ISO Builder Inclusion Guarantee:** Validate that every newly created or modified component resides within canonical paths bundled by `/opt/floworkos/iso-builder/build-live-iso.sh`. Ensure no essential file is blocked by squashfs exclusions so live ISO builds always carry the fix.
- **Sacred Stability Invariant:** The IPC Connector is production-hardened and locked (`@lock @freez`). Treat it as a completed immutable architectural foundation.

## 3. Strict Prohibitions
- NEVER leave any modified file uncommitted or unpushed to `flowork-os/AI-Operating-System-AI-OS-`.
- NEVER touch, refactor, edit, or modify any file in `/opt/floworkos/connector/` or the `/opt/floworkos/bin/flowork-connector` binary. HARAM MENYENTUH CONNECTOR under any condition.
- NEVER introduce unmapped system assets outside the ISO builder's SquashFS packaging scope.
