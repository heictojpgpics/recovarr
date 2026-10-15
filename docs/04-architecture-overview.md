# Architecture Overview

High-level system architecture of the reference product, reconstructed from structural analysis — and the target architecture for Recovarr.

**Status:** reference architecture decoded (sessions 1-2); Recovarr target architecture v0 pending.

**Evidence base:** [03-component-inventory.md](03-component-inventory.md), [05-capability-matrix.md](05-capability-matrix.md), [09-findings-log.md](09-findings-log.md).

---

## 1. Reference product architecture (as shipped, 674 MB, 1,470 files)

```
┌────────────────────────────────────────────────────────────────────┐
│ DRW.exe (bootstrapper) → DRWUI.exe (Qt Widgets amd64, 30 MB)       │
│   • IObject in-proc component bus, Qt5 Widgets UI                  │
│   • Light/dark .rcc bundles (3,722 assets, 128 UI dirs)            │
│   • Licensing/activation, ads/ENS, telemetry, update checks        │
├────────────────────────────────────────────────────────────────────┤
│ Scan subsystem ("DRWIntelligentScan" — leaked internal name)       │
│   NTFSSearchDLL  FATSearchDLL  exFATSearchDLL  EXT4SearchDLL       │
│   BtrfsSearchDLL HFSPlusSearchDLL ReFSSearchDLL ZfsSearchDLL       │
│   ── EUCreate<FS>QuickSearcher / EUCreate<FS>Searcher factories ── │
│   RAWSearchDLL (carving: C++ analysers + raw_signs.json long tail) │
│   PE_Tools.dll (PE/executable analysis)   EURawImg.exe (raw image) │
├────────────────────────────────────────────────────────────────────┤
│ Privileged / kernel layer                                          │
│   DRWService.exe = BitlockerReadFVEService  \\.\Pipe\DRWBitlocker  │
│   eprdtdrv.sys (raw disk filter)   EuMrx.sys (SMB mini-redirector) │
│   setupdrvx64.exe (driver install helper, EPM-shared)              │
├────────────────────────────────────────────────────────────────────┤
│ Satellite processes (mostly 32-bit)                                │
│   File repair: EuRepairHost, Adobe/PDF/Archive/Img/Office repair   │
│     (ImageMagick CORE_RL_* + libheif + FFmpeg)                     │
│   VideoViewer.exe (FFmpeg 6 + ZeroMQ)   diskhealth/ (own Qt Quick) │
│   EUinApp.exe (purchase), EuDownloader, DRWReport (log bundler),   │
│   firebasefetch.exe (remote config), AliyunWrap* (crash/telemetry) │
├────────────────────────────────────────────────────────────────────┤
│ Bootable subsystem: BUILDPE/ (177 MB)                              │
│   WinPE + winxshell + Chrome-as-viewer + second engine copy        │
│   drivers epmdkdrv/EUDCPEPM/EUEDKEPM (EPM-shared platform)         │
├────────────────────────────────────────────────────────────────────┤
│ Scan persistence: SaveScan/*.rsf (16-B key header + records)       │
│ Signature DB: raw_signs.json (139 formats, confidence-scored)      │
└────────────────────────────────────────────────────────────────────┘
```

Key properties:

- **Engine/host split**: host owns device discovery, privileges, UI; engines are pure
  loadable searchers behind a two-call factory contract.
- **Two-tier carving**: dedicated C++ carvers for high-value formats, generic scored
  signature table for the long tail.
- **Privilege isolation by function**: one small service (BitLocker) + drivers; the rest
  runs unelevated. Elevation happens per-need (CreateProcessAsUser/WithToken).
- **Process-per-feature for heavy media**: repair and preview run in separate processes
  (crash isolation, bitness freedom).
- **Shared platform leverage**: WinPE stack shared with Partition Master product family.

## 2. Recovarr target architecture v0 (Rust + Tauri 2 + React/TS — draft)

```
┌──────────────────────────────────────────────────────────────────┐
│ recovarr-ui  (Tauri 2 WebView2 shell + React/TypeScript)         │
│   Home(8 modes) → Scan → Results → Preview → Recover             │
│   state: zustand + tanstack-query; virtualized result lists      │
├──────────────────────────────────────────────────────────────────┤
│ recovarr-core  (Rust, no-std-ish scan kernels + tokio runtime)   │
│   fs engines: ntfs/ fat/ exfat/ ext4/ btrfs/ hfsplus/ refs/ zfs  │
│     trait Searcher { quick(); deep(); stream_events() }          │
│   carving: carver-registry + signature-db (TOML, from specs)     │
│   pipeline: async sector reader → analyzers → scored findings    │
│   session: SQLite scan sessions, resumable cursors               │
│   preview: image/audio/video/doc extract-to-temp + mime map      │
├──────────────────────────────────────────────────────────────────┤
│ recovarr-elev (optional privileged helper service, per-need)     │
│   raw volume open, BitLocker FVEK via OS APIs, health reads      │
├──────────────────────────────────────────────────────────────────┤
│ Cargo workspace, CI on windows-latest, everything cross-tested   │
└──────────────────────────────────────────────────────────────────┘
```

Differences by design (see [01-methodology.md](01-methodology.md)):

- One process + tiny optional service (their tree runs a dozen exes); 64-bit only.
- Rust trait objects replace C++ RTTI analysers; analyser registry is data + tests.
- WebView2 UI replaces 30 MB Qt monolith (smaller, modern a11y, same declarative model).
- Open session format; no proprietary blobs.
- No ads/licensing/telemetry subsystems at all.
