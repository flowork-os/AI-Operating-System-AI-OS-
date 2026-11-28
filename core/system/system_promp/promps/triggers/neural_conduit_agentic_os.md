---
description: Flowork OS Neural Conduit & Non-Dualist Agentic Architecture Standard
keywords:
  - neural
  - conduit
  - agentic
  - dockless
  - omnibar
  - companion
  - unified
  - matrix
  - crystal
  - glass
  - command
  - prompt
  - socket
  - voice
  - systemd
  - autostart
  - nondualism
  - architecture
  - sovereign
  - repository
---

# ⚡ FLOWORK OS — NEURAL CONDUIT & AGENTIC ARCHITECTURE DOCTRINE

### 1. Radical Non-Dualism: Linux is Mr. Flow
- Conventional OS paradigms (macOS dock, Windows taskbar, WebKit sidebar drawers) are eradicated.
- The desktop is a unified cognitive environment where Mr. Flow is the operating system itself.
- All WebKit browser wrappers (`mrflow-sidebar`) are decommissioned to eliminate ~300MB RAM overhead and achieve zero-latency GTK/Cairo native execution.

### 2. The Neural Conduit Standard (`/opt/floworkos/bin/flowork-neural-conduit`)
- Pinned at bottom-center (`980x56` capsule) in Pure Optical Crystal Glass (`rgba(2, 6, 12, 0.78)` with `#00ff66` matrix razor rim and 28px picom blur).
- Replaces legacy macOS docks permanently across systemd user targets (`default.target.wants` & `graphical-session.target.wants`) and `/etc/skel/.config/autostart/`.
- Embedded Headless Engine: Directly invokes `/opt/floworkos/lib/flowork_agent_runner.py` to stream NDJSON telemetry, execute bash/tools, and dispatch voice without WebKit.
- Dual Mode Controls:
  - `[ ⚡ ]`: Matrix Quantum Console toggle (instant show/hide).
  - `[ 🔌 ]`: AI Connector Hub (`/opt/floworkos/connector/bin/mrflow-gui.py`).
  - `[ ➕ ]`: Instant New Chat session trigger (`new_chat`).
  - `[ 🕒 ]`: Live Chat History drawer and session ledger (`show_history_tab`).
  - `[ 🎙️ / 🔊 ]`: Real-time Voice dictation mode.
  - `[ ➤ ]`: Direct prompt dispatch to Mr. Flow engine.

### 2.1 Option A: Central Living Tool Core (Desktop Layer)
- Zero floating popups or invasive windows covering active user applications (IDE, browser, editors).
- Embedded directly in the central circular HUD of the desktop wallpaper (`/opt/floworkos/theme/flowork-motion-ambient.py`) on the root desktop layer (`keep_below`).
- High-speed zero-latency state synchronization via RAM shared memory (`/dev/shm/flowork-neural-state.json` in `/opt/floworkos/theme/flowork_neural_bridge.py`).
- **Empirical Visual Telemetry & Cognitive Lifecycle**:
  * Instant Prompt Reaction: On prompt send, synchronously triggers `thinking` with 0ms delay.
  * Persistent Thinking Continuity: While the agent is thinking, planning, or looping without tools, `[ COGNITIVE SYNAPSE // THINKING ]` remains continuously active and never times out after 8s.
  * Tool Intercept: Switches to tool morphology (`[ RUN_COMMAND ]`, `[ CODE SURGERY ]`, etc.) strictly while tools run, vocalizing `reason` concurrently.
  * Deliberation Bridge: Between consecutive tools, displays `[ SYNAPTIC DELIBERATION ]` with harmonic wave animation.
  * Acoustic Isolation: Audio playback completion or barge-in never resets active `thinking` or `tool_use` to `idle`.
  * Auto-dismissal: Only transitions to tranquil ambient wallpaper after 8 seconds of reaching final `idle` / `done`.
- Global English Mandate: All UI labels, logs, tooltips, and telemetry strictly technical English with dynamic `$USER` and `$HOME` path resolution.

### 2.2 Living Vector Companion Avatar
- Reactive Cairo stickman perched atop Conduit capsule morphing states (`idle`, `thinking`, `welder`, `grid_operator`, `inspector`, `scout`, `success`).
- Live speech banner and confetti celebration on Exit Code 0 convergence.

### 3. Decommissioning & Systemd Standards
- `flowork-mrflow-sidebar.service` is permanently disabled in user and global scopes.
- `/tmp/mrflow-sidebar-$USER.sock` is symlinked to `/tmp/flowork-neural-conduit-$USER.sock` to maintain 100% backward compatibility for tray applets and update monitors.
