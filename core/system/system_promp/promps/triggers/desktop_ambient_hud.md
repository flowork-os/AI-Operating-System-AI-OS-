# AMBIENT OPTICAL CRYSTAL DESKTOP HUD DOCTRINE

## 1. Context & Activation Scope
Triggered when designing, modifying, or debugging desktop widgets, ambient HUDs, hardware vitality telemetry, or desktop glass overlays (`desktop_hud`, `tactical_hud`, `bento_widget`, `ambient_hud`, `glassmorphism_widget`, `dual_wing_hud`).

## 2. Mandatory Behavioral Invariants
- **Layering & Window Stacking:**
  - Desktop HUDs MUST use `self.stick()`, `set_skip_taskbar_hint(True)`, `set_skip_pager_hint(True)`, and `set_accept_focus(False)`.
  - Forbid `set_keep_below(True)`: when running alongside `flowork-motion-ambient`, `keep_below(True)` drops the HUD behind the animated wallpaper canvas.
- **Stealth Ambient Watermark Aesthetics:**
  - Enforce ultra-low contrast idle styling (`alpha ~0.30 - 0.35`, background `rgba(0.01, 0.04, 0.08, 0.16)` to `0.08`, hairline borders `0.07`).
  - Implement dynamic hover flare: transition to illuminated state (`alpha ~0.75`) via `enter-notify-event` and `leave-notify-event`.
  - Symmetrical Ultrawide Dual-Wing framing: Left Wing ($X=24$) for Tactical Mission Matrix and Right Wing ($X=2156$) for Vitality Telemetry, preserving center canvas for floating application windows.
- **Responsive Geometry & Multi-Resolution Scaling:**
  - Widgets (search bar, conduit, dials, reactor) MUST scale dynamically across Compact (1366x768), Standard (1920x1080), and Ultrawide (2560x1080).
  - Hook `screen.connect("size-changed")` and `screen.connect("monitors-changed")` for live hotplugging without restarting daemons.
  - Dynamically center widgets via `(screen_w - width) // 2` and anchor corner dials via `screen_w - win_w - margin`. Never hardcode static display resolutions.
- **Async Telemetry:**
  - Offload hardware I/O (NVIDIA SMI, disk, git status, D-Bus) to background worker threads to guarantee zero GTK frame drops.

## 3. Strict Prohibitions
- NEVER call `set_keep_below(True)` over living motion wallpapers.
- NEVER render high-contrast opaque boxes that clutter the desktop wallpaper.
- NEVER execute blocking subprocesses in the GTK `on_draw` loop.
