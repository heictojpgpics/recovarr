# Scan Engine Analysis

Behavioral analysis of quick scan, deep scan, format support, progress semantics, pause/resume, recovery pipeline.

**Status:** architecture decoded (session 2); algorithm-level detail via public FS specs continues in later sessions.

**Related docs:** [05-capability-matrix.md](05-capability-matrix.md) (engine imports/exports),
[03-component-inventory.md](03-component-inventory.md) (module map), [06-feature-matrix.md](06-feature-matrix.md).

---

## 1. Two-phase scan model (confirmed at API level)

Every engine exposes `EUCreate<FS>QuickSearcher` and `EUCreate<FS>Searcher` (Btrfs names its
deep variant `ComplateSearcher` — typo preserved as evidence of origin). The UI flow strings
confirm the semantics:

1. **Quick scan** — filesystem metadata walk (MFT for NTFS, FAT chains, inode tables). Signals
   observed: `onQuickScanCompleted(int)`, `sigQuickScanFinished(int)`, `CQuickScanCompleteWnd`,
   `Auto-Recover after Advanced Scan Completed`.
2. **Deep scan ("Advanced Scan")** — starts where quick ends: string `Deep scan StartSector=%I64d,
   TotalSector=%I64d` (sector-range progress), `Advanced Scanning` asset folder. Runs the RAW
   carving engine over unallocated + slack + whole-volume as needed.

Progress semantics: sector-range based (`StartSector/TotalSector`), cancellable/pausable
(`pause scan`, `resume scan`, `stop scan` strings), with animated UI states
(`ScanProgress/PngSequence/ScanComplete`, `ScanStop`, `scanloading`).

## 2. Result organization model

From UI strings and RCC assets (see [08-ux-flows.md](08-ux-flows.md)):

- Top-level grouping: **Deleted Files** / **Existing Files** / **Lost Files** (raw/deep-scan
  finds), plus **Lost Partition** / **Unallocated** when partition recovery engages.
- Type filter tree (FileFilter.xml + config `Filter` section): Graphic (30+ extensions incl.
  all camera RAWs), Video, Audio, Document, Archive, Email, Other.
- `BuildTree/Organize` assets — the tree-building/reorganization pass has its own UI states.
- Bad-sector policy: "Program is trying to skip bad sectors to find data" — resilience-first read
  loop with skip-ahead.

## 3. Scan session persistence (.rsf)

- `SaveScan/` directory contains live sessions: `auto_<volume>_<datetime>.rsf`, e.g.
  `auto_Local Disk (H_)10_14_23_42_58.rsf` (52.7 MB — session size scales with found-file count).
- Container (structure-only analysis; contains a third party's file listings which we do not
  republish): 16-byte session key, counts, then length-prefixed records embedding 16-byte keys
  (path-hash-style) + numeric fields; some records high-entropy (compressed/encoded trees).
- UI semantics: "Load last scan session to save your time for rescanning.",
  `Click_Loadsession`, `Load Scan Session Successful, Scan files: %n`.
- **Recovarr plan:** our own open session format (SQLite or versioned binary) with: volume
  identity (disk GUID + offset), scan params, found-file table (path, size, mtime, source
  = metadata|carve, score), resume cursor (sector offset), and incremental append.

## 4. Filesystem coverage map

| FS | Quick scan | Deep scan | Notes |
|---|---|---|---|
| NTFS | yes (MFT) | yes | richest imports; $LogFile/USN journal work implied |
| FAT32 | yes | yes | `DelFat.log` "Fat heighClu" — high-cluster handling |
| exFAT | yes | yes | |
| ext4 | yes | yes | (ext2/3 implied via superblock compat) |
| Btrfs | yes | yes | |
| HFS+ | yes | yes | host-provided handle (no CreateFile imports) |
| ReFS | yes | yes | minimal import set — structure-aware |
| ZFS | yes | yes | 119 imported fns — pool/vdev awareness |
| RAW | — | always | 139-format signature table + dedicated C++ carvers |

BitLocker volumes: decrypted reads via `\\.\Pipe\DRWBitlocker` service (FVE key retrieval),
then treated as normal volumes by the engines. Encrypted-volume states surface in UI
(`system_lock/unlock` icons, `AutoDecrypt` flow assets).

## 5. Carving pipeline (RAWSearchDLL)

- Analyser registry: `EUGetAnalyserList/Map/Multimap` — runtime-queryable carver set.
- Two-tier: dedicated C++ carvers (see [05-capability-matrix.md §6](05-capability-matrix.md))
  for high-value formats; generic signature table (`raw_signs.json` schema) for the long tail.
- Scoring: per-signature confidence weights + min/max size plausibility gates; header+tail
  verification for 46 formats.
- Validation hooks visible in strings: `Exception:ZIP CalcRawSize(%d), office?%d`,
  `TiffAnalyzer GetMainTag tag=%d len=%u size=%u`, `Exception:OFFICE AnalyzeTag(%d)` —
  carvers parse internal structure to compute real file size (crucial for correct carving of
  fragmented/overwritten files).
- Repair-while-carving: `GetIMovMp4Repair` — damaged MP4/MOV get rebuilt during deep scan.

## 6. What we replicate (behavior), improve (design) — Recovarr engine spec v0

**Replicate (from observed behavior):**
- Quick/deep two-phase scan with uniform per-FS engine interface
- Metadata + carve result unification with source attribution and confidence scores
- Sector-range progress, pause/resume/stop, bad-sector skip policy
- Session save/load with resume cursors
- Type filter tree + deleted/existing/lost grouping
- Structure-aware carving (size computation from format internals, not just header match)

**Improve:**
- Pure-Rust, parallel (rayon) sector pipelines; io_uring-style overlapped I/O via
  `tokio::task::spawn_blocking` + vectored reads instead of MapViewOfFile
- Open documented session format instead of proprietary .rsf
- Signature DB in TOML/JSON with tests per signature (fuzz corpus), community-contributable
- No per-format upsell walls — everything free
- Memory-bounded scan (their engines map whole volumes; we chunk with LRU)
