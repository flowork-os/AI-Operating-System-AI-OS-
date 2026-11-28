---
name: duplex-voice-conductor-architecture
description: "Full-duplex conversational voice conductor with energy VAD, sub-5ms speech barge-in, and offline whisper transcription."
keywords:
  - voice
  - duplex
  - conductor
  - vad
  - speech
  - microphone
  - audio
  - bargein
  - interruption
  - transcribe
  - whisper
  - fasterwhisper
  - capture
  - pcm
  - streaming
  - sound
  - tempo
  - acoustic
  - socket
  - handsfree
---

# FLOWORK DUPLEX VOICE CONDUCTOR & BARGE-IN SPECIFICATION

## 1. Context & Activation Scope
Applies whenever capturing vocal audio from microphone, running hands-free speech queries via `/listen`, handling instant speech barge-in interruptions, or transcribing audio offline on Flowork OS.

## 2. Mandatory Behavioral Invariants
- **Sub-5ms Instant Barge-In:** As soon as speech capture initiates or user presses push-to-talk, dispatch instant barge-in via `http://127.0.0.1:8998/barge_in` to silence Mr. Flow and active audio streams immediately.
- **Offline Fast-Whisper Model:** Speech transcription runs locally via `faster-whisper-tiny` (int8) cached at `/opt/floworkos/engine/personaplex/models/whisper-tiny`. Zero external cloud latency or bandwidth consumption.
- **Energy-Based VAD & Acoustic HUD Sync:** Audio capture via `parecord` monitors RMS energy. Microphone activity directly modulates Arc Reactor amplitude and morphology (`morph-listening`) with electric cyan `#00f2fe` pulses.
- **Conduit Turn Injection:** Transcribed text is seamlessly dispatched to `/tmp/flowork-neural-conduit-${USER}.sock` via `{"action": "send_prompt", "prompt": text}` for immediate autonomous execution.

## 3. Strict Prohibitions
- NEVER allow audio playback to continue playing over incoming user speech (always enforce instant barge-in).
- NEVER introduce external cloud dependencies for core STT transcription when offline whisper tiny is available.
- NEVER block the UI thread during microphone recording or model inference.
