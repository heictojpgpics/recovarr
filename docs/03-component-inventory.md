# 03 — Component Inventory

Raw machine-readable inventory: `research/inventory/files.csv` (1,470 files: path,
size, sha256, file type), `ext-histogram.txt`, `dir-sizes.txt`, `pe-files.txt`.
This document is the human-readable classified map. All claims sourced from the
inventory data unless noted.

## Top-level statistics

- 1,470 files, 674 MB uncompressed (installed Windows tree, merged from Part-1/2 zips)
- PE binaries: 284 PE32 (i386) + 281 PE32+ (x64) — a hybrid 32/64-bit product
  (main UI is 32-bit; drivers, PE-environment components, and repair tools are 64-bit)
- UI: 440 QML + 146 qmlc (compiled QML) + 20 qmltypes files — the main UI is Qt Quick
  (declarative), plus 114 .qm translation catalogs
- No .NET assemblies detected; the product is fully native C/C++ (MSVC 2008/2013/2015+
  runtimes bundled; some components carry GNU gettext .mo catalogs indicating a
  MinGW/cross-platform heritage in the PartitionRecovery module)

## Directory map (by size)

| Directory | Size | Role (initial classification) |
|-----------|------|-------------------------------|
| BUILDPE/ | 177M | WinPE bootable media builder; ships a full x64 PE environment plus a copy of the recovery engines (`BUILDPE/EaseUS-x64/` duplicates the search DLLs, DRWUI, etc.) |
| VideoViewer/ | 100M | Video preview stack built on FFmpeg 6.x (avcodec-62, avformat-62, avfilter-11, etc.) |
| SaveScan/ | 66M | Scan-session save/resume subsystem (export/import scan results) |
| diskhealth/ | 55M | Disk health monitoring module (own Qt5Gui copy) |
| EUFileRepair/ | 46M | File repair subsystem runtime (7z.dll, UCRT shims, own tooling) |
| ResourceDark/ + Resource/ | 61M | UI assets, light and dark themes (themdark.ini config at root) |
| PartitionRecovery/ | 27M | Partition/disk recovery engine incl. BitLocker support and kernel drivers |
| language/ | 6.2M | Translations |
| platforms/, styles/, imageformats/, iconengines/ | ~3.7M | Qt runtime plugins (qwindows.dll etc.) |
| EuShare/ | 224K | Network-share redirector driver subsystem (EuMrx.sys) for NAS recovery |
| License/ | 160K | Licensing data |
| log/ | 120K | Runtime logs |
| config/ | 44K | Config: config.ini, RawConfig.ini, FilterFolder.ini, nasconfig.ini, PriorityDisplayType.xml, usefullostfiles.xml, version.ini |
| NasConfig/, NasCacheDirectory/ | 20K | NAS configuration/cache |

## Core processes (root)

| File | Size | Role |
|------|------|------|
| DRW.exe | 127K | Launcher |
| DRWUI.exe | 30.6M | Main UI (Qt Quick/QML, 32-bit) |
| DRWService.exe | 40K | Service wrapper |
| DRWReport.exe | 4.8M | Report/diagnostics tool |

## Filesystem scan engines (root, duplicated into BUILDPE/EaseUS-x64/)

One DLL per filesystem — the engine architecture is modular per-filesystem:
`NTFSSearchDLL.dll`, `FATSearchDLL.dll`, `exFATSearchDLL.dll`, `EXT4SearchDLL.dll`,
`BtrfsSearchDLL.dll`, `HFSPlusSearchDLL.dll`, `ReFSSearchDLL.dll`, `ZfsSearchDLL.dll`,
plus `RAWSearchDLL.dll` (signature-based carving) paired with `raw_signs.json`
(signature database, 35 KB) at root.

## Repair and preview tools (root)

`EUAdobeRepair.exe` (PDF), `EUArchiveRepair.exe`, `EUImgRepair.exe`, `EUVideoRepair.dll`,
`EUOfficeRepairWin32.exe` / `EuOfficeRepair.exe` / `EuOfficeTools.exe` /
`EUOfficeViewer.exe`, `EUHwpViewer.exe` + `EUHwpFilePathCheckerModule.dll` (Hangul
docs), `EURawImg.exe` (RAW camera images), `EUImageEnhance.dll`, `EuRepairHost.exe`,
`EUUnZip.exe`, `7za.exe`, `pdfium.dll` (PDF preview), `heif.dll` (HEIF preview).

## Cloud / online subsystem (root)

`EuICloudRecovery.dll` (iCloud recovery, 7.2M), `AliyunWrap.dll` + `AliyunWrapExe.exe`
+ `AliyunConfig.ini` (Alibaba Cloud OSS), `send_dmp_with_aliyun.exe` (crash dump
upload), `firebaseonlineconfig.dll` + `firebasefetch.exe` + `google-services.json`
(Firebase remote config/telemetry), `EuDownloader.exe` (component downloader),
`EuUserRate.dll`, `EUinApp.exe` (in-app purchase flow).

## Kernel drivers

| Driver | Location | Role |
|--------|----------|------|
| eprdtdrv.sys (+_win7older) | PartitionRecovery/ | Partition recovery device driver (raw disk access), with a Win7-older variant |
| EuMrx.sys | EuShare/ | Windows mini-redirector driver (network share access for NAS recovery) |
| epmdkdrv.sys, ebrntdrv.sys | BUILDPE/.../system32 | PE-environment drivers |
| EUEDKEPM.sys, EUDCPEPM.sys | BUILDPE/.../drivers | EPM-lineage drivers in PE environment |

## Notable runtime libraries (root)

Qt5 (Core 6.2M, Gui 7.2M, Widgets 5.6M, Qml, Quick...), OpenSSL in three generations
(1.0.x libeay32/ssleay32, 1.1 libssl/libcrypto x86+x64, 3.x x64), cpprest141_2_10.dll
(MS C++ REST SDK), libssh2 (SSH/SFTP), libzmq-mt-4_3_5 (ZeroMQ IPC), liblzma, libx265
(HEVC), zlib/zlib1, pdfium, msvcp90/120/140 + msvcr90/120/140 + ucrtbase.

## Config files of interest (root and config/)

`config/config.ini`, `config/RawConfig.ini` (carving engine config), `config/
FilterFolder.ini`, `config/nasconfig.ini`, `config/PriorityDisplayType.xml`,
`config/usefullostfiles.xml`, `config/version.ini`, `Upgrade.ini`, `DataFile.ini`,
`recoveryFree.ini`, `remote_config_data` (62K remote-config cache), `Dict`,
`EUUserData`, `raw_signs.json`, `needcopy.txt`, `style.css` (437K, suggests embedded
HTML views in some component).

## Status and next steps

- [x] File inventory with hashes (files.csv)
- [x] Directory map and rough classification
- [ ] Per-component PE import/export analysis (05-capability-matrix.md)
- [ ] String extraction and feature enumeration (06-feature-matrix.md)
- [ ] BUILDPE WinPE environment layout analysis (04-architecture-overview.md)
