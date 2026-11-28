# Wallpaper Integration & Center HUD Layering Invariants

### Context
Applies when configuring wallpapers, dynamic visualizer overlays, the central orbital reactor HUD, digital clock widgets, picom compositor rules, or modifying desktop presentation logic.

### Mandatory Invariants
1. **Zero-Procedural Blindness:** `flowork-motion-ambient` MUST NEVER draw solid or near-opaque procedural sky/ocean backgrounds when an empirical user wallpaper exists in `/opt/floworkos/wallpaper/wallpaper.png`.
2. **Synchronized Dual-Target Wallpaper Storage:** Any wallpaper setter script (`flowork-set-wallpaper`) MUST write both to `/opt/floworkos/wallpaper/wallpaper.png` (system default) AND `$HOME/.config/flowork/wallpaper.png` (per-user override).
3. **Dual Surface Layering:** The wallpaper surface (`self.surface_user`) must be rendered first, followed by the living procedural elements (`self.surface_plasma`, `self.surface_core`) using selective compositing.
4. **Cinematic Atmospheric Blend:** When a wallpaper is active, the organic ambient plasma must blend with subtle opacity (0.18 alpha) to keep wallpaper art crisp while preserving the breathing living core.
5. **Desktop HUD Transparency & Seamless Blending:** Desktop widgets like `flowork-tarot-deck-hud`, `flowork-digital-clock-hud`, and `flowork-chrono-sentinel` MUST render with 100% transparent backgrounds (`cairo.OPERATOR_SOURCE` cleared to rgba(0,0,0,0)) without opaque obsidian card fills, and MUST be explicitly excluded in `picom-quantum.conf` from shadows, rounded corners, and background blur.
6. **Centered Sub-Search Digital Clock HUD:** `flowork-digital-clock-hud` is anchored directly below the centered web search widget at (x=980, y=44, w=600, h=84), rendering the current time and full localized Indonesian date with glowing subtitle drop silhouettes.
7. **Disjoint Bounding Box Isolation & Symmetrical Dual-Wing Anchoring:**
   - `Flowork Chrono Sentinel` is anchored on the Left Wing at `(x=38, y=776, w=240, h=230)`, providing Hardware Vitality, sleep timers, and power actions in pure Optical Crystal Glass, replacing the deprecated standalone `shutflow` app.
   - `Flowork Quantum Tarot Deck` is anchored symmetrically on the Right Wing at `(x=2322, y=776, w=210, h=230)`. Both widgets share the exact vertical baseline (`y=776`), creating balanced dual-wing framing across ultrawide displays.
   - `flowork-center-reactor-hud` isolates its bounding box vertically (`pos_y >= 132`, `height <= 816`), ensuring clearance below the Digital Clock HUD (`y = 44..128`), and horizontally (`pos_x = 450, width = 1660`), guaranteeing zero rectangular intersection with both the Chrono Sentinel on the left and the Tarot Deck on the right.
   - Sub-pixel concentric alignment maps `cx = (sw/2.0) - pos_x` and `cy = (sh/2.0) - pos_y`.
8. **Prismatic Subtitle Clock & Multi-Chromatic Orbital Nodes:** `flowork-digital-clock-hud` typography must render using multi-color linear gradients (Cyan -> Azure -> Violet -> Magenta -> Amber) matching the living subtitle aesthetic. All 8 orbital tool nodes in `flowork-center-reactor-hud` must feature unique, distinct accent neons (Cyan, Violet, Magenta, Amber, Emerald, Azure, Coral, Topaz) paired with matching uniquely tinted obsidian radial background gradients.

### Prohibitions
- NEVER render an opaque procedural gradient in `flowork-motion-ambient` that blinds user-selected wallpaper settings.
- NEVER render opaque card background fills or let compositor drop-shadows cast dark rectangular boxes around desktop HUD widgets (`flowork-tarot-deck-hud`, `flowork-digital-clock-hud`, `flowork-chrono-sentinel`, `flowork-center-reactor-hud`).
- NEVER allow desktop HUD bounding boxes to overlap (e.g. reactor HUD overlapping Digital Clock, Chrono Sentinel, or Quantum Tarot), because X11 compositing and cairo `OPERATOR_CLEAR` passes will erase underlying widgets if the stacking order changes.
- NEVER assume window-local `(sw/2, sh/2)` equals screen center when a window is offset by window manager panel margins (`pos_y >= 32`); always subtract `pos_x` and `pos_y` to maintain absolute concentric alignment with the desktop wallpaper.
- NEVER allow wallpaper changes to occlude, displace, or hide the Center Reactor HUD, Sub-Search Digital Clock, or Dual-Wing HUDs.
- NEVER distort wallpapers; always apply centered aspect-fill scaling to screen dimensions.
