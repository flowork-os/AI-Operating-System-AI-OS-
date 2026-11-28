#!/usr/bin/env python3
"""
Flowork Live Stage - Virtual Stage Daemon (Phase 1 & Phase 4)
Manages isolated Xephyr display (:99), compositor/WM, Ghost Overlay,
target application lifecycle (Pilot #1: Google Chrome with CDP :9299),
and Pause/Takeover IPC state machine.
"""

import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time

STAGE_DISPLAY = os.environ.get("FLOWORK_STAGE_DISPLAY", ":99")
HOST_DISPLAY = os.environ.get("DISPLAY", ":0")
STAGE_W = int(os.environ.get("FLOWORK_STAGE_W", "1280"))
STAGE_H = int(os.environ.get("FLOWORK_STAGE_H", "720"))
CDP_PORT = int(os.environ.get("FLOWORK_STAGE_CDP_PORT", "9299"))

STAGE_SOCK = "/tmp/flowork-stage.sock"
GHOST_SOCK = "/tmp/flowork-ghost.sock"
STATE_FILE = "/tmp/flowork-stage-state.json"
PID_FILE = "/tmp/flowork-stage.pid"
CHROME_PROFILE = os.environ.get("FLOWORK_STAGE_PROFILE", os.path.expanduser("~/.config/flowork-stage-chrome"))


class StageDaemon:
    def __init__(self):
        self.lock = threading.Lock()
        self.mode = "AI_ACTIVE"  # AI_ACTIVE | PAUSED_USER_TAKEOVER
        self.status_text = "AI CO-PILOT ACTIVE"
        self.running = True
        self.procs = {}

    def _write_state(self):
        state = {
            "running": self.running,
            "display": STAGE_DISPLAY,
            "host_display": HOST_DISPLAY,
            "width": STAGE_W,
            "height": STAGE_H,
            "cdp_port": CDP_PORT,
            "mode": self.mode,
            "status_text": self.status_text,
            "pids": {k: p.pid for k, p in self.procs.items() if p and p.poll() is None},
        }
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

    def send_ghost(self, payload: dict):
        if not os.path.exists(GHOST_SOCK):
            return False
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(GHOST_SOCK)
            s.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            s.close()
            return True
        except Exception:
            return False

    def start_stage(self):
        # Clean stale X lock if any
        disp_num = STAGE_DISPLAY.lstrip(":")
        lock_file = f"/tmp/.X{disp_num}-lock"
        if os.path.exists(lock_file):
            try:
                os.unlink(lock_file)
            except OSError:
                pass

        host_env = os.environ.copy()
        host_env["DISPLAY"] = HOST_DISPLAY

        # 1. Start Xephyr Virtual Stage on :0
        xephyr_cmd = [
            "Xephyr",
            STAGE_DISPLAY,
            "-ac",
            "-br",
            "-screen",
            f"{STAGE_W}x{STAGE_H}",
            "-title",
            "Flowork Live Stage",
        ]
        self.procs["xephyr"] = subprocess.Popen(
            xephyr_cmd,
            env=host_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for Xephyr display socket
        x_sock = f"/tmp/.X11-unix/X{disp_num}"
        for _ in range(40):
            if os.path.exists(x_sock):
                break
            time.sleep(0.1)

        stage_env = os.environ.copy()
        stage_env["DISPLAY"] = STAGE_DISPLAY
        stage_env["FLOWORK_STAGE_W"] = str(STAGE_W)
        stage_env["FLOWORK_STAGE_H"] = str(STAGE_H)
        stage_env["FLOWORK_GHOST_SOCK"] = GHOST_SOCK

        # 2. Start xfwm4 with compositor=on inside :99 for RGBA transparency
        self.procs["xfwm4"] = subprocess.Popen(
            ["xfwm4", f"--display={STAGE_DISPLAY}", "--compositor=on"],
            env=stage_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.6)

        # 3. Start Ghost Overlay inside :99
        overlay_script = os.path.join(os.path.dirname(__file__), "ghost_overlay.py")
        self.procs["ghost"] = subprocess.Popen(
            [sys.executable, overlay_script],
            env=stage_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(30):
            if os.path.exists(GHOST_SOCK):
                break
            time.sleep(0.1)

        self.send_ghost({"cmd": "mode", "mode": self.mode, "status": self.status_text})
        self._write_state()

    def launch_browser(self, url: str = "about:blank"):
        # Check if Chrome is already running on CDP_PORT
        p = self.procs.get("chrome")
        if p and p.poll() is None:
            return {"ok": True, "already_running": True, "cdp_port": CDP_PORT}

        os.makedirs(CHROME_PROFILE, exist_ok=True)
        stage_env = os.environ.copy()
        stage_env["DISPLAY"] = STAGE_DISPLAY

        chrome_cmd = [
            "google-chrome",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={CHROME_PROFILE}",
            f"--window-size={STAGE_W},{STAGE_H}",
            "--window-position=0,0",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-sync",
            url,
        ]
        self.procs["chrome"] = subprocess.Popen(
            chrome_cmd,
            env=stage_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Wait for CDP port to listen
        for _ in range(50):
            try:
                s = socket.create_connection(("127.0.0.1", CDP_PORT), timeout=0.2)
                s.close()
                break
            except OSError:
                time.sleep(0.15)

        self._write_state()
        return {"ok": True, "cdp_port": CDP_PORT, "pid": self.procs["chrome"].pid}

    def set_mode(self, mode: str, status_text: str = None):
        with self.lock:
            self.mode = mode
            if status_text:
                self.status_text = status_text
            elif mode == "PAUSED_USER_TAKEOVER":
                self.status_text = "USER TAKEOVER - YOUR TURN"
            else:
                self.status_text = "AI CO-PILOT ACTIVE"
            self._write_state()
        self.send_ghost({"cmd": "mode", "mode": self.mode, "status": self.status_text})

    def stop_all(self):
        self.running = False
        for name in ["chrome", "ghost", "xfwm4", "xephyr"]:
            p = self.procs.get(name)
            if p and p.poll() is None:
                try:
                    p.terminate()
                    p.wait(timeout=2)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
        for path in [STAGE_SOCK, GHOST_SOCK, STATE_FILE, PID_FILE]:
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def handle_request(self, req: dict) -> dict:
        action = req.get("action", "")
        if action == "status":
            with self.lock:
                return {
                    "ok": True,
                    "running": self.running,
                    "display": STAGE_DISPLAY,
                    "cdp_port": CDP_PORT,
                    "mode": self.mode,
                    "status_text": self.status_text,
                    "chrome_alive": bool(self.procs.get("chrome") and self.procs["chrome"].poll() is None),
                }
        elif action == "pause":
            self.set_mode("PAUSED_USER_TAKEOVER", req.get("status"))
            return {"ok": True, "mode": self.mode}
        elif action == "resume":
            self.set_mode("AI_ACTIVE", req.get("status"))
            return {"ok": True, "mode": self.mode}
        elif action == "toggle":
            new_mode = "PAUSED_USER_TAKEOVER" if self.mode == "AI_ACTIVE" else "AI_ACTIVE"
            self.set_mode(new_mode)
            return {"ok": True, "mode": self.mode}
        elif action == "launch_browser":
            return self.launch_browser(req.get("url", "about:blank"))
        elif action == "ghost":
            payload = req.get("payload", {})
            ok = self.send_ghost(payload)
            return {"ok": ok}
        elif action == "stop":
            threading.Thread(target=self._delayed_stop, daemon=True).start()
            return {"ok": True, "stopping": True}
        return {"ok": False, "error": f"Unknown action: {action}"}

    def _delayed_stop(self):
        time.sleep(0.15)
        self.stop_all()
        os._exit(0)

    def serve(self):
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        if os.path.exists(STAGE_SOCK):
            os.unlink(STAGE_SOCK)
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(STAGE_SOCK)
        os.chmod(STAGE_SOCK, 0o666)
        srv.listen(16)

        def sig_handler(signum, frame):
            self.stop_all()
            sys.exit(0)

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        while self.running:
            try:
                conn, _ = srv.accept()
            except OSError:
                break
            try:
                data = conn.recv(8192).decode("utf-8", errors="ignore").strip()
                if data:
                    req = json.loads(data)
                    resp = self.handle_request(req)
                    conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
            except Exception as e:
                try:
                    conn.sendall((json.dumps({"ok": False, "error": str(e)}) + "\n").encode("utf-8"))
                except Exception:
                    pass
            finally:
                conn.close()


def main():
    daemon = StageDaemon()
    daemon.start_stage()
    if "--with-browser" in sys.argv:
        daemon.launch_browser("https://www.google.com")
    daemon.serve()


if __name__ == "__main__":
    main()
