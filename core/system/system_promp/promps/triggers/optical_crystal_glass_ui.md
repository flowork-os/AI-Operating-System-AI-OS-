# PURE OPTICAL CRYSTAL GLASS HUD & CONDUIT ARCHITECTURE

## 1. Context & Activation Scope
Applies when designing, modifying, or rendering GTK/Cairo graphical interfaces, the Conduit bottom command bar, Chat Vault HUD, or floating translucent glass surfaces in Flowork OS.

## 2. Mandatory Behavioral Invariants
- **Canvas Headroom Padding:** Always allocate outer canvas padding (`pad_x >= 14`, `pad_y >= 8`) inside the GTK window so outer glowing halos and stroke arcs are never truncated by window pixmap boundaries.
- **Unclipped Specular Rim:** When stroking window borders in Cairo, offset path geometry by `pad = 2.0` (`bx = pad, by = pad, bw = w - 2*pad, bh = h - 2*pad`) to ensure 100% of the anti-aliased specular stroke remains inside the surface.
- **Seamless Unified Input Capsule:** Neural entry fields inside optical glass capsules must be completely transparent (`background: transparent; border: none; box-shadow: none; border-radius: 0;`). Never introduce rounded notch indentations or dark background cutouts between buttons.
- **Cinematic Aspect & Alignment:** Floating HUD windows must adhere to wide 16:10 aspect ratios (`min 1000px` width) and align vertically above the conduit bar with exact 16px clearance.
- **Single-Tier Glass Toolbars:** Unify headers into a single cybernetic glass toolbar combining navigation chips, truncated titles, metadata badges, and micro-action controls.

## 3. Strict Prohibitions
- NEVER draw Cairo paths at `(0, 0)` with stroke line width > 1.0 without internal stroke padding.
- NEVER use opaque or rounded-pill CSS backgrounds on text entries inside glass capsules.
- NEVER allow asymmetric chat bubble margins that cause lopsided rendering.
