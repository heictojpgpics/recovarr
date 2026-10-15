# 02 — Source Files, Provenance, and Hashes

All four source files were downloaded 2026-10-15 from the same Cloudflare R2 bucket
(`pub-f1a27c5e49e74a6f8f15960475387544.r2.dev`). Sizes verified byte-exact against HTTP
HEAD Content-Length before download; SHA-256 computed after download. The download
script and manifest live at `scripts/download_sources.sh` and
`research/downloads/MANIFEST.txt`.

## Manifest

| File | Original URL name | Bytes | SHA-256 |
|------|-------------------|-------|---------|
| `EaseUS-DRW-Part-1.zip` | EaseUS-Data-Recovery-Wizard-Part-1.zip | 183,446,644 | `af2d44077d53d3348ae6b57863a2cd31c6dcadb2b616af7a1b89e3c287e90a14` |
| `EaseUS-DRW-Part-2.zip` | EaseUS-Data-Recovery-Wizard-Part-2.zip | 171,613,300 | `91aa2dab86e3faa40306a36d3ccdff3e1c3b9df8d1d22a2dbb845675eb2c1e48` |
| `DRW-mac-installer.dmg` | datarecovery_free_Setup_20261015.17920523914876b6212563apz27289351.dmg | 4,808,563 | `6ccb507ea097eeb41b39218602f22a144b65c02b27e8865134d9ebcdbfe31270` |
| `DRW-win-installer.exe` | drw_fr_installer.17920523404316b6212556apz27289349.exe | 2,837,784 | `31469c17128d37c60d3bc1228b1bbc8f793a9d973bae42b16f25a8ce338b7e86` |

## What each source is

**Part-1.zip + Part-2.zip** — two disjoint halves of one installed EaseUS Data Recovery
Wizard for Windows tree (an Inno Setup installation; `unins000.exe` present). Merged at
`research/extracted/windows-installed/` = 1,470 files, 674 MB uncompressed. Timestamps
inside the zips run 2025-01 to 2026-10-15, indicating an installed snapshot taken
2026-10-15 (logs present: EPMLOG.log, reglog_win.txt, strutureReg.log).
[source: unzip listings, file inventory]

**DRW-win-installer.exe** — Nullsoft (NSIS) self-extracting stub. Contains the EaseUS
Download Manager v2.0.0 ("2free" channel, French locale): `EDownloader.exe`, language
INIs, skin.zip, and an Aliyun sub-kit. It is a web-downloader that fetches the real
installer at install time; not the full product payload. Extracted at
`research/extracted/windows-installer/`. [source: 7zz extraction, file listings]

**DRW-mac-installer.dmg** — genuine Apple UDIF disk image (koly trailer present,
notarization plist with cdhashes + Apple CMS timestamp signature appended). Reconstructed
losslessly to a 51,200,000-byte GPT disk image (`research/extracted/mac-installer/
disk-image.bin`) via our own UDIF parser (`scripts/parse_udif_v2.py`) with zero decode
errors. Contains one Apple_HFS volume holding a Cocoa stub app "Data Recovery Wizard
Installer.app" (localized fr/de/en/es). The Windows product is the analysis priority;
mac analysis is deferred. [source: koly header, blkx table, HFS+ volume header]

Note on the UDIF chunk type field: this dmg labels its zlib chunks type `0x80000005`
(nominally "bzip2" in some references) while the payload is unambiguously zlib
(`78 da` streams, adler32-verified by clean eof). We decode by content sniffing with
strict verification, not by trusting the type label. [source: empirical decode, all
chunks decoded with exact expected output lengths]
