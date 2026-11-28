# FLOWORK LIVE STAGE ISOLATED BROWSER

## 1. Context & Activation Scope
Activated whenever Mr. Flow opens websites, automates web apps (such as Suno, YouTube, or social platforms), handles user logins, or invokes `agent_browser` and CDP automation.

## 2. Mandatory Behavioral Invariants
- **Default to Isolated Stage Browser:** Always use Flowork Live Stage (`flowork-stage`) running on isolated Xvfb display `:99` with Chrome CDP port `9299` instead of launching or hijacking the user's regular desktop Chrome.
- **Startup & Connection Sequence:** Check `flowork-stage status`. If not running, start it via `flowork-stage start --with-browser`. Connect `agent_browser` to `http://127.0.0.1:9299` before opening URLs or taking snapshots.
- **Persistent Login Profile:** `flowork-stage` stores its Chrome user data in `$HOME/.config/flowork-stage-chrome` (never `/tmp` or `/dev/shm`) so cookies, Google/Suno sessions, and logins survive PC restarts.
- **Human-in-the-Loop Login:** When a site requires manual login or 2FA, open the target URL in `flowork-stage` (`:99`), ensure the Live Stage viewer is visible to the user, and wait for confirmation before resuming automation.

## 3. Strict Prohibitions
- NEVER launch regular `google-chrome` on display `:0` for AI web automation when `flowork-stage` is available.
- NEVER store `flowork-stage` Chrome profiles in volatile `/tmp` or `/dev/shm` directories.
- NEVER use `browser_new_page` or `browser_navigate_page` on the user's personal browser session when isolated automation is requested.
