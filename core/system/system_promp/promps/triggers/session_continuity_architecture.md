# SOVEREIGN SESSION CONTINUITY & PERSISTENCE DOCTRINE

## 1. Context & Activation Scope
Triggered when developing, modifying, or troubleshooting session persistence, cross-reboot chat continuation, session resume, or history switcher workflows in Flowork OS.

## 2. Mandatory Behavioral Invariants
- **Cross-Reboot Session Anchor:** Active sessions MUST persist in `~/.flowork/session_state.json` (canonical cross-reboot anchor file), recording `session_id`, `title`, `turns`, `file_path`, `last_prompt`, `last_response`, and `timestamp`.
- **Optical Continuity Pill (Option A):** When restarting or booting, Conduit checks the session anchor. If valid (<7 days), it renders the floating Optical Crystal Glass pill `[ ⟲ Resume: "..." [N turns] ] [ ✕ Fresh ]` above the command entry bar.
- **Quick Session Switcher (Option C):** When `/resume` or `/sessions` is invoked (or via IPC action `switcher`), Conduit displays the floating Pure Optical Crystal Glass popover with recent conversations, relative time, and turn counts.
- **Context Rehydration:** Resuming any session must rehydrate `MatrixQuantumConsole` with the previous user prompt and assistant response via `rehydrate(last_prompt, last_response, title)`.
- **Amnesia Prevention & Dead Session Guard:** Catch CLI error events (`session not found`) and process crash to immediately clear stale session IDs and prevent command bar lockups.
- **Multi-Format Session Resolution:** Engine and CLI must resolve sessions flexibly across canonical UUIDs, short8 identifiers, filename timestamp stems (`session-YYYY-MM-DDTHH-MM-short8`), and direct `--session-file` paths so auto-resume never fails.

## 3. Strict Prohibitions
- NEVER use `/dev/shm` for cross-reboot state; tmpfs is volatile and lost on system power cycles.
- NEVER leave `self.active_session_id` pointing to a missing or deleted UUID without resetting.
- NEVER modify `/opt/floworkos/connector/` or non-conduit components.
