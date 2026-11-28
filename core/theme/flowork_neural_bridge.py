#!/usr/bin/env python3
# =============================================================================
# 🚀 Flowork Sovereign OS — Neural State Bridge (RAM Shared Memory)
# Real-Time Bridge connecting Mr. Flow Agents, Voice Daemon & Living Wallpaper
# Zero Disk I/O: Atomic JSON updates in /dev/shm
# Co-authored-by: Flowork OS Architecture Board & Dr. Flow <agent@floworkos.com>
# =============================================================================

import os
import json
import time

STATE_FILE = "/dev/shm/flowork-neural-state.json"

def get_tool_morphology(tool_name: str) -> str:
    """Map tool name to its unique Flowork Sovereign visual morphology."""
    name = (tool_name or "").lower()
    if any(k in name for k in ("screenshot", "screen", "capture", "maim", "camera")):
        return "morph-camera"
    if "replace" in name or "patch" in name or "diff" in name:
        return "morph-diff"
    if "write" in name:
        return "morph-blueprint"
    if any(k in name for k in ("view", "read_file", "cat", "inspect")):
        return "morph-laser"
    if any(k in name for k in ("search_web", "search", "grep", "find")):
        return "morph-radar"
    if any(k in name for k in ("read_url", "url", "web_fetch", "fetch")):
        return "morph-conduit"
    if any(k in name for k in ("invoke_subagent", "manage_subagents", "swarm", "subagent")):
        return "morph-swarm"
    if "manage_task" in name or "task" in name:
        return "morph-pipeline"
    if any(k in name for k in ("schedule", "cron", "timer")):
        return "morph-chronometer"
    if any(k in name for k in ("send_message", "message", "ipc")):
        return "morph-signal"
    if any(k in name for k in ("ask_question", "question", "ask")):
        return "morph-query"
    if any(k in name for k in ("generate_image", "image", "draw")):
        return "morph-canvas"
    if any(k in name for k in ("define_subagent", "foundry")):
        return "morph-foundry"
    return "morph-terminal"

def set_neural_state(state: str, tool_name: str = "", morphology: str = "", action: str = "", amplitude: float = 0.0,
                     command: str = "", logs: list = None, exit_code: int = 0, duration_ms: int = 0, status: str = "",
                     args: dict = None, reason: str = None):
    """
    Atomically updates the neural reactor state in shared memory (/dev/shm).
    state: "idle" | "thinking" | "tool_use" | "speaking"
    """
    try:
        morph = morphology
        if not morph:
            if state == "speaking":
                morph = "morph-speech"
            elif state in ("compacting", "defragmenting") or "compact" in (tool_name or "").lower():
                morph = "morph-compacting"
            elif state == "tool_use":
                morph = get_tool_morphology(tool_name)
            elif state == "thinking":
                morph = "morph-thinking"
            elif state == "deliberation":
                morph = "morph-deliberation"
            else:
                morph = "morph-idle"

        cur_logs = logs if logs is not None else []
        cur_args = args or {}
        cur_reason = ""
        if reason is not None and str(reason).strip():
            cur_reason = str(reason).strip()
        elif isinstance(cur_args, dict) and (cur_args.get("reason") or cur_args.get("goal")):
            cur_reason = str(cur_args.get("reason") or cur_args.get("goal") or "").strip()
        elif state in ("deliberation", "thinking", "tool_use"):
            try:
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, "r", encoding="utf-8") as rf:
                        prev = json.load(rf)
                        if time.time() - prev.get("timestamp", 0) <= 120.0:
                            cur_reason = str(prev.get("reason") or "").strip()
            except Exception:
                pass

        data = {
            "state": state,
            "tool_name": tool_name or "",
            "morphology": morph,
            "action": action or "",
            "reason": cur_reason,
            "amplitude": max(0.0, min(1.0, float(amplitude))),
            "command": command or "",
            "args": cur_args,
            "logs": cur_logs[-8:] if isinstance(cur_logs, list) else [str(cur_logs)],
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "status": status or ("running" if state in ("tool_use", "thinking", "deliberation") else "idle"),
            "timestamp": time.time()
        }
        tmp_file = f"{STATE_FILE}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_file, STATE_FILE)
    except Exception:
        pass

def get_neural_state():
    """Reads current neural state from shared memory with auto-expiration guard."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Auto expire if state is older than 60 seconds to prevent stale states
                if time.time() - data.get("timestamp", 0) > 60.0:
                    return {
                        "state": "idle", "morphology": "morph-idle", "amplitude": 0.0,
                        "tool_name": "", "action": "", "reason": "", "command": "", "args": {}, "logs": [],
                        "exit_code": 0, "duration_ms": 0, "status": "idle", "timestamp": 0
                    }
                return data
    except Exception:
        pass
    return {
        "state": "idle", "morphology": "morph-idle", "amplitude": 0.0,
        "tool_name": "", "action": "", "reason": "", "command": "", "args": {}, "logs": [],
        "exit_code": 0, "duration_ms": 0, "status": "idle", "timestamp": 0
    }
