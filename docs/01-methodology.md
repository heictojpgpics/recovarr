# 01 — Methodology: Clean-Room Functional Analysis

This document defines how this project studies EaseUS Data Recovery Wizard (hereafter
"the reference product") and builds our own product from what we learn. It exists to keep
the project legally defensible, ethically sound, and technically honest. Every agent
working on this project is bound by it. If a task seems to require violating anything in
this document, stop and reassess.

## 1. Goal

Understand, at a functional level, what a mature commercial data recovery product does:
its feature scope, architecture concepts, behavior, and edge-case coverage. Use that
understanding to design and build an original, free, open-source data recovery wizard
(Rust core + Tauri 2 + React/TypeScript) whose capability matches and then exceeds the
reference product.

## 2. What we extract from the reference product

- **Feature inventory**: every user-facing capability, including which are free vs
  license-gated (from the product's own UI, public documentation, and marketing pages).
- **Behavior**: scan phases, progress reporting granularity, pause/resume/cancel
  semantics, filter and search behavior, preview types, recovery output options,
  handling of damaged/encrypted/locked media.
- **Architecture concepts**: component decomposition (engine vs UI vs services vs
  drivers), inter-process communication patterns, how work is parallelized, how the UI
  stays responsive during long scans.
- **Format and protocol facts**: configuration formats, database files, log formats,
  which OS facilities each component uses (raw disk access, VSS, WMI, etc.).
- **Edge-case coverage**: what failure modes and unusual scenarios the product handles,
  which informs our test matrix.

## 3. What we never take

- **Decompiled logic transplanted into our code.** Translating decompiled code into
  Rust (or any language) is creating a derivative work. It does not matter that the
  language, runtime, or architecture differ. Our code is written from public
  specifications and behavioral requirements, not from their implementation internals.
- **Assets, strings, icons, dialogs, or pixel-level UI clones.** Trade dress and
  trademark law apply, and an original product needs an original identity anyway.
- **Anything obtained by defeating license enforcement.** We never patch, bypass,
  hook, or emulate activation or license checks, and we never run the product with
  defeated protection. What license-gated features *do* is a public question: the
  vendor documents its free/pro feature matrix extensively, and the free version's UI
  exposes the gated feature list. That is our source of truth.

## 4. Implementation sources (what our code is actually built from)

- Microsoft's published filesystem specifications: NTFS (including $MFT, $LogFile,
  $UsnJrnl structures), FAT32/exFAT (Microsoft spec documents, publicly published).
- Academic and practitioner literature: file carving (Garfinkel 2007 and successors),
  filesystem forensics texts, $LogFile journal replay papers, ext4 kernel docs.
- Open-source prior art studied for *design* with licenses respected (The Sleuth Kit,
  PhotoRec, scalpel): we read their design and write our own code.
- Original engineering: our own scan scheduling, caching, async architecture, UI.

Where a behavior of the reference product is unclear from black-box observation, we form
a hypothesis, verify it against public specifications, and implement from the
specification. Limited static inspection (imports, exports, strings, structural
metadata) is used to understand *what* components exist and *which* system facilities
they use, not to transcribe *how* algorithms are implemented internally.

## 5. Legal context, briefly (not legal advice)

- Reverse engineering for learning and interoperability has long-standing legal
  precedent (e.g., Sega v. Accolade; EU Directive 2009/24/EC Art. 6 interoperability
  exceptions), but most commercial EULAs prohibit reverse engineering, and
  enforceability of those clauses varies by jurisdiction.
- Keeping our artifacts at the functional/behavioral level (rather than reproducing
  code internals) is what keeps this defensible across jurisdictions.
- Anti-circumvention law (DMCA §1201 in the US, similar elsewhere) is unforgiving
  about defeating license checks, independent of copyright fair-use arguments.
  This is why §3's license line is absolute.
- Our product will carry fully original branding and will not reference the vendor's
  trademarks in its name, UI, or marketing.

## 6. Toolchain plan (phased)

Phase 1 (structural): file inventory, hashing, type identification, archive unpacking
(7-Zip 26.00 static, innoextract, msitools, cabextract as needed).

Phase 2 (component analysis): PE header/section/import/export analysis (readpe/pev,
llvm-readobj, objdump), .NET identification (monodis, ILSpyCmd if .NET components are
found), string extraction (FLOSS), packer detection (DIE).

Phase 3 (deep static): Ghidra headless, radare2/rizin for targeted questions only,
with the constraint of §3: output is functional descriptions, never transcribed
algorithm implementations destined for our codebase.

Phase 4 (behavioral): public documentation research, free-version UI observation,
published benchmarks and reviews. Dynamic analysis under Wine is possible if needed,
always on the free version, never touching license mechanisms.

Phase 5 (our product): Rust + Tauri 2 + React/TypeScript development, with GitHub
Actions Windows runners for CI/CD, test datasets, and benchmark harnesses.

## 7. Documentation discipline

- Every finding gets a dated entry in `09-findings-log.md`.
- Raw output is kept under `research/inventory/` or `research/archive/`, never deleted
  silently.
- Claims about the reference product must state their source (observation, static
  metadata, public docs). Speculation is marked as such.
- The worklog at the project root records every session.
