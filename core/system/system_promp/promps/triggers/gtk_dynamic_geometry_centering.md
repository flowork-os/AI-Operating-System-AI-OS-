# GTK DYNAMIC GEOMETRY & CONDUIT CENTERING DOCTRINE

## 1. Context & Activation Scope
Applies when styling, aligning, or positioning GTK3/Cairo overlay windows, conduit panels, chat history vaults, and floating HUD overlays across Flowork OS.

## 2. Mandatory Behavioral Invariants
- **Dynamic Allocation Centering:** Never compute horizontal screen positioning using static initial dimensions (`set_default_size`). Connect to the GTK `size-allocate` signal and compute `pos_x = (screen_width - allocation.width) // 2` dynamically on every layout change.
- **Explicit Container Sizing:** When top-level boxes hold dynamically packed child widgets, invoke `set_size_request(target_w, target_h)` to prevent container collapse (e.g. shrinking from 728px to 516px), which causes asymmetrical left margin offsets.
- **Anchored Floating Sub-Surfaces:** Position secondary floating popups (Quantum Console, History Vault, Quick Switcher) using dynamic root allocation math: `popup_x = conduit_x + (conduit_w - popup_w) // 2`.
- **Display Reconfiguration Handling:** Re-evaluate geometry inside `on_screen_changed` and `on_monitors_changed` to ensure precise centering persists across resolution and multi-head changes.

## 3. Strict Prohibitions
- Never hardcode screen center offsets or assume fixed screen resolutions.
- Never rely solely on window manager auto-centering for custom un-decorated overlay windows (`set_type_hint(Gdk.WindowTypeHint.DOCK)`).
- Never allow child widget layout changes to shift the visual optical center.
