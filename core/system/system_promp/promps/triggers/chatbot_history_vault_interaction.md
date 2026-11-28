# CHATBOT HISTORY VAULT & TOOL ACCORDION PROTOCOL

## 1. Context & Activation Scope
Applies when rendering Neural Conduit Chat Vault, streaming live telemetry, or displaying conversational sessions.

## 2. Mandatory Behavioral Invariants
- **0ms Instant Vault Load:** Scan compact `transcript.jsonl` instead of full logs. Cache sessions by `(path, mtime, size)` for 0ms opening with zero stutter.
- **Antigravity Parity (Thinking & Tools):** Interleave chain-of-thought (`obj["thinking"]`) and tools chronologically into single-line rows (`🧠 Thought for Xs ›`, `Ran <cmd> [✓ OK] ›`). Use Antigravity action verbs (`Ran`, `Analyzed`, `Edited`, `Searched`).
- **Activity Summary Pills:** Collapse historical turns into sleek summary pills (`Exploring X files, running Y commands ⌵`), keeping user prompt capsules visible.
- **Real-Time Live Indicators:** Stream `obj["thinking"]` and tool execution into inline pulsing rows and the bottom telemetry indicator bar (`⚙️ WORKING: <tool>`).
- **Sequential Prompt Parsing:** Parse `# User Requests` from `CHECKPOINT` via sequential integer regex (`rf"\n{idx}\.\s+"`) with `transcript_full.jsonl` fallback to eliminate summary bleed.
- **Bottom-Anchored Copy:** Anchor copy buttons (`[📋 COPY]`) at the bottom-right footer of message cards.
- **Pure Optical Crystal Glass:** Obsidian glass (`rgba(2, 6, 12, 0.78)`), #00ff66 matrix rims, 28px blur.

## 3. Strict Prohibitions
- Never read megabytes of raw JSONL during UI activation.
- Never let oversized tool blocks push user prompt capsules out of viewport.
- Never use non-English UI text.
