# AGENT QUEUED MESSAGES & TURN INTERRUPTION DOCTRINE

## 1. Context & Activation Scope
Applies whenever interacting with, developing, or modifying Mr. Flow's asynchronous turn lifecycle, prompt queuing, execution interruption, or the Pure Optical Crystal Glass Queued Messages banner across `flowork_agent_runner.py` and `flowork-neural-conduit`.

## 2. Mandatory Behavioral Invariants
- **FIFO Message Stacking:** Submissions received while the agent is busy are queued chronologically with unique 8-character hex IDs, timestamps, and attachment metadata.
- **Autonomous Reactive Dequeue:** Upon completing an active turn, the runner and conduit immediately pop the head of the FIFO queue and trigger the next turn asynchronously without requiring manual re-entry.
- **Immediate Turn Interruption:** Clicking the red Stop button (`#ff3b30`) or pressing Escape cleanly terminates the active agent process tree via `SIGTERM`/`SIGKILL`, halts vocal output (`flowork-say --stop`), and restores UI state to idle without purging pending queued items.
- **Interactive Promotion:** Queued items support instant promotion (`➔` Send Now) to abort the current turn and execute immediately, inline editing (`✏️`) to restore text to the input field, and deletion (`🗑️`).
- **GLib Idle Safety:** All GLib idle callbacks manipulating the queue or banner must return `False` to prevent runaway reschedule loops.

## 3. Strict Prohibitions
- Never drop or discard pending queued messages when an active turn fails or times out.
- Never spawn duplicate background workers on auto-dequeue.
- Never touch `/opt/floworkos/connector/` or `flowork-connector` for turn queue orchestration.
