# Recovarr

**Open-source, free data recovery wizard for Windows** — Rust core + Tauri 2 (WebView2) + React/TypeScript canvas UI. No Electron, no browser bloat. macOS support planned after Windows GA.

This repository currently contains the **research & analysis phase**: a complete clean-room study of how a commercial-grade data recovery product is architected (component layout, scan engine design, UX flows, capability matrix), used strictly as *learning material* for designing our own original implementation. No third-party code is copied into this repository or into the product.

## Repository layout

```
research/
├── docs/                  # Research documentation (start at 00-README.md)
│   ├── 00-README.md       # Doc index + how to use these docs
│   ├── 01-methodology.md  # Clean-room rules (READ FIRST - legally binding)
│   ├── 02-sources-and-hashes.md
│   ├── 03-component-inventory.md
│   ├── 04-architecture-overview.md
│   ├── 05-capability-matrix.md
│   ├── 06-feature-matrix.md
│   ├── 07-scan-engine-analysis.md
│   ├── 08-ux-flows.md
│   ├── 09-findings-log.md     # Append-only log of verified findings
│   └── 10-open-questions.md
├── inventory/             # File inventories (metadata only: paths/sizes/hashes/types)
├── scripts/               # Analysis tooling we wrote (Python/bash)
└── worklog.md             # Session-by-session work log
```

## Ground rules (binding for all contributors & agents)

1. **Clean-room methodology** — see `docs/01-methodology.md`. We study architecture and *behavior* of commercial software to inform our own original design. We do not copy code, resources, strings tables, signature databases, or any copyrighted artifact into the product. Our implementations are written from public specifications (NTFS/FAT/exFAT/ext4/HFS+/ReFS specs, published file-format documentation, academic carving literature).
2. **Original code only** — every line in this repo is written by us or pulled from permissively-licensed dependencies (MIT/Apache-2.0/BSD) with attribution.
3. **No binaries from third-party proprietary software are committed.** Analysis artifacts are metadata (hashes, sizes, structure notes) only.

## Product goal (phase 1 — Windows)

- Recover deleted/lost files from internal disks, external HDDs/SSDs, SD cards, USB sticks
- File systems: NTFS (incl. MFT-based deep scan + $LogFile journal replay), FAT32/exFAT, ext4, HFS+ (read), ReFS (structure awareness), RAW carving for everything else
- Quick scan (metadata-based) + deep scan (signature carving) two-phase engine
- Scan session save/resume
- Preview (images, video, audio, documents, archives) before recovery
- Free and open source — **no paywalled features, no artificial limits**

Out of scope for phase 1 (later phases): bootable WinPE rescue media, NAS/RAID recovery, cloud recovery, crashed-PC rescue, disk health monitoring, VM image recovery.

## Status

- [x] Session 1: Source acquisition, structural analysis, component inventory, dmg format crack
- [ ] Session 2: PE capability matrix, strings sweep, raw signature DB format study, BUILDPE layout, feature matrix
- [ ] Rust core scaffolding, Tauri 2 shell, first NTFS reader

See `worklog.md` for the detailed track record.
