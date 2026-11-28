# DRAG GESTURE DONUT VERIFICATION & CONNECTOR MODEL TRANSITION DOCTRINE

## 1. Context & Activation Scope
Triggered when developing or refactoring contextual drag-and-drop radial menus (`flowork-radial-donut`), desktop panels (`xfce4-panel`), or model routing in sovereign connector (`flowork-connector`).

## 2. Mandatory Behavioral Invariants
- **X11 Pointer Grab Deadlock Prevention:** Daemons tracking cursor drags (`XRecord`, `query_pointer`) must NEVER grab pointers or popup windows while file managers (Nemo/Thunar) hold active X11 pointer grabs. Keep radial menus disabled from autostart unless explicitly invoked.
- **Strict Media Domain Gating:** Radial menus MUST restrict domains strictly to media (`AUDIO`, `IMAGE`). Generic code files (`.js`, `.py`, `.ts`), documents, and folders must reject drops immediately (`context.finish(False, False, time)`) and dismiss to release pointer grabs instantly.
- **Dwell Time Verification:** Slices require 280ms hover dwell threshold before accepting drops. Premature drops or cursor passes cancel cleanly.
- **Dead Center Neutral Zone:** Centers MUST provide 65px radius neutral cancel zone.
- **Header Panel Purity:** Desktop panels must not duplicate chat dock widgets. Lock panel configs in `xfce4-panel.xml` across user and skel profiles.
- **Dynamic Model Normalization:** The connector router dynamically normalizes model IDs with legacy fallback, never hardcoding static strings.

## 3. Strict Prohibitions
- Never hijack drag-and-drop operations for code, generic files, or folders.
- Never run pointer grab polling daemons deadlocking X11 during desktop drags.
- Never modify files without intentional slice dwell arming.
