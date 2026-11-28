# ANTIGRAVITY-GRADE LOOP GUARD & SYNTHESIS ARCHITECTURE

## 1. Context & Activation Scope
Applies when designing, debugging, or configuring agent execution loops, semantic repetition detection, tool loop mitigations, and autonomous agent resilience in `mrflow-rs`.

## 2. Mandatory Behavioral Invariants
- **Non-Fatal Interception:** Autonomous harnesses must never kill or abort agent processes with raw `break` or process exit upon detecting tool loops. Redundant tool executions must be blocked and converted into directive prompt feedback (`[Loop Guard Intervention]`).
- **File Pagination Disambiguation:** File reading tools (`view_file`, `read_file`) MUST incorporate chunk ranges (`start_line`, `end_line`, `ContentOffset`) into semantic signatures so legitimate multi-page reading is not misclassified as a loop.
- **Progressive Intervention Escalation:** Escalate repetition defensively: first issue an advisory notice (`Loop Guard Advisory`), then intercept and block redundant execution (`Loop Guard Intervention`), and upon 4 consecutive interventions, inject a forced synthesis prompt compelling the model to wrap up and present its final report.
- **Metadata Scrubbing:** Strip noisy execution metadata (`toolAction`, `toolSummary`, `reason`, `goal`) during signature normalization so semantic hashing strictly evaluates substantive tool arguments.

## 3. Strict Prohibitions
- Never execute fatal breaks or raw terminations on tool repetition; the agent must always finish its turn and answer the user.
- Never omit line slice bounds when computing signatures for file inspection tools.
- Never silence loop warnings without providing guidance on how the model should self-correct.
