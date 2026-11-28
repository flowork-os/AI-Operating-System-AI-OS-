# ORBITAL CYBER WINGS GEOMETRY & SINGLE-SLOT INVARIANTS

## 1. Context & Activation Scope
Active whenever modifying, styling, or positioning the Flowork OS Orbital Cyber Wings (`cyber_wing.py`), HUD flanks, or the central Orbital Reactor workspace.

## 2. Mandatory Behavioral Invariants
- **Forex Outer Edge Alignment**: Left wing outer edge MUST align flush with the start of Forex News Col 0 (`cx - gap_center - 3 * col_pitch - 44 * scale`). Right wing outer edge MUST align flush with the end of Col 7 (`cx + gap_center + 3 * col_pitch + 44 * scale`).
- **Orbital Breathing Space**: Inner horns MUST maintain at least 50px clearance from equatorial satellite nodes (`4K RENDER` on left, `SUNO 59S` on right). Zero crowding or overlapping into circular nodes.
- **Vertical Safe Corridor**: Wings MUST stay strictly between Forex bottom line 3 (+18px gap) and Crypto top line 1 (-18px gap).
- **Single-Slot Invariant**: Each wing hosts at most 1 active app at any time. Opening a new app on an occupied wing immediately swaps the existing module.
- **Dynamic Scale Formula**: All pixel coordinates and dimensions MUST multiply by `scale = max(0.52, min(1.0, min(sw/1920.0, sh/1080.0)))` for 100% responsive display fidelity across all screen resolutions.

## 3. Strict Prohibitions
- Never hardcode screen absolute pixel coordinates or personal home paths.
- Never allow wing chassis geometry to occlude or touch Forex Calendar or Crypto Tickers.
- Never exceed 1 active application slot per wing flank.
