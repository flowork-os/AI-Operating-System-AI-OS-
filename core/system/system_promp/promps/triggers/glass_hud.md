# [FLOWORK SOVEREIGN SOLID UI & HUD DIRECTIVE]

## 1. Context & Activation Scope
Active when configuring HUD overlays, compositor settings, or explicit translucency parameters.

## 2. Mandatory Behavioral Invariants
- **Solid Opaque Default for All Apps:** All desktop applications, panels, cards, and windows MUST use **100% SOLID OPAQUE** surfaces (`#0b111a` primary shell, `#111a26` elevated cards, `#162232` interactive pills) with crisp borders (`1px solid #243447`, top highlight `1px solid #334b66`).
- **Typography & Cyber Accents:** `JetBrains Mono` Bold, pure `#ffffff` text, `#00ff66` (Neon Emerald) and `#00f2fe` (Electric Aqua) cyber accents, rounded capsule geometry (`border-radius: 20px` to `28px`, `999px` pills).
- **Window Frame Invariants:** Standard solid titlebars with centered window controls and `borderless_maximize: false`.
- **Compositor Safety:** NEVER hard-kill Picom with `pkill -9 picom` (causes Electron/Chromium Ozone GPU crash `trap int3`). Reload gracefully or via smooth restart.

## 3. Strict Prohibitions
- NEVER make application windows, cards, or backgrounds transparent or see-through (`rgba` translucent window shells or `backdrop-filter` see-through blur are FORBIDDEN unless explicitly requested by the user).
- NEVER use square, sharp-cornered boxes (`border-radius: 0px/4px/8px` forbidden).
- NEVER use dull gray (`#94a3b8`, `#64748b`) or purple (`#a855f7`).
- NEVER set `borderless_maximize: true` or strip window controls, drag headers, and resize borders.
- NEVER create `.bak`, `.orig`, or backup files anywhere. Git is sovereign.
