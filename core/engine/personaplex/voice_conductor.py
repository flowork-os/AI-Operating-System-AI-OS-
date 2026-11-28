#!/usr/bin/env python3
"""
👑 FLOWORK OS — PERSONAPLEX DUPLEX VOICE CONDUCTOR
Author: Dr. Flow (System Architect) & Flowork Architecture Board
Universal Root: /opt/floworkos

Full-duplex conversational voice conductor:
- Real-time energy VAD microphone capture
- Sub-5ms instant speech barge-in (/barge_in on port 8998)
- Blazing-fast faster-whisper (tiny int8) local offline transcription
- Live Arc Reactor pulse & acoustic amplitude synchronization
- Seamless conduit prompt injection over UNIX domain socket
"""

import os
import sys
import time
import json
import socket
import struct
import signal
import argparse
import subprocess
import urllib.request
import urllib.error
import numpy as np

DAEMON_URL = "http://127.0.0.1:8998"
USER = os.environ.get("USER", os.path.basename(os.path.expanduser("~")))
CONDUIT_SOCK = f"/tmp/flowork-neural-conduit-{USER}.sock"
WHISPER_MODEL_DIR = "/opt/floworkos/runtime/models/whisper-tiny"

# Neural bridge integration for pure crystal glass Arc Reactor HUD
try:
    if "/opt/floworkos/theme" not in sys.path:
        sys.path.insert(0, "/opt/floworkos/theme")
    import flowork_neural_bridge
except Exception:
    flowork_neural_bridge = None


def barge_in():
    """Immediately stop speech playback across voice daemon and audio processes."""
    success = False
    try:
        req = urllib.request.Request(
            f"{DAEMON_URL}/barge_in",
            data=b"{}",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=0.6) as resp:
            success = resp.status == 200
    except Exception:
        pass

    # Terminate orphan audio players if any
    try:
        subprocess.run(["pkill", "-f", "flowork_say_edge.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    return success


def send_to_conduit(prompt_text):
    """Inject transcribed prompt into Neural Conduit active turn queue."""
    if not prompt_text or not prompt_text.strip():
        return False
    if not os.path.exists(CONDUIT_SOCK):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(CONDUIT_SOCK)
        payload = json.dumps({"action": "send_prompt", "prompt": prompt_text.strip()}).encode("utf-8")
        s.sendall(payload)
        resp = s.recv(128)
        s.close()
        return True
    except Exception as e:
        print(f"[Conduit IPC Error]: {e}", file=sys.stderr)
        return False


_cached_model = None

def get_whisper_model():
    global _cached_model
    if _cached_model is None:
        from faster_whisper import WhisperModel
        _cached_model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8",
            download_root=WHISPER_MODEL_DIR
        )
    return _cached_model


def transcribe_pcm(pcm_bytes, language=None):
    """Transcribe raw 16kHz 16-bit mono PCM bytes to text."""
    if not pcm_bytes or len(pcm_bytes) < 3200:  # Less than 0.1s
        return "", ""

    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    model = get_whisper_model()
    segments, info = model.transcribe(audio, beam_size=1, language=language)
    full_text = " ".join(s.text for s in segments).strip()
    return full_text, info.language


def calculate_rms(chunk):
    """Calculate Root Mean Square (RMS) energy level of 16-bit PCM chunk."""
    count = len(chunk) // 2
    if count == 0:
        return 0.0
    shorts = struct.unpack(f"{count}h", chunk)
    sum_sq = sum(s * s for s in shorts)
    return (sum_sq / count) ** 0.5


def record_interactive(max_sec=15.0, silence_timeout=1.6, energy_threshold=320.0, target_lang=None):
    """
    Full-duplex recording with energy VAD and live Arc Reactor HUD synchronization:
    1. Triggers instant barge-in to silence Mr. Flow.
    2. Streams microphone input via parecord.
    3. Detects speech onset and trailing silence.
    4. Transcribes speech via offline faster-whisper tiny.
    """
    # 1. Trigger instant barge-in to silence speaker
    barge_in()

    # 2. Update HUD to listening state
    if flowork_neural_bridge:
        try:
            flowork_neural_bridge.set_neural_state(
                "listening",
                morphology="morph-listening",
                amplitude=0.3,
                action="Mendengarkan instruksi suara...",
                status="running"
            )
        except Exception:
            pass

    # 3. Start parecord subprocess (16000 Hz, 1 channel, 16-bit s16le PCM)
    cmd = ["parecord", "--channels=1", "--rate=16000", "--format=s16le"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error launching parecord: {e}", file=sys.stderr)
        return ""

    chunk_size = 3200  # 100ms of audio (1600 samples * 2 bytes)
    collected_frames = []
    speaking_started = False
    silence_frames = 0
    max_silence_frames = int(silence_timeout * 10)  # 10 chunks per second
    max_total_chunks = int(max_sec * 10)
    total_chunks = 0

    t_start = time.time()
    try:
        while total_chunks < max_total_chunks:
            chunk = proc.stdout.read(chunk_size)
            if not chunk or len(chunk) < chunk_size:
                break

            total_chunks += 1
            collected_frames.append(chunk)

            rms = calculate_rms(chunk)
            # Normalize amplitude for Arc Reactor visualizer (0.0 to 1.0)
            vis_amp = min(1.0, max(0.1, rms / 1200.0))

            if rms > energy_threshold:
                if not speaking_started:
                    speaking_started = True
                    # Re-trigger barge-in to ensure absolute silence
                    barge_in()
                silence_frames = 0
                if flowork_neural_bridge:
                    try:
                        flowork_neural_bridge.set_neural_state(
                            "listening",
                            morphology="morph-listening",
                            amplitude=vis_amp,
                            action="Mendengarkan suara...",
                            status="running"
                        )
                    except Exception:
                        pass
            else:
                if speaking_started:
                    silence_frames += 1
                    if silence_frames >= max_silence_frames:
                        # User has finished speaking!
                        break
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=0.5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    all_pcm = b"".join(collected_frames)

    # 4. Transcribe
    if flowork_neural_bridge:
        try:
            flowork_neural_bridge.set_neural_state(
                "thinking",
                morphology="morph-thinking",
                amplitude=0.5,
                action="Mentranskripsikan ucapan...",
                status="running"
            )
        except Exception:
            pass

    text, detected_lang = transcribe_pcm(all_pcm, language=target_lang)

    # Reset HUD state
    if flowork_neural_bridge:
        try:
            flowork_neural_bridge.set_neural_state("idle", morphology="morph-idle", amplitude=0.0)
        except Exception:
            pass

    return text


def main():
    parser = argparse.ArgumentParser(description="Flowork Duplex Voice Conductor")
    subparsers = parser.add_subparsers(dest="command")

    # barge-in command
    subparsers.add_parser("barge-in", help="Instantly mute voice daemon playback")

    # listen command
    p_listen = subparsers.add_parser("listen", help="Interactive full-duplex speech capture")
    p_listen.add_argument("-m", "--max-sec", type=float, default=15.0, help="Maximum recording duration")
    p_listen.add_argument("-s", "--silence-sec", type=float, default=1.6, help="Trailing silence timeout")
    p_listen.add_argument("-t", "--threshold", type=float, default=320.0, help="Energy RMS VAD threshold")
    p_listen.add_argument("-l", "--lang", default=None, help="Target language code (e.g. id, en)")
    p_listen.add_argument("--send-conduit", action="store_true", help="Automatically inject text into Neural Conduit")

    # transcribe command
    p_trans = subparsers.add_parser("transcribe", help="Transcribe existing WAV file")
    p_trans.add_argument("wav_file", help="Path to WAV audio file")
    p_trans.add_argument("-l", "--lang", default=None, help="Language code")

    args = parser.parse_args()

    if args.command == "barge-in":
        res = barge_in()
        print(f"Barge-in dispatched: {res}")
        sys.exit(0 if res else 1)

    elif args.command == "listen":
        print("🎤 [Duplex Voice Conductor]: Listening for voice input...", file=sys.stderr)
        text = record_interactive(
            max_sec=args.max_sec,
            silence_timeout=args.silence_sec,
            energy_threshold=args.threshold,
            target_lang=args.lang
        )
        if text:
            print(f"✓ Transcribed: {text}")
            if args.send_conduit:
                ok = send_to_conduit(text)
                print(f"  Sent to Neural Conduit: {ok}", file=sys.stderr)
        else:
            print("No speech detected.", file=sys.stderr)
        sys.exit(0)

    elif args.command == "transcribe":
        if not os.path.exists(args.wav_file):
            print(f"File not found: {args.wav_file}", file=sys.stderr)
            sys.exit(1)
        model = get_whisper_model()
        segments, info = model.transcribe(args.wav_file, beam_size=1, language=args.lang)
        full_text = " ".join(s.text for s in segments).strip()
        print(full_text)
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
