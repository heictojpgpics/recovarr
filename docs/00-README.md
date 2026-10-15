# Research Documentation Index

Functional analysis of EaseUS Data Recovery Wizard as a design reference for our own
original data recovery product (Rust + Tauri 2 + React/TypeScript).

**Read `01-methodology.md` first. It defines what this project does and does not do, and
it is binding for every agent working here.**

## Reading order

| # | File | Purpose | Status |
|---|------|---------|--------|
| 00 | `00-README.md` | This index | final |
| 01 | `01-methodology.md` | Clean-room rules, legal guardrails, toolchain plan | final |
| 02 | `02-sources-and-hashes.md` | Source files, provenance, sizes, SHA-256 | final |
| 03 | `03-component-inventory.md` | Every file in the product, classified | in progress |
| 04 | `04-architecture-overview.md` | Component map, tech stack findings, interconnections | pending |
| 05 | `05-capability-matrix.md` | OS APIs and system capabilities per component | pending |
| 06 | `06-feature-matrix.md` | Full feature set, free vs licensed, from public sources | pending |
| 07 | `07-scan-engine-analysis.md` | Behavioral analysis of scan/recovery pipeline | pending |
| 08 | `08-ux-flows.md` | Wizard flow, screens, states, UX patterns worth matching | pending |
| 09 | `09-findings-log.md` | Dated findings feed, newest last | live |
| 10 | `10-open-questions.md` | Open questions and how to resolve each | live |

## Where raw data lives

- `research/downloads/` — original source files, untouched, with MANIFEST.txt
- `research/extracted/` — unpacked trees (windows-installed, windows-installer, mac-installer)
- `research/inventory/` — machine-readable inventories (CSV, histograms, listings)
- `research/archive/` — superseded raw analysis output

## Related project artifacts

- `/home/z/my-project/worklog.md` — session-by-session work log
- The product repository (to be created once credentials are rotated) — original code only

## Ground rules recap

1. We document behavior, architecture concepts, formats, and feature scope. Functional level.
2. We never transplant code, decompiled logic, assets, strings, or branding into our product.
3. We never bypass or defeat license/activation checks. Locked features are studied from
   public documentation, marketing pages, and the free version's own UI.
4. Our implementation sources: Microsoft NTFS/FAT/exFAT specifications, $LogFile journal
   literature, file carving research (Garfinkel et al. and successors), and original work.
