#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flowork OS Sovereign Agent Runner
Direct execution engine for Mr. Flow AI without WebKit browser overhead.
Bypasses legacy web sidebar: executes mrflow CLI, streams real-time telemetry,
synthesizes streaming voice via PersonaPlex, and feeds the living desktop HUD.
"""

import os
import sys
import re
import json
import time
import socket
import signal
import selectors
import threading
import subprocess
import urllib.request
import uuid

HOME = os.environ.get("HOME", os.path.expanduser("~"))
USER = os.environ.get("USER", "mrflow")
LOG_PATH = f"/tmp/flowork-agent-runner-{USER}.log"


def log_runner(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [AGENT-RUNNER] {msg}\n"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(line, end="", file=sys.stderr)


def sanitize_clause(text: str) -> str:
    """Strips markdown and formats text cleanly for voice synthesis."""
    if not text:
        return ""
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\|[^\n]+\|', '', text)
    text = re.sub(r'</?speech>', '', text, flags=re.IGNORECASE)
    # Strip non-Latin scripts
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F\s\.,!\?\'\-]', ' ', text)
    # Strip markdown symbols & emojis
    text = re.sub(r'[#*_~>\[\]\(\)\{\}\\\|/+=^%$@&<>]', ' ', text)
    return ' '.join(text.split()).strip()


ABBREV_SET = {'mr.', 'dr.', 'prof.', 'no.', 'vs.', 'dll.', 'dsb.', 'dst.', 'etc.', 'inc.', 'ltd.'}


def extract_sentences_streaming(buf: str, is_final: bool = False):
    """Splits a streaming text buffer into sentence-length chunks for voice synthesis."""
    sentences = []
    while True:
        pattern = r'([\.\!\?]+(?:\s+|\n+|$)|[\n]{1,})' if is_final else r'([\.\!\?]+(?:\s+|\n+)|[\n]{2,})'
        m = re.search(pattern, buf)
        if not m:
            break
        split_pos = m.end()
        candidate = buf[:split_pos].strip()

        # Avoid splitting list item numbers like '1.' or '2.'
        if re.match(r'^\s*\d+[\.\)]\s*$', candidate):
            if not is_final:
                break

        last_word = candidate.split()[-1].lower() if candidate.split() else ''
        if last_word in ABBREV_SET and not is_final:
            m2 = re.search(pattern, buf[split_pos:])
            if not m2:
                break
            split_pos += m2.end()
            candidate = buf[:split_pos].strip()

        clean_c = sanitize_clause(candidate)
        if len(clean_c) >= 3:
            sentences.append(clean_c)
        buf = buf[split_pos:].lstrip()

    return sentences, buf


class FloworkAgentRunner:
    """
    Sovereign headless runner for mrflow CLI.
    Emits real-time callbacks directly to GTK/Cairo HUD and PersonaPlex voice.
    """
    def __init__(self, event_callback=None):
        self.event_callback = event_callback or (lambda event_type, payload: None)
        self.active_proc = None
        self.current_session_id = None
        self.current_workspace = HOME
        self.is_busy = False
        self.turn_lock = threading.Lock()
        self.active_turn_id = 0
        self.message_queue = []
        self.queue_lock = threading.Lock()

    def set_callback(self, cb):
        self.event_callback = cb

    def is_running(self):
        return self.is_busy and self.active_proc is not None

    def enqueue(self, prompt: str, session_id: str = None, workspace: str = None, new_session: bool = False, attachment: dict = None):
        msg_id = str(uuid.uuid4())[:8]
        disp = prompt.strip()[:140] if prompt and prompt.strip() else (os.path.basename(attachment.get("path", "")) if attachment and "path" in attachment else "Instruction")
        item = {
            "id": msg_id,
            "prompt": prompt,
            "session_id": session_id,
            "workspace": workspace,
            "new_session": new_session,
            "attachment": attachment,
            "created_at": time.time(),
            "display_text": disp
        }
        with self.queue_lock:
            self.message_queue.append(item)
        log_runner(f"QUEUED MESSAGE #{msg_id} added. Total queued: {len(self.message_queue)}")
        self.event_callback("queue_updated", {"queue": list(self.message_queue), "count": len(self.message_queue)})
        return item

    def get_queue(self):
        with self.queue_lock:
            return list(self.message_queue)

    def remove_from_queue(self, msg_id: str):
        removed = None
        with self.queue_lock:
            for i, it in enumerate(self.message_queue):
                if it["id"] == msg_id:
                    removed = self.message_queue.pop(i)
                    break
        if removed:
            self.event_callback("queue_updated", {"queue": list(self.message_queue), "count": len(self.message_queue)})
        return removed

    def promote_queued_message(self, msg_id: str):
        item = self.remove_from_queue(msg_id)
        if item:
            log_runner(f"PROMOTING QUEUED MESSAGE #{msg_id}: aborting active turn and dispatching immediately")
            self.abort()
            time.sleep(0.06)
            self.run_prompt_async(
                prompt=item["prompt"],
                session_id=item.get("session_id") or self.current_session_id,
                workspace=item.get("workspace") or self.current_workspace,
                new_session=item.get("new_session", False),
                attachment=item.get("attachment")
            )
        return item

    def clear_queue(self):
        with self.queue_lock:
            self.message_queue.clear()
        self.event_callback("queue_updated", {"queue": [], "count": 0})

    def abort(self):
        """Immediately aborts running agent turn cleanly with zero zombies."""
        with self.turn_lock:
            if not self.active_proc:
                self.is_busy = False
                return
            proc = self.active_proc
            self.active_proc = None
            self.is_busy = False

        log_runner(f"Aborting agent process PID {proc.pid}")
        try:
            # Send stop to voice daemon
            subprocess.Popen(["flowork-say", "--stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        try:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGTERM)
            time.sleep(0.08)
            if proc.poll() is None:
                os.killpg(pgid, signal.SIGKILL)
        except Exception as e:
            try:
                proc.kill()
            except Exception:
                pass
        log_runner("Agent process terminated cleanly")

    def run_prompt_async(self, prompt: str, session_id: str = None, workspace: str = None, new_session: bool = False, attachment: dict = None):
        """Starts agent turn in a background worker thread or queues it if busy."""
        with self.turn_lock:
            if self.is_busy:
                log_runner(f"Runner is BUSY with turn #{self.active_turn_id}: enqueuing prompt.")
                return self.enqueue(prompt, session_id, workspace, new_session, attachment)

        t = threading.Thread(
            target=self._execute_turn,
            args=(prompt, session_id, workspace, new_session, attachment),
            daemon=True
        )
        t.start()
        return t

    def _execute_turn(self, prompt: str, session_id: str = None, workspace: str = None, new_session: bool = False, attachment: dict = None):
        if not prompt or not prompt.strip():
            if not attachment:
                return
            prompt = "Inspect the attached file."

        with self.turn_lock:
            self.active_turn_id += 1
            my_turn_id = self.active_turn_id
            self.is_busy = True

        if new_session:
            self.current_session_id = None
        elif session_id:
            self.current_session_id = session_id

        ws = workspace or self.current_workspace or HOME
        if not os.path.isdir(ws):
            ws = HOME
        self.current_workspace = ws

        # Process attachment directive
        if attachment and isinstance(attachment, dict):
            att_path = attachment.get("path")
            kb = attachment.get("size_kb", 0)
            if attachment.get("type") == "image":
                prompt = (
                    f'[User Attached Screenshot: {att_path} ({kb} KB)]\n'
                    f'SYSTEM DIRECTIVE: The user has attached a screenshot at "{att_path}". '
                    f'You MUST execute view_file with AbsolutePath="{att_path}" to visually inspect the image before answering.\n\n'
                    f'User Instruction/Question:\n{prompt}'
                )
            else:
                prompt = (
                    f'[User Attached File: {att_path} ({kb} KB)]\n'
                    f'SYSTEM DIRECTIVE: The user has attached file "{att_path}". Inspect it if relevant.\n\n'
                    f'User Instruction/Question:\n{prompt}'
                )

        log_runner(f"STARTING SOVEREIGN TURN #{my_turn_id}: prompt='{prompt[:60]}...', sess='{self.current_session_id}', ws='{ws}'")

        # 0. Time-Machine Pre-Turn Snapshot (Instant atomic state anchor)
        try:
            tm_bin = "/opt/floworkos/bin/flowork-timemachine"
            if os.path.exists(tm_bin) and ws and os.path.isdir(ws):
                subprocess.Popen(
                    [tm_bin, "snapshot", "-w", ws, "-s", str(self.current_session_id or "default"), "-t", str(my_turn_id), "-p", str(prompt[:80])],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
        except Exception as e:
            log_runner(f"Time-machine snapshot non-fatal notice: {e}")

        # 1. Check Voice Mode Status
        voice_flag = f"/run/user/{os.getuid()}/flowork-voice-mode.enabled"
        voice_mode_on = os.path.exists(voice_flag)
        if voice_mode_on:
            voice_prompt_directive = (
                "\n\n[VOICE MODE ACTIVE — SOVEREIGN DUAL-MODALITY & ZERO-TEXT-REDUNDANCY MANDATE:\n"
                "The user is listening to your answer aloud through speakers.\n"
                "1. TURN-START INTENT: At the start of the turn if you plan to use tools, state your initial intention inside <speech>...</speech> in spoken Indonesian (e.g. <speech>Sebentar saya periksa dulu...</speech>). Intermediate tool calls will execute silently in background to avoid audio clutter.\n"
                "2. FULL FINAL ANSWER: When all tools finish and you conclude the turn (or when no tools are needed), deliver your full, comprehensive conversational response inside <speech>...</speech>. Explain your findings, insights, and recommendations thoroughly in fluent Indonesian.\n"
                "3. ZERO REDUNDANCY IN TEXT: Voice is the primary medium. DO NOT rewrite, summarize, or mirror spoken explanations in markdown text outside <speech>. NEVER generate unprompted tables, lists, or visual cards. Text area is reserved STRICTLY for raw code snippets, diffs, or terminal commands explicitly requested by the user. If the user did not ask for code or command execution, leave the text area 100% EMPTY.]"
            )
            prompt_to_run = prompt + voice_prompt_directive
        else:
            prompt_to_run = prompt

        # 2. Build mrflow CLI Command
        cmd = ["/usr/local/bin/mrflow", "-p", prompt_to_run, "-o", "stream-json"]
        if self.current_session_id:
            cmd.extend(["--resume", self.current_session_id])

        # Whitelist extra directories
        screenshots_dir = os.path.join(HOME, "Pictures", "Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        artifacts_dir = "/opt/floworkos/documents/artifacts"
        os.makedirs(artifacts_dir, exist_ok=True)
        for extra_dir in [screenshots_dir, "/opt/floworkos/screenshots", artifacts_dir, "/tmp"]:
            if os.path.isdir(extra_dir):
                cmd.extend(["--include-directories", extra_dir])

        # 3. Prepare Environment
        env = dict(os.environ)
        env["TERM"] = "xterm-256color"
        env["HOME"] = HOME
        mrflow_env_path = "/opt/floworkos/system/mrflow.env"
        if os.path.exists(mrflow_env_path):
            try:
                with open(mrflow_env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("export "):
                            k, _, v = line[7:].partition("=")
                            env[k.strip()] = v.strip(' "\'')
            except Exception as e:
                log_runner(f"Failed to load mrflow.env: {e}")
        env.setdefault("FLOWORK_CONNECTOR_URL", "http://127.0.0.1:9099")
        env.setdefault("GOOGLE_GEMINI_BASE_URL", "http://127.0.0.1:9099")
        env.setdefault("FLOWORK_API_KEY", "flowork-sovereign-token")
        env.setdefault("GEMINI_API_KEY", "flowork-sovereign-token")

        # 4. Spawn Subprocess
        proc = None
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=ws,
                env=env,
                start_new_session=True
            )
            with self.turn_lock:
                self.active_proc = proc

            self.event_callback("turn_start", {"turn_id": my_turn_id, "prompt": prompt})

            stderr_lines = []
            last_activity = [time.time()]
            INFERENCE_TIMEOUT = 360.0

            def _drain_stderr(pipe):
                try:
                    for err_l in iter(pipe.readline, ''):
                        err_str = err_l.strip()
                        if err_str:
                            last_activity[0] = time.time()
                            log_runner(f"STDERR: {err_str}")
                            stderr_lines.append(err_str)
                            self.event_callback("stderr", {"text": err_str})
                except Exception:
                    pass
                finally:
                    try:
                        pipe.close()
                    except Exception:
                        pass

            err_thread = threading.Thread(target=_drain_stderr, args=(proc.stderr,), daemon=True)
            err_thread.start()

            sel = selectors.DefaultSelector()
            sel.register(proc.stdout, selectors.EVENT_READ)

            # Voice synthesis streaming buffer state
            in_speech_tag = False
            speech_tag_detected = False
            speech_tag_used_in_turn = False
            speech_stream_buffer = ""
            first_voice_chunk_dispatched = False
            auto_voice_direct_mode = False
            content_since_last_speech = 0
            tool_voice_count = [0]

            def dispatch_voice_stream(text_to_speak: str, reset: bool = False):
                def _voice_worker():
                    try:
                        payload = json.dumps({"text": text_to_speak, "reset": reset}).encode("utf-8")
                        req = urllib.request.Request(
                            "http://127.0.0.1:8998/stream/push",
                            data=payload,
                            headers={"Content-Type": "application/json"}
                        )
                        with urllib.request.urlopen(req, timeout=4) as resp:
                            pass
                    except Exception as ex:
                        log_runner(f"Voice stream push error: {ex}")
                threading.Thread(target=_voice_worker, daemon=True).start()

            def vocalize_tool_use(event):
                nonlocal first_voice_chunk_dispatched
                nonlocal in_speech_tag, speech_tag_detected, auto_voice_direct_mode, content_since_last_speech, speech_stream_buffer
                if not voice_mode_on:
                    return

                try:
                    tool_voice_count[0] += 1

                    # Flush pending pre-tool model intent
                    pending_model_text = speech_stream_buffer.strip()
                    in_speech_tag = False
                    speech_tag_detected = False
                    auto_voice_direct_mode = False
                    content_since_last_speech = 0
                    speech_stream_buffer = ""

                    if pending_model_text:
                        sents, rem = extract_sentences_streaming(pending_model_text, is_final=True)
                        for s in sents:
                            if len(s) >= 3:
                                r_reset = not first_voice_chunk_dispatched
                                first_voice_chunk_dispatched = True
                                log_runner(f"VOICE PRE-TOOL INTENT: '{s}'")
                                dispatch_voice_stream(s, reset=r_reset)
                        if rem.strip():
                            clean_rem = sanitize_clause(rem)
                            if len(clean_rem) >= 3:
                                r_reset = not first_voice_chunk_dispatched
                                first_voice_chunk_dispatched = True
                                log_runner(f"VOICE PRE-TOOL INTENT (REM): '{clean_rem}'")
                                dispatch_voice_stream(clean_rem, reset=r_reset)

                    # Only vocalize Tool #1 at the START of turn. Intermediate tools execute silently.
                    if tool_voice_count[0] > 1 or first_voice_chunk_dispatched:
                        log_runner(f"TOOL #{tool_voice_count[0]} vocalization muted (silent background run)")
                        return

                    tool_name = (event.get("tool_name") or event.get("tool") or "").lower()
                    params = event.get("parameters") or event.get("args") or {}

                    voice_intent = params.get("voice_intent") or params.get("reason_voice") or params.get("reason")
                    if voice_intent and isinstance(voice_intent, str) and len(voice_intent.strip()) > 3:
                        spoken = voice_intent.strip()
                    else:
                        action = params.get("toolAction") or params.get("toolSummary") or ""
                        action_lower = action.lower() if isinstance(action, str) else ""

                        if tool_name in ("search_web", "read_url_content") or "web" in action_lower or "brows" in action_lower:
                            spoken = "Gua cari referensi di web dulu ya bro..."
                        elif "test" in action_lower:
                            spoken = "Gua lagi jalankan pengujian sistem dulu ya bro..."
                        elif "git" in action_lower or "commit" in action_lower:
                            spoken = "Gua cek status dan sinkronisasi git dulu bro..."
                        elif "search" in action_lower or "analyz" in action_lower:
                            spoken = "Gua telusuri berkas kodenya dulu..."
                        elif "view" in action_lower or "read" in action_lower:
                            fname = os.path.basename(params.get("AbsolutePath") or params.get("TargetFile") or params.get("file_path") or "")
                            spoken = f"Gua periksa berkas {fname} dulu bro..." if fname else "Gua baca berkas kodenya dulu..."
                        elif "write" in action_lower or "edit" in action_lower or "replac" in action_lower:
                            fname = os.path.basename(params.get("TargetFile") or params.get("target") or "")
                            spoken = f"Gua simpan perubahan ke berkas {fname}..." if fname else "Gua perbarui kodenya dulu..."
                        elif "upload" in action_lower or "push" in action_lower:
                            spoken = "Gua upload pembaruan ke repositori sistem ya bro..."
                        elif tool_name in ("run_command", "bash"):
                            cmd_str = (params.get("CommandLine") or params.get("command") or "").lower()
                            if "git" in cmd_str:
                                spoken = "Gua jalankan sinkronisasi git dulu..."
                            elif "systemctl" in cmd_str:
                                spoken = "Gua kelola layanan sistem dulu bro..."
                            elif "python" in cmd_str or "cargo" in cmd_str:
                                spoken = "Gua jalankan proses eksekusi kode dulu..."
                            else:
                                spoken = "Gua jalankan perintah terminal-nya dulu bro..."
                        else:
                            spoken = f"Gua jalankan {tool_name} dulu bro..."

                    clean = sanitize_clause(spoken)
                    if len(clean) >= 3:
                        first_voice_chunk_dispatched = True
                        log_runner(f"VOICE PRE-TOOL INTENT #{tool_voice_count[0]}: '{clean}'")
                        dispatch_voice_stream(clean, reset=True)
                except Exception as e:
                    log_runner(f"Error in vocalize_tool_use: {e}")

            def process_voice_delta(delta: str):
                nonlocal in_speech_tag, speech_tag_detected, speech_tag_used_in_turn
                nonlocal speech_stream_buffer, first_voice_chunk_dispatched
                nonlocal auto_voice_direct_mode, content_since_last_speech

                if not voice_mode_on:
                    return

                speech_stream_buffer += delta
                content_since_last_speech += len(delta)

                if not in_speech_tag:
                    lower_buf = speech_stream_buffer.lower()
                    if "<speech>" in lower_buf:
                        in_speech_tag = True
                        speech_tag_detected = True
                        speech_tag_used_in_turn = True
                        auto_voice_direct_mode = False
                        idx = lower_buf.find("<speech>") + len("<speech>")
                        speech_stream_buffer = speech_stream_buffer[idx:]
                        content_since_last_speech = 0
                    elif not speech_tag_used_in_turn and content_since_last_speech >= 30:
                        trimmed = speech_stream_buffer.lstrip()
                        if not (trimmed.startswith("#") or trimmed.startswith("|") or trimmed.startswith("```") or trimmed.startswith("---")):
                            auto_voice_direct_mode = True
                            in_speech_tag = True
                    elif speech_tag_used_in_turn:
                        last_angle = speech_stream_buffer.rfind('<')
                        if last_angle != -1:
                            speech_stream_buffer = speech_stream_buffer[last_angle:]
                        else:
                            speech_stream_buffer = ""

                if in_speech_tag:
                    lower_buf = speech_stream_buffer.lower()
                    if not auto_voice_direct_mode and "</speech>" in lower_buf:
                        idx = lower_buf.find("</speech>")
                        inside_speech = speech_stream_buffer[:idx]

                        tail = speech_stream_buffer[idx + len("</speech>"):]
                        last_angle = tail.rfind('<')
                        speech_stream_buffer = tail[last_angle:] if last_angle != -1 else ""

                        in_speech_tag = False
                        auto_voice_direct_mode = False
                        content_since_last_speech = 0

                        sents, rem = extract_sentences_streaming(inside_speech, is_final=True)
                        for s in sents:
                            if len(s) >= 3:
                                r_reset = not first_voice_chunk_dispatched
                                first_voice_chunk_dispatched = True
                                log_runner(f"VOICE CLAUSE (FINAL): '{s}'")
                                dispatch_voice_stream(s, reset=r_reset)
                        if rem.strip():
                            clean = sanitize_clause(rem)
                            if len(clean) >= 3:
                                r_reset = not first_voice_chunk_dispatched
                                first_voice_chunk_dispatched = True
                                log_runner(f"VOICE CLAUSE (FINAL REM): '{clean}'")
                                dispatch_voice_stream(clean, reset=r_reset)
                    else:
                        sents, speech_stream_buffer = extract_sentences_streaming(speech_stream_buffer, is_final=False)
                        for s in sents:
                            if len(s) >= 3:
                                r_reset = not first_voice_chunk_dispatched
                                first_voice_chunk_dispatched = True
                                log_runner(f"VOICE CLAUSE (STREAM): '{s}'")
                                dispatch_voice_stream(s, reset=r_reset)

            # 5. Main Stream Reading Loop
            full_text_accum = ""
            while True:
                if proc.poll() is not None:
                    # Drain remaining lines
                    for line in iter(proc.stdout.readline, ''):
                        trimmed = line.strip()
                        if trimmed and trimmed.startswith("{") and trimmed.endswith("}"):
                            try:
                                ev = json.loads(trimmed)
                                ev_type = ev.get("type")
                                if ev_type == "init":
                                    self.current_session_id = ev.get("session_id")
                                    self.event_callback("init", {"session_id": self.current_session_id})
                                elif ev_type in ("content", "message"):
                                    c_txt = ev.get("content") or ev.get("text") or ""
                                    if c_txt:
                                        full_text_accum += c_txt
                                        process_voice_delta(c_txt)
                                        self.event_callback("content", {"text": c_txt, "full": full_text_accum})
                                elif ev_type == "tool_use":
                                    vocalize_tool_use(ev)
                                    self.event_callback("tool_use", ev)
                                elif ev_type == "tool_result":
                                    self.event_callback("tool_result", ev)
                                elif ev_type in ("result", "done"):
                                    c_txt = ev.get("result") or ev.get("summary") or ev.get("text") or ""
                                    if c_txt:
                                        full_text_accum += c_txt
                                    self.event_callback("done", {"summary": c_txt, "full": full_text_accum})
                            except Exception:
                                pass
                    break

                events = sel.select(timeout=0.3)
                if events:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    last_activity[0] = time.time()
                    trimmed = line.strip()
                    if trimmed and trimmed.startswith("{") and trimmed.endswith("}"):
                        try:
                            ev = json.loads(trimmed)
                            ev_type = ev.get("type")
                            if ev_type == "init":
                                self.current_session_id = ev.get("session_id")
                                log_runner(f"SESSION INITIALIZED: {self.current_session_id}")
                                self.event_callback("init", {"session_id": self.current_session_id})
                            elif ev_type in ("content", "message"):
                                c_txt = ev.get("content") or ev.get("text") or ""
                                if c_txt:
                                    full_text_accum += c_txt
                                    process_voice_delta(c_txt)
                                    self.event_callback("content", {"text": c_txt, "full": full_text_accum})
                            elif ev_type == "thought":
                                th_txt = ev.get("thought") or ev.get("text") or ""
                                if th_txt:
                                    self.event_callback("thought", {"text": th_txt})
                            elif ev_type == "tool_use":
                                vocalize_tool_use(ev)
                                self.event_callback("tool_use", ev)
                            elif ev_type == "tool_result":
                                self.event_callback("tool_result", ev)
                            elif ev_type in ("result", "done"):
                                c_txt = ev.get("result") or ev.get("summary") or ev.get("text") or ""
                                if c_txt:
                                    full_text_accum += c_txt
                                self.event_callback("done", {"summary": c_txt, "full": full_text_accum})
                                break
                            elif ev_type == "error":
                                err_msg = ev.get("message") or ev.get("error") or "Unknown engine error"
                                self.event_callback("error", {"message": err_msg})
                                break
                        except Exception as e:
                            log_runner(f"Failed to parse NDJSON line: {e}")

                # Watchdog check
                if time.time() - last_activity[0] > INFERENCE_TIMEOUT:
                    log_runner(f"INFERENCE TIMEOUT EXCEEDED ({INFERENCE_TIMEOUT}s): aborting stalled turn")
                    self.abort()
                    self.event_callback("error", {"message": f"Turn timed out after {INFERENCE_TIMEOUT}s"})
                    break

            proc.wait(timeout=2.0)
            exit_code = proc.returncode or 0
            log_runner(f"Turn #{my_turn_id} completed with exit code {exit_code}")

            # Flush any remaining voice stream
            if voice_mode_on and speech_stream_buffer.strip():
                clean_tail = sanitize_clause(speech_stream_buffer)
                if len(clean_tail) >= 3:
                    dispatch_voice_stream(clean_tail, reset=not first_voice_chunk_dispatched)

            self.event_callback("turn_finish", {
                "turn_id": my_turn_id,
                "exit_code": exit_code,
                "full_text": full_text_accum
            })

        except Exception as ex:
            log_runner(f"Exception during turn #{my_turn_id}: {ex}")
            self.event_callback("error", {"message": str(ex)})
        finally:
            with self.turn_lock:
                if self.active_proc == proc:
                    self.active_proc = None
                self.is_busy = False

            # Reactive auto-dequeue: automatically resume execution with next queued message
            next_turn = None
            with self.queue_lock:
                if self.message_queue:
                    next_turn = self.message_queue.pop(0)

            if next_turn:
                self.event_callback("queue_updated", {"queue": list(self.message_queue), "count": len(self.message_queue)})
                log_runner(f"REACTIVE AUTO-DEQUEUE: Launching queued prompt #{next_turn['id']}: '{next_turn['display_text']}'")
                self.run_prompt_async(
                    prompt=next_turn["prompt"],
                    session_id=next_turn.get("session_id") or self.current_session_id,
                    workspace=next_turn.get("workspace") or self.current_workspace,
                    new_session=next_turn.get("new_session", False),
                    attachment=next_turn.get("attachment")
                )
            else:
                self.event_callback("idle", {})
