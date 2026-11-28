---
name: neural-timemachine-rollback-architecture
description: "Sovereign instant Copy-on-Write state snapshotting, checkpointing, and /undo rollback engine for Flowork OS."
keywords:
  - timemachine
  - rollback
  - undo
  - snapshot
  - checkpoint
  - cow
  - ext4
  - hardlink
  - git
  - restore
  - state
  - recovery
  - atomic
  - turn
  - registry
  - filesystem
  - revert
  - delta
  - workspace
  - history
---

# FLOWORK NEURAL TIME-MACHINE ARCHITECTURE & ROLLBACK SPECIFICATION

## 1. Context & Activation Scope
Applies whenever restoring prior filesystem checkpoints, executing `/undo` or `/rollback`, inspecting snapshot history via `/snapshots`, or managing turn state integrity in Flowork OS workspaces.

## 2. Mandatory Behavioral Invariants
- **Pre-Turn Atomic Checkpointing:** Before executing any prompt, `flowork_agent_runner.py` automatically invokes `/opt/floworkos/bin/flowork-timemachine snapshot` to capture active workspace state in `<10ms`.
- **Hybrid Git & Hardlink CoW Engine:** Git repositories utilize zero-byte shadow tree snapshots (`git stash create` / tree references). Non-git workspaces utilize ext4 hardlink snapshots and delta tracking stored at `~/.flowork/timemachine/snapshots/`.
- **Atomic Undo Actuation:** When `/undo` or `/rollback` is issued in Neural Conduit, execute `/opt/floworkos/bin/flowork-timemachine rollback`. Reverted snapshots restore modified files, delete newly created untracked files, and notify the user via `MatrixQuantumConsole`.
- **Timeline Discovery:** Run `flowork-timemachine list` to render past turn checkpoints with ISO timestamps and file delta counts.

## 3. Strict Prohibitions
- NEVER perform destructive multi-file overwrites without an active Time-Machine pre-turn checkpoint.
- NEVER leave orphaned temporary snapshot files outside `~/.flowork/timemachine/`.
- NEVER bypass POSIX Exit Code 0 verification during rollback validation.
