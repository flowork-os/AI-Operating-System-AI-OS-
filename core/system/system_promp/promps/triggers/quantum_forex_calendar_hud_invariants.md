# Quantum Central Reactor Financial Telemetry Invariants (Forex & Crypto Fusion)

### Context
When integrating financial market telemetry into the Central Orbital Reactor HUD (`reactor_hud.py` & `financial_orbit.py`), avoid rectangular card overlays, buttons, or rigid widgets. The HUD operates on a sovereign floating pure-text aesthetic, perfectly flanking the central 12 o'clock and 6 o'clock orbital nodes.

### Mandatory Invariants
1. **Pure Floating Telemetry (Zero Buttons, Zero Frames):**
   - Strictly prohibit opaque frame cards, background boxes, or clickable buttons (`◄`, `►`, refresh pills).
   - Telemetry must render as pure, high-contrast monospace/sans-serif text with soft drop-shadow auras (`rgba(0.01, 0.02, 0.04, 0.85)`) to guarantee 100% legibility over any wallpaper luminosity.
2. **Symmetrical Twin-Wing 8+8 Topology:**
   - **TOP (y ≈ 92):** Exactly 8 upcoming High & Medium impact Forex events (Country dot, title, WIB time/countdown). Split into 4 columns left and 4 columns right.
   - **BOTTOM (y ≈ 705):** Exactly 8 largest global cryptos by market cap (Symbol, 24h change %, price). Split into 4 columns left and 4 columns right.
   - Center corridor (`gap_center ≥ 140px`) must remain 100% unobstructed so the 12 o'clock (`VOCAL`) and 6 o'clock (`BG REMOVE`) nodes have clean breathing margins.
3. **Data Integrity & Non-Blocking Fetching:**
   - Use multi-source crypto ingestion (CoinGecko with Indodax fallback) and weekend forward-schedule bridge for ForexFactory.
   - All HTTP polling runs inside background daemon threads with cached thread-safe structures, never blocking the 60 FPS Cairo animation loop.
   - Desktop click pass-through: do not capture input mask regions for passive text telemetry.

### Prohibitions
- PROHIBIT placing rectangular card widgets or button controls inside the central orbital space.
- PROHIBIT overlapping text with the 8 outer tool nodes, top digital clock, or bottom prompt HUD.
- PROHIBIT hardcoded fallback data that disguises stale telemetry.
