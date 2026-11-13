# Canonical specification relationship

Architecture source: immutable `spec/ViralOS_Launch_v3/` snapshot (v3.0.0). Do not edit canonical originals while implementing features.

Working code layers: original canonical SQLite migration 001–003, **additive M1/M3 implementation migration 004**, and **additive M2 Studio implementation migration 005**. The implemented Studio route/renderer/contracts are *not* claimed to be all Ultimate features; they are a carefully scoped CPU-only proof of real media composition.

Whenever the v3 design and this implementation differ, document the discrepancy, avoid silent behavioral assumptions, and preserve backward compatibility. Active code completion is reported in `docs/STATUS_M2.md` and `docs/M2_STUDIO_IMPLEMENTATION.md`.


## Additive M2.1 implementation note (2026-11-12)

The canonical `spec/ViralOS_Launch_v3` specification is unchanged. M2.1 introduces an **implementation-specific** deterministic script-to-shot draft and measured per-segment narration adapter (`docs/M2_1_DIRECTOR_IMPLEMENTATION.md`). It does not assert that Ultimate's automated creative intelligence or multilingual dubbing are complete. SQL migration 006 extends rather than replaces previous tables. All claims still require human evidence and rights review, and YouTube publishing stays disabled.
