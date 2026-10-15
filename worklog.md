# Project Worklog

Working name: `recovery-wizard` (codename pending final product naming decision)

Mission: build a state-of-the-art, free and open-source data recovery wizard for Windows
(later macOS), using Rust core + Tauri 2 (WebView2) + React/TypeScript UI. EaseUS Data
Recovery Wizard is studied as a functional reference under a strict clean-room methodology
to understand feature scope, architecture concepts, and behavior. No code, assets, or
decompiled logic is ever transplanted. All implementations are original, built from public
specifications and academic literature.

## Rules for all agents on this project

1. Read `research/docs/01-methodology.md` before doing anything. It is binding.
2. Append every work session to this file. Never delete prior entries.
3. All raw data (hashes, inventories, listings, analysis output) lives under `research/`.
4. Never echo secrets (tokens, keys) into logs, docs, or commits.
5. The two bright lines: no license/activation circumvention, no code transplantation.

---

## 2026-10-15 — Session 1: workspace reset, source acquisition, structural analysis begins

- Wiped previous session artifacts (decompress project) per user instruction.
- Kept platform-managed files (.git workspace versioning, .env, skills/, upload/) intact.
- Created fresh structure: research/{downloads,extracted,windows-installed,windows-installer,
  mac-installer,inventory,docs,archive}, scripts/, tools/
- HEAD-probed all four R2 sources. Sizes: Part-1.zip 183,446,644 B; Part-2.zip 171,613,300 B;
  dmg 4,808,563 B; exe 2,837,784 B. Note: exe and dmg are far too small for full installers,
  likely stub/web downloaders. The two zips are the installed product payload.
- apt-get unavailable (no root). Installed 7-Zip 26.00 static Linux binary to tools/7zz.
- Launched parallel background downloads of all four sources (scripts/download_sources.sh).
- Wrote research docs skeleton: 00-README, 01-methodology, stubs 03-10, 09-findings-log.

(pending: merge zips, unpack installer/dmg, inventory sweep, component classification)

## Continued — Session 1 (same day, later)

- Downloaded all 4 sources; sizes verified byte-exact vs HEAD; SHA-256 in
  research/downloads/MANIFEST.txt (also in docs/02-sources-and-hashes.md).
- Merged Part-1 + Part-2 zips -> research/extracted/windows-installed/ (1,470 files,
  674M). Installed tree is Inno Setup based (unins000.exe present).
- Extracted NSIS win-installer stub -> EaseUS Download Manager v2.0.0 (web downloader).
- Solved the mac dmg: genuine UDIF (koly trailer, notarization plist). Built
  scripts/parse_udif_v2.py (empirical mish layout: blockCount@0x40, chunks@0xCC, 40B
  entries). Reconstructed 51.2MB GPT image with ZERO decode errors -> research/
  extracted/mac-installer/disk-image.bin. Contains Apple_HFS volume with Cocoa stub
  installer app. Mac analysis deferred (Windows first).
- Ran full inventory sweep -> research/inventory/files.csv (path,size,sha256,type),
  ext-histogram, dir-sizes, pe-files lists.
- Wrote docs: 02-sources-and-hashes.md, 03-component-inventory.md (full component map),
  13 findings appended to 09-findings-log.md.
- Key architecture findings: Qt Quick/QML UI (440 qml files); nine per-filesystem scan
  engine DLLs + RAWSearchDLL + raw_signs.json; hybrid 32/64-bit; kernel drivers
  (eprdtdrv.sys, EuMrx.sys NAS redirector); BUILDPE WinPE subsystem (177M); SaveScan
  save/resume subsystem (66M); FFmpeg 6.x video preview; file repair suite; cloud
  integrations (iCloud, Aliyun, Firebase); no .NET anywhere.

Next session:
1. PE import/export analysis for capability matrix (need readpe/pev or llvm tools —
   apt blocked, no root; use static binaries or Python pefile via pip/uv).
2. Strings sweep (feature enumeration, scan phase names, format lists).
3. raw_signs.json structure analysis (carving signature categories — read format only;
   our own signature DB will be built from published format specs).
4. BUILDPE layout + config file analysis.
5. Feature matrix research from public docs (free vs pro).
6. Project repo creation pending rotated GitHub token from user (old one exposed in
   chat twice; user instructed to revoke).
