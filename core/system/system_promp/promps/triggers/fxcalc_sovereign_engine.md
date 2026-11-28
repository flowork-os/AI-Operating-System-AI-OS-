# FXCALC SOVEREIGN POSITION & RISK ENGINE INVARIANTS

## 1. Context & Activation Scope
Active whenever modifying, styling, or routing the Flowork OS Forex Position Size & Risk Calculator (`fxcalc.py`), its Right Cyber Wing integration, or its CLI binary dispatcher.

## 2. Mandatory Behavioral Invariants
- **Canonical Engine Path**: FXCalc is a core system engine located exclusively at `/opt/floworkos/engine/fxcalc/fxcalc.py`. Never place it inside `/opt/floworkos/apps/`.
- **Reactor Irisan Sector Integration**: Central Orbital Reactor sector (302°-358°, label "FXCALC", subtext "Forex Position Calc") directly toggles FXCalc inside the Right Cyber Wing (`cyber_wing.py toggle right fxcalc`).
- **Binary Dispatcher**: `/opt/floworkos/bin/flowork-fxcalc` routes CLI args (`--calc`, `--margin`, `--risk`, `--sl`, `--pair`, `--leverage`) to headless JSON calculations, and default no-arg invocations to the Right Cyber Wing.
- **Pure Crystal Glass Aesthetics**: Follow Flowork OS Optical Ice design with #00ff66 Matrix Green glow, #00f3ff Electric Cyan accents, 28px blur translucency, and JetBrains Mono typography.
- **Single-Slot Wing Swapping**: FXCalc operates as a first-class module within the Right Cyber Wing, swapping smoothly with any other app on the right flank without stacking.

## 3. Strict Prohibitions
- Never move FXCalc to `/opt/floworkos/apps/`.
- Never restore dead "CODE" irisan menu sector.
- Never output unvalidated position sizes exceeding maximum leverage capacity.
