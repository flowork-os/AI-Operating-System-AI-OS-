# INTERACTIVE RADIAL APPLICATION & TRENDING SECTOR REACTOR HUD

## 1. Context & Activation Scope
Triggered when developing, configuring, or debugging central desktop interactive overlays, radial annular dials, and hover/click application menus (`reactor_hud`, `radial_menu`, `center_reactor`, `interactive_ambient`, `app_launcher_radial`, `annular_dial`).

## 2. Mandatory Behavioral Invariants
- **Idle Transparency & Clean Unmapping Invariant:**
  - The central desktop area MUST remain completely clean, quiet, and unobtrusive when idle.
  - Transparent overlay windows MUST enforce dynamic input shape masking (`input_shape_combine_region`). When idle, only the center circle intercepts mouse motion; all other desktop space passes clicks straight through to active user windows.
  - Overlay MUST set `self.set_type_hint(Gdk.WindowTypeHint.DOCK)` and `self.hide()` (unmap from X11) when idle to prevent compositor frames, rectangular box shadows ("shadow kotak"), or bottom seam lines.
  - Picom MUST include `class_g = 'flowork-center-reactor-hud'`, `class_g = 'xfce4-panel'`, and `window_type = 'dock'` in `shadow-exclude` and `blur-background-exclude`.
- **Occlusion Auto-Sleep Invariant:**
  - Sub-millisecond window stack scan via `Gdk.Screen.get_window_stack()`. If any application window covers coordinates `(1280, 540)`, hover bloom is deactivated immediately to save resources and prevent popups over active workflows.
- **6-Sector Modular Annular Architecture (56° per sector + 3° Laser Gap):**
  - Radial Annular Ring ($r_{in} = 80\text{px}, r_{out} = 175\text{px}$) partitioned into 6 distinct sectors:
    - S1: `KODING` (IDE, Shell & Terminal) — Razor Green (`#00ff66`) -> Blooms to Right Wing (`X=1480, Y=60`).
    - S2: `INTERNET` (Browser & Download) — Cyan (`#00f2fe`) -> Blooms to Right Wing (`X=1480, Y=280`).
    - S3: `MEDIA` (Desain & Video) — Amber (`#ffb800`) -> Blooms to Right Wing (`X=1480, Y=500`).
    - S4: `SISTEM` (Pengaturan & Alat) — Red (`#ff5959`) -> Blooms to Left Wing (`X=590, Y=500`).
    - S5: `ANDROID` (FlowOS Android & APK) — Mint (`#00f5a0`) -> Blooms to Left Wing (`X=590, Y=280`).
    - S6: `TRENDING` (Berita Cyber & GitHub) — Gold (`#ffd000`) -> Blooms to Left Wing (`X=590, Y=60`).
- **Targeted Bloom & Core Reset Invariant:**
  - Clicking a sector blooms ONLY that category's 5 cards with an angled laser conduit ray and diamond elbow node. All other areas remain clean.
  - Clicking the center Quantum Core ($r \le 74\text{px}$) or clicking the active sector again smoothly folds the cards back into the dial.
  - Moving mouse away collapses the dial back to idle and unmaps the window.
- **Debounce Latch & Dual Execution:**
  - Hardware debounce latch ($300\text{ms}$) enforces that 1 click yields exactly 1 execution.
  - Supports dual action types: `cmd` (launches desktop applications via `subprocess.Popen`) and `url` (launches Chrome with research feed).

## 3. Strict Prohibitions
- NEVER use sci-fi fluff or exaggerated jargon; use clean, functional, down-to-earth terms (`Koding`, `Internet`, `Media`, `Sistem`, `Android`, `Trending`).
- NEVER bloom all categories simultaneously; keep the screen serene via targeted blooming.
- NEVER block window clicks outside active HUD bounds during idle state.
