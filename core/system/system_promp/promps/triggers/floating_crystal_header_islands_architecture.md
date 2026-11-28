# FLOATING PURE OPTICAL CRYSTAL HEADER ISLANDS ARCHITECTURE

## 1. Context & Activation Scope
Applies when engineering, styling, or debugging top panel islands, status capsules, and system tray containers in Flowork OS (`xfce4-panel`, `gtk.css`, `picom-quantum.conf`).

## 2. Mandatory Behavioral Invariants
- **Header Docking & Island Topology:**
  1. *Left Capsule:* Flowork Emblem whisker menu launcher pill.
  2. *Center Capsule:* SEO Search Pill docked directly at $Y=3, H=34$ (`Gdk.WindowTypeHint.DOCK`), seamlessly centered in panel space, unfolding downward dynamically without obscuring the Center Reactor HUD.
  3. *Right Capsule:* Window tasklist, unified systray, Pulseaudio, and authentic camera screenshot launcher.
- **X11 Input Focus Invariant for Panel-Docked Widgets:**
  - `xfwm4` does NOT automatically transfer keyboard focus to `_NET_WM_WINDOW_TYPE_DOCK` windows upon mouse click.
  - Any search bar or interactive widget docked at $Y \le 40$ MUST explicitly invoke `XRaiseWindow` and `XSetInputFocus(display, xid, RevertToParent, CurrentTime)` on `button-press-event` and `enter-notify-event` to eliminate the perceived "invisible barrier" and guarantee immediate physical typing.
- **Zero Nested Borders:** Strip GtkEntry default border via `entry.set_has_frame(False)` and user-level zero-frame CSS to eliminate clashing double outlines ("garis tumpang tindih").
- **Strict English Locale & Telemetry:** All telemetry, tactical HUD boxes, search placeholders, and session anchors must strictly use 100% English.

## 3. Strict Prohibitions
- Never allow `xfce4-panel` to cover docked search widgets by omitting `XRaiseWindow`.
- Never create boxy, sharp-cornered containers or opaque edge-to-edge panel bars.
- Never use Indonesian language strings in desktop HUDs, tickers, or conduits.

