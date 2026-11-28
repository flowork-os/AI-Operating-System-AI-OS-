# CONDUIT FD LEAK PREVENTION & ASYNC TURN DISPATCH MANDATE

## 1. Context & Activation Scope
Applies when modifying, debugging, or extending `flowork-neural-conduit`, GTK text entry widgets, Apport crash hooks, TTS vocalization, or turn conclusion lifecycles.

## 2. Mandatory Behavioral Invariants
- **Strict Exception Hook Hygiene:** Disable Ubuntu Apport crash interception at script initialization (`sys.excepthook = sys.__excepthook__`) to prevent file descriptor leaks to `/proc/<pid>` during unhandled UI exceptions.
- **Complete GTK Entry Interface Contracts:** Any custom subclass of `Gtk.TextView` or `Gtk.Entry` (e.g., `MultiLineNeuralEntry`) MUST implement standard text entry interfaces including `get_position()` and `set_position()` to prevent keystroke exceptions.
- **Asynchronous Audio Vocalization:** External audio playback (`flowork-say`) must execute inside background worker threads (`threading.Thread`) with detached subprocesses (`subprocess.Popen`) so turn conclusions dispatch immediately without blocking UI state or send button transitions.
- **File Descriptor Monitoring:** Verify that open file descriptors remain below 32 during continuous keystrokes and agent response streams.

## 3. Strict Prohibitions
- NEVER allow synchronous blocking audio calls during turn conclusion handlers.
- NEVER leave `MultiLineNeuralEntry` or input widgets without standard GTK cursor position methods.
- NEVER allow unhandled exceptions to spawn orphaned crash handlers leaking file descriptors.
