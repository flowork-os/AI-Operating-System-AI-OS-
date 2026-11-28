# PASSIVE TRIGGER: POST-TROUBLESHOOTING KNOWLEDGE CRYSTALLIZATION

## 1. Context & Activation Scope
Triggered during multi-attempt debugging, recurring errors, troubleshooting loops, or post-fix verification (`troubleshoot`, `loop`, `retry`, `stuck`, `root_cause`, `regression`, `debug`, `crystallize`, `passive_trigger`).

## 2. Mandatory Behavioral Invariants
- **Root-Cause Crystallization Mandate:** Whenever a non-obvious bug, repeated failure, or multi-turn troubleshooting loop is empirically resolved (Exit Code 0), immediately check `/opt/floworkos/system/system_promp/promps/triggers.json` for an existing passive trigger covering that failure mode.
- **Create Missing Passive Trigger:** If no matching trigger exists, author a concise directive under `/opt/floworkos/system/system_promp/promps/triggers/<snake_case_name>.md` (strictly under 250 words, English only, 3-part format: Context, Mandatory Behavioral Invariants, Strict Prohibitions).
- **Precision Keyword Routing:** Register the new trigger in `triggers.json` using exact `hasKeywords([...])` and `promptContains([...])` tokens matching both English technical symbols and natural Indonesian/English user phrasing so it injects Just-In-Time on future related turns.
- **Empirical Validation:** Validate `triggers.json` JSON syntax and run `cargo test` in `/opt/floworkos/mrflow-rs` before concluding.

## 3. Strict Prohibitions
- NEVER bloat base prompts (`00_preamble.md`, `01_core_mandates.md`, `02_operational_guidelines.md`) with troubleshooting lessons.
- NEVER create overly broad trigger conditions that fire on unrelated turns.
- NEVER finish a hard-won bugfix without ensuring the root cause is crystallized against future repetition.
