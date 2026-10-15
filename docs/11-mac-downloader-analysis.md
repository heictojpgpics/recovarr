# 11 — Mac Installer Analysis: the DRW Downloader Stub

**Scope:** structural analysis of `DRW-mac-installer.dmg` (4,808,563 B, SHA-256 in
`docs/02-sources-and-hashes.md`). The DMG is **not** the product — it is a
1 MB-class Cocoa downloader stub ("Data Recovery Wizard Installer") that fetches
the real Mac product as a ZIP at runtime. Analysis is read-only and structural
(clean-room rules of `01-methodology.md` apply; no code transplantation).

Full volume listing: `inventory/mac-stub-hfs-filelist.txt`.

---

## 1. Container layers (all parsed with our own tools)

| Layer | Format | Tool | Result |
|---|---|---|---|
| 1 | UDIF DMG (koly trailer, notarization plist) | `scripts/parse_udif_v3.py` | 8 blkx mish tables, 51,200,000 B flat image |
| 2 | GPT + Apple_HFS partition (sector 40, 99,920 sectors) | GPT parse | volume "Data Recovery Wizard Installer" |
| 3 | HFS+ (block 4096, catalog B-tree 64 nodes) | `scripts/parse_hfsplus.py` | 86 records (58 files, 28 folders, 6,255,112 B payload) |
| 4 | Fat Mach-O (x86_64 + arm64) | `scripts/analyze_macho.py` | stub + libLog.dylib anatomy |

### Format notes recorded for our own tooling (from public specs + empirical validation)

- **UDIF mish table** (validated: chunk offset chains are contiguous):
  `sig 'mish'@0, SectorNumber u64@8, SectorCount u64@16, DataOffset u64@24`,
  CRC32 checksum block `@0x40`, **entries start `@0xCC`**, 40 B each:
  `type u32, comment u32, sector u64, count u64, offset u64, length u64`;
  terminator type `0xffffffff`. This DMG: 15 zlib chunks (7.4 MB), one raw
  1 MB chunk (incompressible region), 42.7 MB sparse (zero-fill).
- **HFS+ catalog record layout** (validated against known file sizes, e.g.
  PkgInfo = 8 B): `keyLength u16, parentID u32, nameLen u16, UTF-16BE name`;
  file record: `type s16@0, flags@2, reserved@4, fileID@8, 5×dates@12-31,
  BSDInfo@32-47, FinderInfo 40B@48-87, dataFork@88 (logicalSize u64,
  clumpSize u32, totalBlocks u32, 8×extents), resourceFork@168`.
  Node: `BTNodeDescriptor` 14 B (`kind s8@8`: leaf=-1, index=0, header=1),
  `numRecords u16@10`, record offsets at node end (reverse u16 array).
- **rsf-style lesson**: their installer is itself an example of "small stub +
  server-driven payload" — the pattern we can adopt for our own downloads.

## 2. What the stub is

- Bundle: `Data Recovery Wizard Installer.app`,
  `CFBundleIdentifier = com.easeus.downloaderformacdrw`, v2.0.0
  (build `02000020250311X`, built 2025-03-11, Xcode 13, macOS 12 SDK,
  min macOS 10.13). `NSAppTransportSecurity → NSAllowsArbitraryLoads = true`
  (permits plain-HTTP endpoints).
- Universal binary: x86_64 (462 KB slice) + arm64 (511 KB slice).
- Links only 8 dylibs: **libcurl.4**, own `libLog.dylib`, Foundation, AppKit,
  CoreFoundation, objc, libc++, libSystem — a pure Cocoa + curl app; no
  Electron/Qt on the Mac stub side.
- UI = classic 3-step wizard (nib-based): `ZZFirstViewCtl` (intro/EULA) →
  `ZZSecondViewCtl` (download with custom circular `ZZProgressView`) →
  `ZZThirdViewCtl` (install/finish), plus `ZZMessageWinCtl` dialogs and a
  `ZZMaskWindow` overlay. 20 `.lproj` localizations shipped.

## 3. Downloader architecture (method-level, from Mach-O symbols)

- `ZZDownloaderIDMan` (singleton): reads `config.plist` keys, parses the
  download-info JSON, persists downloader state under
  `Library/Application Support/EaseUSDownloader`, derives a cross-product
  "DownloaderID" **from the DMG filename** — the same stub is parameterized
  for every EaseUS Mac product (leftover `EaseUS NTFS Writer.app` string).
- `downloader` class (curl engine):
  `DoGetDownloadInfo:withVersion:AndInfoURL:` → 3-host failover API
  (`download{,2,3}.easeus.com/api2/.../Apicp/Drwdl202004/`),
  `GetRemoteFileSize:`, `DoDownloadFromURL:StartWith:AndEndPos:ToBuffer:`
  (**HTTP range resume**), `DownloadFile:AndNeedRetryOtherUrlIfFailed:`
  (URL failover), `CalcFileMd5:` + `CompareMD5:` (**payload verification**),
  background `DownloadThread`.
- `config.plist` (server-decoupled config): `DirectDownloadUrl`
  (`https://d1.easeus.com/macdrw/free/datarecovery_free.zip`), fallback URL,
  API host list, EULA/privacy/help URLs, edition "free", pid 26, and the
  **target bundle IDs: `com.easeus.datarecoverynet` +
  `com.easeus.datarecoveryloaderapp`** — i.e. the real Mac product is a
  .NET-based app plus a native loader (not the Qt stack used on Windows).
- Install flow (strings): `unzip -o "%@" -d "%@"` → checks
  `runningApplicationsWithBundleIdentifier:` (blocker dialog
  `KeyErrAppIsRunningInfo`) → `do shell script "rm -rf '%@' && mv -f '%@'
  '%@'" with administrator privileges` (osascript elevation to replace the
  app in `/Applications`) → also `hdiutil info -plist` for DMG-path installs.
  Reads `SystemVersion.plist` for OS gating (string "EI Capitan" for ≤10.11).

## 4. Telemetry & kill-switch (`libLog.dylib` + `log_config.json`)

- `libLog.dylib` (shared EaseUS logging dylib): curl + **IOKit** (hardware
  fingerprint) + Foundation; ships `log_config.json` with
  **double-base64-obfuscated Alibaba Cloud SLS credentials** embedded in a
  public download (endpoint `us-east-1.log.aliyuncs.com`, project
  `easeusinfo`, logstore `logstore_macdrw_installer_noip`, real
  `LTAI…` AccessKey — values redacted here; treat as compromised-by-design).
- Remote feature switch: `track.easeus.com/product/index.php?c=main&a=getstatus&pid=26`.

## 5. Implications for recovarr (design input, not copying)

1. **Stub installer pattern is worth adopting**: tiny notarized downloader +
   server-side URL/MD5 manifest + 3-host failover + range-resume + checksum
   verify. Our releases can publish a signed JSON manifest instead of
   embedding keys at all.
2. **Never embed telemetry credentials in binaries** — their SLS keys are
   effectively public. For us: opt-in, local-first logging; no secrets in
   clients; documented endpoints.
3. **macOS product targets .NET (`datarecoverynet`)** — cross-platform story
   differs from Windows Qt. Recovarr's Tauri/Rust stack gives us one codebase
   for both OSes, avoiding exactly this dual-stack maintenance cost.
4. **osascript admin elevation for /Applications replace** is the standard
   pattern; we can also consider plain user-level installs to
   ~/Applications to avoid privilege prompts entirely.
5. The stub gatekeeps nothing — no DRM logic in the stub; the free/pro split
   happens server-side (edition flag) and in the product itself.

---

## Session 4 addendum (2026-10-16): stub app identified — via our own engine

Re-verified on a fresh environment: re-downloaded the DMG, re-ran the
UDIF reconstruction (0 decode problems, 51,200,000 bytes), parsed the
GPT (1 partition: 'disk image' / Apple HFS+ GUID, sectors 40..99959),
then implemented the full HFS+ engine in data-wizard-rs (dw-hfs) and
scanned the volume with it.

Empirical HFS+ facts recorded while building the engine (all validated
against this volume, cross-cited to Apple hfs_format.h / TN1150):

| Structure | Empirical finding |
|---|---|
| B-tree node kinds | leaf = 0xFF (-1), header node = 0x01 (NOT 1/2/3 as first assumed) |
| Record types | folder = 1, file = 2, folder-thread = 3, file-thread = 4 |
| Folder record data | 88 bytes (28 hdr/dates + 16 BSDInfo + 44 more) |
| File record data | 248 bytes = the 88-byte base + dataFork(80)@88 + rsrcFork(80)@168 |
| Record census | type1=28 (27 folders + root), type2=58 (= VH fileCount), type3/4 threads 28/58 |
| Bitmap | LSB-first; free-run count vs header freeBlocks drifts by 1 block (tolerance documented) |
| Mystery block | bytes 44..84 contain a Unix-epoch timestamp (0x67CFCC96 = 2025-05-28); not interpreted |

**The stub app (the answer to the interrupted session-3 question):**

`Data Recovery Wizard Installer.app` — a small Cocoa *downloader wizard*,
NOT the recovery engine:

```
/Data Recovery Wizard Installer.app
  Contents/MacOS/Data Recovery Wizard Installer   (executable)
  Contents/Frameworks/libLog.dylib
  Contents/Info.plist, PkgInfo
  Contents/Log/log_config.json                    (634 B — downloader config)
  Contents/Resources/
    ZZ{First,Second,Third}ViewCtl.nib, ZZMessageWinCtl.nib  (Cocoa UI)
    iFirst/iSecond_01-04/iThird/iNetErr/iWarnning(.png|@2x), datarecovery_bkg@2x.png
    ~22 x <lang>.lproj/Localizable.strings        (22 languages)
/.background/datarecovery_bkg@2x.png, .VolumeIcon.icns, .DS_Store
/EULA and Privacy Policy.pdf
```

Conclusion: the DMG ships only the installer/downloader shell; the real
DRW engine for macOS is fetched by it at install time (mirrors the
Windows NSIS stub = EaseUS Download Manager v2.0.0 finding).

Toolchain note: the HFS+ work was done with dw-hfs (our Rust engine) +
python for empirical layout dumps — no proprietary code, icons or
strings entered any repository; only structural facts.
