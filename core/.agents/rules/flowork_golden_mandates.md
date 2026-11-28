# 👑 FLOWORK OS — SOVEREIGN DEVELOPMENT GOLDEN MANDATES (2-DAY WORK SESSION)

> **AUTHORITY:** Architect AWENKAUDICO / Dr. Flow
> **STATUS:** STRICTLY ENFORCED & NON-NEGOTIABLE
> **SCOPE:** Active across all development, refactoring, and refinement turns.

---

## 🛑 MANDATE 1: MANDATORY GITHUB AUTO-PUSH UPON ANY FILE MODIFICATION
Whenever ANY file is fixed, modified, or created in `/opt/floworkos`, `/usr/local/bin`, `/etc/systemd/system`, or `/etc/skel`:
1. **Target Repository:** `https://github.com/flowork-os/AI-Operating-System-AI-OS-.git` (branch `main`).
2. **Execution Vector:** Immediately run `/home/mrflow/Downloads/upload-flowork-os.sh "<descriptive commit message>"` or `/opt/floworkos/bin/flowork-upload`.
3. **Integrity Guarantee:** Never leave uncommitted or unpushed modifications. Ensure cryptographic SHA-256 manifest sync and `git push` achieve Exit Code 0.

---

## 💿 MANDATE 2: LIVE ISO BUILDER INCLUSION AUDIT
Every fix, new script, daemon, or tool MUST be accounted for in the Live ISO build pipeline:
1. Ensure all system modifications reside within canonical paths: `/opt/floworkos/`, `/usr/local/bin/`, `/etc/systemd/system/`, or `/etc/skel/`.
2. Verify against `/opt/floworkos/iso-builder/build-live-iso.sh` exclusion rules to guarantee that no essential file is omitted from the SquashFS image.
3. Validate that `flowork-iso-master check` and `build-live-iso.sh` will cleanly package the changes into future ISO builds.

---

## ⚡ MANDATE 3: SACRED & UNTOUCHABLE CONNECTOR (@lock @freez)
**HARAM MENYENTUH CONNECTOR!**
1. `/opt/floworkos/connector/` and `/opt/floworkos/bin/flowork-connector` are 100% stable, hardened, and locked.
2. ABSOLUTE PROHIBITION: Zero modifications, zero refactoring, zero touching of connector code, configuration, or binaries under any circumstances.
