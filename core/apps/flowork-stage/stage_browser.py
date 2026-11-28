#!/usr/bin/env python3
"""
Flowork Live Stage - Semantic Browser Bridge (Phase 3: Pilot #1)
Wraps `agent-browser` connected to the Virtual Stage Chrome (:9299) with:
1. Takeover Gate (pauses cleanly if user clicked Pause/Take Over, auto re-snapshots on resume)
2. ~1ms Bounding Box query via `agent-browser get box <target> --json`
3. Ghost Cursor choreography (highlight -> smooth glide -> click ripple / typing pill)
4. Full-speed semantic execution via `agent-browser`
"""

import json
import os
import socket
import subprocess
import sys
import time

STAGE_SOCK = "/tmp/flowork-stage.sock"
CDP_PORT = os.environ.get("FLOWORK_STAGE_CDP_PORT", "9299")
SESSION = os.environ.get("FLOWORK_STAGE_SESSION", "stage")


def ipc_call(req: dict) -> dict:
    if not os.path.exists(STAGE_SOCK):
        return {"ok": False, "error": "Stage daemon not running"}
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(STAGE_SOCK)
        s.sendall((json.dumps(req) + "\n").encode("utf-8"))
        data = s.recv(8192).decode("utf-8", errors="ignore").strip()
        s.close()
        return json.loads(data) if data else {"ok": False}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_ghost(payload: dict):
    ipc_call({"action": "ghost", "payload": payload})


def wait_if_paused() -> bool:
    """Blocks while user is in Takeover mode. Returns True if a pause occurred."""
    paused_once = False
    while True:
        st = ipc_call({"action": "status"})
        if not st.get("ok"):
            return paused_once
        if st.get("mode") == "PAUSED_USER_TAKEOVER":
            paused_once = True
            time.sleep(0.25)
        else:
            break
    if paused_once:
        # Re-sync DOM snapshot after user takeover
        run_ab(["snapshot", "-i"])
    return paused_once


def run_ab(args: list) -> subprocess.CompletedProcess:
    cmd = ["agent-browser", "--session", SESSION] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def get_chrome_top_offset() -> float:
    res = run_ab(["eval", "window.outerHeight - window.innerHeight"])
    try:
        val = float(res.stdout.strip().splitlines()[-1])
        if 40 <= val <= 160:
            return val
    except Exception:
        pass
    return 88.0


def get_element_box(target: str):
    res = run_ab(["get", "box", target, "--json"])
    if res.returncode != 0:
        return None
    try:
        data = json.loads(res.stdout)
        # Handle either {"x":..,"y":..,"width":..,"height":..} or {"data":{"box":{...}}}
        box = data.get("box") or data.get("data", {}).get("box") or data.get("data") or data
        if all(k in box for k in ("x", "y", "width", "height")):
            return (
                float(box["x"]),
                float(box["y"]),
                float(box["width"]),
                float(box["height"]),
            )
    except Exception:
        pass
    return None


def choreograph_target(target: str, label: str, action_type: str = "click", text: str = ""):
    box = get_element_box(target)
    if not box:
        return
    x, y, w, h = box
    top_offset = get_chrome_top_offset()
    sy = y + top_offset
    cx = x + w / 2.0
    cy = sy + h / 2.0

    send_ghost({"cmd": "highlight", "x": x, "y": sy, "w": w, "h": h, "label": label})
    send_ghost({"cmd": "move", "x": cx, "y": cy, "duration": 0.22, "label": label})
    time.sleep(0.24)

    if action_type == "click":
        send_ghost({"cmd": "click", "x": cx, "y": cy, "label": label})
    elif action_type == "type":
        send_ghost({"cmd": "type", "x": cx, "y": cy, "text": text})


def main():
    if len(sys.argv) < 2:
        print("Usage: flowork-stage-browser <connect|open|snapshot|click|fill|type|press|hover|get|eval> [args...]")
        sys.exit(1)

    action = sys.argv[1]
    args = sys.argv[2:]

    if action == "connect":
        res = run_ab(["connect", CDP_PORT])
        print(res.stdout, end="")
        if res.stderr:
            print(res.stderr, file=sys.stderr, end="")
        sys.exit(res.returncode)

    wait_if_paused()

    if action == "open" and args:
        send_ghost({"cmd": "mode", "mode": "AI_ACTIVE", "status": f"NAVIGATING: {args[0][:28]}"})
        res = run_ab(["open"] + args)
        send_ghost({"cmd": "mode", "mode": "AI_ACTIVE", "status": "AI CO-PILOT ACTIVE"})
    elif action in ("click", "dblclick", "hover") and args:
        target = args[0]
        choreograph_target(target, f"{action.upper()} {target}", "click")
        res = run_ab([action] + args)
    elif action in ("fill", "type") and len(args) >= 2:
        target = args[0]
        text = args[1]
        choreograph_target(target, f"TYPE {target}", "type", text=text)
        res = run_ab([action] + args)
    else:
        res = run_ab([action] + args)

    print(res.stdout, end="")
    if res.stderr:
        print(res.stderr, file=sys.stderr, end="")
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
