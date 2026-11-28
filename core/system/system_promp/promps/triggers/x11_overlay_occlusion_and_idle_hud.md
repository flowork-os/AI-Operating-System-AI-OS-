# PASSIVE TRIGGER: X11 OVERLAY OCCLUSION & IDLE REACTOR HUD INVARIANTS

## 1. Context & Activation Scope
Triggered when building, debugging, or verifying X11/GTK3/Cairo desktop overlays, `flowork-center-reactor-hud`, `is_center_covered()`, Irisan radial menus, or F-Cleaner idle HUD rendering.

## 2. Mandatory Behavioral Invariants
- **Z-Order & Visibility Occlusion (`is_center_covered`):** When inspecting `Gdk.Screen.get_window_stack()`, iterate top-down and stop immediately upon reaching the HUD's own XID (`my_xid`) so windows stacked below the HUD never trigger false occlusion. Always define `geom = w.get_geometry()` before checking bounds.
- **Idle Layer 1 Contact & Dynamic Chat Orbit Expansion:** At idle, the 8 orbital nodes MUST snugly touch the outer boundary of the first layer ring (`r_orbit_idle = r_out + r_node - 2px`) without excessive outward spread. When chat or Matrix Quantum Console is active (`is_chat_active()` or `is_center_covered()`), the nodes dynamically and smoothly expand outward to `r_orbit_expanded (~315px)` to frame the chat interface cleanly without disappearing.
- **Hover-Only Irisan Sectors & Purge Core:** Keep the 6 annular Irisan sectors and `F-CLEANER` / `PURGE NOW` center core strictly hidden at idle (`p_sec = p`, rendered only when `p > 0.01`). At idle, only the subtle first layer guide ring at `r_out` and dormant core watermark are visible.
- **High-Contrast Living Core Luminance:** The central holographic arc reactor rendered by `flowork-motion-ambient` MUST maintain high contrast and radiant luminescence at idle (`rint >= 0.85` with deep obsidian glass backdrop) so all concentric rings, gyro brackets, 40 precision compass ticks, and synaptic waveforms remain crisp and legible against any wallpaper.
- **Scoped Input Shape:** Restrict `input_shape_combine_region` strictly to active interactive bounds (center core and orbital nodes at idle; expanded dial when bloomed) so surrounding desktop clicks pass through cleanly.

## 3. Strict Prohibitions
- NEVER treat minimized or hidden application windows as covering the screen center.
- NEVER allow the 6 Irisan sectors or large Purge button to permanently clutter the desktop when unhovered.
- NEVER render the center living reactor core with dim ghost wireframe (< 0.50 opacity) or obscure it with dark fill smudges in the HUD overlay.
- NEVER completely abort rendering the 8 outer nodes when the center is covered by a window; expand nodes outward instead.
