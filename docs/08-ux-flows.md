# UX Flows

Wizard flow, screens, states, error handling patterns, UX standards worth matching or beating.

**Status:** structure mapped (session 2) from RCC resource taxonomy + strings; pixel-level pass pending.

**Primary evidence:** `inventory/rcc-resource-tree.txt` (3,722 assets, 128 UI directories),
`inventory/strings/classified.json`, `config/config.ini`.

---

## 1. Product shell

- Qt Widgets desktop app, custom frame (Titlebar assets: close/max/restore/normal/hover/pressed
  states, custom menu, share, helper), light + dark themes (drw_light.rcc / drw_dark.rcc).
- Brand fonts: DIN-Black / DINCond-Black (we will use an open font stack — e.g. Inter + a
  display face; DIN is licensed).
- Window: default 1240×840, min 800×600, high-DPI aware, opens maximized (config.ini
  `windowsSize`), per-locale font stacks (Segoe UI / Meiryo / Malgun Gothic / Microsoft YaHei).
- 22 languages shipped.

## 2. Home screen — 8 recovery modes (RCC `Home/nav`)

| Mode | Asset dir | Phase-1 for us? |
|---|---|---|
| PC recovery (internal disks) | `Home/nav/icoPC` | **yes** |
| SD card recovery | `Home/nav/icoSD`, `SDCard/` | **yes** |
| BitLocker volume recovery | `Home/nav/icoBitlocker`, `Home/Bitlocker/`, `PopWnd/Bitlocker/AutoDecrypt` | yes (free) |
| NAS recovery | `Home/nav/icoNAS`, `NASView/`, `NAS_linux/` | later |
| RAID recovery | `Home/nav/icoRAID`, `RaidView/` | later |
| Cloud drive recovery | `Home/nav/icoCloud`, `Cloud Drive/` | later |
| Crashed PC (WinPE boot) | `Home/nav/icoPE`, `PEView/` | later |
| Crashed PC (linux env) | `NAS_linux/` | later |

Device taxonomy (ImageResource.xml `DriveTypes`): system / external disk / USB existing+lost ×
locked+unlocked / partition existing+lost / camera (Sony icon), UAV/drone, SD, desktop, recycle
bin, folder, HD, tachograph/dashcam — the "location" mental model covers cameras, drones,
dashcams as first-class citizens.

## 3. Wizard flow (reconstructed)

1. **Home** — mode selection + location list (`Home` assets, `long button` hover/linkage
   animation sequences, `Introduction` first-run tips, `RecoveryChances` tips).
2. **Scanning** — `ScanProgress/`: sector-range progress, per-phase animations
   (`scanloading`, `Scanmove purple`, `Advanced Scanning`), scan-complete/stop sequences,
   pause/resume/stop controls, `Filter` panel becomes live (`Filter/filter_freeze`,
   `Filter/loading` sequences), bad-sector toast.
3. **Results** — `BuildTree/Organize` tree assembly animation; left tree (`LeftTree/` 199
   assets) with Deleted/Existing/Lost + Lost Partition/Unallocated groups; type filter
   (`Filter/`), search (`Search/`), sort; file list with `FileTypes/` per-type icons (105).
4. **Preview** — `Preview/` with per-type loading animations (LoadingImg/Video/Audio/Doc),
   document/image viewers, audio/video playback (VideoViewer satellite, FFmpeg-based),
   `ScanningMovable` for preview-while-scanning.
5. **Recover** — target selection (`PopWnd/Recover`, `Path/` 95 assets for path browsing),
   `Recovery/` progress, `PopWnd/finish` completion, `PopWnd/ruturehome` (return home),
   `Save/` for session save, `Auto-Recover` auto-recovery option.
6. **Repair** (secondary flow) — `file repair/` with Nav, repairing animations, PDF/Video
   repair modules (Repair/PDF, Repair/Video).
7. **Boot media** (secondary) — `PEView/` create/creating/createfinish sequences.

## 4. Monetization surfaces in the UX (to be deliberately removed in Recovarr)

- `Ad/` (32 assets) + ENS ad coordinates in config.ini + `gift/` + retention cards
  (`bg_Retention`, `Retention_card`) + `Evaluate/` rating prompts (anger/general/happy faces)
  + `PopWnd/ActivateBuy/` + `Titlebar/Activate/` + upsell toasts at every gate
  (`Scan_Click_Upgrade*`, `Recovering_Click_Upgrade*`...).
- Their free flow interrupts at: recovery >2 GB (hard stop), preview-only trial mode,
  NAS/Linux/SD features, doc/video repair.
- **Recovarr:** none of these. The "upgrade" moments become plain progress/feature moments.

## 5. Error handling & resilience patterns observed

- Bad-sector skip with user toast (transparent resilience).
- Crash-dump ring (Drwdump0-5.DMP) + log set (DRWUI.log, DefaultLog.txt, DelFat.log,
  BuildRaw.log) — support bundle assembly via DRWReport.exe + DRWReport.ini manifest.
- "Wait to filter again after scan completes" — live filtering deferred under load.
- Load-session fallback: "Last scan session found" on startup; session load failure surfaces
  as its own state (`Loadsessionfail`).
- `Tips/` assets — contextual guidance system (fifty-frame tip animations).

## 6. Standards worth matching (our baseline targets)

- Two-click start: pick location → Scan (single primary CTA per screen).
- Progressive disclosure: quick results visible while deep scan continues.
- Non-blocking previews during scan; per-type loading states.
- All progress cancellable/granular; nothing modal that takes minutes.
- Session resume offered automatically, not buried.

## 7. Standards we will beat

- No ad/gift/rating surfaces anywhere; no fake urgency.
- Dark/light/system theme tri-state from day one (they ship two static .rcc bundles).
- Real accessibility (keyboard nav, screen reader names, contrast) — their Qt Widgets setup
  has basic Qt a11y at best; React + aria gives us a stronger floor.
- Instant search across million-file result sets (virtualized lists, worker-side filtering).
- Honest empty states ("no files found because X" with next-step guidance).
