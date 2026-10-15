# 09 — Findings Log

Dated findings, oldest first. Each entry states its evidence source.

## 2026-10-15

- **Source sizes confirmed via HTTP HEAD** (server: Cloudflare R2): Part-1.zip 183,446,644 B; Part-2.zip 171,613,300 B; mac dmg 4,808,563 B; win exe 2,837,784 B. The exe and dmg are far too small for full installers; consistent with stub/web-downloader installers. The two zips (~339 MB total) carry the actual installed payload. [source: HTTP HEAD metadata]

- **Product is Qt Quick/QML, not Widgets**: 440 QML + 146 qmlc files with Qt5 runtime. Direct conceptual parallel to our React/TS declarative UI approach; the reference product validates declarative UI for this product category. [source: file inventory]
- **Modular per-filesystem scan engine architecture**: nine search DLLs (NTFS, FAT, exFAT, EXT4, Btrfs, HFS+, ReFS, ZFS, RAW carving) + raw_signs.json signature DB. The engines are separate loadable modules — strong support for our per-filesystem Rust module design. [source: file inventory]
- **Hybrid 32/64-bit**: main UI 32-bit i386; drivers and BUILDPE components 64-bit. Our product will be native 64-bit only. [source: PE headers via file(1)]
- **Kernel drivers for raw access and NAS**: eprdtdrv.sys (partition recovery raw disk access, with Win7 legacy variant), EuMrx.sys (SMB mini-redirector for NAS recovery). [source: file inventory]
- **WinPE bootable media subsystem**: BUILDPE/ ships a full x64 WinPE environment (177M) with a second copy of the engines — bootable recovery is a first-class feature. [source: directory analysis]
- **File repair suite is separate executables**: Adobe/PDF, archive, image, video, office (incl. Hangul HWP), RAW image repair tools, each own process. [source: file inventory]
- **Cloud integrations**: iCloud recovery (7.2MB DLL), Aliyun OSS wrappers, Firebase remote config, crash dump uploader. [source: file inventory]
- **Video preview via FFmpeg 6.x** (avcodec-62/avformat-62/avfilter-11), PDF preview via pdfium, HEIF via heif.dll. [source: file inventory]
- **The Windows "installer" exe is an NSIS web-downloader stub** (EaseUS Download Manager v2.0.0, French locale, Aliyun download URLs). [source: 7zz extraction]
- **The mac dmg is a genuine UDIF image, notarized** (cdhashes plist + Apple CMS timestamp), containing a Cocoa stub installer app with fr/de/en/es localizations. Fully reconstructed to a 51.2MB GPT disk image with zero decode errors using our own parser. Note: its UDIF chunk type field says 0x80000005 while payload is verifiably zlib — decode must trust content sniffing, not type labels. [source: koly/blkx parse, HFS+ header]
- **Scan session save/resume** is a major subsystem (SaveScan/, 66M) — matching EaseUS behavior means our engine must support serializable scan state. [source: directory analysis]
- **Zero .NET assemblies**: entire product is native C/C++; .NET RE tooling not needed for this product. [source: file type inventory]
