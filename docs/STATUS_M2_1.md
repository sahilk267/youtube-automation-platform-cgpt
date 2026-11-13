> Historical status for **M2.1** only. For newer optional owner-reviewed M2.2 final exports and strictly PRIVATE M3 YouTube adapter, read `docs/STATUS_M2_2_M3.md`.

# ViralOS M2.1 verified capability status

| Capability | Reality |
|---|---|
| M0–M3 local research/script/studio prototype | Retained; test suite exercises baseline |
| Deterministic script → creative shot list | IMPLEMENTED; 2–12 shots; original text source, no invented facts |
| HOOK/EXPLANATION/PAYOFF and caption text | IMPLEMENTED; limited heuristic, **not** professional director AI |
| Per-shot owner WAV normalization and measured shot boundary | IMPLEMENTED; FFmpeg 16k mono, PCM16, 180ms pad |
| Segmented audio assembly with immutable hash | IMPLEMENTED; one bound voice file per plan |
| SRT sidecar file from measured segments | IMPLEMENTED; not word-level |
| Conservative existing claim-link to shot mapping | IMPLEMENTED; exact unique quotes only; fact verification remains manual |
| Captions from exact authored segments | IMPLEMENTED; measured boundaries, **not forced per-word alignment** |
| Hindi/English and other owner-reviewed script variants | IMPLEMENTED contract; only tested en-US/hi-IN, fonts/quality depend on OS |
| Optional Piper generation per shot | ADAPTER WIRED; mocked tests; **real installed model not tested** |
| Native natural narration quality | NOT VERIFIED; demo uses synthetic eSpeak |
| Full automatic translation and dubbing | NOT IMPLEMENTED |
| Real lip-sync and forced ASR word alignment | NOT IMPLEMENTED |
| 12 specialized domain visual directors | NOT IMPLEMENTED; launch sports illustrative renderer only |
| Viral clip reuse or licensed footage workflow | NOT IMPLEMENTED; no downloader / copyright bypass |
| Actual upload to YouTube | DISABLED |
| Professional finished video | NOT PROVEN; full editorial review needed |
| Exact target Windows i7 8th gen / 32GB | NOT TESTED in this container |

All reports explicitly mark `publish_ready: false`. Full tests include mocked adapters but no cloud data or real licensed game media.
