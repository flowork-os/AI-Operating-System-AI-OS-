---
name: craft-anything-headless
description: Unified headless reverse engineering and clean-room application cloning workflow powered by craft-anything-cli (321+ tools, Ghidra, Binwalk, ADB, Web/JS, and MCP).
domain: security
keywords:
  - craft_anything
  - headless_engine
  - reverse_engineering
  - clean_room
  - app_cloning
  - binary_analysis
  - ghidra_decompile
  - apk_decompilation
  - electron_asar
  - firmware_unpack
  - web_reconstruction
  - game_assets
  - symbol_extraction
  - strings_triage
  - rebuild_pipeline
  - mcp_server
  - report_generation
  - architecture_blueprint
  - flowork_os
  - security_audit
---

# Craft Anything Headless — Unified Reverse Engineering & Clean-Room Cloning Engine

## 1. Executive Summary & Objective
This skill establishes the canonical headless workflow for Flowork OS using `/opt/floworkos/bin/craft-anything-cli` (321+ tools across 16 toolsets) as the primary sovereign engine for binary triage, multi-platform reverse engineering, and clean-room application cloning. It eliminates standalone GUI dependencies and unifies static analysis, dynamic inspection, architectural specification, and clean-room reconstruction into a single deterministic CLI and MCP pipeline.

## 2. Prerequisites & Environment
- **Headless Engine Binary:** `/opt/floworkos/bin/craft-anything-cli` (symlinked at `/usr/local/bin/craft-anything-cli`).
- **License & Attribution Archive:** `/opt/floworkos/share/doc/craft-anything/` (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`).
- **Installed Analysis Engines:** Verify via `craft-anything-cli doctor` (Ghidra headless at `~/.config/craft-anything/engines/ghidra/`, `binwalk`, `tshark`, `objdump`, `adb`, `chromium`, `java`).
- **Output Territory:** All generated reports, architectural blueprints, and clean-room dossiers MUST be written to `/opt/floworkos/documents/` (or a dedicated project workspace directory).

## 3. Standard Operating Procedure (SOP)

### Phase 1: Engine Health & Target Triage
1. Verify engine readiness and available backends:
   ```bash
   craft-anything-cli doctor
   craft-anything-cli capabilities --output-format json
   ```
2. Choose the analysis mode explicitly:
   - `--clean-room`: Black-box mode (never reads inside target code, files, or page source; used for clean-room `rebuild` from external behavior/URLs).
   - `--deep`: Deep inspection mode (required for `core-target-open`, binary/APK/ASAR/firmware inspection, and `report` generation).
3. Open the target (ELF/PE/Mach-O binary, APK, Electron `.asar`, firmware image, or folder) and inspect baseline evidence:
   ```bash
   craft-anything-cli --deep --output-format json core-target-open --path /abs/path/to/target
   craft-anything-cli --deep --output-format json core-session-show
   craft-anything-cli --deep --output-format json core-evidence-show
   ```

### Phase 2: Domain-Specific Deep Inspection
Select the appropriate toolset based on target classification (use `--deep` only when authorized to inspect internal code/source):
- **Native Binaries (ELF / PE / Mach-O / Go):**
  - `native-sections-list`, `native-functions-list`, `native-functions-search`, `native-strings-browse`, `native-strings-find`, `native-xrefs-list`, `native-go-binary-show`, `native-pe-resources-list`.
  - Apple Mach-O targets: `apple-macho-show`, `apple-objc-classes-list`, `apple-swift-types-list`, `apple-plist-show`.
- **Web Apps, Electron & JavaScript Bundles:**
  - `js-app-map`, `js-electron-pages-list`, `js-electron-fuses-show`, `js-sources-restore`, `js-function-explain`.
  - Live web capture & state mapping: `web-site-open`, `web-site-capture`, `web-page-states-capture`, `web-scripts-save`, `web-site-close`.
- **Android APKs & Live Devices:**
  - Static APK inspection: `android-package-show`, `android-classes-find`, `android-class-show`, `android-components-list`, `android-resources-read`.
  - Live ADB inspection: `adb-devices-find`, `adb-apps-list`, `adb-app-show`, `adb-running-processes-list`, `adb-log-read`.
- **Firmware, Archives, Managed (.NET/Java) & Game Assets:**
  - Firmware & packed files: `firmware-regions-list`, `firmware-image-extract`, `core-packed-files-list`, `core-packed-files-unpack`, `core-archive-show`.
  - Managed / JVM / WASM: `managed-assembly-show`, `managed-ilspy-decompile`, `java-archive-show`, `java-vineflower-decompile`, `formats-wasm-module-show`.
  - Game engines: `game-archives-list`.
- **Dynamic Runtime & Instrumentation:**
  - `runtime-walkthrough-record`, `runtime-ui-read`, `frida-devices-find`, `frida-session-begin`, `native-gdb-session-begin`.

### Phase 3: Clean-Room Specification & Report Generation
1. Track findings and unknowns inside a persistent project file (`*.cany`) or export structured evidence:
   ```bash
   craft-anything-cli --output-format json core-evidence-export
   ```
2. Generate a human-readable Markdown or HTML investigation dossier in `/opt/floworkos/documents/`:
   ```bash
   craft-anything-cli --deep report --out /opt/floworkos/documents/target_dossier.md /abs/path/to/target
   craft-anything-cli --deep report --html --out /opt/floworkos/documents/target_dossier.html /abs/path/to/target
   ```
3. For clean-room cloning, extract ONLY functional specifications, state machines, API contracts, and design tokens (`app-feature-follow`, `app-ledger-build`, `app-coverage-evaluate`).

### Phase 4: Clean-Room Cloning & Rebuild Pipeline
1. Execute clean-room architectural reconstruction using `rebuild` or Flowork OS native synthesis:
   ```bash
   craft-anything-cli rebuild <TARGET_URL_OR_PATH> "<CLEAN_ROOM_SPEC_REQUEST>"
   ```
2. Inspect and verify generated project artifacts via `project-list`, `project-show`, `build-files-list`, `build-checklist`, and `build-command-run`.
3. Enforce Flowork OS Solid Sovereign Obsidian UI (`#0b111a` shell, `#111a26` panel, `#162232` pill, `#070c12` console, 100% opaque surfaces) for any newly synthesized desktop/web UI.
4. Perform a mandatory brand and asset sweep to ensure zero third-party trademarks, logos, or copyrighted strings remain in the cloned output.

### Phase 5: Headless MCP Server Integration
When integrating directly with an MCP-capable agent loop over stdio:
```bash
craft-anything-cli mcp
```

## 4. Verification & Quality Gates
- `craft-anything-cli doctor` returns `"healthy": true` with Exit Code `0`.
- Every CLI invocation uses `--output-format json` (before the tool subcommand) when parsed programmatically, returning valid JSON with Exit Code `0`.
- Generated reports exist in `/opt/floworkos/documents/` and are non-empty.
- Cloned/rebuilt projects pass `build-checklist` and `build-command-run` (tests/linters/build) with Exit Code `0` and zero proprietary brand leakage.

## 5. Failure Modes & Recovery
- **Missing Optional Engine (`jadx`, `apktool`, `frida`, `rizin`):**
  - *Recovery:* Run `craft-anything-cli engines-list` and `craft-anything-cli engines-install <engine_id>`, or fall back to available engines (`ghidra`, `binwalk`, `objdump`, `tshark`, `adb`).
- **Flag Collision (`--format` vs `--output-format`):**
  - *Recovery:* Always pass `--output-format json` BEFORE the tool subcommand name because tools like `core-target-open` define their own `--format` flag.
- **Clean-Room Policy Block on Source Read:**
  - *Recovery:* Verify whether deep inspection is authorized; if authorized for local audit, pass `--deep` explicitly for that single run without altering global clean-room defaults.

## 6. Prohibitions & Anti-Patterns
- **PROHIBITED** to copy proprietary source code, copyrighted assets, logos, or trademarks verbatim during clean-room cloning.
- **PROHIBITED** to reinstall standalone GUI wrappers or `.desktop` launchers for `craft-anything` inside `/opt/floworkos/apps/`.
- **PROHIBITED** to modify or patch the original target binary in-place during static triage.
- **PROHIBITED** to omit `--output-format json` when chaining CLI outputs into automated scripts.
