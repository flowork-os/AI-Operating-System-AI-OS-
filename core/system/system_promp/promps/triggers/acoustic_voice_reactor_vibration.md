# ACOUSTIC VOICE SYNCHRONIZATION & NATIVE DESKTOP REACTOR DOCTRINE

## 1. Context & Activation Scope
Triggered when designing, modifying, or diagnosing voice synthesis cadence, ambient desktop motion wallpapers, or audio reactive vector visuals (`voice_cadence`, `audio_envelope`, `ambient_wallpaper`, `reactor_vibration`, `speech_tempo`, `retina_vector_core`).

## 2. Mandatory Behavioral Invariants
- **Dual-Surface Decoupled Architecture (Zero Blur & Ultra-Low CPU):**
  - Atmospheric fluid gradients are soft; render on a dynamic 640x270 buffer with static background caching (`surface_static_bg`, 0.08ms render time).
  - High-definition vector arc reactors MUST NOT be rasterized into downscaled buffers or full-screen 4K surfaces. Allocate a dedicated 440x440 1:1 retina surface (`surface_core`, `sc = 2.4`, 0.24ms render time).
  - Blit `surface_core` unscaled at screen center (`cx - 220, cy - 220`) via `OPERATOR_OVER` directly in `on_draw` at 10 FPS (100ms interval, <0.4% total CPU).
- **Sub-harmonic Acoustic Vibration & Tempo Dancing:**
  - During active speech (`state == "speaking"` or `morph == "morph-speech"`), modulate kinetic physics via RMS energy:
    - Micro-tremor vibration: `vibration = (0.04 * sin(t*32) + 0.02 * cos(t*18)) * amp`.
    - Pulse & iris expansion: `pulse = 1.0 + 0.18 * amp + vibration`, `iris_pulse = 1.0 + 0.32 * amp + vibration * 1.5`.
    - Radial VU flaring: flare precision ticks outward proportionally to speech amplitude (`tick_flare = 8.0 * amp`).
    - Multi-layered silk waveforms: 36Hz syllable bounce harmonics undulating across the core.
- **Intelligent HUD & Telemetry State Arbitration:**
  - Empirical Tool HUD is exclusively for tool execution telemetry (`tool_use`, `deliberation`, `status == "running"`). Persists for exactly 8 seconds post-completion to display output and Exit Code 0.
  - When agent speaks (`state == "speaking"`), Tool HUD yields immediately to the pristine vibrating Arc Reactor.
  - Pure conversational turns without tools yield immediately to cognitive flux (fast gyroscopic spin and synaptic inter-node laser web).

## 3. Strict Prohibitions
- NEVER render full-screen 4K Cairo vectors every tick (chokes X11 compositor).
- NEVER stretch low-resolution raster surfaces for vector graphics (causes blurry smudges).
- NEVER obscure voice vibration with lingering or empty tool cards during voice vocalization.
