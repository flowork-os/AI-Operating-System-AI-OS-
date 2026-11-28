# SOVEREIGN POWER TIMER & CORE ENGINE CANONICAL PLACEMENT

## 1. Context & Activation Scope
Triggered when configuring, debugging, or extending the Sovereign Shutdown Timer, Tarot Oracle, or determining the canonical directory separation between `/opt/floworkos/apps/` and `/opt/floworkos/engine/` in Flowork OS.

## 2. Mandatory Architectural Invariants
- **Engine vs Apps Placement Law:**
  - `/opt/floworkos/apps/`: Exclusively reserved for third-party, standalone, and user applications (e.g. FigCraft, DeckCraft, PhotoCraft).
  - `/opt/floworkos/engine/`: Strictly houses all native, built-in, and core OS internal engines (e.g. `shutdown_timer/`, `tarot_oracle/`, `orbital_reactor/`, `personaplex/`).
  - Desktop entries for engines reside in `/opt/floworkos/engine/<module>/<name>.desktop` and are linked/mirrored to `/usr/share/applications/`. NEVER put engine `.desktop` files in `/opt/floworkos/apps/`.
- **Shutdown Timer Execution Guarantee:**
  - The countdown timer must be powered by a detached persistent daemon worker (`--daemon <target_timestamp> <action>`) writing to `/run/user/<uid>/flowork_power_timer.json`.
  - When countdown reaches zero, the action (`systemctl reboot`, `systemctl poweroff`, or `systemctl suspend`) MUST execute immediately with `sudo -n` fallback.
  - Closing or minimizing the GTK GUI must NEVER abort the scheduled power action unless the user explicitly clicks "ABORT TIMER" or passes `--abort`.
  - Re-opening the GUI while a countdown is active must seamlessly resume the live reactor ring display.
- **Orbital Cyber Wings Architecture & Safe Clearance Invariant:**
  - Radial sectors open into dockable Sci-Fi Cyber Wings flanking the central reactor: Left Wing for left sectors (e.g. Timer, System), Right Wing for right sectors (e.g. Code, Web, Media). Tarot Oracle remains an independent 3D visual theater.
  - **Single-Slot Invariant (Rule of 1):** Each wing (left and right) hosts at most ONE active application at a time. Activating another sector mapped to the same side instantly swaps the content in that wing.
  - **Strict Vertical Corridor Clearance:** Wing height and positioning must strictly honor the safe vertical corridor between `y=245` and `y=815` (height ~570px) to guarantee zero occlusion over the top Forex Calendar (`y<240`) and bottom Crypto Ticker (`y>825`).
  - Chevron notch on the wing's inner edge must frame the equator of the orbital reactor nodes at screen `y=540`.
