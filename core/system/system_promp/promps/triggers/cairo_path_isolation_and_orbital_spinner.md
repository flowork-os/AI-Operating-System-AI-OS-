# Cairo Path Isolation & Orbital Spinner Animation Invariants

### Context
When rendering concentric HUDs, orbital nodes, or circular menus using Cairo graphics in PyGObject/GTK3, unclosed paths or missing `new_path()` calls cause Cairo to draw unwanted line segments connecting the previous point (e.g. text/icon coordinates) to the start angle of `cr.arc()` (0 degrees / 3 o'clock). Additionally, orbital nodes require realistic physics simulation (fidget spinner deceleration) when transitioning between compact and expanded floating states.

### Mandatory Invariants
1. **Zero Stray Lines (Explicit Path Cleansing):** Always invoke `cr.new_path()` immediately before calling `cr.arc(...)`, `cr.arc_negative(...)`, or any geometric primitives. Never assume previous strokes cleared the active point.
2. **Context Scope Isolation:** Always sandwich complex rendering sub-routines (such as `_draw_active_node`) with `cr.save()` + `cr.new_path()` at entry, and `cr.new_path()` + `cr.restore()` at exit.
3. **Spinner Physics Integration:** When orbital nodes expand into floating state, apply an angular impulse velocity (`spin_velocity = 28.0 deg/frame`) with progressive exponential friction damping (`velocity *= 0.94`) until smoothly settling back to aligned slot coordinates.
4. **Interactive Tactile Control:** Bind `scroll-event` to allow bidirectional manual spinning via the mouse wheel.

### Prohibitions
- Never execute `cr.arc()` without an explicit prior `cr.new_path()` if prior text or paths were drawn in the same context.
- Never leave `spin_angle` drifting indefinitely at an arbitrary angle; always settle cleanly back to home slot alignment.
